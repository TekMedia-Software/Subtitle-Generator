import os
import shutil
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from PIL import Image, ImageTk
from faster_whisper import WhisperModel
from googletrans import Translator
import ffmpeg
import shlex
import subprocess
import math
import cv2

class SubtitleGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TekMededia's Subtitle Generator")
        self.root.protocol("WM_DELETE_WINDOW", self.clear_outputs)
         # Set the window size
        window_width = 400
        window_height = 450
        
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the position to center the window
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        # Set the geometry with the calculated position
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        self.root.configure(bg="#F4F7FA")
        self.root.resizable(False, False)

        # First window UI
        self.setup_window1()

        self.download_frame = tk.Frame(self.root)
        self.download_frame.pack(pady=20)

        self.input_video_path = None 
        self.generated_video = None

        # Variables
        self.input_video_path = None
        self.output_video_path = None
        self.subtitles_folder = os.path.join(os.path.dirname(__file__), "./session_temp/subtitles")
        self.outputs_folder = os.path.join(os.path.dirname(__file__), "./session_temp/outputs")
        if not os.path.exists(self.subtitles_folder):
            os.makedirs(self.subtitles_folder)
        if not os.path.exists(self.outputs_folder):
            os.makedirs(self.outputs_folder)

    def setup_window1(self):
        """Setup the first window UI."""
        self.title_label = tk.Label(
            self.root, text="Subtitle Generator", font=("Helvetica", 20, "bold"),
            bg="#F4F7FA", fg="#2C3E50"  # Dark blue text for the title
        )
        self.title_label.pack(padx=(50, 20), pady=(20, 0))
        
        
        self.title_label_desc = tk.Label(
            self.root, text="Upload MP4 videos to get subtitles", font=("Helvetica", 12),
            bg="#F4F7FA", fg="#2C3E50"  # Dark blue text for the title
        )
        self.title_label_desc.pack(padx=(50, 20), pady=(0, 15))

        novideoThumbnail_path = os.path.join(os.path.dirname(__file__), "static", "thumbnail.png")
        self.thumbnail_label = tk.Label(self.root, bg="#F4F7FA")
        self.show_initial_thumbnail(novideoThumbnail_path)
        self.thumbnail_label.pack(pady=(10, 0))

        self.label2 = tk.Label(
            self.root, 
            text="", 
            font=("Helvetica", 12, "bold"),  
            bg="#F4F7FA", 
            fg="#34495E" 
        )
        self.label2.pack(pady=0)

        self.select_button = tk.Button(
            self.root, text="Browse", command=self.select_video_file,
            bg="#054991", fg="white", font=("Helvetica", 12, "bold"), height=2, width=15
        )
        self.select_button.pack(pady=(25,5))

        self.upload_button = tk.Button(
            self.root, text="Upload", command=self.open_window2, state=tk.DISABLED,
            bg="#054991", fg="white", font=("Helvetica", 12, "bold"), height=2, width=15 
        )
        self.upload_button.pack(pady=5)

       
        self.add_logo(self.root)

    def add_logo(self, window):
        """Add the logo to a given window."""
        # Load the logo image
        logo_path = os.path.join(os.path.dirname(__file__), "static", "logo.png")
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((65, 65))  # Resize the image if necessary

        # Convert the image to a format tkinter can use
        logo_tk = ImageTk.PhotoImage(logo_image)

        # Create a label widget to display the logo
        logo_label = tk.Label(window, image=logo_tk, bg="#F4F7FA")
        logo_label.image = logo_tk  # Keep a reference to the image

        # Adjust the x, y coordinates as necessary for each window
        if window == self.root:
            logo_label.place(x=25, y=10)  # Position on main window (adjust as needed)
        elif window == self.window2:
            logo_label.place(x=25, y=10)  

    def select_video_file(self):
        self.input_video_path = filedialog.askopenfilename(
            title="Select a Video File",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if self.input_video_path:
            self.label2.config(text=f"{os.path.basename(self.input_video_path)}")
            self.upload_button.config(state=tk.NORMAL)
            self.show_thumbnail(self.input_video_path)

    def show_thumbnail(self, video_path):
        """Generate and display a thumbnail from the middle of the selected video."""
        cap = cv2.VideoCapture(video_path)
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        middle_frame_index = total_frames // 2

        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index)

        ret, frame = cap.read()
        
        if ret:
            # Convert the frame to RGB (OpenCV uses BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to an Image object using Pillow
            image = Image.fromarray(frame)

            # Resize the image to fit the thumbnail size
            image.thumbnail((200, 150))  # Adjust size as needed

            # Convert the Image to a format tkinter can display
            thumbnail_tk = ImageTk.PhotoImage(image)

            # Update the thumbnail label with the image
            self.thumbnail_label.config(image=thumbnail_tk)
            self.thumbnail_label.image = thumbnail_tk  # Keep a reference to the image
        
        cap.release()

    def show_initial_thumbnail(self, image_path):
        """Generate and display a thumbnail from the middle of the selected video."""
        cap = cv2.VideoCapture(image_path)
        ret, frame = cap.read()
        
        if ret:
            # Convert the frame to RGB (OpenCV uses BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to an Image object using Pillow
            image = Image.fromarray(frame)

            # Resize the image to fit the thumbnail size
            image.thumbnail((200, 150))  # Adjust size as needed

            # Convert the Image to a format tkinter can display
            thumbnail_tk = ImageTk.PhotoImage(image)

            # Update the thumbnail label with the image
            self.thumbnail_label.config(image=thumbnail_tk)
            self.thumbnail_label.image = thumbnail_tk  # Keep a reference to the image
        
        cap.release()
    
    def add_back_button(self):
        # Back button
        self.back_button = tk.Button(
            self.window2, text="Back to Uploads", command=self.back_to_uploads,
            bg="#2C3E50", fg="white", font=("Helvetica", 12, "bold"), height=2, width=15
        )
        self.back_button.pack(pady=(0,0))

    def check_button_state_changed(self, *args):
        """
        This function is called whenever a checkbox state changes.
        It checks if at least one checkbox is selected and enables/disables the 'Generate Subtitles' button.
        """
        # Check if any checkbox is selected
        any_selected = any(var.get() for var in self.language_vars.values())

        # Enable or disable the 'Generate Subtitles' button
        if any_selected:
            self.convert_button.config(state=tk.NORMAL)  # Enable button
        else:
            self.convert_button.config(state=tk.DISABLED)  # Disable button


    def open_window2(self):
        self.root.withdraw()  # Hide window 1
        self.window2 = tk.Toplevel(self.root)
        self.window2.title("TekMededia's Subtitle Generator")
        self.window2.protocol("WM_DELETE_WINDOW", self.clear_outputs)  # Ensure close_window is called properly
        self.window2.resizable(False, False)
        # Set the window size
        window_width = 400
        window_height = 450
        
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the position to center the window
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        # Set the geometry with the calculated position
        self.window2.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.window2.configure(bg="#F4F7FA")

        self.add_logo(self.window2)

        title_label = tk.Label(
            self.window2, text="Subtitle Generator", font=("Helvetica", 20, "bold"),
            bg="#F4F7FA", fg="#2C3E50"  # Dark blue text for the title
        )
        title_label.pack(padx=(50, 20), pady=(20, 0))
        
        
        title_label_desc = tk.Label(
            self.window2, text="Upload MP4 videos to get subtitles", font=("Helvetica", 12),
            bg="#F4F7FA", fg="#2C3E50"  # Dark blue text for the title
        )
        title_label_desc.pack(padx=(50, 20), pady=(0, 15))

        # Display video file name
        self.video_name_label = tk.Text(self.window2, height=1, width=30, bg="#F4F7FA", fg="#2C3E50", font=("Helvetica", 13, "bold"), bd=0, highlightthickness=0)
        self.video_name_label.pack(pady=(10,5))

        # Insert the static part of the text
        self.video_name_label.insert(tk.END, "Video File: ")

        # Change color for the video file name part
        self.video_name_label.insert(tk.END, os.path.basename(self.input_video_path), ("highlight",))

        # Apply tag for color change
        self.video_name_label.tag_configure("highlight", foreground="#054991")  # You can change this color

        # Center the text
        self.video_name_label.tag_add("center", "1.0", "end")
        self.video_name_label.tag_configure("center", justify='center')

        # Disable editing
        self.video_name_label.config(state=tk.DISABLED)


        # Language selection label
        self.language_label = tk.Label(
            self.window2, text="Choose Languages:", font=("Helvetica", 13, "bold"),
            bg="#F4F7FA", fg="#2C3E50"
        )
        self.language_label.pack(pady=(5,8))

        # Available language options
        language_options = ["English", "Hindi", "Tamil", "German", "Spanish"]
        self.language_vars = {}  # Dictionary to store language variable references
        self.language_checkboxes = []  # List to store checkbox widgets

        # Create a frame to contain checkboxes for proper alignment
        self.language_frame = tk.Frame(self.window2, bg="#F4F7FA")
        self.language_frame.pack(pady=0, padx=20, anchor="center")

        # Loop through the language options and create checkboxes
        for language in language_options:
            var = tk.BooleanVar()  # Variable to track the checkbox state
            checkbox = tk.Checkbutton(
                self.language_frame, text=language, variable=var, bg="#F4F7FA", fg="#054991",
                font=("Helvetica", 12, "bold"), onvalue=True, offvalue=False,
                bd=0, highlightthickness=0
            )
            checkbox.pack(side="top", anchor="w", padx=20, pady=2)  # side="top" for vertical stacking

            # Store the BooleanVar and checkbox widget for later use
            self.language_vars[language] = var
            self.language_checkboxes.append(checkbox)
            var.trace_add("write", self.check_button_state_changed)
        
        # Placeholder for displaying selected languages
        self.language_display_label = tk.Label(
            self.window2, text="", font=("Helvetica", 12, "bold"), bg="#F4F7FA", fg="#054991"
        )
        self.language_display_label.pack_forget()


        # Convert button
        self.convert_button = tk.Button(
            self.window2, text="Generate Subtitles", command=self.start_conversion,
            bg="#054991", fg="white", font=("Helvetica", 12, "bold"), height=2, width=15, state=tk.DISABLED
        )
        self.convert_button.pack(pady=(20,10))

        self.add_back_button()

        self.download_frame = tk.Frame(self.window2, bg="#F4F7FA")
        self.download_frame.pack(pady=10)

    def start_conversion(self):
        """Start subtitle generation process in a separate thread."""
        self.back_button.config(state=tk.DISABLED)
        self.language_frame.pack_forget()
        # Collect selected languages
        self.selected_languages = [
            language for language, var in self.language_vars.items() if var.get()
        ]

        # Hide checkboxes
        for checkbox in self.language_checkboxes:
            checkbox.pack_forget()  # Remove the checkboxes from the UI

        # Update the label to display selected languages
        if self.selected_languages:
            selected_text = ", ".join(self.selected_languages)
        else:
            selected_text = "No languages selected.\nNo subtitle generated."

        self.language_display_label.pack(pady=(0, 0), before=self.convert_button)
        self.language_display_label.config(text=selected_text)
        self.language_label.config(text="Selected Languages : ")

        # Display the "Generating Subtitles" text after button click
        self.convert_button.config(state=tk.DISABLED, text="Generating...")
        
        # Start the subtitle generation in a separate thread
        thread = threading.Thread(target=self.generate_subtitles_process)
        thread.start()

    def generate_subtitles_process(self):
        try:
            # Extract audio and transcribe the video
            extracted_audio = self.extract_audio()
            language, segments = self.transcribe(audio=extracted_audio)
            subtitle_file = self.generate_subtitle_file(language=language, segments=segments)

            if os.path.exists(extracted_audio):                 
                os.remove(extracted_audio)

            selected_languages = [lang for lang, var in self.language_vars.items() if var.get()]
            language_codes = {
                "English": "en", "German": "de", "Tamil": "ta",
                "Hindi": "hi", "Spanish": "es"
            }

            subtitle_files = []

            # Generate and translate subtitles for each selected language
            for selected_language in selected_languages:
                subtitle_file_for_language = subtitle_file  # Default to English
                if selected_language != "English":
                    target_language = language_codes[selected_language]
                    subtitle_file_for_language = self.translate_subtitle(subtitle_file, target_language=target_language)
                
                subtitle_files.append((subtitle_file_for_language, language_codes[selected_language]))

            # Embed all subtitle tracks into one video
            output_path = self.add_subtitle_to_video(subtitle_files)
            self.generated_video = output_path  # Store the generated video path
            self.convert_button.pack_forget()
            # Add the play button and download button for the final video
            self.create_play_button(self.generated_video)  # Add Play button
            self.create_download_button(self.generated_video)  # Add Download button
            self.back_button.config(state=tk.ACTIVE)
            messagebox.showinfo("Success", "Subtitle generation completed with all selected language tracks embedded!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


    def download_video(self, video_path):
        if os.path.exists(video_path):
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(downloads_folder):
                os.makedirs(downloads_folder)

            download_path = os.path.join(downloads_folder, os.path.basename(video_path))
            shutil.copy(video_path, download_path)
            messagebox.showinfo("Success", f"Video saved to: {download_path}")
        else:
            messagebox.showerror("Error", "No video found!")

    def extract_audio(self):
        extracted_audio = f"./session_temp/audio-{os.path.basename(self.input_video_path).replace('.mp4', '.wav')}"
        stream = ffmpeg.input(self.input_video_path)
        stream = ffmpeg.output(stream, extracted_audio)
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return extracted_audio

    def transcribe(self, audio):
        model = WhisperModel("small")
        segments, info = model.transcribe(audio)
        language = info.language
        return language, segments

    def format_time(self, seconds):
        hours = math.floor(seconds / 3600)
        seconds %= 3600
        minutes = math.floor(seconds / 60)
        seconds %= 60
        milliseconds = round((seconds - math.floor(seconds)) * 1000)
        seconds = math.floor(seconds)
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"
        return formatted_time

    def generate_subtitle_file(self, language, segments):
        subtitle_file = os.path.join(self.subtitles_folder, f"sub-{os.path.basename(self.input_video_path).replace('.mp4', '')}.{language}.srt")
        text = ""
        for index, segment in enumerate(segments):
            segment_start = self.format_time(segment.start)
            segment_end = self.format_time(segment.end)
            text += f"{str(index + 1)}\n"
            text += f"{segment_start} --> {segment_end}\n"
            text += f"{segment.text}\n\n"

        with open(subtitle_file, "w") as f:
            f.write(text)

        return subtitle_file

    def translate_subtitle(self, subtitle_file, target_language):
        translator = Translator()
        translated_subtitle_file = subtitle_file.replace(".en.", f".{target_language}.")
        
        with open(subtitle_file, "r") as f:
            lines = f.readlines()

        with open(translated_subtitle_file, "w") as f:
            for line in lines:
                if "-->" not in line and line.strip().isdigit() == False:
                    if line.strip():  # Translate only non-empty lines
                        try:
                            translated_line = translator.translate(line.strip(), dest=target_language).text
                        except Exception as e:
                            translated_line = line  # Fall back to the original line
                            print(f"Translation failed for line: {line.strip()}, Error: {e}")
                        f.write(translated_line + "\n")
                    else:
                        f.write(line)  # Keep empty lines as-is
                else:
                    f.write(line)

        return translated_subtitle_file

    def add_subtitle_to_video(self, subtitle_files):
        output_video_name = f"{os.path.splitext(os.path.basename(self.input_video_path))[0]}_multi_lang_subtitled.mp4"
        output_video_path = os.path.join(self.outputs_folder, output_video_name)

        # Input stream for the video
        video_input_stream = ffmpeg.input(self.input_video_path)

        # List for subtitle streams and their respective metadata
        subtitle_streams = []
        output_args = {
            'c:v': 'copy',  # Copy the video codec
            'c:a': 'copy',  # Copy the audio codec
            'c:s': 'mov_text',  # Set subtitle codec for MP4
        }
        language_codes = {
                "English": "en", "German": "de", "Tamil": "ta",
                "Hindi": "hi", "Spanish": "es"
            }

        # Add subtitle streams and define metadata with subtitle file name
        for idx, (subtitle_file, _) in enumerate(subtitle_files):
            subtitle_stream = ffmpeg.input(subtitle_file)
            subtitle_file_name = os.path.basename(subtitle_file)  # Extract the subtitle file name
            subtitle_file_name = subtitle_file_name[:-4]

            for lang in language_codes:
                if subtitle_file_name.endswith(language_codes[lang]):
                    subtitle_file_name = lang
            
            # Append the subtitle stream
            subtitle_streams.append(subtitle_stream)
            
            # Set the subtitle file name as the track name metadata
            output_args[f'metadata:s:s:{idx}'] = f'title={subtitle_file_name}'

        # Build the FFmpeg output with mapped streams
        streams = [video_input_stream] + subtitle_streams
        stream = ffmpeg.output(
            *streams,
            output_video_path,
            **output_args
        )

        # Run FFmpeg with the generated stream
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        return output_video_path


    def create_download_button(self, video_path):
        button = tk.Button(
            self.download_frame,
            text="Download",
            command=lambda: self.download_video(video_path),
            bg="#054991", fg="white", font=("Helvetica", 12, "bold"),
            height=2, width=15
        )
        button.pack(pady=(5,0))
        self.add_back_button()

    def back_to_uploads(self):
        """Go back to the first window."""
        self.window2.destroy()  
        self.root.deiconify()  

    def create_play_button(self, video_path, subtitle_file=None):
        """Create a play button for the video with subtitle options."""
        self.back_button.pack_forget()
        button = tk.Button(
            self.download_frame,
            text="Play with VLC",
            command=lambda: self.play_video(video_path, subtitle_file),
            bg="#054991", fg="white", font=("Helvetica", 12, "bold"),
            height=2, width=15
        )
        button.pack(pady=(15,5))

        

    def play_video(self, video_path, subtitle_file=None):
        """Play the generated subtitled video in a smaller VLC popup window at the center bottom of the screen."""
        if os.path.exists(video_path):
            width = 200
            height = 300

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            x_pos = (screen_width - width) // 2 
            y_pos = screen_height - height 

            command = [
                "vlc", video_path,
                "--width", str(width),
                "--height", str(height),
                "--video-x", str(x_pos),
                "--video-y", str(y_pos),
                "--no-video-title-show",
                "--no-fullscreen",
                "--vout=x11", 
            ]
 
            if subtitle_file and os.path.exists(subtitle_file):
                command.extend(["--sub-file", subtitle_file])

            subprocess.run(command)
        else:
            messagebox.showerror("Error", "Video not found!")

    def clear_outputs(self):
        shutil.rmtree("./session_temp")
        root.destroy()

def create_session_temp_structure(base_path):
    # Define the paths for the directories
    session_temp_path = os.path.join(base_path, "session_temp")
    outputs_path = os.path.join(session_temp_path, "outputs")
    subtitles_path = os.path.join(session_temp_path, "subtitles")
    
    # Remove the session_temp directory if it exists
    if os.path.exists(session_temp_path):
        shutil.rmtree(session_temp_path)  # Deletes the directory and all its contents
    
    # Create the session_temp directory and its subdirectories
    os.makedirs(outputs_path)  # Create the "outputs" directory
    os.makedirs(subtitles_path)  # Create the "subtitles" directory

if __name__ == "__main__":
    create_session_temp_structure("./")
    root = tk.Tk()
    app = SubtitleGeneratorApp(root)
    root.mainloop()

