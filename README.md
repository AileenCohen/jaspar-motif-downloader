

A standalone Python GUI application for quickly searching and downloading human Transcription Factor (TF) binding motifs (PFM files) from the JASPAR CORE database.
## Project Overview

This program offers a responsive interface for retrieving Position Frequency Matrices (PFMs) from the JASPAR database.

This project was significantly improved to include concurrency (threading) to prevent the application from freezing during long network operations, and advanced file handling for structured batch processing and logging.

## Why would you use this?
This application provides essential functionality for studying gene regulation, specifically the role of TFs. TFs bind to specific DNA sequences (motifs) to control gene expression (turning genes on or off).  So this tool is relevant because:
- *Accelerated Discovery*: It provides fast, dedicated access to the highly curated JASPAR database, enabling quick retrieval of binding motifs needed for immediate analysis in genomics and genetics research.
- *Batch Automation*: Modern experiments often identify hundreds of potential TFs. The Batch Download from CSV feature enables the automation of downloading entire lists and generating organized reports, transforming a manual, hours-long task into a fast, automated pipeline step.
- *Data Reliability and Traceability*: The integrated logging (jaspar_log.txt) and structured CSV reporting ensure every data retrieval is documented, meeting standards for data reliability and traceability required in scientific research in general.


## Features

**Responsive GUI**: Network-intensive tasks (Search, Single Download, Batch Process) run in separate threads, ensuring the graphical interface (Tkinter) remains responsive and does not freeze.

**Batch Processing**: Read a list of TF keywords from an input CSV file and automatically download the corresponding motifs.

**Structured Report Generation**: Writes a new CSV report file (jaspar_batch_report_...csv) summarizing the success, Matrix ID, file path, or error for every TF in the batch. 
*(Uses CSV File Writing).*

**Activity Logging**: Records all successful actions (searches, downloads, batch completion) in a local file, jaspar_log.txt. 
*(Uses Text File Appending).*

**Robust Filenaming**: Safely sanitizes motif names to prevent crashes when saving files with illegal characters (:, /, etc.) on Windows or Linux.

**Human-Specific Filtering**: Automatically limits results to Homo sapiens (Tax ID 9606).

## Project Structure
```
jaspar-motif-downloader/
├── main.py                   # Application entry point (starts the GUI)
├── motif_search_gui.py       # Handles the Tkinter User Interface and threading
├── motif_search.py           # Core logic (API, Logging, Thread Locking, CSV processing)
├── requirements.txt          # Python dependencies
├── .gitignore                # Excludes cache files and logs
├── README.md                 # This documentation file
├── Example_batch_input.csv   # An example file containing a bunch of TFs for you to try.               
└── jaspar_log.txt            # (Generated) Log file documenting all operations

```
## Installation
Prerequisites

- Python 3.7

## Setup

Clone the repository:
```
git clone https://github.com/aileencohen/jaspar-motif-downloader.git
cd jaspar-motif-downloader
```

Install dependencies:
```
pip install -r requirements.txt
```
Usage

Run the application:
```
python main.py
```

**Mode 1**: Single Search & Download

- Enter a TF name (e.g., "FOS").

- Click "Search JASPAR" to view results in the table.

- Select one motif and click "Download Selected Motif".

**Mode 2**: Batch Download from CSV (Advanced File Handling)

- Prepare a CSV file where Column A contains the list of TF names you wish to download (e.g., SPI1, JUN, CEBPA).

- Example input format:
```
SPI1
JUN
HNF4A
```
- Click "Batch Download from CSV".

- The app will first prompt you to select your Input CSV file.

- Next, it will prompt you to select the Output Folder where all PFM files and the summary report will be saved.

- The app processes the list, downloading the best-matching human motif for each TF

## File Handling and Report Generation

The batch mode relies heavily on structured file handling:

*CSV Input Reading*: The app uses the csv module to safely read the list of TFs from the user's input file.

*CSV Report Writing*: Upon completion, the app generates a detailed report CSV (e.g., jaspar_batch_report_...csv) using csv.DictWriter. This report allows you to quickly verify the outcome of every request:

*TF_Keyword*: The name you searched for.

*Status*: SUCCESS or FAILED.

*Matrix_ID*: The ID of the downloaded motif.

*File_Path*: The local path to the saved PFM file.

*Error_Message*: Details if the download failed.

*Log File*: The non-structured jaspar_log.txt is continuously updated using file appending ('a'), providing a chronological history of all application actions.

## Possible Future Enhancements

- Support additional JASPAR collections (not only CORE).

- Allow selecting the output directory from the GUI.

- Optional integration with motif visualization or alignment tools.

Please offer more if you have any suggestions!
