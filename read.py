import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import os
import json
import datetime
from operator import itemgetter
from tkinter import messagebox
import pandas as pd

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

class FolderBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EMERSON LOG SUMMARY")

        # first frame

        frame = ttk.Labelframe(root, text="Configuration")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw", columnspan=7)

        self.max_test_label = tk.Label(frame, text="Max Testing :")
        self.max_test_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.max_test_display = tk.Entry(frame, text="", width=15 )
        self.max_test_display.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.max_test_display.insert(0, "3")

        self.upload_button = tk.Button(frame, text="Folder", command=self.upload_folder, width=57)
        self.upload_button.grid(row=1, column=3, padx=10, pady=10, columnspan=4)

        self.dir_label = tk.Label(frame, text="Directory :")
        self.dir_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.dir_display = tk.Entry(frame, text="", width=88)
        self.dir_display.grid(row=2, column=2, padx=10, pady=10, columnspan=5)
        self.dir_display.insert(0, "")
        self.dir_display.config(state=tk.DISABLED)

        # second frame

        frame2 = ttk.Labelframe(root, text="Log File Summary")
        frame2.grid(row=3, column=0, padx=10, pady=10, sticky="nw", columnspan=7)

        # row

        self.total_log_label = tk.Label(frame2, text="Total Logfile :")
        self.total_log_label.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        Tooltip(self.total_log_label, "Number of total log file (.txt) in the folder")

        self.total_log_display = tk.Entry(frame2, text="", width=15 )
        self.total_log_display.grid(row=4, column=2, padx=10, pady=10, sticky="w")
        self.total_log_display.insert(0, "")
        self.total_log_display.config(state=tk.DISABLED)

        self.total_pcb_label = tk.Label(frame2, text="Total Serial :",)
        self.total_pcb_label.grid(row=4, column=3, padx=10, pady=10, sticky="w")
        Tooltip(self.total_pcb_label, "Number of unique serial number")

        self.total_pcb_display = tk.Entry(frame2, text="", width=15)
        self.total_pcb_display.grid(row=4, column=4, padx=10, pady=10, sticky="w")
        self.total_pcb_display.insert(0, "")
        self.total_pcb_display.config(state=tk.DISABLED)
        # third frame

        frame3 = ttk.Labelframe(root, text="Yield Data")
        frame3.grid(row=4, column=0, padx=10, pady=10, sticky="nw", columnspan=7)

        # row

        self.total_passed_label = tk.Label(frame3, text="Total Passed :")
        self.total_passed_label.grid(row=8, column=1, padx=10, pady=10, sticky="nw")
        Tooltip(self.total_passed_label, "Total passed (UNIQUE) with multiple test. i.e : (PASS-PASS-*PASS : 1), (FAIL-FAIL-*PASS : 1), (FAIL-*PASS-FAIL : 1)")

        self.total_passed_display = tk.Entry(frame3, text="", width=15)
        self.total_passed_display.grid(row=8, column=2, padx=10, pady=10, sticky="nw")
        self.total_passed_display.insert(0, "")
        self.total_passed_display.config(state=tk.DISABLED)

        self.total_passed_listbox = tk.Listbox(frame3, width=30, height=5)
        self.total_passed_listbox.grid(row=8, column=3, rowspan=2, padx=10, pady=10, sticky="w", columnspan=2)
        self.total_passed_listbox.bind("<Button-3>", self.copy_all_to_clipboard_2)


        self.not_first_passed_label = tk.Label(frame3, text="False Passed :",)
        self.not_first_passed_label.grid(row=8, column=5, padx=10, pady=10, sticky="nw")
        Tooltip(self.not_first_passed_label, "Total duplicate passed with multiple test. i.e : (*PASS-*PASS-PASS : 2), (FAIL-FAIL-PASS : 0), (FAIL-*PASS-PASS : 1)")

        self.not_first_passed_display = tk.Entry(frame3, text="", width=15)
        self.not_first_passed_display.grid(row=8, column=6, padx=10, pady=10, sticky="nw")
        self.not_first_passed_display.insert(0, "")
        self.not_first_passed_display.config(state=tk.DISABLED)
        
        # row

        self.false_reject_label = tk.Label(frame3, text="False Reject :",)
        self.false_reject_label.grid(row=9, column=5, padx=10, pady=10, sticky="nw")
        Tooltip(self.false_reject_label, "Total FAILED with PASSED test (NOT UNIQUE). i.e : (*FAIL-PASS-PASS : 1), (PASS-*FAIL-*FAIL : 2), (*FAIL-*FAIL-PASS: 2)")

        self.false_reject_display = tk.Entry(frame3, text="", width=15)
        self.false_reject_display.grid(row=9, column=6, padx=10, pady=10, sticky="nw")
        self.false_reject_display.insert(0, "")
        self.false_reject_display.config(state=tk.DISABLED)

        # row

        self.true_reject_label = tk.Label(frame3, text="True Reject :")
        self.true_reject_label.grid(row=10, column=1, padx=10, pady=10, sticky="nw")
        Tooltip(self.true_reject_label, "Total failed (UNIQUE) with multiple/single test. i.e : (FAIL-*FAIL : 1), (*FAIL : 1), (FAIL-PASS : 0)")

        self.true_reject_display = tk.Entry(frame3, text="", width=15)
        self.true_reject_display.grid(row=10, column=2, padx=10, pady=10, sticky="nw")
        self.true_reject_display.insert(0, "")
        self.true_reject_display.config(state=tk.DISABLED)
        
        self.true_reject_listbox = tk.Listbox(frame3, width=30, height=5)
        self.true_reject_listbox.grid(row=10, column=3, padx=10, pady=10, sticky="w", columnspan=2)
        self.true_reject_listbox.bind("<Button-3>", self.copy_all_to_clipboard_3)

        self.uncounted_test_label = tk.Label(frame3, text="Uncounted Test :",)
        self.uncounted_test_label.grid(row=10, column=5, padx=10, pady=10, sticky="nw")
        Tooltip(self.uncounted_test_label, "File exceed number of test trial")

        self.uncounted_test_display = tk.Entry(frame3, text="", width=15)
        self.uncounted_test_display.grid(row=10, column=6, padx=10, pady=10, sticky="nw")
        self.uncounted_test_display.insert(0, "")
        self.uncounted_test_display.config(state=tk.DISABLED)

        # row

        self.first_passed_label = tk.Label(frame3, text="First Passed :")
        self.first_passed_label.grid(row=11, column=1, padx=10, pady=10, sticky="nw")
        Tooltip(self.first_passed_label, "Total passed (UNIQUE) with single test.")

        self.first_passed_display = tk.Entry(frame3, text="", width=15)
        self.first_passed_display.grid(row=11, column=2, padx=10, pady=10, sticky="nw")
        self.first_passed_display.insert(0, "")
        self.first_passed_display.config(state=tk.DISABLED)
        
        self.first_passed_listbox = tk.Listbox(frame3, width=30, height=5)
        self.first_passed_listbox.grid(row=11, column=3, padx=10, pady=10, sticky="w", columnspan=2)
        self.first_passed_listbox.bind("<Button-3>", self.copy_all_to_clipboard_1)

        # row

        self.early_passed_label = tk.Label(frame3, text="Early Passed :")
        self.early_passed_label.grid(row=12, column=1, padx=10, pady=10, sticky="nw")
        Tooltip(self.early_passed_label, "Total passed with failed last test (UNIQUE), multiple test. i.e : (*PASS-FAIL : 1), (FAIL-PASS : 0), (FAIL-PASS-PASS : 0)")

        self.early_passed_display = tk.Entry(frame3, text="", width=15)
        self.early_passed_display.grid(row=12, column=2, padx=10, pady=10, sticky="nw")
        self.early_passed_display.insert(0, "")
        self.early_passed_display.config(state=tk.DISABLED)
        
        self.early_passed_listbox = tk.Listbox(frame3, width=30, height=5)
        self.early_passed_listbox.grid(row=12, column=3, padx=10, pady=10, sticky="w", columnspan=2)
        self.early_passed_listbox.bind("<Button-3>", self.copy_all_to_clipboard_4)

    def upload_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dir_display.config(state=tk.NORMAL)
            self.dir_display.delete(0, tk.END)
            self.dir_display.insert(0, folder_selected)
            self.dir_display.config(state=tk.DISABLED)
            self.analyst_information(folder_selected)

    def analyst_information(self, folder):
        files = os.listdir(folder)
        txt_files_count = len([file for file in files if file.endswith('.txt')])

        self.total_log_display.config(state=tk.NORMAL)
        self.total_log_display.delete(0, tk.END)
        self.total_log_display.insert(0, txt_files_count)
        self.total_log_display.config(state=tk.DISABLED)

        summaries = []
        for file in files:
            file_path = os.path.join(folder, file)
            if file_path.endswith('.txt'):
                summary = self.display_file_content(file_path, file)
                summaries.append(summary)

        self.calculateYield(summaries, folder)

    def display_file_content(self, file_path, file):
        failure = []
        summary = {
            "Operator": "", 
            "Serial Number": "", 
            "Start Date": "", 
            "Execution time": "", 
            "Part Number": "", 
            "UUT Result": "",
            "Log File": file,
            "failure":[]
        }
        with open(file_path, 'r') as file:
            for line in file:
                # Print each line (you can process each line as needed)
                stripped_line = line.strip()
                # search_strings = ['Operator:','Serial Number:','Start Date:','Start Time:', 'Execution Time:','UUT Result:','Part Number:']
                if 'Operator:' in stripped_line:
                    summary['Operator'] = stripped_line.replace('Operator:', '').strip()
                elif 'Serial Number:' in stripped_line:
                    summary['Serial Number'] = stripped_line.replace('Serial Number:', '').strip()
                elif 'Start Date:' in stripped_line:
                    stripped_line = stripped_line.replace('/', '-').strip()
                    summary['Start Date'] = stripped_line.replace('Start Date:', '').strip()
                elif 'Start Time:' in stripped_line:
                    summary['Start Date'] = summary['Start Date'] + ' ' + stripped_line.replace('Start Time:', '').strip()
                elif 'Execution Time:' in stripped_line:
                    summary['Execution time'] = stripped_line.replace('Execution Time:', '').strip()
                elif 'Part Number:' in stripped_line:
                    summary['Part Number'] = stripped_line.replace('Part Number:', '').strip()
                elif 'UUT Result:' in stripped_line:
                    summary['UUT Result'] = stripped_line.replace('UUT Result:', '').strip()
                elif 'FAILED' in stripped_line or 'failed' in stripped_line or 'terminated' in stripped_line:
                    failure.append(stripped_line)
        summary['failure'] = failure
        return summary
    
    def calculateYield(self, data, folder):
        
        try:
            max_trial = int(self.max_test_display.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer.")
            return
        
        sorted_data = self.sortedData(data)

        unique_serial = []
        existing_serial_numbers = {item['Serial Number'] for item in unique_serial}
        uncountedTest = 0

        for item in sorted_data:

            serialNumber = item['Serial Number']
            if item['UUT Result'].upper() == 'PASSED':
                result = 'PASSED'
            else:
                result = 'FAILED'

            if serialNumber in existing_serial_numbers: #1
                for item1 in unique_serial:
                    if item1['Serial Number'] == serialNumber and item1['Checked'] >= max_trial:
                        item['Test Number'] = 'MAX TRIAL EXCEED'
                        uncountedTest = uncountedTest + 1
                        break
                    elif item1['Serial Number'] == serialNumber and item1['Checked'] < max_trial:
                    
                        _result = item1['Result']
                        _result.append(result)
                        item1['Checked'] = item1['Checked'] + 1
                        item1['Result'] = _result
                        item['Test Number'] = item1['Checked']
                        break
            else: #2
                item['Test Number'] = 1
                unique_serial.append({
                    "Serial Number" : serialNumber,
                    "Checked" : 1,
                    "Result" : [result]
                })
                existing_serial_numbers = {item['Serial Number'] for item in unique_serial}

        # Create DataFrame from summaries
        df = pd.DataFrame(sorted_data)
        excel_file = folder + '/Data Summary.xlsx'
        if os.path.exists(excel_file):
            os.remove(excel_file)  # Delete if the file already exists
        df.to_excel(excel_file, index=False)

        serialCategory = {
            "first passed" : [],
            "total passed" : [],
            "true reject" : [],
            "passed not last" : []
        }

        firstPassed = 0
        totalPassed = 0
        falsePassed = 0
        falseReject = 0
        trueReject = 0
        passNotInLast = 0

        for item in unique_serial:
            serialNumber = item['Serial Number']
            results = item['Result']
            if len(results) == 1 and results[0] == 'PASSED':
                firstPassed = firstPassed + 1
                totalPassed = totalPassed + 1
                serialCategory['first passed'].append(serialNumber)
                serialCategory['total passed'].append(serialNumber)
            elif len(results) == 1 and results[0] == 'FAILED':
                trueReject = trueReject + 1
                serialCategory['true reject'].append(serialNumber)
            elif len(results) > 1:
                _passed = False
                _falseReject = 0
                _countPassed = 0
                for i in range(len(results)):
                    if results[i] == 'PASSED':
                        _countPassed = _countPassed + 1
                        _passed = True
                    else:
                        _falseReject = _falseReject + 1
                
                if _countPassed > 1:
                    falsePassed = falsePassed + _countPassed - 1
                # to check if exist passed
                if _passed:
                    totalPassed = totalPassed + 1
                    falseReject = falseReject + _falseReject
                    serialCategory['total passed'].append(serialNumber)
                    # to check pass not at least try
                    if results[len(results)-1] == 'FAILED':
                        passNotInLast = passNotInLast + 1
                        serialCategory['passed not last'].append(serialNumber)
                else:
                    trueReject = trueReject + 1
                    serialCategory['true reject'].append(serialNumber)
        
        self.false_reject_display.config(state=tk.NORMAL)
        self.false_reject_display.delete(0, tk.END)
        self.false_reject_display.insert(0, falseReject)
        self.false_reject_display.config(state=tk.DISABLED)

        self.first_passed_display.config(state=tk.NORMAL)
        self.first_passed_display.delete(0, tk.END)
        self.first_passed_display.insert(0, firstPassed)
        self.first_passed_display.config(state=tk.DISABLED)

        self.total_passed_display.config(state=tk.NORMAL)
        self.total_passed_display.delete(0, tk.END)
        self.total_passed_display.insert(0, totalPassed)
        self.total_passed_display.config(state=tk.DISABLED)

        self.true_reject_display.config(state=tk.NORMAL)
        self.true_reject_display.delete(0, tk.END)
        self.true_reject_display.insert(0, trueReject)
        self.true_reject_display.config(state=tk.DISABLED)

        self.early_passed_display.config(state=tk.NORMAL)
        self.early_passed_display.delete(0, tk.END)
        self.early_passed_display.insert(0, passNotInLast)
        self.early_passed_display.config(state=tk.DISABLED)
        
        total_pcb = totalPassed + trueReject

        self.total_pcb_display.config(state=tk.NORMAL)
        self.total_pcb_display.delete(0, tk.END)
        self.total_pcb_display.insert(0, total_pcb)
        self.total_pcb_display.config(state=tk.DISABLED)

        self.not_first_passed_display.config(state=tk.NORMAL)
        self.not_first_passed_display.delete(0, tk.END)
        self.not_first_passed_display.insert(0, falsePassed)
        self.not_first_passed_display.config(state=tk.DISABLED)

        # total_log_file = int(self.total_log_display.get())
        # uncounted_test = total_log_file - totalPassed - falseReject - trueReject

        self.uncounted_test_display.config(state=tk.NORMAL)
        self.uncounted_test_display.delete(0, tk.END)
        self.uncounted_test_display.insert(0, uncountedTest)
        self.uncounted_test_display.config(state=tk.DISABLED)
        
        self.first_passed_listbox.delete(0, tk.END)
        for item in serialCategory['first passed']:
            self.first_passed_listbox.insert(tk.END, item)
        
        self.total_passed_listbox.delete(0, tk.END)
        for item in serialCategory['total passed']:
            self.total_passed_listbox.insert(tk.END, item)
        
        self.true_reject_listbox.delete(0, tk.END)
        for item in serialCategory['true reject']:
            self.true_reject_listbox.insert(tk.END, item)
        
        self.early_passed_listbox.delete(0, tk.END)
        for item in serialCategory['passed not last']:
            self.early_passed_listbox.insert(tk.END, item)

    def sortedData(self, data):
        # convert to datetime format
        for item in data:
            item['Start Date'] = datetime.datetime.strptime(item['Start Date'], '%Y-%m-%d %H:%M:%S')
        # sorted data by datetime
        sorted_data = sorted(data, key=lambda x: x['Start Date'])
        # re-convert to string format
        for item in sorted_data:
            item['Start Date'] = item['Start Date'].strftime('%Y-%m-%d %H:%M:%S')

        return sorted_data
                
    def copy_all_to_clipboard_1(self, event):
        items = self.first_passed_listbox.get(0, tk.END)  # Get all items from the listbox
        items_text = ",".join(items)  # Concatenate items into a single string
        
        self.root.clipboard_clear()
        self.root.clipboard_append(items_text)
        messagebox.showinfo("Copied", "All items copied to clipboard.")
                
    def copy_all_to_clipboard_2(self, event):
        items = self.total_passed_listbox.get(0, tk.END)  # Get all items from the listbox
        items_text = ",".join(items)  # Concatenate items into a single string
        
        self.root.clipboard_clear()
        self.root.clipboard_append(items_text)
        messagebox.showinfo("Copied", "All items copied to clipboard.")
                
    def copy_all_to_clipboard_3(self, event):
        items = self.true_reject_listbox.get(0, tk.END)  # Get all items from the listbox
        items_text = ",".join(items)  # Concatenate items into a single string
        
        self.root.clipboard_clear()
        self.root.clipboard_append(items_text)
        messagebox.showinfo("Copied", "All items copied to clipboard.")
                
    def copy_all_to_clipboard_4(self, event):
        items = self.early_passed_listbox.get(0, tk.END)  # Get all items from the listbox
        items_text = ",".join(items)  # Concatenate items into a single string
        
        self.root.clipboard_clear()
        self.root.clipboard_append(items_text)
        messagebox.showinfo("Copied", "All items copied to clipboard.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FolderBrowserApp(root)
    root.mainloop()
