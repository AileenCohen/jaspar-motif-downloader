import requests
from typing import List, Dict
import datetime
import re 
import threading 
import csv 

# Configuration constants are now defined directly in the logic file
JASPAR_BASE_URL = "https://jaspar.genereg.net/api/v1/"
HUMAN_TAX_ID = "9606"
JASPAR_COLLECTION = "CORE"
MAX_RESULTS = 10

# Global lock to ensure only one file operation happens at a time (e.g., logging)
file_lock = threading.Lock() 

def log_action(message: str):
    """
    Appends a timestamped message to a local log file (jaspar_log.txt).
    Uses a thread lock to ensure safe file access in a multi-threaded environment.
    """
    with file_lock:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            # Use 'a' (append) mode for file handling
            with open("jaspar_log.txt", "a") as f:
                f.write(log_entry)
        except Exception as e:
            # Print error but don't stop the application if logging fails
            print(f"[LOG] Failed to write to log file: {e}") 

def search_jaspar_motifs(keyword: str) -> List[Dict[str, str]]:
    """
    Searches the JASPAR CORE collection for human motifs, filtering by keyword 
    and human tax_id. Returns motif metadata.
    """
    keyword = keyword.strip()
    if not keyword:
        log_action("Search failed: Keyword was empty.")
        return []

    search_url = (
        f"{JASPAR_BASE_URL}matrix/?"
        f"search={keyword}&tax_id={HUMAN_TAX_ID}&collection={JASPAR_COLLECTION}"
    )
    
    log_action(f"Searching JASPAR for: '{keyword}'")

    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for i, motif in enumerate(data.get('results', [])):
            if i >= MAX_RESULTS:
                break
            
            download_url = f"{JASPAR_BASE_URL}matrix/{motif.get('matrix_id')}/?format=pfm"
            
            results.append({
                "id": str(i + 1),
                "matrix_id": motif.get('matrix_id'),
                "name": motif.get('name'),
                "url": download_url
            })
        
        # In batch mode, we only need the first result (the best match)
        return results[:1]
        
    except requests.exceptions.RequestException as e:
        log_action(f"JASPAR API search error for '{keyword}': {e}")
        raise
    except Exception as e:
        log_action(f"Unexpected error during search for '{keyword}': {e}")
        raise


def download_file(url: str, output_path: str, update_callback=None) -> bool:
    """
    Downloads the actual motif data (PFM format) from the JASPAR API.
    """
    try:
        if update_callback:
            # Update callback is disabled for background batch processing
            pass 
            
        log_action(f"Starting download to: {output_path}")

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(output_path, 'w') as file_handle:
            file_handle.write(response.text)

        log_action(f"Download successful for URL: {url}")
        return True

    except requests.exceptions.RequestException as e:
        error_message = f"Error during download from {url}: {e}"
        log_action(error_message)
        raise
    except Exception as e:
        error_message = f"An unexpected error occurred during file operation: {e}"
        log_action(error_message)
        raise

def sanitize_filename(text: str) -> str:
    """
    Sanitize text to create a safe filename, removing common illegal characters.
    """
    s = re.sub(r'[\\/:*?"<>|]', '-', text)
    s = s.strip()
    return s

def batch_download_motifs(input_csv_path: str, output_dir: str, status_callback) -> str:
    """
    Handles batch processing: reads a CSV, searches/downloads each TF, and generates a report.
    This function uses advanced file handling for reading and writing structured data.
    """
    
    # 1. Prepare report file path
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"{output_dir}/jaspar_batch_report_{timestamp}.csv"
    
    # 2. Initialize the report file
    report_data = []
    
    try:
        # 3. Read input CSV
        with open(input_csv_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            tf_list = [row[0].strip() for row in reader if row and row[0].strip()]

        total_tfs = len(tf_list)
        status_callback(f"Starting batch download for {total_tfs} TFs...")
        log_action(f"Starting batch download for {total_tfs} TFs from {input_csv_path}.")

        # 4. Process each TF
        for i, keyword in enumerate(tf_list):
            keyword = keyword.upper()
            status_callback(f"[{i + 1}/{total_tfs}] Processing: {keyword}...")
            
            result_row = {"TF_Keyword": keyword, "Status": "FAILED", "Matrix_ID": "", "File_Path": "", "Error_Message": ""}
            
            try:
                # 4a. Search for the motif (only takes the first/best result)
                results = search_jaspar_motifs(keyword)
                
                if results:
                    motif = results[0]
                    safe_name = sanitize_filename(motif['name'])
                    default_filename = f"{motif['matrix_id']}_{safe_name}.pfm"
                    output_path = f"{output_dir}/{default_filename}"

                    # 4b. Download the file
                    download_file(motif['url'], output_path)
                    
                    # 4c. Record success in the report
                    result_row.update({
                        "Status": "SUCCESS",
                        "Matrix_ID": motif['matrix_id'],
                        "File_Path": output_path
                    })
                else:
                    result_row.update({"Error_Message": "No human motif found."})

            except Exception as e:
                # Record the error in the report
                result_row.update({"Error_Message": str(e)})

            report_data.append(result_row)
            
        # 5. Write the final report CSV
        with open(report_path, 'w', newline='') as outfile:
            fieldnames = ["TF_Keyword", "Status", "Matrix_ID", "File_Path", "Error_Message"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(report_data)

        log_action(f"Batch download complete. Report saved to {report_path}")
        return report_path
        
    except FileNotFoundError:
        log_action(f"Batch download failed: Input file not found: {input_csv_path}")
        return f"Error: Input file not found at {input_csv_path}"
    except Exception as e:
        log_action(f"Batch download failed due to an unexpected error: {e}")
        return f"Error during batch processing: {e}"