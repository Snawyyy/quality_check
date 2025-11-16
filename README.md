# Quality Check - Automatic Table Filling System

A comprehensive data validation and comparison tool for land registry and property management systems. This application compares data between multiple sources to identify discrepancies in property records.

## Features

- **Data Comparison**: Compares property data between CSV and Excel sources
- **Discrepancy Detection**: Identifies mismatches in block numbers, parcel numbers, plot numbers, and addresses
- **User-Friendly GUI**: Simple interface for file selection and processing
- **Detailed Reporting**: Generates comprehensive reports with statistics and discrepancies
- **Standalone Executable**: Available as a Windows executable requiring no Python installation

## Components

### Core Scripts
- `scripts/auto_fill_table.py`: Basic implementation of the comparison logic
- `scripts/auto_fill_enhanced.py`: Enhanced version with progress tracking and detailed reporting
- `quality_check_gui.py`: Graphical user interface application

### Input Files
The system requires three input files:
- **Complot CSV**: Main source data file (CSV format)
- **Layer Excel**: GIS layer data file (Excel format)
- **Recommendations Template**: Excel template for output (Excel format)

### Output
- **Filled Excel Table**: Results with comparison data
- **Detailed Report**: Text file with processing statistics

## Prerequisites

- Python 3.8+ (for running scripts directly)
- pandas
- numpy

For the standalone executable, no prerequisites are needed.

## Installation

### Using Standalone Executable (Recommended)
1. Download the latest release
2. Run `QualityCheckGUI.exe`
3. No installation required

### From Source
1. Clone the repository
2. Install dependencies: `pip install pandas numpy`
3. Run the GUI: `python quality_check_gui.py`

## Usage

### GUI Application
1. Select the Complot CSV file
2. Select the Layer Excel file
3. Select the Recommendations template Excel file
4. Specify output location for results
5. Click "Run Quality Check"

### Command Line (Advanced)
Use the scripts in the `scripts/` directory for command line processing:
- `python scripts/auto_fill_table.py`
- `python scripts/auto_fill_enhanced.py`

## Data Fields Comparison

The system compares the following property fields:
- **Block Number** (גוש)
- **Parcel Number** (חלקה)
- **Plot Number** (מגרש)
- **Address** (כתובת)
- **File Link** (קישור לקובץ)

## Sample Data Format

### Complot CSV
Expected columns: `קישור לקובץ`, `גוש`, `חלקה`, `מגרש`, `כתובת`, etc.

### Layer Excel
Expected columns: `קישור לקובץ`, `גוש`, `חלקה`, `מגרש`, `כתובת`, etc.

### Recommendations Template
Expected columns: Various comparison and output fields.

## Output Format

The output Excel file contains:
- Data from both sources
- Comparison results (TRUE/FALSE) for each field
- Discrepancy notes
- Summary information

## Building from Source

To create your own executable:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "QualityCheckGUI" quality_check_gui.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## Support

For support, please file an issue in the repository or contact the maintainers.

## Version History

- 1.0.0: Initial release with basic and enhanced scripts
- 1.1.0: Added GUI application
- 1.2.0: Added standalone executable build