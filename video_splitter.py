import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
import tempfile
import shutil
import webbrowser

class VideoSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fastest Video Splitter")
        self.root.geometry("610x480")
        self.root.resizable(False, False)
        
        self.ffmpeg_path = None
        self.temp_dir = None
        self.ffmpeg_loaded = False
        
        self.setup_ui()
        self.setup_temp_dir()
        self.extract_ffmpeg()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Fastest Video Splitter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Input file selection
        ttk.Label(main_frame, text="Source Video:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.select_input_file).grid(row=1, column=2, pady=5)
        
        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_dir = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=2, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.select_output_dir).grid(row=2, column=2, pady=5)
        
        # Segment time
        ttk.Label(main_frame, text="Segment Duration (minutes):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.segment_time = tk.StringVar(value="20")
        ttk.Entry(main_frame, textvariable=self.segment_time, width=10).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        # Split button
        self.split_button = ttk.Button(main_frame, text="Split Video", command=self.split_video)
        self.split_button.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Log text area
        ttk.Label(main_frame, text="Process Log:").grid(row=6, column=0, sticky=tk.W, pady=(15, 5))
        self.log_text = tk.Text(main_frame, height=8, width=70)
        self.log_text.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=7, column=3, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # GitHub link
        github_link = ttk.Label(main_frame, text="GitHub: https://github.com/mehmetgozlemeci/FastestVideoSplitter", 
                               foreground="blue", cursor="hand2")
        github_link.grid(row=8, column=0, columnspan=3, pady=(10, 0))
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/mehmetgozlemeci/FastestVideoSplitter"))
    
    def setup_temp_dir(self):
        """Create temp directory in application folder"""
        try:
            if getattr(sys, 'frozen', False):
                # EXE directory
                base_dir = os.path.dirname(sys.executable)
            else:
                # Python script directory
                base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Create temp directory
            self.temp_dir = os.path.join(base_dir, "temp")
            os.makedirs(self.temp_dir, exist_ok=True)
            self.log(f"Temp directory created: {self.temp_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create temp directory: {str(e)}")
    
    def extract_ffmpeg(self):
        """Extract FFmpeg binary - only once at startup"""
        try:
            if not self.temp_dir:
                self.setup_temp_dir()
            
            self.ffmpeg_path = os.path.join(self.temp_dir, "ffmpeg.exe")
            
            # Only extract if not already extracted
            if os.path.exists(self.ffmpeg_path):
                self.log("FFmpeg already loaded")
                self.ffmpeg_loaded = True
                return
            
            # Copy FFmpeg binary from embedded data
            if getattr(sys, 'frozen', False):
                # Packaged with PyInstaller
                base_path = sys._MEIPASS
            else:
                # Development mode
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            # Find ffmpeg.exe
            possible_paths = [
                os.path.join(base_path, "ffmpeg.exe"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe"),
                "ffmpeg.exe"
            ]
            
            ffmpeg_found = False
            for path in possible_paths:
                if os.path.exists(path):
                    shutil.copy2(path, self.ffmpeg_path)
                    self.log("FFmpeg loaded successfully")
                    self.ffmpeg_loaded = True
                    ffmpeg_found = True
                    break
            
            if not ffmpeg_found:
                messagebox.showerror("Error", "FFmpeg not found! Please place ffmpeg.exe in the application directory.")
                self.split_button.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading FFmpeg: {str(e)}")
            self.split_button.config(state='disabled')
    
    def select_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select video file",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            # Set default output directory
            output_dir = os.path.join(os.path.dirname(filename), "output")
            self.output_dir.set(output_dir)
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir.set(directory)
    
    def generate_output_pattern(self, input_file):
        """Generate output pattern based on input file name"""
        file_name = os.path.basename(input_file)
        name_without_ext, ext = os.path.splitext(file_name)
        output_pattern = f"{name_without_ext}_splitted_%03d{ext}"
        return output_pattern
    
    def log(self, message):
        """Write log message to screen"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
    
    def clean_up(self):
        """Clean up temporary files - but keep FFmpeg for reuse"""
        try:
            # Don't remove the entire temp directory, just clean other files if any
            # Keep FFmpeg for future use
            if self.temp_dir and os.path.exists(self.temp_dir):
                # Remove everything except ffmpeg.exe
                for item in os.listdir(self.temp_dir):
                    if item != "ffmpeg.exe":
                        item_path = os.path.join(self.temp_dir, item)
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                self.log("Temporary files cleaned up (FFmpeg preserved)")
        except Exception as e:
            self.log(f"Cleanup error: {str(e)}")
    
    def split_video(self):
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select a video file!")
            return
        
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory!")
            return
        
        # Check if FFmpeg is available
        if not self.ffmpeg_loaded or not self.ffmpeg_path or not os.path.exists(self.ffmpeg_path):
            self.log("FFmpeg not found, attempting to reload...")
            self.extract_ffmpeg()
            if not self.ffmpeg_loaded or not self.ffmpeg_path or not os.path.exists(self.ffmpeg_path):
                messagebox.showerror("Error", "FFmpeg failed to load! Please restart the application.")
                return
        
        try:
            # Clear previous log for new operation
            self.clear_log()
            
            # Create output directory
            os.makedirs(self.output_dir.get(), exist_ok=True)
            
            # Generate output file pattern
            output_pattern = self.generate_output_pattern(self.input_path.get())
            output_file = os.path.join(self.output_dir.get(), output_pattern)
            
            segment_time = f"00:{self.segment_time.get()}:00"
            
            cmd = [
                self.ffmpeg_path,
                "-i", self.input_path.get(),
                "-c", "copy",
                "-map", "0",
                "-segment_time", segment_time,
                "-f", "segment",
                "-reset_timestamps", "1",
                "-loglevel", "warning",  # Show only warnings and errors
                output_file
            ]
            
            self.log("=" * 50)
            self.log("Starting video splitting process...")
            self.log(f"Input file: {os.path.basename(self.input_path.get())}")
            self.log(f"Output directory: {self.output_dir.get()}")
            self.log(f"Segment duration: {self.segment_time.get()} minutes")
            self.log(f"Output pattern: {output_pattern}")
            self.log("-" * 50)
            
            # Disable button and start progress bar
            self.split_button.config(state='disabled')
            self.progress.start()
            
            # Run FFmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Show only important messages
            for line in process.stdout:
                line = line.strip()
                # Show only progress or error messages
                if any(keyword in line.lower() for keyword in ['error', 'warning', 'time=', 'frame=']):
                    if 'time=' in line and 'frame=' in line:
                        # Simplify progress bar message
                        if 'time=' in line:
                            time_part = line.split('time=')[1].split()[0]
                            self.log(f"Processing... {time_part}")
                    else:
                        self.log(line)
            
            process.wait()
            
            # Stop progress bar
            self.progress.stop()
            self.split_button.config(state='normal')
            
            if process.returncode == 0:
                self.log("-" * 50)
                self.log("✓ Video successfully split!")
                
                # List created files
                output_dir = self.output_dir.get()
                pattern_base = self.generate_output_pattern(self.input_path.get()).replace("%03d", "*")
                import glob
                created_files = glob.glob(os.path.join(output_dir, pattern_base))
                created_files.sort()
                
                self.log("Created files:")
                for file in created_files:
                    file_size = os.path.getsize(file) / (1024 * 1024)  # in MB
                    self.log(f"  ✓ {os.path.basename(file)} ({file_size:.2f} MB)")
                
                self.log(f"Total {len(created_files)} files created.")
                self.log("=" * 50)
                messagebox.showinfo("Success", "Video successfully split!")
                
            else:
                self.log("✗ Error: Video splitting failed!")
                messagebox.showerror("Error", "Video splitting failed!")
                
        except Exception as e:
            self.progress.stop()
            self.split_button.config(state='normal')
            self.log(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Error during process: {str(e)}")
        
        finally:
            # Clean up temporary files (but keep FFmpeg)
            self.clean_up()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoSplitterApp(root)
    
    # Clean up temp files when window is closed (but keep FFmpeg for multiple runs)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.clean_up(), root.destroy()))
    root.mainloop()