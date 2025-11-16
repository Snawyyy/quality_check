#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Script to automatically fill recommendations table
Features:
- Progress tracking
- Data validation
- Detailed reporting
- Error handling
Created by: Eitan
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

class TableFiller:
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
        print("\n📁 Loading data files...")
        
        # Load Complot CSV
        print("  • Loading Complot data...")
        self.complot_df = pd.read_csv(self.complot_path)
        self.complot_df.columns = self.complot_df.columns.str.strip()
        
        # Load Layer Excel
        print("  • Loading Layer data...")
        self.layer_df = pd.read_excel(self.layer_path)
        self.layer_df.columns = self.layer_df.columns.str.strip()
        
        # Load Recommendations Excel
        print("  • Loading Recommendations template...")
        self.rec_df = pd.read_excel(self.recommendations_path)
        
        print(f"\n📊 Data loaded successfully:")
        print(f"  • Complot records: {len(self.complot_df)}")
        print(f"  • Layer records: {len(self.layer_df)}")
        print(f"  • Recommendations rows: {len(self.rec_df)}")
        
        self.report.append(f"Data Loading Summary:")
        self.report.append(f"- Complot records: {len(self.complot_df)}")
        self.report.append(f"- Layer records: {len(self.layer_df)}")
        self.report.append(f"- Recommendations template rows: {len(self.rec_df)}")
        
    def clean_data(self):
        """Clean and standardize data"""
        print("\n🧹 Cleaning and standardizing data...")
        
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
        
        print("  ✓ Data cleaning completed")
    
    def process_matches(self):
        """Process and match records between Complot and Layer"""
        print("\n🔄 Processing matches...")
        
        # Initialize filled dataframe
        self.filled_df = pd.DataFrame()
        
        # Get all unique file links
        complot_links = set(self.complot_df['קישור לקובץ'].dropna().unique())
        layer_links = set(self.layer_df['קישור לקובץ'].dropna().unique())
        all_links = complot_links | layer_links
        
        print(f"  • Found {len(all_links)} unique file links")
        print(f"    - In Complot only: {len(complot_links - layer_links)}")
        print(f"    - In Layer only: {len(layer_links - complot_links)}")
        print(f"    - In both: {len(complot_links & layer_links)}")
        
        self.report.append(f"\nFile Link Analysis:")
        self.report.append(f"- Total unique links: {len(all_links)}")
        self.report.append(f"- Complot only: {len(complot_links - layer_links)}")
        self.report.append(f"- Layer only: {len(layer_links - complot_links)}")
        self.report.append(f"- In both sources: {len(complot_links & layer_links)}")
        
        # Process each link
        rows = []
        perfect_matches = 0
        partial_matches = 0
        
        for i, link in enumerate(sorted(all_links), 1):
            if i % 50 == 0:
                print(f"  • Processed {i}/{len(all_links)} links...")
            
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
        
        print(f"\n✓ Processing completed:")
        print(f"  • Perfect matches: {perfect_matches}")
        print(f"  • Partial matches: {partial_matches}")
        print(f"  • Total rows generated: {len(self.filled_df)}")
        
        self.report.append(f"\nMatch Results:")
        self.report.append(f"- Perfect matches: {perfect_matches}")
        self.report.append(f"- Partial matches: {partial_matches}")
        self.report.append(f"- Total rows: {len(self.filled_df)}")
    
    def save_results(self, output_path):
        """Save the filled table and report"""
        print(f"\n💾 Saving results...")
        
        # Save filled table
        self.filled_df.to_excel(output_path, index=False)
        print(f"  ✓ Filled table saved to: {output_path}")
        
        # Save report
        report_path = output_path.replace('.xlsx', '_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("Automatic Table Filling Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write("\n".join(self.report))
        print(f"  ✓ Report saved to: {report_path}")
        
        return output_path, report_path
    
    def run(self, output_path):
        """Execute the complete filling process"""
        print("\n" + "=" * 70)
        print("AUTOMATIC TABLE FILLING SCRIPT")
        print("=" * 70)
        
        try:
            self.load_data()
            self.clean_data()
            self.process_matches()
            filled_path, report_path = self.save_results(output_path)
            
            print("\n" + "=" * 70)
            print("✅ PROCESS COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print(f"\n📄 Output files:")
            print(f"  1. Filled table: {Path(filled_path).name}")
            print(f"  2. Report: {Path(report_path).name}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main execution function"""
    # File paths
    complot_path = '/mnt/user-data/uploads/קומפלוט.csv'
    layer_path = '/mnt/user-data/uploads/שכבה.xlsx'
    recommendations_path = '/mnt/user-data/uploads/המלצות_טיוב.xlsx'
    output_path = '/mnt/user-data/outputs/המלצות_טיוב_מלא.xlsx'
    
    # Create filler instance and run
    filler = TableFiller(complot_path, layer_path, recommendations_path)
    success = filler.run(output_path)
    
    return success

if __name__ == "__main__":
    main()
