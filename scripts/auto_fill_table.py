#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to automatically fill the recommendations table by comparing Complot and Layer data
Created by: Eitan
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def clean_numeric_field(value):
    """Clean numeric fields, handling <Null> and other non-numeric values"""
    if pd.isna(value) or value == '<Null>' or value == 'nan':
        return np.nan
    try:
        return float(value)
    except:
        return value

def compare_values(val1, val2):
    """Compare two values, handling NaN and type differences"""
    # If both are NaN, consider them equal
    if pd.isna(val1) and pd.isna(val2):
        return True
    # If one is NaN and the other isn't, they're not equal
    if pd.isna(val1) or pd.isna(val2):
        return False
    # Convert to string for comparison to avoid type issues
    return str(val1).strip() == str(val2).strip()

def main():
    print("=" * 70)
    print("Starting automatic table filling process...")
    print("=" * 70)
    
    # File paths
    complot_path = '/mnt/user-data/uploads/קומפלוט.csv'
    layer_path = '/mnt/user-data/uploads/שכבה.xlsx'
    recommendations_path = '/mnt/user-data/uploads/המלצות_טיוב.xlsx'
    output_path = '/mnt/user-data/outputs/המלצות_טיוב_מלא.xlsx'
    
    # Read files
    print("\n📁 Reading input files...")
    complot_df = pd.read_csv(complot_path)
    layer_df = pd.read_excel(layer_path)
    rec_df = pd.read_excel(recommendations_path)
    
    print(f"  • Complot records: {len(complot_df)}")
    print(f"  • Layer records: {len(layer_df)}")
    print(f"  • Recommendations table rows: {len(rec_df)}")
    
    # Clean column names
    complot_df.columns = complot_df.columns.str.strip()
    layer_df.columns = layer_df.columns.str.strip()
    
    # Clean numeric fields in layer data
    layer_df['חלקה'] = layer_df['חלקה'].apply(clean_numeric_field)
    layer_df['מגרש'] = layer_df['מגרש'].apply(clean_numeric_field)
    layer_df['גוש'] = layer_df['גוש'].apply(clean_numeric_field)
    
    # Clean numeric fields in complot data
    complot_df['חלקה'] = complot_df['חלקה'].apply(clean_numeric_field)
    complot_df['מגרש'] = complot_df['מגרש'].apply(clean_numeric_field)
    complot_df['גוש'] = complot_df['גוש'].apply(clean_numeric_field)
    
    # Create a new DataFrame for the filled recommendations
    filled_df = rec_df.copy()
    
    print("\n🔄 Processing matches and filling table...")
    
    # Get unique file links from both sources
    all_file_links = set()
    if 'קישור לקובץ' in complot_df.columns:
        all_file_links.update(complot_df['קישור לקובץ'].dropna().unique())
    if 'קישור לקובץ' in layer_df.columns:
        all_file_links.update(layer_df['קישור לקובץ'].dropna().unique())
    
    # Process each unique file link
    matches_found = 0
    rows_filled = 0
    
    for i, file_link in enumerate(all_file_links):
        if pd.isna(file_link):
            continue
            
        # Find matching records in complot
        complot_match = complot_df[complot_df['קישור לקובץ'] == file_link]
        
        # Find matching records in layer
        layer_match = layer_df[layer_df['קישור לקובץ'] == file_link]
        
        if not complot_match.empty or not layer_match.empty:
            # If we need more rows, add them
            if i >= len(filled_df):
                new_row = pd.Series(dtype=object)
                filled_df = pd.concat([filled_df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Fill complot data
            if not complot_match.empty:
                row = complot_match.iloc[0]
                filled_df.loc[i, 'מהקומפלוט - \nקישור לקובץ'] = row.get('קישור לקובץ', '')
                filled_df.loc[i, 'מהקומפלוט - \nדיסק'] = row.get('דיסק', '')
                filled_df.loc[i, 'מהקומפלוט - \nמשלוח'] = row.get('משלוח', '')
                filled_df.loc[i, 'מהקומפלוט - \nארגז'] = row.get('ארגז', '')
                filled_df.loc[i, 'מהקומפלוט - \nתיק בניין'] = row.get('תיק בניין', '')
                filled_df.loc[i, 'מהקומפלוט - \nמספר בקשה'] = row.get('מספר בקשה', '')
                filled_df.loc[i, 'מהקומפלוט - \nגוש'] = row.get('גוש', '')
                filled_df.loc[i, 'מהקומפלוט - \nחלקה'] = row.get('חלקה', '')
                filled_df.loc[i, 'מהקומפלוט - \nמגרש'] = row.get('מגרש', '')
                filled_df.loc[i, 'מהקומפלוט - \nכתובת'] = row.get('כתובת', '')
            
            # Fill layer data
            if not layer_match.empty:
                row = layer_match.iloc[0]
                filled_df.loc[i, 'מהשכבה - \nקישור לקובץ'] = row.get('קישור לקובץ', '')
                filled_df.loc[i, 'מהשכבה - \nגוש\nלפי בדיקה גאוגרפית'] = row.get('גוש', '')
                filled_df.loc[i, 'מהשכבה - \nחלקה\nלפי בדיקה גאוגרפית'] = row.get('חלקה', '')
                filled_df.loc[i, 'מהשכבה - \nמגרש\nלפי בדיקה גאוגרפית'] = row.get('מגרש', '')
                filled_df.loc[i, 'מהשכבה - \nכתובת\nלפי בדיקה גאוגרפית'] = row.get('כתובת', '')
            
            # Perform comparisons
            if not complot_match.empty and not layer_match.empty:
                matches_found += 1
                complot_row = complot_match.iloc[0]
                layer_row = layer_match.iloc[0]
                
                # Compare file link (should always be TRUE if we're here)
                filled_df.loc[i, 'השוואה - \nקישור לקובץ\n(הערך החד ערכי\nהתוצאה חייבת\nלהיות TRUE)'] = True
                
                # Compare גוש (Block)
                filled_df.loc[i, 'השוואה - \nגוש'] = compare_values(
                    complot_row.get('גוש'), 
                    layer_row.get('גוש')
                )
                
                # Compare חלקה (Parcel)
                filled_df.loc[i, 'השוואה - \nחלקה'] = compare_values(
                    complot_row.get('חלקה'), 
                    layer_row.get('חלקה')
                )
                
                # Compare מגרש (Plot)
                filled_df.loc[i, 'השוואה - \nמגרש'] = compare_values(
                    complot_row.get('מגרש'), 
                    layer_row.get('מגרש')
                )
                
                # Compare כתובת (Address)
                filled_df.loc[i, 'השוואה - \nכתובת'] = compare_values(
                    complot_row.get('כתובת'), 
                    layer_row.get('כתובת')
                )
                
                # Add note if there are discrepancies
                discrepancies = []
                if not compare_values(complot_row.get('גוש'), layer_row.get('גוש')):
                    discrepancies.append('גוש')
                if not compare_values(complot_row.get('חלקה'), layer_row.get('חלקה')):
                    discrepancies.append('חלקה')
                if not compare_values(complot_row.get('מגרש'), layer_row.get('מגרש')):
                    discrepancies.append('מגרש')
                if not compare_values(complot_row.get('כתובת'), layer_row.get('כתובת')):
                    discrepancies.append('כתובת')
                
                if discrepancies:
                    filled_df.loc[i, 'הערות'] = f"אי התאמה ב: {', '.join(discrepancies)}"
            
            rows_filled += 1
    
    # Remove completely empty rows from the end
    filled_df = filled_df.dropna(how='all')
    
    # Save the filled table
    print(f"\n💾 Saving filled table to: {output_path}")
    filled_df.to_excel(output_path, index=False)
    
    # Print summary statistics
    print("\n📊 Summary Statistics:")
    print(f"  • Total unique file links processed: {len(all_file_links)}")
    print(f"  • Matches found (in both sources): {matches_found}")
    print(f"  • Total rows filled: {rows_filled}")
    
    # Check for discrepancies
    if 'השוואה - \nגוש' in filled_df.columns:
        gush_matches = filled_df['השוואה - \nגוש'].sum()
        print(f"\n  • גוש (Block) matches: {gush_matches}/{matches_found}")
    if 'השוואה - \nחלקה' in filled_df.columns:
        helka_matches = filled_df['השוואה - \nחלקה'].sum()
        print(f"  • חלקה (Parcel) matches: {helka_matches}/{matches_found}")
    if 'השוואה - \nמגרש' in filled_df.columns:
        migrash_matches = filled_df['השוואה - \nמגרש'].sum()
        print(f"  • מגרש (Plot) matches: {migrash_matches}/{matches_found}")
    if 'השוואה - \nכתובת' in filled_df.columns:
        address_matches = filled_df['השוואה - \nכתובת'].sum()
        print(f"  • כתובת (Address) matches: {address_matches}/{matches_found}")
    
    print("\n✅ Process completed successfully!")
    print(f"📄 Output file saved as: המלצות_טיוב_מלא.xlsx")
    
    return filled_df

if __name__ == "__main__":
    result_df = main()
