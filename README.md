# Free Classifier
_Automated Document Classifier._

A Python script for classifying a batch of PDF files. This tool is designed for legal professionals who need to efficiently catalog and manage large volumes of discovery documents.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

## Overview

Managing large batches of PDF files can be daunting and creating lists of logs of files organized by classification (e.g. bank statements, credit card statements, emails, etc.) is always tedious. This script will run through a folder of documents and create a CSV/Excel file containing a list of documents along with their classifications.

## Features

- **Multimodal Input Support**: Processes PDF files that are either scanned images or searchable. It will also process common image formats such as JPG, GIF, and PNG.
- **Hidden Directory Filtering**: Automatically excludes directories starting with "." (following Linux convention)
- **Error Handling**: Continues processing even when individual files encounter issues
- **CSV Output**: Generates structured data ready for import into legal case management systems

## Built With

![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/-OpenAI-412991?logo=openai&logoColor=white)
![Anthropic](https://img.shields.io/badge/-Anthropic-D97757?logo=claude&logoColor=white)
![Gemini](https://img.shields.io/badge/-Gemini-8E75B2?logo=googlegemini&logoColor=white)

## Requirements

- Python 3.6+
- Git client
- openai library
- anthropic library
- googlegemini library

## Prerequisites

*You will need to have the ```git``` software installed on your computer before you begin ([GIT Installation Page](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)). For Windows, you can install from this link: [Windows Installation](https://git-scm.com/download/win). For Mac, you can install from this link: [Mac Installation](https://git-scm.com/download/mac).*

*You need the ```python``` interpreter installed on your system before you can run the script. ([Python Installation page](https://www.python.org/downloads/windows/)).*

*You need an API token from one or more of the following: OpenAI, Anthropic, Google Gemini*

## Installation

1. Clone this repository:
```bash
git clone https://github.com/tjdaley/free_classifier.git
cd free+classifier
```

2. Create a virtual environment and activate the environment:
```bash
python -m venv venv
venv\scripts\activate.bat
```

4. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Variables to Set

The following variables control the ooperation of the script:

* BATES_PATTERN: Regular expression for locating the Bates number.
* BASE_DIRECTORY: Folder to start searching for PDFs (if using the option to scan a folder and subfolders)
* OUTPUT_FILE: Name of the output CSV file that will contiain a list of files scanned along with their beginning and ending Bates numbers

### Basic Usage

Update the ```BASE_DIRECTORY``` variable and your ```BATES_PATTERN``` values and then run the script:

```bash
python bates_extractor.py
```

### Input Options

#### Option 1: Hardcoded File List
Modify the `file_list` variable in the script with your file paths:
```python
file_list = [
    r"C:\path\to\document1.pdf",
    r"C:\path\to\document2.pdf",
    # Add more files...
]
```

#### Option 2: Directory Scanning
Scan a directory recursively for all PDF files:
```python
BASE_DIRECTORY = r"C:\path\to\discovery\documents"
```

## Bates Number Pattern

The script searches for Bates numbers matching the pattern: `TJD######` (where # represents digits). To modify for different patterns, update the `BATES_PATTERN` variable:

```python
BATES_PATTERN = r'TJD\d{6}'  # Current pattern: TJD followed by 6 digits
```

## Output Format

The script generates a CSV file with the following columns:
- `beginning_bates`: First Bates number found in the document
- `ending_bates`: Last Bates number found in the document  
- `filename`: Name of the PDF file (without path)
- `path`: Full path name of the file

Example output:
```csv
beginning_bates,ending_bates,filename
TJD000001,TJD000005,Discovery_Production.pdf,c:\clients\xyz\statements\Discovery_Production.pdf
TJD000010,TJD000010,Expert_Report.pdf,c:\clients\xyz\statements\Expert_Report.pdf
TJD000025,TJD000030,Bank_Statements.pdf,c:\clients\xyz\statements\Bank_Statements.pdf
```

## Error Handling

The script includes comprehensive error handling:
- Skips non-existent files with warnings
- Continues processing if individual PDFs encounter errors
- Reports processing status for each file
- Logs errors without stopping the entire process

## Advanced Features

### Multiple Extraction Methods
The script attempts several extraction techniques:
1. Standard text extraction
2. Simple text extraction (alternative algorithm)
3. Footer region extraction (bottom 10% of page)
4. Annotations and stamps extraction
5. Character-level extraction

### Hidden Directory Filtering
When scanning directories, the script automatically excludes any directories starting with "." to avoid processing hidden system folders.

## Troubleshooting

**Bates numbers not found**: If Adobe Acrobat can find the numbers but the script cannot, the numbers may be in annotations or stamps. The script's comprehensive extraction methods should handle most cases.

**Memory issues with large files**: For very large PDF files, consider processing in smaller batches.

**Path issues on Windows**: Use raw strings (prefix with `r`) for Windows file paths to handle backslashes correctly.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Thomas J. Daley** is a family law litigation attorney practicing primarily in Collin County, Texas and representing clients in family disputes throughout the State of Texas and the United States. As a tech entrepreneur, he leverages AI to bring high-quality legal services that work better, faster, and cheaper than traditional approaches to resolving cases.

---

<p align="center">Made with ❤️ in Texas by <a href="https://github.com/tjdaley">Tom Daley</a></p>