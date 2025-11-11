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
cd free_classifier
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

### Update the .env File

The ```.env``` file controls certain aspects of how the program works. Here are the variables you need to set:

Variable | Description | Permitted Values
----|----|----
llm_name | The LLM vendor you are using | openai or anthropic or gemini
llm_model | The LLM model you are using | It must be a multimodal model (one that will process text and images). The LLM vendors list their models on their web sites.
llm_api_key | The API key assigned to you by the LLM vendor | Any string provided by the vendor
prompt_file | Name of the file that contains the classification prompt | Any valid filename

### Basic Usage

```bash
python classifier.py path_to_files
```

## Output Format

The script generates a CSV file with the following columns:
- `filename`: Name of the PDF file (without path)
- `label`: Classification assigned to this file by the LLM
- `llm`: Name of the LLM vendor producing the label
- `model`: Name of the LLM model producing the label
- `path`: Full path name of the file

Example output:
```csv
filename,label,llm,model,path
053565-053579  ABC Co Amd & Restated Director Def Com Agmt.pdf,other,openai,gpt-4o-mini,test_files\053565-053579  ABC Co Amd & Restated Director Def Com Agmt.pdf
AB x3581  2014.09.pdf,bank_statement,openai,gpt-4o-mini,test_files\AB x3581  2014.09.pdf
AngelBank x2086  2024.07.25.pdf,bank_statement,openai,gpt-4o-mini,test_files\AngelBank x2086  2024.07.25.pdf
Apple Pay Transactions  2022.01 - 2024.06.pdf,credit_card_statement,openai,gpt-4o-mini,test_files\Apple Pay Transactions  2022.01 - 2024.06.pdf
BS x0075  2015.02.pdf,bank_statement,openai,gpt-4o-mini,test_files\BS x0075  2015.02.pdf
CBTX x9999  2013.07.pdf,bank_statement,openai,gpt-4o-mini,test_files\CBTX x9999  2013.07.pdf
ETrade x8989  2020.06.pdf,brokerage_account_statement,openai,gpt-4o-mini,test_files\ETrade x8989  2020.06.pdf
JPM x7777  2016.01.pdf,brokerage_account_statement,openai,gpt-4o-mini,test_files\JPM x7777  2016.01.pdf
"ML  x1111, x2222  2010.05.pdf",brokerage_account_statement,openai,gpt-4o-mini,"test_files\ML  x1111, x2222  2010.05.pdf"
MS x5555  2022.08.pdf,brokerage_account_statement,openai,gpt-4o-mini,test_files\MS x5555  2022.08.pdf
"MS x5555, x4024  2022.11~2.pdf",brokerage_account_statement,openai,gpt-4o-mini,"test_files\MS x5555, x4024  2022.11~2.pdf"
SB x4343  2013.11.pdf,bank_statement,openai,gpt-4o-mini,test_files\SB x4343  2013.11.pdf
TDA x6767  2018.08.pdf,brokerage_account_statement,openai,gpt-4o-mini,test_files\TDA x6767  2018.08.pdf

```

## Error Handling

The script includes comprehensive error handling:
- Skips non-existent files with warnings
- Continues processing if individual PDFs encounter errors
- Reports processing status for each file
- Logs errors without stopping the entire process

## Advanced Features

### Hidden Directory Filtering
When scanning directories, the script automatically excludes any directories starting with "." to avoid processing hidden system folders.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Thomas J. Daley** is a family law litigation attorney practicing primarily in Collin County, Texas and representing clients in family disputes throughout the State of Texas and the United States. As a tech entrepreneur, he leverages AI to bring high-quality legal services that work better, faster, and cheaper than traditional approaches to resolving cases.

---

<p align="center">Made with ❤️ in Texas by <a href="https://github.com/tjdaley">Tom Daley</a></p>