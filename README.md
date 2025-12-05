# JASPAR Motif Downloader (Human TFs)

A standalone Python GUI application for quickly searching and downloading human Transcription Factor (TF) binding motifs (PFM files) from the JASPAR CORE database.

## Project Overview

This program provides a user-friendly interface for researchers and students to interact with the JASPAR database. It streamlines the retrieval of Position Frequency Matrices (PFMs), which are essential for analyzing regulatory elements in the human genome.

The application follows modern Python best practices, separating the core logic (API communication, file handling) from the user interface (Tkinter GUI).

## Features

**JASPAR CORE Search**: Query the JASPAR API using a TF name (e.g., FOS, STAT1).

**Human-Specific Filtering**: Limits all results to Homo sapiens (Tax ID 9606).

**Safe File Handling**: Generates robust, OS-safe default filenames.

**Download Logging**: All searches and downloads are recorded in jaspar_log.txt.

**Intuitive GUI**: Clean Tkinter interface for easy searching and downloading.

## Project Structure
```
jaspar-motif-downloader/
├── main.py                   # Application entry point (starts the GUI)
├── motif_search_gui.py       # Handles the Tkinter User Interface
├── motif_search.py           # Core logic: API communication, file handling, logging
├── README.md                 # This documentation file
├── requirements.txt          # Python dependencies (e.g., requests)
└── .gitignore                # Excludes virtual environments and cache files
```
## Installation
Prerequisites

- Python 3.7

## Setup

Clone the repository:
```
git clone https://github.com/USERNAME/jaspar-motif-downloader.git
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

A GUI window will open, allowing you to enter a transcription factor name, search JASPAR, and download PFM files.

## Important Notes

Logging: All search queries and successful downloads are saved in jaspar_log.txt.

Rate Limiting: API requests are handled safely to respect standard limits.

## Future Enhancements

Support additional JASPAR collections (not only CORE).

Allow selecting the output directory from the GUI.

Optional integration with motif visualization or alignment tools.
