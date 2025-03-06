import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox
import threading

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
        else:
            messagebox.showerror("Error", "No video streams found!")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch video: {e}")

# ------------------ Function to Download Video or Audio ------------------
def download_video():
    url = url_entry.get().strip()
    resolution = resolution_var.get()

    if not url or not resolution:
        messagebox.showerror("Error", "Please enter a URL and select an option!")
        return
    
    if resolution == "Audio Only":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(title)s.%(ext)s",
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
            "outtmpl": "%(title)s.%(ext)s",
            "progress_hooks": [progress_hook]
        }

    def run_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", "Download complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {e}")

    threading.Thread(target=run_download, daemon=True).start()

# ------------------ Progress Indicator ------------------
def progress_hook(d):
    if d["status"] == "downloading":
        progress_label.config(text=f"Downloading... {d['_percent_str']}")
    elif d["status"] == "finished":
        progress_label.config(text="✅ Download Complete!")

# ------------------ Tkinter GUI ------------------
root = tk.Tk()
root.title("YouTube Video & Audio Downloader")
root.geometry("500x350")
root.resizable(False, False)

# URL Entry
tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Fetch Info Button
fetch_btn = tk.Button(root, text="Fetch Video Info", command=fetch_video_info)
fetch_btn.pack(pady=5)

# Title Label
title_label = tk.Label(root, text="Title: ", wraplength=450)
title_label.pack(pady=5)

# Resolution Dropdown
resolution_var = tk.StringVar()
resolution_dropdown = ttk.Combobox(root, textvariable=resolution_var, state="readonly")
resolution_dropdown.pack(pady=5)

# Download Button
download_btn = tk.Button(root, text="Download", command=download_video)
download_btn.pack(pady=10)

# Progress Label
progress_label = tk.Label(root, text="")
progress_label.pack(pady=5)

# Run Tkinter Loop
root.mainloop()
