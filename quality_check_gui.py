#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI for Quality Check - Automatic Table Filling System
Allows users to select input files and output location with a simple interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
from datetime import datetime
import threading
import os

warnings.filterwarnings('ignore')

class TableFiller:
    """Modular table filling functionality that can be used independently"""
    
    def __init__(self, complot_path, layer_path, recommendations_path):
        self.complot_path = complot_path
        self.layer_path = layer_path
        self.recommendations_path = recommendations_path
        self.complot_df = None
        self.layer_df = None
        self.rec_df = None
        self.filled_df = None
        self.report = []

    def clean_numeric_field(self, value):
        """Clean numeric fields, handling <Null> and other non-numeric values"""
        if pd.isna(value) or value == '<Null>' or value == 'nan' or value == '':
            return np.nan
        try:
            return float(value)
        except:
            return value

    def compare_values(self, val1, val2):
        """Compare two values with smart handling of types and nulls"""
        # Both NaN = equal
        if pd.isna(val1) and pd.isna(val2):
            return True
        # One NaN = not equal
        if pd.isna(val1) or pd.isna(val2):
            return False
        # Convert to string and strip for comparison
        str1 = str(val1).strip().lower()
        str2 = str(val2).strip().lower()
        return str1 == str2

    def load_data(self):
        """Load all data files"""
        # Load Complot CSV
        self.complot_df = pd.read_csv(self.complot_path)
        self.complot_df.columns = self.complot_df.columns.str.strip()

        # Load Layer Excel
        self.layer_df = pd.read_excel(self.layer_path)
        self.layer_df.columns = self.layer_df.columns.str.strip()

        # Load Recommendations Excel
        self.rec_df = pd.read_excel(self.recommendations_path)

    def clean_data(self):
        """Clean and standardize data"""
        # Clean numeric fields
        numeric_fields = ['חלקה', 'מגרש', 'גוש']

        for field in numeric_fields:
            if field in self.layer_df.columns:
                self.layer_df[field] = self.layer_df[field].apply(self.clean_numeric_field)
            if field in self.complot_df.columns:
                self.complot_df[field] = self.complot_df[field].apply(self.clean_numeric_field)

        # Clean text fields
        text_fields = ['כתובת', 'קישור לקובץ']
        for field in text_fields:
            if field in self.layer_df.columns:
                self.layer_df[field] = self.layer_df[field].apply(
                    lambda x: x.strip() if isinstance(x, str) else x
                )
            if field in self.complot_df.columns:
                self.complot_df[field] = self.complot_df[field].apply(
                    lambda x: x.strip() if isinstance(x, str) else x
                )

    def process_matches(self):
        """Process and match records between Complot and Layer"""
        # Initialize filled dataframe
        self.filled_df = pd.DataFrame()

        # Get all unique file links
        complot_links = set(self.complot_df['קישור לקובץ'].dropna().unique())
        layer_links = set(self.layer_df['קישור לקובץ'].dropna().unique())
        all_links = complot_links | layer_links

        # Process each link
        rows = []
        perfect_matches = 0
        partial_matches = 0

        for link in sorted(all_links):
            row = {}

            # Get complot data
            complot_match = self.complot_df[self.complot_df['קישור לקובץ'] == link]
            if not complot_match.empty:
                c = complot_match.iloc[0]
                row['מהקומפלוט - \nקישור לקובץ'] = c.get('קישור לקובץ', '')
                row['מהקומפלוט - \nדיסק'] = c.get('דיסק', '')
                row['מהקומפלוט - \nמשלוח'] = c.get('משלוח', '')
                row['מהקומפלוט - \nארגז'] = c.get('ארגז', '')
                row['מהקומפלוט - \nתיק בניין'] = c.get('תיק בניין', '')
                row['מהקומפלוט - \nמספר בקשה'] = c.get('מספר בקשה', '')
                row['מהקומפלוט - \nגוש'] = c.get('גוש', '')
                row['מהקומפלוט - \nחלקה'] = c.get('חלקה', '')
                row['מהקומפלוט - \nמגרש'] = c.get('מגרש', '')
                row['מהקומפלוט - \nכתובת'] = c.get('כתובת', '')

            # Get layer data
            layer_match = self.layer_df[self.layer_df['קישור לקובץ'] == link]
            if not layer_match.empty:
                l = layer_match.iloc[0]
                row['מהשכבה - \nקישור לקובץ'] = l.get('קישור לקובץ', '')
                row['מהשכבה - \nגוש\nלפי בדיקה גאוגרפית'] = l.get('גוש', '')
                row['מהשכבה - \nחלקה\nלפי בדיקה גאוגרפית'] = l.get('חלקה', '')
                row['מהשכבה - \nמגרש\nלפי בדיקה גאוגרפית'] = l.get('מגרש', '')
                row['מהשכבה - \nכתובת\nלפי בדיקה גאוגרפית'] = l.get('כתובת', '')

            # Perform comparisons if both sources have data
            if not complot_match.empty and not layer_match.empty:
                c = complot_match.iloc[0]
                l = layer_match.iloc[0]

                row['השוואה - \nקישור לקובץ\n(הערך החד ערכי\nהתוצאה חייבת\nלהיות TRUE)'] = True

                # Compare fields
                gush_match = self.compare_values(c.get('גוש'), l.get('גוש'))
                helka_match = self.compare_values(c.get('חלקה'), l.get('חלקה'))
                migrash_match = self.compare_values(c.get('מגרש'), l.get('מגרש'))
                address_match = self.compare_values(c.get('כתובת'), l.get('כתובת'))

                row['השוואה - \nגוש'] = gush_match
                row['השוואה - \nחלקה'] = helka_match
                row['השוואה - \nמגרש'] = migrash_match
                row['השוואה - \nכתובת'] = address_match

                # Add notes for discrepancies
                discrepancies = []
                if not gush_match:
                    discrepancies.append(f"גוש ({c.get('גוש')} ≠ {l.get('גוש')})")
                if not helka_match:
                    discrepancies.append(f"חלקה ({c.get('חלקה')} ≠ {l.get('חלקה')})")
                if not migrash_match:
                    discrepancies.append(f"מגרש ({c.get('מגרש')} ≠ {l.get('מגרש')})")
                if not address_match:
                    discrepancies.append(f"כתובת")

                if discrepancies:
                    row['הערות'] = "אי התאמה: " + ", ".join(discrepancies)
                    partial_matches += 1
                else:
                    row['הערות'] = "התאמה מלאה"
                    perfect_matches += 1
            elif not complot_match.empty:
                row['הערות'] = "נמצא בקומפלוט בלבד"
            elif not layer_match.empty:
                row['הערות'] = "נמצא בשכבה בלבד"

            rows.append(row)

        self.filled_df = pd.DataFrame(rows)

        return perfect_matches, partial_matches, len(self.filled_df)

    def save_results(self, output_path):
        """Save the filled table and report"""
        # Save filled table
        self.filled_df.to_excel(output_path, index=False)

        # Save report
        report_path = output_path.replace('.xlsx', '_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("Automatic Table Filling Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Complot file: {self.complot_path}\n")
            f.write(f"Layer file: {self.layer_path}\n")
            f.write(f"Recommendations file: {self.recommendations_path}\n")
            f.write(f"Output file: {output_path}\n")
            
        return output_path, report_path

    def run(self, output_path):
        """Execute the complete filling process"""
        self.load_data()
        self.clean_data()
        perfect_matches, partial_matches, total_rows = self.process_matches()
        filled_path, report_path = self.save_results(output_path)
        
        return {
            'perfect_matches': perfect_matches,
            'partial_matches': partial_matches,
            'total_rows': total_rows,
            'filled_path': filled_path,
            'report_path': report_path
        }


class QualityCheckGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quality Check - Automatic Table Filling System")
        self.root.geometry("600x400")
        
        # Variables for file paths
        self.complot_path_var = tk.StringVar()
        self.layer_path_var = tk.StringVar()
        self.rec_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        
        # Status variable
        self.status_var = tk.StringVar(value="Ready to start")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Quality Check - Automatic Table Filling System", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Complot file selection
        ttk.Label(main_frame, text="Complot CSV File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.complot_path_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_complot).grid(row=1, column=2, pady=5)
        
        # Layer file selection
        ttk.Label(main_frame, text="Layer Excel File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.layer_path_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_layer).grid(row=2, column=2, pady=5)
        
        # Recommendations template file selection
        ttk.Label(main_frame, text="Recommendations Template:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.rec_path_var, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_rec).grid(row=3, column=2, pady=5)
        
        # Output location
        ttk.Label(main_frame, text="Output Excel File:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_path_var, width=50).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=4, column=2, pady=5)
        
        # Run button
        self.run_button = ttk.Button(main_frame, text="Run Quality Check", command=self.run_process)
        self.run_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Progress/status bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Result text area
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(8, weight=1)
        
        # Scrollable text area for results
        self.result_text = tk.Text(result_frame, height=8, width=70)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
    
    def browse_complot(self):
        file_path = filedialog.askopenfilename(
            title="Select Complot CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.complot_path_var.set(file_path)
    
    def browse_layer(self):
        file_path = filedialog.askopenfilename(
            title="Select Layer Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.layer_path_var.set(file_path)
    
    def browse_rec(self):
        file_path = filedialog.askopenfilename(
            title="Select Recommendations Template Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.rec_path_var.set(file_path)
    
    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Output Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.output_path_var.set(file_path)
    
    def run_process(self):
        # Validate inputs
        if not self.complot_path_var.get():
            messagebox.showerror("Error", "Please select Complot CSV file")
            return
        if not self.layer_path_var.get():
            messagebox.showerror("Error", "Please select Layer Excel file")
            return
        if not self.rec_path_var.get():
            messagebox.showerror("Error", "Please select Recommendations template file")
            return
        if not self.output_path_var.get():
            messagebox.showerror("Error", "Please select output file location")
            return
        
        # Disable run button during processing
        self.run_button.config(state=tk.DISABLED)
        self.status_var.set("Processing...")
        self.progress['value'] = 0
        
        # Run in separate thread to keep UI responsive
        threading.Thread(target=self._process_thread, daemon=True).start()
    
    def _process_thread(self):
        try:
            # Create filler instance and run
            filler = TableFiller(
                self.complot_path_var.get(),
                self.layer_path_var.get(),
                self.rec_path_var.get()
            )
            
            result = filler.run(self.output_path_var.get())
            
            # Update UI in main thread
            self.root.after(0, self._update_ui_success, result)
            
        except Exception as e:
            # Handle errors in main thread
            self.root.after(0, self._update_ui_error, str(e))
    
    def _update_ui_success(self, result):
        self.progress['value'] = 100
        self.status_var.set("Process completed successfully!")
        
        # Display results
        result_text = f"""Process completed successfully!

Results:
- Perfect matches: {result['perfect_matches']}
- Partial matches: {result['partial_matches']} 
- Total rows: {result['total_rows']}

Output files:
- Filled table: {result['filled_path']}
- Report: {result['report_path']}
"""
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text)
        
        # Re-enable run button
        self.run_button.config(state=tk.NORMAL)
        
        # Show completion message
        messagebox.showinfo("Success", "Quality check completed successfully!")
    
    def _update_ui_error(self, error_message):
        self.progress['value'] = 0
        self.status_var.set("Error occurred")
        
        # Display error
        error_text = f"Error occurred during processing:\n\n{error_message}"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, error_text)
        
        # Re-enable run button
        self.run_button.config(state=tk.NORMAL)
        
        # Show error message
        messagebox.showerror("Error", f"An error occurred:\n{error_message}")


def main():
    root = tk.Tk()
    app = QualityCheckGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()