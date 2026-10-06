import tkinter as tk
import cv2
import time
import threading
import queue

from PIL import Image, ImageTk
from ultralytics import YOLO
import pyttsx3


# ============================================================
# SMART YOLO ASSISTIVE VISION SYSTEM
# STEP 7.8
# YOLO + TRACKING + DISTANCE + SMART VOICE + HISTORY
# ============================================================


# ============================================================
# 1. LOAD YOLO MODEL
# ============================================================

print("Loading YOLO model...")

model = YOLO("yolo11n.pt")

print("YOLO model loaded.")


# ============================================================
# 2. DISTANCE CALIBRATION
# ============================================================

# Your actual calibration:
# 187 pixels = 1 meter

REFERENCE_PIXEL_WIDTH = 187
REFERENCE_DISTANCE = 1.0


def calculate_distance(pixel_width):

    if pixel_width <= 0:
        return None

    distance = (
        REFERENCE_PIXEL_WIDTH
        * REFERENCE_DISTANCE
        / pixel_width
    )

    return distance


# ============================================================
# 3. VOICE QUEUE
# ============================================================

voice_queue = queue.Queue()


def voice_worker():

    engine = pyttsx3.init()

    engine.setProperty(
        "rate",
        160
    )

    engine.setProperty(
        "volume",
        1.0
    )

    while True:

        text = voice_queue.get()

        if text is None:

            voice_queue.task_done()

            break

        try:

            print(
                "VOICE:",
                text
            )

            engine.say(text)

            engine.runAndWait()

        except Exception as e:

            print(
                "Voice error:",
                e
            )

        voice_queue.task_done()


voice_thread = threading.Thread(
    target=voice_worker,
    daemon=True
)

voice_thread.start()


# ============================================================
# 4. SMART VOICE SETTINGS
# ============================================================

VOICE_COOLDOWN = 5

last_spoken = {}

MAX_VOICE_QUEUE = 2


def speak(text):

    if voice_queue.qsize() >= MAX_VOICE_QUEUE:

        return

    voice_queue.put(text)


# ============================================================
# 5. CREATE GUI
# ============================================================

root = tk.Tk()

root.title(
    "Smart YOLO Assistive Vision System"
)

root.geometry(
    "1000x850"
)

root.resizable(
    False,
    False
)


# ============================================================
# 6. TITLE
# ============================================================

title_label = tk.Label(
    root,
    text="SMART YOLO ASSISTIVE VISION SYSTEM",
    font=("Arial", 22, "bold")
)

title_label.pack(
    pady=10
)


# ============================================================
# 7. CAMERA AREA
# ============================================================

camera_frame = tk.Frame(
    root,
    width=900,
    height=450,
    relief="solid",
    borderwidth=2
)

camera_frame.pack(
    pady=5
)

camera_frame.pack_propagate(
    False
)


camera_label = tk.Label(
    camera_frame
)

camera_label.pack(
    expand=True
)


# ============================================================
# 8. INFORMATION AREA
# ============================================================

info_frame = tk.Frame(
    root
)

info_frame.pack(
    pady=8
)


objects_label = tk.Label(
    info_frame,
    text="Objects: 0",
    font=("Arial", 13, "bold")
)

objects_label.grid(
    row=0,
    column=0,
    padx=20
)


fps_label = tk.Label(
    info_frame,
    text="FPS: 0",
    font=("Arial", 13, "bold")
)

fps_label.grid(
    row=0,
    column=1,
    padx=20
)


tracking_label = tk.Label(
    info_frame,
    text="Tracking: ON",
    font=("Arial", 13, "bold")
)

tracking_label.grid(
    row=0,
    column=2,
    padx=20
)


voice_label = tk.Label(
    info_frame,
    text="Smart Voice: ON",
    font=("Arial", 13, "bold")
)

voice_label.grid(
    row=0,
    column=3,
    padx=20
)


# ============================================================
# 9. STATUS
# ============================================================

status_label = tk.Label(
    root,
    text="Starting...",
    font=("Arial", 14, "bold")
)

status_label.pack(
    pady=3
)


# ============================================================
# 10. DETECTION HISTORY
# ============================================================

history_frame = tk.Frame(
    root,
    relief="solid",
    borderwidth=1
)

history_frame.pack(
    pady=5
)


history_title = tk.Label(
    history_frame,
    text="DETECTION HISTORY",
    font=("Arial", 13, "bold")
)

history_title.pack(
    pady=3
)


history_text = tk.Text(
    history_frame,
    width=105,
    height=7,
    font=("Courier New", 10)
)

history_text.pack(
    padx=5,
    pady=3
)


history_text.insert(
    tk.END,
    "Object        ID     Confidence     Distance      Status\n"
)

history_text.insert(
    tk.END,
    "-" * 82 + "\n"
)

history_text.config(
    state=tk.DISABLED
)


# ============================================================
# 11. UPDATE HISTORY
# ============================================================

