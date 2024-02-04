from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from pydub.effects import normalize
import ffmpeg
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path

# Constants for compression ratios and target audio level for normalization
COMPRESSION_THRESHOLD = -20.0  # dB
COMPRESSION_RATIO = 2.0
NORMALIZATION_DBFS = -14.0  # dBFS, typical for podcasts

class FileSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video File Selector")

        # Set the initial download path
        self.download_path = "C:\\"

        # Create and set the download path label
        self.path_label = tk.Label(root, text="Download Path:")
        self.path_label.pack()

        self.path_var = tk.StringVar()
        self.path_var.set(self.download_path)

        self.path_entry = tk.Entry(
            root, textvariable=self.path_var, state="readonly", width=40)
        self.path_entry.pack()

        # Create the Browse button
        self.browse_button = tk.Button(
            root, text="Browse", command=self.browse_file)
        self.browse_button.pack()

    def browse_file(self):
        # Open the file dialog
        file_path = filedialog.askopenfilename(initialdir=self.download_path, title="Select a Video File",
                                               filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])

        if file_path:
            # Update the download path entry with the selected file's path
            self.download_path = "/".join(file_path.split("/")[:-1])
            self.path_var.set(self.download_path)
            filepath = Path(file_path)
            out = Path(filepath.parent /
                       f"{filepath.stem}_converted{filepath.suffix}")
            process_video(str(file_path), str(out))



def compress_and_normalize_audio(audio_segment):
    """
    Compresses and normalizes the given PyDub AudioSegment.
    """
    # Apply compression
    audio_segment = audio_segment.compress_dynamic_range(
        threshold=COMPRESSION_THRESHOLD,
        ratio=COMPRESSION_RATIO
    )

    # Normalize audio level
    return normalize(audio_segment, headroom=NORMALIZATION_DBFS)


def process_video(video_path, output_path):
    # Load the video file
    video_clip = VideoFileClip(video_path)

    # Saving original audio to a temp file
    temp_audio_path = "temp_audio.wav"
    video_clip.audio.write_audiofile(temp_audio_path)

    # Load audio using PyDub for processing
    original_audio = AudioSegment.from_file(temp_audio_path)

    # Compress and normalize audio
    processed_audio = compress_and_normalize_audio(original_audio)

    # Save the processed audio to a new temp file
    processed_audio_path = "processed_audio.wav"
    processed_audio.export(processed_audio_path, format="wav")

    # Load the processed audio into MoviePy
    new_audio_clip = AudioFileClip(processed_audio_path)

    # Set the new audio clip to the video
    video_clip.audio = new_audio_clip

    # Write the video file with the new audio
    video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    # Cleanup temp files
    os.remove(temp_audio_path)
    os.remove(processed_audio_path)
    exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSelectorApp(root)
    root.mainloop()

