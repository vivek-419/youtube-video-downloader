import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os

# ------------------ Function to Fetch Video Info ------------------
def fetch_video_info():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube link!")
        return
    
    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
        
        resolutions = sorted(set(f"{fmt['height']}p" for fmt in formats if fmt.get("height")))

        if resolutions:
            resolution_dropdown["values"] = ["Audio Only"] + resolutions
            resolution_var.set("Audio Only")
            title_label.config(text=f"Title: {info.get('title', 'N/A')}")
            preview_btn.config(state=tk.NORMAL)  # Enable preview button
        else:
            messagebox.showerror("Error", "No video streams found!")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch video: {e}")

# ------------------ Function to Preview Video ------------------
def preview_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube link!")
        return
    
    os.system(f'open "{url}"' if os.name == "posix" else f'start {url}')

# ------------------ Function to Download Video or Audio ------------------
def download_video():
    url = url_entry.get().strip()
    resolution = resolution_var.get()

    if not url or not resolution:
        messagebox.showerror("Error", "Please enter a URL and select an option!")
        return

    # Ask user where to save the file
    save_path = filedialog.askdirectory()
    if not save_path:
        return  # User canceled

    if resolution == "Audio Only":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "progress_hooks": [progress_hook]
        }
    else:
        ydl_opts = {
            "format": f"bestvideo[height={resolution[:-1]}]+bestaudio/best",
            "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook]
        }

    def run_download():
        try:
            progress_var.set(0)
            progress_bar.start(10)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            progress_bar.stop()
            messagebox.showinfo("Success", "Download complete!")
        except Exception as e:
            progress_bar.stop()
            messagebox.showerror("Error", f"Download failed: {e}")

    threading.Thread(target=run_download, daemon=True).start()

# ------------------ Progress Indicator ------------------
import re  # Import the `re` module for regular expressions

# ------------------ Progress Indicator ------------------
def progress_hook(d):
    if d["status"] == "downloading":
        # Extract the percentage string and remove color codes (e.g., '\x1b[0;94m')
        percent_str = d["_percent_str"].strip('%')
        percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)  # Remove ANSI escape codes
        try:
            percent = float(percent_str)  # Convert cleaned percentage to float
            progress_var.set(percent)
            progress_label.config(text=f"Downloading... {d['_percent_str']}")
        except ValueError:
            pass  # Ignore errors if conversion fails (though unlikely)
    elif d["status"] == "finished":
        progress_label.config(text="✅ Download Complete!")


# ------------------ Drag & Drop Function ------------------
def drop(event):
    url = event.data.strip()
    url_entry.delete(0, tk.END)
    url_entry.insert(0, url)

# ------------------ Tkinter GUI ------------------
root = tk.Tk()
root.title("YouTube Video & Audio Downloader")
root.geometry("550x400")
root.resizable(False, False)

# ------------------ Dark & Light Mode ------------------
def switch_theme():
    if theme_var.get() == "Dark Mode":
        root.config(bg="#181818")
        title_label.config(bg="#181818", fg="#ff0000")
        resolution_dropdown.config(background="#181818", foreground="white")
        progress_label.config(bg="#181818", fg="white")
    else:
        root.config(bg="white")
        title_label.config(bg="white", fg="black")
        resolution_dropdown.config(background="white", foreground="black")
        progress_label.config(bg="white", fg="black")

theme_var = tk.StringVar(value="Dark Mode")
theme_dropdown = ttk.Combobox(root, textvariable=theme_var, values=["Dark Mode", "Light Mode"], state="readonly")
theme_dropdown.pack(pady=5)
theme_dropdown.bind("<<ComboboxSelected>>", lambda e: switch_theme())

# ------------------ URL Entry ------------------
tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Enable drag & drop (Mac/Linux support)
try:
    root.drop_target_register(tk.DND_FILES)
    root.dnd_bind("<<Drop>>", drop)
except AttributeError:
    pass

# ------------------ Buttons ------------------
fetch_btn = tk.Button(root, text="Fetch Video Info", command=fetch_video_info)
fetch_btn.pack(pady=5)

preview_btn = tk.Button(root, text="Preview Before Download", command=preview_video, state=tk.DISABLED)
preview_btn.pack(pady=5)

# ------------------ Title Label ------------------
title_label = tk.Label(root, text="Title: ", wraplength=500)
title_label.pack(pady=5)

# ------------------ Resolution Dropdown ------------------
resolution_var = tk.StringVar()
resolution_dropdown = ttk.Combobox(root, textvariable=resolution_var, state="readonly")
resolution_dropdown.pack(pady=5)

# ------------------ Download Button ------------------
download_btn = tk.Button(root, text="Download", command=download_video)
download_btn.pack(pady=10)

# ------------------ Animated Progress Bar ------------------
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=300, mode="determinate")
progress_bar.pack(pady=5)

# ------------------ Progress Label ------------------
progress_label = tk.Label(root, text="")
progress_label.pack(pady=5)

# Apply Initial Theme
switch_theme()

# Run Tkinter Loop
root.mainloop()