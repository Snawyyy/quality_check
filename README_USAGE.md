# מדריך שימוש - סקריפט מילוי טבלה אוטומטי
# Automatic Table Filling Script - Usage Guide

## תיאור כללי / Overview
סקריפט זה ממלא אוטומטית את טבלת המלצות הטיוב על ידי השוואת נתונים מקובץ הקומפלוט (CSV) וקובץ השכבה (Excel).

This script automatically fills the recommendations table by comparing data from the Complot CSV file and the Layer Excel file.

## קבצים נדרשים / Required Files
1. **קומפלוט.csv** - קובץ נתוני המקור הראשי
2. **שכבה.xlsx** - קובץ נתוני השכבה מ-GIS
3. **המלצות_טיוב.xlsx** - טבלת ההמלצות הריקה (template)

## הרצת הסקריפט / Running the Script

### אופציה 1: סקריפט בסיסי / Basic Script
```bash
python3 auto_fill_table.py
```

### אופציה 2: סקריפט משופר / Enhanced Script
```bash
python3 auto_fill_enhanced.py
```

## תוצרים / Output Files
1. **המלצות_טיוב_מלא.xlsx** - הטבלה המלאה עם כל הנתונים
2. **המלצות_טיוב_מלא_report.txt** - דוח מפורט של התהליך

## מה הסקריפט עושה / What the Script Does

### 1. טעינת נתונים / Data Loading
- קורא את כל שלושת הקבצים
- מנקה ומתקנן את הנתונים

### 2. התאמת רשומות / Record Matching
- מוצא את כל הקישורים הייחודיים לקבצים
- מתאים רשומות בין הקומפלוט לשכבה לפי "קישור לקובץ"

### 3. השוואות / Comparisons
השוואה של השדות הבאים:
- **גוש** (Block)
- **חלקה** (Parcel)
- **מגרש** (Plot)
- **כתובת** (Address)

### 4. סימון אי-התאמות / Discrepancy Marking
- מסמן TRUE/FALSE לכל השוואה
- מוסיף הערות כאשר יש אי-התאמות

## סטטיסטיקות מהריצה האחרונה / Last Run Statistics
- **סה"כ קישורים ייחודיים**: 360
- **נמצאו בשני המקורות**: 161
- **התאמות מושלמות**: 31
- **התאמות חלקיות**: 130
- **רק בקומפלוט**: 195
- **רק בשכבה**: 4

## התאמות מיוחדות / Special Adjustments
- מטפל בערכים ריקים ו-<Null>
- משווה ערכים תוך התעלמות מרווחים ואותיות גדולות/קטנות
- מזהה ומדווח על כל אי-התאמה בפירוט

## דוגמה לשימוש מתקדם / Advanced Usage Example

אם תרצה לשנות את נתיבי הקבצים, ערוך את השורות הבאות בסקריפט:

```python
# File paths
complot_path = '/path/to/your/קומפלוט.csv'
layer_path = '/path/to/your/שכבה.xlsx'
recommendations_path = '/path/to/your/המלצות_טיוב.xlsx'
output_path = '/path/to/output/המלצות_טיוב_מלא.xlsx'
```

## טיפול בבעיות / Troubleshooting

### בעיה: קידוד עברית
פתרון: הסקריפט כבר מוגדר לעבוד עם UTF-8

### בעיה: חוסר התאמות רבות
פתרון: בדוק שהשדה "קישור לקובץ" זהה בשני הקבצים

### בעיה: ערכים לא מזוהים
פתרון: הסקריפט מטפל אוטומטית ב-<Null>, NaN, וערכים ריקים

## יצירת קשר / Contact
נוצר על ידי: איתן
תאריך: נובמבר 2025
