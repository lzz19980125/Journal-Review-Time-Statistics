# Journal Review Time Statistics

A Python tool for automatically extracting and analyzing review process timelines from academic journal articles (PDF format). This tool helps researchers understand the typical review duration of different journals by extracting submission, revision, and acceptance dates from PDF files.

## Features

- 📄 **Automatic PDF Text Extraction**: Uses PyMuPDF (fitz) to extract text from PDF files
- 🔍 **Multi-Format Support**: Compatible with multiple journal formats including:
  - Elsevier journals (e.g., "Received in revised form" format)
  - IEEE journals (e.g., "revised" format)
- 📊 **Comprehensive Statistics**: Calculates mean, median, minimum, and maximum review times
- ⏱️ **Dual Time Units**: Displays results in both days and months (30 days/month)
- 🎯 **Smart Date Recognition**: Handles various date formats and cross-line date information
- 📁 **Batch Processing**: Processes all PDF files in a specified directory

## Requirements

- Python 3.6+
- PyMuPDF (fitz)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/journal-review-time-statistics.git
cd journal-review-time-statistics
```

2. Install required dependencies:

```bash
pip install PyMuPDF
```

Or if using conda:

```bash
conda install -c conda-forge pymupdf
```

## Usage

1. Organize your PDF files in the following structure:

```
journal article archive/
├── IEEE Sens J/
│   ├── article1.pdf
│   ├── article2.pdf
│   └── ...
├── Another Journal/
│   └── ...
└── ...
```

2. Modify the `journal_name` in `main.py` to specify which journal to analyze:

```python
journal_name = "IEEE Sens J"  # Change this to your target journal
pdf_folder = rf"journal article archive/{journal_name}"
```

3. Run the script:

```bash
python main.py
```

## Supported Date Formats

The tool recognizes the following date patterns commonly used in academic journals:

### Elsevier Format

```
Received 8 April 2024; Received in revised form 23 August 2024; Accepted 15 September 2024
```

### IEEE Format

```
Received 17 January 2025; revised 31 March 2025; accepted 24 April 2025.
Date of publication 15 May 2025; date of current version 30 May 2025.
```

## Sample Output

```
================================================================================
找到 10 个PDF文件
================================================================================

处理文件: article1.pdf
  Received: 2024-04-08
  Revised:  2024-08-23
  Accepted: 2024-09-15
  >> Received -> Revised: 137 天 (4.6 个月)
  >> Received -> Accepted: 160 天 (5.3 个月)
--------------------------------------------------------------------------------

...

================================================================================
【统计结果】
================================================================================

处理IEEE Sens J的PDF文件总数: 10
成功提取Received→Revised时间的文件数: 10
成功提取Received→Accepted时间的文件数: 10

【Received -> Revised 平均时间】: 220.2 天 (7.3 个月)
   中位数: 183.5 天 (6.1 个月)
   最短: 54 天 (1.8 个月)
   最长: 440 天 (14.7 个月)

【Received -> Accepted 平均时间】: 242.6 天 (8.1 个月)
   中位数: 201.0 天 (6.7 个月)
   最短: 80 天 (2.7 个月)
   最长: 449 天 (15.0 个月)

================================================================================
```

## How It Works

1. **PDF Text Extraction**: The script reads the first 3 pages of each PDF file to locate date information
2. **Pattern Matching**: Uses regular expressions to identify and extract dates with keywords:
   - "Received" - Initial submission date
   - "Revised" or "Received in revised form" - Revision submission date
   - "Accepted" - Final acceptance date
3. **Date Parsing**: Converts various date formats into standardized datetime objects
4. **Time Calculation**: Computes the number of days between key milestones
5. **Statistical Analysis**: Calculates mean, median, min, and max values across all processed papers

## Project Structure

```
.
├── main.py                     # Main script
├── README.md                   # This file
└── journal article archive/    # Directory containing PDF files
    ├── IEEE Sens J/
    ├── Elsevier Journal/
    └── ...
```

## Key Functions

- `extract_text_from_pdf(pdf_path)`: Extracts text from PDF files
- `parse_date(date_string)`: Parses various date formats into datetime objects
- `extract_dates_from_text(text)`: Identifies and extracts received/revised/accepted dates
- `calculate_days_difference(date1, date2)`: Calculates the difference in days
- `process_pdf_folder(folder_path)`: Processes all PDFs in a directory
- `calculate_statistics(results, journal_name)`: Computes and displays statistics

## Use Cases

- 📖 **Journal Selection**: Help researchers choose journals with faster review times
- 📈 **Trend Analysis**: Analyze how review times change over different periods
- 🔬 **Research Planning**: Better estimate publication timelines for grant applications
- 📊 **Comparative Studies**: Compare review efficiency across different journals

## Notes

- The script assumes date information appears in the first 3 pages of the PDF
- Dates are expected to follow common academic journal formats
- For best results, ensure PDFs are text-based (not scanned images)
- Review times are calculated from the received date to revision/acceptance dates

## Troubleshooting

**Issue**: Chinese characters display as garbled text in Windows PowerShell

**Solution**: 

- Run the script in a Python IDE (PyCharm, VS Code, etc.) for proper UTF-8 display
- Or execute `chcp 65001` in PowerShell before running the script

**Issue**: No dates extracted from PDFs

**Solution**:

- Verify that the PDFs contain text (not scanned images)
- Check if the date format matches supported patterns
- The date information should be within the first 3 pages

## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests to support additional journal formats
- Improve date pattern recognition

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created for academic research purposes to help researchers make informed decisions about journal submissions.

## Acknowledgments

- PyMuPDF team for the excellent PDF processing library
- The academic community for inspiring this tool

---

**Note**: This tool is designed for personal research and analysis purposes. Please respect copyright laws when processing PDF files.
