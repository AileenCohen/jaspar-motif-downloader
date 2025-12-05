import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict
import threading 

from motif_search import search_jaspar_motifs, download_file, log_action, sanitize_filename, batch_download_motifs


class JasparDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JASPAR Motif Downloader (Human TFs)")
        self.geometry("600x450") # Slightly larger window
        self.results_data: List[Dict[str, str]] = []
        
        log_action("Application started.")
        
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 10, 'bold'))
        style.configure('TLabel', font=('Helvetica', 10))
        
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        # Increased rowspan to accommodate the new batch section
        main_frame.grid(row=0, column=0, sticky="nsew", rowspan=5) 
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        
        # --- Search Frame (Row 0) ---
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1) 
        
        ttk.Label(search_frame, text="1. Single Search:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        self.keyword_entry = ttk.Entry(search_frame, width=30)
        self.keyword_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        self.search_button = ttk.Button(search_frame, text="Search JASPAR", command=self.start_search_thread)
        self.search_button.grid(row=0, column=2, sticky="e")
        
        # --- Status Label (Row 1) ---
        self.status_var = tk.StringVar(value="Enter a human TF name and click Search or use Batch Mode.")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.RIDGE, anchor=tk.W)
        self.status_label.grid(row=1, column=0, sticky="ew", pady=(0, 10), ipady=5)
        
        # --- Results Frame (Row 2) ---
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 0))
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        self.results_list = ttk.Treeview(results_frame, columns=('Matrix ID', 'TF Name'), show='headings', selectmode='browse')
        
        self.results_list.heading('Matrix ID', text='Matrix ID', anchor=tk.W)
        self.results_list.column('Matrix ID', width=120, stretch=tk.NO)
        self.results_list.heading('TF Name', text='Transcription Factor Name', anchor=tk.W)
        self.results_list.column('TF Name', stretch=tk.YES)
        
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_list.yview)
        self.results_list.configure(yscrollcommand=vsb.set)
        
        self.results_list.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky='ns')
        
        self.results_list.bind('<<TreeviewSelect>>', self.enable_download)

        # --- Single Download Button (Row 3) ---
        download_frame = ttk.Frame(main_frame)
        download_frame.grid(row=3, column=0, sticky="ew", pady=(15, 15))
        self.download_button = ttk.Button(download_frame, text="2. ⬇️ Download Selected Motif (PFM Format)",
                                             state=tk.DISABLED, command=self.start_download_thread)
        self.download_button.pack(fill=tk.X)
        
        # --- NEW Batch Section (Row 4) ---
        batch_frame = ttk.Frame(main_frame)
        batch_frame.grid(row=4, column=0, sticky="ew", pady=(5, 0))
        batch_frame.columnconfigure(0, weight=1)

        self.batch_button = ttk.Button(batch_frame, text="3. 📂 Batch Download from CSV (TF Name in Col A)", 
                                       command=self.start_batch_thread)
        self.batch_button.pack(fill=tk.X)


    def set_gui_state(self, is_enabled: bool, message: str = None):
        """Enables or disables key GUI elements while a task is running."""
        state = tk.NORMAL if is_enabled else tk.DISABLED
        self.search_button.config(state=state)
        self.keyword_entry.config(state=state)
        self.batch_button.config(state=state)
        
        if is_enabled:
            self.enable_download(None) 
        else:
            self.download_button.config(state=tk.DISABLED)

        if message:
            self.update_status(message)
        self.update_idletasks()


    def update_status(self, message: str, is_error: bool = False):
        """Updates the GUI status label."""
        self.status_var.set(message)
        self.status_label.config(foreground='red' if is_error else 'black')
        self.update_idletasks()

    def start_search_thread(self):
        """Starts the single search operation in a new thread."""
        keyword = self.keyword_entry.get().strip()
        
        if not keyword:
            self.update_status("Search field is empty. Please enter a TF name.", is_error=True)
            return
            
        self.set_gui_state(False, f"Searching JASPAR for motifs matching '{keyword}'... (Please wait)")
        
        thread = threading.Thread(target=self.handle_search, args=(keyword,))
        thread.start()

    def handle_search(self, keyword):
        """Threaded function to handle the actual search and UI update."""
        try:
            for i in self.results_list.get_children():
                self.results_list.delete(i)
                
            self.results_data = search_jaspar_motifs(keyword)
            
            if not self.results_data:
                self.update_status(f"No human motifs found for '{keyword}'. Check spelling or try a broader search.", is_error=True)
            else:
                for item in self.results_data:
                    self.results_list.insert('', tk.END, iid=item['id'], values=(item['matrix_id'], item['name']))
                self.update_status(f"Found {len(self.results_data)} matching motifs. Select one to download.")
                
        except Exception as e:
            self.update_status(f"Search failed: {e.__class__.__name__} - {e}", is_error=True)
            log_action(f"Search thread failed: {e}")
            
        finally:
            self.set_gui_state(True)


    def enable_download(self, event):
        """Enables the download button when a result is selected."""
        if self.results_list.selection():
            self.download_button.config(state=tk.NORMAL)
        else:
            self.download_button.config(state=tk.DISABLED)

    def start_download_thread(self):
        """Starts the single download operation in a new thread."""
        try:
            selected_item_id = self.results_list.selection()[0]
            selected_result = next(r for r in self.results_data if r["id"] == selected_item_id)
        except (IndexError, StopIteration):
            self.update_status("Please select a motif from the list.", is_error=True)
            return
            
        self.set_gui_state(False, f"Preparing to download {selected_result['matrix_id']}... (Do not close)")

        thread = threading.Thread(target=self.handle_download, args=(selected_result,))
        thread.start()


    def handle_download(self, selected_result):
        """Threaded function to handle the actual download and file save."""
        
        url = selected_result['url']
        safe_name = sanitize_filename(selected_result['name'])
        default_filename = f"{selected_result['matrix_id']}_{safe_name}.pfm"
        
        # File dialog MUST run on the main thread
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pfm",
            initialfile=default_filename,
            title="Save JASPAR Motif File",
            filetypes=[("PFM Motif Files", "*.pfm"), ("All files", "*.*")]
        )
        
        if not output_path:
            self.update_status("Download canceled by user.")
            log_action("User canceled file save dialog.")
            self.set_gui_state(True)
            return

        try:
            # Note: Single download still uses update_callback for status messages
            success = download_file(url, output_path, update_callback=self.update_status)
            
            if success:
                log_action(f"Motif {selected_result['matrix_id']} saved successfully to: {output_path}")
                messagebox.showinfo("Success", f"Motif file downloaded successfully to:\n{output_path}")
            else:
                messagebox.showerror("Error", self.status_var.get())
                
        except Exception as e:
            error_message = f"Download failed: {e.__class__.__name__} - {e}"
            self.update_status(error_message, is_error=True)
            messagebox.showerror("Error", error_message)
            log_action(error_message)

        finally:
            self.set_gui_state(True)

    # --- NEW BATCH IMPLEMENTATION ---

    def start_batch_thread(self):
        """Opens file dialogs and starts the batch download in a new thread."""
        
        # 1. Ask for input CSV file
        input_csv_path = filedialog.askopenfilename(
            title="Select CSV file containing TF names (one per row)",
            filetypes=[("CSV Files", "*.csv"), ("All files", "*.*")]
        )
        
        if not input_csv_path:
            self.update_status("Batch download canceled: No input CSV selected.")
            return

        # 2. Ask for the output directory
        output_dir = filedialog.askdirectory(
            title="Select folder to save PFM files and report CSV"
        )
        
        if not output_dir:
            self.update_status("Batch download canceled: No output directory selected.")
            return

        self.set_gui_state(False, "Batch download process starting... (Check status bar for progress)")
        
        # Start the background thread for processing
        thread = threading.Thread(target=self.handle_batch_download, args=(input_csv_path, output_dir))
        thread.start()


    def handle_batch_download(self, input_csv_path: str, output_dir: str):
        """Threaded function to run the batch processing logic."""
        
        # We pass the update_status function as the callback for batch logic to update the GUI
        result_message = batch_download_motifs(input_csv_path, output_dir, self.update_status)
        
        self.set_gui_state(True)
        
        # Display the final outcome
        if result_message.startswith("Error"):
            messagebox.showerror("Batch Error", result_message)
            self.update_status(result_message, is_error=True)
        else:
            final_msg = f"Batch process finished successfully! Report saved to:\n{result_message}"
            messagebox.showinfo("Batch Success", final_msg)
            self.update_status(f"Batch process complete. Report available: {result_message}")