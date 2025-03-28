import tkinter as tk
from tkinter import filedialog, ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from mdconverter import create_epub

class Obsidian2EpubUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Obsidian to EPUB Converter")
        self.root.geometry("900x800")
        
        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="30")
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Title with subtitle
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=X, pady=(0, 30))
        
        title_label = ttk.Label(
            title_frame,
            text="Obsidian to EPUB Converter",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack(anchor=W)
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Convert your Obsidian notes to EPUB format",
            font=("Helvetica", 12),
            bootstyle="secondary"
        )
        subtitle_label.pack(anchor=W, pady=(5, 0))
        
        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Input Settings", padding="20")
        input_frame.pack(fill=X, pady=(0, 20))
        
        # Input folder selection
        folder_frame = ttk.Frame(input_frame)
        folder_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            folder_frame,
            text="Markdown Folder:",
            font=("Helvetica", 10, "bold")
        ).pack(side=LEFT)
        
        self.folder_path = tk.StringVar()
        ttk.Entry(
            folder_frame,
            textvariable=self.folder_path,
            width=50,
            bootstyle="default"
        ).pack(side=LEFT, padx=10)
        
        ttk.Button(
            folder_frame,
            text="Browse",
            command=self.browse_folder,
            bootstyle="primary-outline",
            width=10
        ).pack(side=LEFT)
        
        # Tag settings
        tag_frame = ttk.Frame(input_frame)
        tag_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            tag_frame,
            text="Tag Settings:",
            font=("Helvetica", 10, "bold")
        ).pack(side=LEFT)
        
        ttk.Label(tag_frame, text="Name:").pack(side=LEFT, padx=(20, 5))
        self.tag_name = tk.StringVar(value="moved_to_kindle")
        ttk.Entry(
            tag_frame,
            textvariable=self.tag_name,
            width=25,
            bootstyle="default"
        ).pack(side=LEFT, padx=5)
        
        ttk.Label(tag_frame, text="Criteria:").pack(side=LEFT, padx=(20, 5))
        self.tag_criteria = tk.StringVar(value="does not contain")
        tag_criteria_combo = ttk.Combobox(
            tag_frame,
            textvariable=self.tag_criteria,
            values=["contains", "does not contain"],
            state="readonly",
            width=15,
            bootstyle="default"
        )
        tag_criteria_combo.pack(side=LEFT, padx=5)
        
        # Selection settings
        selection_frame = ttk.Frame(input_frame)
        selection_frame.pack(fill=X)
        
        ttk.Label(
            selection_frame,
            text="Selection Settings:",
            font=("Helvetica", 10, "bold")
        ).pack(side=LEFT)
        
        ttk.Label(selection_frame, text="Number of Entries:").pack(side=LEFT, padx=(20, 5))
        self.num_entries = tk.StringVar(value="")
        ttk.Entry(
            selection_frame,
            textvariable=self.num_entries,
            width=10,
            bootstyle="default"
        ).pack(side=LEFT, padx=5)
        ttk.Label(selection_frame, text="(Leave empty for all)").pack(side=LEFT, padx=5)
        
        ttk.Label(selection_frame, text="Mode:").pack(side=LEFT, padx=(20, 5))
        self.selection_mode = tk.StringVar(value="newest")
        selection_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.selection_mode,
            values=["newest", "oldest", "random"],
            state="readonly",
            width=10,
            bootstyle="default"
        )
        selection_combo.pack(side=LEFT, padx=5)
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="20")
        output_frame.pack(fill=X, pady=(0, 20))
        
        # Output filename
        filename_frame = ttk.Frame(output_frame)
        filename_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            filename_frame,
            text="Output Filename:",
            font=("Helvetica", 10, "bold")
        ).pack(side=LEFT)
        
        self.output_filename = tk.StringVar(value="articles.epub")
        ttk.Entry(
            filename_frame,
            textvariable=self.output_filename,
            width=50,
            bootstyle="default"
        ).pack(side=LEFT, padx=10)
        
        # Output directory
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=X)
        
        ttk.Label(
            dir_frame,
            text="Output Directory:",
            font=("Helvetica", 10, "bold")
        ).pack(side=LEFT)
        
        self.output_dir = tk.StringVar()
        ttk.Entry(
            dir_frame,
            textvariable=self.output_dir,
            width=50,
            bootstyle="default"
        ).pack(side=LEFT, padx=10)
        
        ttk.Button(
            dir_frame,
            text="Browse",
            command=self.browse_output_dir,
            bootstyle="primary-outline",
            width=10
        ).pack(side=LEFT)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="20")
        progress_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))
        
        # Progress text area with scrollbar
        text_frame = ttk.Frame(progress_frame)
        text_frame.pack(fill=BOTH, expand=YES)
        
        self.progress_text = tk.Text(
            text_frame,
            height=8,
            width=50,
            wrap=tk.WORD,
            font=("Helvetica", 10)
        )
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.progress_text.yview)
        self.progress_text.configure(yscrollcommand=scrollbar.set)
        
        self.progress_text.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Status label
        self.status_label = ttk.Label(
            progress_frame,
            text="",
            font=("Helvetica", 10)
        )
        self.status_label.pack(pady=(10, 0))
        
        # Convert button
        self.convert_button = ttk.Button(
            main_frame,
            text="Convert to EPUB",
            command=self.convert,
            bootstyle="success",
            width=20
        )
        self.convert_button.pack(pady=(0, 10))
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            
    def browse_output_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir.set(folder)
            
    def update_progress(self, message):
        """Update the progress text area with a new message."""
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update()
            
    def convert(self):
        # Clear previous progress
        self.progress_text.delete(1.0, tk.END)
        
        # Validate inputs
        if not self.folder_path.get():
            self.status_label.config(text="Please select a markdown folder", bootstyle="danger")
            return
            
        if not self.tag_name.get():
            self.status_label.config(text="Please enter a tag name", bootstyle="danger")
            return
            
        if not self.output_filename.get():
            self.status_label.config(text="Please enter an output filename", bootstyle="danger")
            return
            
        if not self.output_dir.get():
            self.status_label.config(text="Please select an output directory", bootstyle="danger")
            return
            
        # Parse number of entries
        num_entries = None
        if self.num_entries.get().strip():
            try:
                num_entries = int(self.num_entries.get())
                if num_entries <= 0:
                    self.status_label.config(text="Number of entries must be positive", bootstyle="danger")
                    return
            except ValueError:
                self.status_label.config(text="Number of entries must be a valid number", bootstyle="danger")
                return
            
        # Disable convert button and show progress
        self.convert_button.config(state=DISABLED)
        self.status_label.config(text="Converting...", bootstyle="info")
        
        try:
            # Create output path
            output_path = os.path.join(self.output_dir.get(), self.output_filename.get())
            
            # Run conversion with progress callback
            create_epub(
                self.folder_path.get(),
                self.tag_name.get(),
                output_path,
                num_entries=num_entries,
                selection_mode=self.selection_mode.get(),
                tag_criteria=self.tag_criteria.get(),
                progress_callback=self.update_progress
            )
            
            self.status_label.config(
                text=f"Successfully created EPUB at {output_path}",
                bootstyle="success"
            )
            
        except ValueError as e:
            self.status_label.config(
                text=str(e),
                bootstyle="danger"
            )
            self.update_progress(str(e))
            
        except Exception as e:
            self.status_label.config(
                text=f"Error: {str(e)}",
                bootstyle="danger"
            )
            self.update_progress(f"Error: {str(e)}")
            
        finally:
            # Re-enable convert button
            self.convert_button.config(state=NORMAL)

def main():
    root = ttk.Window(themename="cosmo")
    app = Obsidian2EpubUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 