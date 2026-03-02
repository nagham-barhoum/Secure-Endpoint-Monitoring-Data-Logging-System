# Secure Endpoint Monitoring & Data Logging System

🎓 Academic Cybersecurity Research Project

---

## 📌 Overview

This repository contains an academic prototype of an endpoint monitoring and data logging system developed for cybersecurity research and digital forensics studies.

The system demonstrates controlled data capture techniques within a supervised and ethical academic environment.

⚠️ This project is strictly for educational and research purposes. It is NOT intended for unauthorized surveillance or malicious use.

---

## 🎯 Project Objectives

- Demonstrate endpoint activity capture techniques
- Explore integration with cloud storage APIs
- Study secure handling of captured data
- Apply cybersecurity best practices in secret management
- Simulate digital forensics data collection workflow

---

## 🧠 Core Features

- 🎤 Audio recording (controlled testing environment)
- 🖥️ Screen capture
- 📷 Front camera capture
- ⌨️ Keystroke logging simulation
- ☁️ Secure upload integration using Google Drive API
- 🗂 Structured data logging

---

## 🏗 System Architecture (High-Level)

1. Data Capture Layer  
   - Audio, screen, camera, keystroke input

2. Processing & Packaging Layer  
   - File generation
   - Structured logging

3. Cloud Integration Layer  
   - Google Drive API authentication
   - Secure file upload

---

## 🛠 Technologies Used

- Python
- Google Drive API
- Service Account Authentication
- Local File Handling & Logging

---

## 📁 Project Structure
Secure-Endpoint-Monitoring-Data-Logging-System/
│
├── Keylogger.py
├── ready_with_the_four_iteam.py
├── fix_with_the_four.py
├── credentials.example.json
├── README.md

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```
git clone https://github.com/nagham-barhoum/Secure-Endpoint-Monitoring-Data-Logging-System.git
cd Secure-Endpoint-Monitoring-Data-Logging-System
Install Dependencies
pip install -r requirements.txt

If requirements.txt is not available, install required Python packages manually.
Google Drive API Configuration

Create a Service Account inside Google Cloud

Generate a new private key

Download credentials JSON

Rename:

credentials.example.json → credentials.json

Insert your own credentials locally
Demonstration Video

A controlled academic demonstration is available via an unlisted YouTube link.

🔗 Video Link:
https://youtu.be/nzjjvl1DNR0

The video demonstrates:

System workflow

Data capture simulation

Google Drive integration

Execution in controlled environment

🛡 Ethical & Legal Notice

This project was developed in a controlled academic environment for research purposes only.

It must not be used for:

Unauthorized monitoring

Privacy violations

Malicious surveillance

Illegal activity

The author does not take responsibility for misuse of this code.

📚 Academic Context

This project was developed as a graduation research prototype in the field of:

Cybersecurity

Endpoint Monitoring Systems

Digital Forensics

Secure Cloud Integration

📜 License

This repository is published for academic and research reference only.

All rights reserved.
```