def update_history(detected_objects):

    history_text.config(
        state=tk.NORMAL
    )

    history_text.delete(
        "1.0",
        tk.END
    )

    history_text.insert(
        tk.END,
        "Object        ID     Confidence     Distance      Status\n"
    )

    history_text.insert(
        tk.END,
        "-" * 82 + "\n"
    )


    if len(detected_objects) == 0:

        history_text.insert(
            tk.END,
            "No objects detected.\n"
        )


    for item in detected_objects:

        object_name = item["name"]

        track_id = item["id"]

        confidence = item["confidence"]

        distance = item["distance"]

        safety = item["safety"]


        if track_id is None:

            track_id = "-"


        confidence_text = (
            f"{confidence * 100:.1f}%"
        )


        if distance is not None:

            distance_text = (
                f"{distance:.2f} m"
            )

        else:

            distance_text = "-"


        line = (
            f"{object_name:<14}"
            f"{str(track_id):<7}"
            f"{confidence_text:<15}"
            f"{distance_text:<14}"
            f"{safety}\n"
        )


        history_text.insert(
            tk.END,
            line
        )


    history_text.config(
        state=tk.DISABLED
    )


# ============================================================
# 12. OPEN WEBCAM
# ============================================================

print("Opening webcam...")

cap = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
)


if not cap.isOpened():

    print(
        "Camera 0 failed."
    )

    cap.release()

    cap = cv2.VideoCapture(
        1,
        cv2.CAP_DSHOW
    )


if not cap.isOpened():

    print(
        "ERROR: Webcam could not be opened."
    )

    status_label.config(
        text="Camera Error"
    )


# ============================================================
# 13. FPS
# ============================================================

previous_time = time.time()


# ============================================================
# 14. VOICE PRIORITY
# ============================================================

def get_priority(item):

    safety = item["safety"]

    distance = item["distance"]


    if safety == "DANGER":

        safety_priority = 0

    elif safety == "WARNING":

        safety_priority = 1

    else:

        safety_priority = 2


    if distance is None:

        distance_priority = 999

    else:

        distance_priority = distance


    return (
        safety_priority,
        distance_priority
    )


# ============================================================
# 15. SMART VOICE
# ============================================================

def process_voice(detected_objects):

    current_time = time.time()


    detected_objects.sort(
        key=get_priority
    )


    for item in detected_objects:

        object_name = item["name"]

        track_id = item["id"]

        distance = item["distance"]

        safety = item["safety"]


        object_key = (
            object_name,
            track_id
        )


        if object_key in last_spoken:

            elapsed = (
                current_time -
                last_spoken[object_key]
            )

            if elapsed < VOICE_COOLDOWN:

                continue


        # ----------------------------------------------------
        # DANGER MESSAGE
        # ----------------------------------------------------

        if safety == "DANGER":

            if distance is not None:

                message = (
                    f"Warning. "
                    f"{object_name} "
                    f"is very close. "
                    f"Approximately "
                    f"{distance:.1f} meters away."
                )

            else:

                message = (
                    f"Warning. "
                    f"{object_name} "
                    f"is very close."
                )


        # ----------------------------------------------------
        # WARNING MESSAGE
        # ----------------------------------------------------

        elif safety == "WARNING":

            if distance is not None:

                message = (
                    f"{object_name} detected. "
                    f"Approximately "
                    f"{distance:.1f} meters away."
                )

            else:

                message = (
                    f"{object_name} detected."
                )


        # ----------------------------------------------------
        # SAFE MESSAGE
        # ----------------------------------------------------

        else:

            if distance is not None:

                message = (
                    f"{object_name} detected. "
                    f"Approximately "
                    f"{distance:.1f} meters away."
                )

            else:

                message = (
                    f"{object_name} detected."
                )


        speak(
            message
        )


        last_spoken[
            object_key
        ] = current_time


        # Only one announcement is selected
        # during each camera update.

        break


# ============================================================
# 16. UPDATE CAMERA
# ============================================================

