# Object Detection and Recognition Using Webcam with Voice Using YOLO

## 📌 Project Overview

This project is an AI-based assistive vision system that uses a webcam and the YOLO object detection algorithm to detect and recognize objects in real time.

The system provides visual information through bounding boxes, confidence scores, tracking IDs, distance estimation, and safety levels. It also provides voice announcements to help users understand the surrounding objects.

## 🎯 Objective

The main objective of this project is to develop a real-time object detection and recognition system that can provide useful information about nearby objects through both visual and voice feedback.

The system is designed as a prototype of an assistive vision system that can potentially help visually impaired users understand their surroundings.

## 🛠️ Technologies Used

* Python
* YOLO
* OpenCV
* Tkinter
* Pillow
* pyttsx3
* CSV
* Webcam

## ⭐ Main Features

### 1. Real-Time Object Detection

The system uses YOLO to identify objects captured by the webcam in real time.

### 2. Confidence Score

Each detected object displays a confidence score indicating how confident the model is about the detection.

### 3. Object Counting

The system displays the number of objects detected in the current camera frame.

### 4. Object Tracking

Each detected object can receive a tracking ID, allowing the system to follow objects across video frames.

### 5. Distance Estimation

The system estimates the approximate distance of detected objects using the calibrated pixel-width measurement.

The current calibration used in the project is:

**187 pixels = 1 meter**

### 6. Safety Classification

Objects are classified according to their estimated distance:

* SAFE
* WARNING
* DANGER

### 7. Voice Assistance

The system announces detected objects using text-to-speech.

Nearby objects receive stronger warning messages.

### 8. Smart Voice Priority

When multiple objects are detected, the system gives priority to objects that are closer or have a higher safety risk.

### 9. Graphical User Interface

The system provides a GUI containing:

* Live webcam feed
* Object count
* FPS
* Tracking status
* Voice status
* Detection history
* Camera controls

### 10. Detection History

The GUI displays information about detected objects including:

* Object name
* Tracking ID
* Confidence
* Distance
* Safety status

### 11. CSV Logging

Important detection events are stored in:

`detection_history.csv`

The CSV contains:

* Time
* Object
* Tracking ID
* Confidence
* Distance
* Status

### 12. Camera Controls

The GUI provides:

* START CAMERA
* STOP CAMERA
* EXIT

## 🔄 System Workflow

```text
Webcam
   ↓
Video Frame
   ↓
YOLO Object Detection
   ↓
Object Recognition
   ↓
Confidence Calculation
   ↓
Object Tracking
   ↓
Distance Estimation
   ↓
Safety Classification
   ↓
Smart Voice Alert
   ↓
GUI Display
   ↓
Detection History
   ↓
CSV Logging
```

## 📂 Project Structure

```text
yolo_obj_det/
│
├── gui.py
├── main.py
├── yolo11n.pt
├── detection_history.csv
├── requirements.txt
├── README.md
└── venv/
```

## ▶️ How to Run

### Step 1 — Activate the virtual environment

Open PowerShell inside the project folder and run:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 2 — Run the application

```powershell
python gui.py
```

### Step 3 — Use the webcam

Allow the application to access the webcam.

The system will begin detecting objects and displaying the results in the GUI.

## 📊 Detection History

The project automatically records meaningful detection events in:

```text
detection_history.csv
```

This file can be opened using Microsoft Excel for further analysis.

## 🌍 Real-Life Application

This project can be considered a prototype for an assistive vision system.

For visually impaired users, the system can provide information about objects in front of a camera through voice announcements.

For example:

```text
"Person detected. Approximately 1.5 meters away."

"Warning. Chair is nearby."

"Warning! Bottle is very close."
```

## ⚠️ Limitations

* Distance estimation is approximate.
* The current distance calculation depends on calibration.
* Webcam quality can affect detection accuracy.
* Lighting conditions can affect object detection.
* Voice announcements depend on the text-to-speech system.
* YOLO detection accuracy depends on the trained model and detected object category.

## 🚀 Future Scope

Possible future improvements include:

* Improved distance estimation using depth cameras
* GPS and navigation integration
* Mobile application support
* More advanced obstacle detection
* Improved voice interaction
* Custom-trained object detection models
* Edge/embedded deployment
* Real-world assistive device integration

## 👩‍💻 Project Type

**Artificial Intelligence / Computer Vision / Deep Learning**

## 📌 Project Title

**Object Detection and Recognition Using Webcam with Voice Using YOLO Algorithm**