def update_camera():

    global previous_time


    # --------------------------------------------------------
    # READ CAMERA
    # --------------------------------------------------------

    ret, frame = cap.read()


    if not ret:

        status_label.config(
            text="Camera Error"
        )

        root.after(
            100,
            update_camera
        )

        return


    # --------------------------------------------------------
    # YOLO TRACKING
    # --------------------------------------------------------

    results = model.track(
        frame,
        persist=True,
        conf=0.30,
        verbose=False
    )


    result = results[0]


    # --------------------------------------------------------
    # COPY FRAME
    # --------------------------------------------------------

    annotated_frame = frame.copy()


    # --------------------------------------------------------
    # DETECTED OBJECTS
    # --------------------------------------------------------

    detected_objects = []


    # --------------------------------------------------------
    # OBJECT COUNT
    # --------------------------------------------------------

    object_count = 0


    if result.boxes is not None:

        object_count = len(
            result.boxes
        )


    # --------------------------------------------------------
    # PROCESS EACH OBJECT
    # --------------------------------------------------------

    if result.boxes is not None:

        boxes = result.boxes


        for i in range(
            len(boxes)
        ):

            # ------------------------------------------------
            # CONFIDENCE
            # ------------------------------------------------

            confidence = float(
                boxes.conf[i]
            )


            # ------------------------------------------------
            # CLASS ID
            # ------------------------------------------------

            class_id = int(
                boxes.cls[i]
            )


            object_name = model.names[
                class_id
            ]


            # ------------------------------------------------
            # BOUNDING BOX
            # ------------------------------------------------

            x1, y1, x2, y2 = map(
                int,
                boxes.xyxy[i].tolist()
            )


            # ------------------------------------------------
            # TRACK ID
            # ------------------------------------------------

            track_id = None


            if boxes.id is not None:

                track_id = int(
                    boxes.id[i]
                )


            # ------------------------------------------------
            # PIXEL WIDTH
            # ------------------------------------------------

            pixel_width = (
                x2 - x1
            )


            # ------------------------------------------------
            # DISTANCE
            # ------------------------------------------------

            distance = calculate_distance(
                pixel_width
            )


            # ------------------------------------------------
            # SAFETY STATUS
            # ------------------------------------------------

            if distance is not None:

                if distance < 0.75:

                    safety = "DANGER"

                elif distance < 1.5:

                    safety = "WARNING"

                else:

                    safety = "SAFE"

            else:

                safety = "UNKNOWN"


            # ------------------------------------------------
            # STORE DETECTION
            # ------------------------------------------------

            detected_objects.append({

                "name": object_name,

                "id": track_id,

                "distance": distance,

                "safety": safety,

                "confidence": confidence

            })


            # ------------------------------------------------
            # BOX COLOR
            # ------------------------------------------------

            if safety == "DANGER":

                box_color = (
                    0,
                    0,
                    255
                )

            elif safety == "WARNING":

                box_color = (
                    0,
                    165,
                    255
                )

            else:

                box_color = (
                    0,
                    255,
                    0
                )


            # ------------------------------------------------
            # DRAW BOX
            # ------------------------------------------------

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                box_color,
                2
            )


            # ------------------------------------------------
            # OBJECT LABEL
            # ------------------------------------------------

            if track_id is not None:

                label = (
                    f"{object_name} "
                    f"ID:{track_id} "
                    f"{confidence:.2f}"
                )

            else:

                label = (
                    f"{object_name} "
                    f"{confidence:.2f}"
                )


            cv2.putText(
                annotated_frame,
                label,
                (
                    x1,
                    max(
                        y1 - 10,
                        20
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                box_color,
                2
            )


            # ------------------------------------------------
            # DISTANCE
            # ------------------------------------------------

            if distance is not None:

                cv2.putText(
                    annotated_frame,
                    f"Distance: {distance:.2f} m",
                    (
                        x1,
                        y2 + 25
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    box_color,
                    2
                )


            # ------------------------------------------------
            # SAFETY
            # ------------------------------------------------

            cv2.putText(
                annotated_frame,
                safety,
                (
                    x1,
                    y2 + 48
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                box_color,
                2
            )


    # ========================================================
    # UPDATE HISTORY
    # ========================================================

    update_history(
        detected_objects
    )


    # ========================================================
    # SMART VOICE
    # ========================================================

    if len(detected_objects) > 0:

        process_voice(
            detected_objects
        )


    # ========================================================
    # FPS
    # ========================================================

    current_time = time.time()


    fps = 1 / max(
        current_time -
        previous_time,
        0.001
    )


    previous_time = current_time


    # ========================================================
    # UPDATE GUI INFORMATION
    # ========================================================

    objects_label.config(
        text=f"Objects: {object_count}"
    )


    fps_label.config(
        text=f"FPS: {fps:.1f}"
    )


    status_label.config(
        text="Detection + Tracking + Distance + Voice Running"
    )


    # ========================================================
    # FPS ON CAMERA
    # ========================================================

    cv2.putText(
        annotated_frame,
        f"FPS: {fps:.1f}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    # ========================================================
    # CONVERT IMAGE
    # ========================================================

    frame_rgb = cv2.cvtColor(
        annotated_frame,
        cv2.COLOR_BGR2RGB
    )


    image = Image.fromarray(
        frame_rgb
    )


    image = image.resize(
        (850, 430)
    )


    photo = ImageTk.PhotoImage(
        image=image
    )


    camera_label.config(
        image=photo
    )


    camera_label.image = photo


    # ========================================================
    # RUN AGAIN
    # ========================================================

    root.after(
        10,
        update_camera
    )


# ============================================================
# 17. CLOSE PROGRAM
# ============================================================

def close_program():

    cap.release()

    cv2.destroyAllWindows()

    voice_queue.put(
        None
    )

    root.destroy()


# ============================================================
# 18. EXIT BUTTON
# ============================================================

exit_button = tk.Button(
    root,
    text="EXIT",
    font=("Arial", 13, "bold"),
    command=close_program,
    width=12
)

exit_button.pack(
    pady=5
)


# ============================================================
# 19. WINDOW CLOSE
# ============================================================

root.protocol(
    "WM_DELETE_WINDOW",
    close_program
)


# ============================================================
# 20. START
# ============================================================

update_camera()

root.mainloop()