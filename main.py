import cv2
import pyttsx3
import time
import threading
import queue
import csv
from datetime import datetime

from ultralytics import YOLO
from distance import calculate_distance


# ============================================================
# 1. LOAD YOLO MODEL
# ============================================================

print("Loading YOLO model...")

model = YOLO("yolo11n.pt")

print("YOLO model loaded.")


# ============================================================
# 2. OBJECT POSITION FUNCTION
# ============================================================

def get_position(x1, x2, frame_width):

    center_x = (x1 + x2) / 2

    left_limit = frame_width / 3
    right_limit = (frame_width / 3) * 2

    if center_x < left_limit:
        return "left"

    elif center_x > right_limit:
        return "right"

    else:
        return "center"


# ============================================================
# 3. VOICE SYSTEM
# ============================================================

voice_queue = queue.PriorityQueue(maxsize=1)


def voice_worker():

    engine = pyttsx3.init()

    engine.setProperty("rate", 160)
    engine.setProperty("volume", 1.0)

    while True:

        priority, message = voice_queue.get()

        try:

            print("VOICE:", message)

            engine.say(message)
            engine.runAndWait()

        except Exception as e:

            print("Voice error:", e)

        finally:

            voice_queue.task_done()


voice_thread = threading.Thread(
    target=voice_worker,
    daemon=True
)

voice_thread.start()


def speak(message, priority=2):

    try:

        # Priority 1 = danger
        # Remove waiting normal messages

        if priority == 1:

            while not voice_queue.empty():

                try:

                    voice_queue.get_nowait()
                    voice_queue.task_done()

                except queue.Empty:

                    break

        if voice_queue.empty():

            voice_queue.put_nowait(
                (priority, message)
            )

    except queue.Full:

        pass


# ============================================================
# 4. OPEN WEBCAM
# ============================================================

print()
print("Opening webcam...")


# First try Windows DirectShow
cap = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
)


# If that fails, try normal OpenCV camera
if not cap.isOpened():

    print("DirectShow failed. Trying default camera...")

    cap.release()

    cap = cv2.VideoCapture(0)


# If still not working
if not cap.isOpened():

    print("ERROR: Could not open webcam.")
    print("Please check if another application is using the camera.")

    exit()


# Set resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


print()
print("============================================")
print(" SMART YOLO ASSISTIVE VISION SYSTEM")
print("============================================")
print("Webcam started.")
print("Press Q to quit.")
print()


# ============================================================
# 5. VOICE CONTROL
# ============================================================

last_voice_time = 0

VOICE_COOLDOWN = 4


last_object_voice_time = 0

OBJECT_VOICE_COOLDOWN = 5


# ============================================================
# 6. PREVIOUS OBJECTS
# ============================================================

previous_objects = set()
# ============================================================
# DETECTION LOGGING
# ============================================================

LOG_FILE = "detection_log.csv"

# Create CSV file with headers if it doesn't exist
try:
    with open(LOG_FILE, "x", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Time",
            "Object",
            "Confidence",
            "Distance",
            "Position",
            "Safety"
        ])

except FileExistsError:

    pass


# ============================================================
# 7. FPS
# ============================================================

previous_time = time.time()


# ============================================================
# 8. MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # READ FRAME
    # --------------------------------------------------------

    ret, frame = cap.read()


    if not ret:

        print("Could not read frame.")

        break


    # --------------------------------------------------------
    # YOLO TRACKING
    # IMPORTANT: ONLY CALL ONCE
    # --------------------------------------------------------

    results = model.track(
        frame,
        persist=True,
        conf=0.50,
        verbose=False
    )


    result = results[0]


    # --------------------------------------------------------
    # FRAME VARIABLES
    # --------------------------------------------------------

    detected_objects = set()

    detected_information = []


    # ========================================================
    # 9. PROCESS DETECTED OBJECTS
    # ========================================================

    if result.boxes is not None:

        for box in result.boxes:

            # ------------------------------------------------
            # CLASS
            # ------------------------------------------------

            class_id = int(box.cls[0])

            object_name = model.names[class_id]


            # ------------------------------------------------
            # CONFIDENCE
            # ------------------------------------------------

            confidence = float(box.conf[0])


            # ------------------------------------------------
            # BOUNDING BOX
            # ------------------------------------------------

            x1, y1, x2, y2 = box.xyxy[0]

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)


            width = x2 - x1

            height = y2 - y1


            # ------------------------------------------------
            # OBJECT POSITION
            # ------------------------------------------------

            frame_height, frame_width = frame.shape[:2]

            position = get_position(
                x1,
                x2,
                frame_width
            )


            # ------------------------------------------------
            # TRACKING ID
            # ------------------------------------------------

            if box.id is not None:

                object_id = int(box.id[0])

            else:

                object_id = -1


            # ------------------------------------------------
            # ADD OBJECT
            # ------------------------------------------------

            detected_objects.add(
                object_name
            )


            # ------------------------------------------------
            # DISTANCE
            # ------------------------------------------------

            distance = calculate_distance(
                object_name,
                width,
                height
            )


            # ------------------------------------------------
            # SAVE INFORMATION
            # ------------------------------------------------

            detected_information.append({

                "name": object_name,

                "confidence": confidence,

                "id": object_id,

                "width": width,

                "height": height,

                "distance": distance,

                "position": position

            })


            # ------------------------------------------------
            # TERMINAL OUTPUT
            # ------------------------------------------------

            if distance is not None:

                print(
                    f"{object_name} | "
                    f"ID: {object_id} | "
                    f"Confidence: {confidence:.2f} | "
                    f"Distance: {distance:.2f} m"
                )

            else:

                print(
                    f"{object_name} | "
                    f"ID: {object_id} | "
                    f"Confidence: {confidence:.2f} | "
                    f"Distance: Not calibrated"
                )


    # ========================================================
    # 10. FPS
    # ========================================================

    current_time = time.time()

    fps = 1 / max(
        current_time - previous_time,
        0.001
    )

    previous_time = current_time


    # ========================================================
    # 11. DISTANCE ZONES
    # ========================================================

    danger_objects = []

    close_objects = []

    nearby_objects = []


    for item in detected_information:

        distance = item["distance"]


        if distance is None:

            continue


        # Less than 0.75 meter
        if distance < 0.75:

            danger_objects.append(item)


        # 0.75 - 1 meter
        elif distance < 1.0:

            close_objects.append(item)


        # 1 - 2 meters
        elif distance < 2.0:

            nearby_objects.append(item)


    # ========================================================
    # 12. CURRENT TIME
    # ========================================================

    now = time.time()
    # ========================================================
# 12A. SAVE DETECTIONS TO CSV
# ========================================================

    if len(detected_information) > 0:

        # Determine current safety level

        if len(danger_objects) > 0:

            current_safety = "DANGER"

        elif len(close_objects) > 0:

            current_safety = "CLOSE"

        elif len(nearby_objects) > 0:

            current_safety = "NEARBY"

        else:

            current_safety = "NORMAL"


        current_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        with open(
            LOG_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)


            for item in detected_information:

                distance = item["distance"]


                if distance is not None:

                    distance_value = f"{distance:.2f}"

                else:

                    distance_value = "N/A"


                writer.writerow([

                    current_time,

                    item["name"],

                    f"{item['confidence']:.2f}",

                    distance_value,

                    item["position"],

                    current_safety

                ])


        # ========================================================
        # 13. DANGER VOICE
        # ========================================================

        if len(danger_objects) > 0:

            if now - last_voice_time >= VOICE_COOLDOWN:

                # -----------------------------------------------
                # ONE DANGER OBJECT
                # -----------------------------------------------

                if len(danger_objects) == 1:

                    danger_item = danger_objects[0]

                    name = danger_item["name"]

                    position = danger_item["position"]

                    distance = danger_item["distance"]


                    if distance is not None:

                        message = (

                            f"Warning. "

                            f"{name} "

                            f"is very close, "

                            f"approximately "

                            f"{distance:.1f} meters "

                            f"on your {position}."

                        )

                    else:

                        message = (

                            f"Warning. "

                            f"{name} "

                            f"is very close "

                            f"on your {position}."

                        )


                # -----------------------------------------------
                # MULTIPLE DANGER OBJECTS
                # -----------------------------------------------

                else:

                    danger_names = []

                    for item in danger_objects:

                        danger_names.append(
                            item["name"]
                        )


                    danger_names = list(
                        dict.fromkeys(
                            danger_names
                        )
                    )


                    message = (

                        "Warning. "

                        + ", ".join(danger_names)

                        + " are very close."

                    )


                print(
                    "DANGER:",
                    message
                )


                # Priority 1
                speak(
                    message,
                    priority=1
                )


                last_voice_time = now


        # ========================================================
        # 14. OBJECT VOICE
        # ========================================================

        objects_changed = (

            detected_objects
            != previous_objects

        )


        if objects_changed:

            if (
                now - last_object_voice_time
                >= OBJECT_VOICE_COOLDOWN
            ):

                object_messages = []


                # -----------------------------------------------
                # CREATE MESSAGE FOR EACH OBJECT
                # -----------------------------------------------

                for item in detected_information:

                    name = item["name"]

                    distance = item["distance"]

                    position = item["position"]


                    if distance is not None:

                        object_messages.append(

                            f"{name} "

                            f"on your {position}, "

                            f"approximately "

                            f"{distance:.1f} "

                            f"meters away"

                        )

                    else:

                        object_messages.append(

                            f"{name} "

                            f"on your {position}"

                        )


                # -----------------------------------------------
                # REMOVE DUPLICATES
                # -----------------------------------------------

                object_messages = list(

                    dict.fromkeys(
                        object_messages
                    )

                )


                # -----------------------------------------------
                # CREATE FINAL MESSAGE
                # -----------------------------------------------

                if len(object_messages) > 0:

                    if len(object_messages) == 1:

                        message = (

                            object_messages[0]

                            + " detected."

                        )

                    else:

                        message = (

                            "I can see "

                            + ", ".join(
                                object_messages
                            )

                            + "."

                        )


                    # -------------------------------------------
                    # DON'T INTERRUPT DANGER
                    # -------------------------------------------

                    if len(danger_objects) == 0:

                        print(
                            "OBJECT VOICE:",
                            message
                        )


                        speak(
                            message,
                            priority=2
                        )


                        last_object_voice_time = now


        # ========================================================
        # 15. SAVE CURRENT OBJECTS
        # ========================================================

        previous_objects = detected_objects.copy()


        # ========================================================
        # 16. DRAW YOLO RESULTS
        # ========================================================

        annotated_frame = result.plot()


        # ========================================================
        # 17. ADD DISTANCE + POSITION LABELS
        # ========================================================

        for item in detected_information:

            name = item["name"]

            object_id = item["id"]

            distance = item["distance"]

            position = item["position"]


            # ----------------------------------------------------
            # FIND MATCHING BOX
            # ----------------------------------------------------

            if result.boxes is None:

                continue


            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )

                current_name = model.names[
                    class_id
                ]


                if current_name != name:

                    continue


                if box.id is not None:

                    current_id = int(
                        box.id[0]
                    )

                else:

                    current_id = -1


                if current_id != object_id:

                    continue


                x1, y1, x2, y2 = box.xyxy[0]

                x1 = int(x1)

                y1 = int(y1)

                x2 = int(x2)

                y2 = int(y2)


                if distance is not None:

                    distance_text = (
                        f"{distance:.2f} m"
                    )

                else:

                    distance_text = "N/A"


                label = (

                    f"ID {object_id} | "

                    f"{position} | "

                    f"{distance_text}"

                )


                cv2.putText(

                    annotated_frame,

                    label,

                    (x1, y2 + 25),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.55,

                    (0, 255, 255),

                    2

                )


                break


        # ========================================================
        # 18. OBJECT COUNT
        # ========================================================

        object_count = len(
            detected_information
        )


        cv2.putText(

            annotated_frame,

            f"Objects: {object_count}",

            (20, 40),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.75,

            (0, 255, 0),

            2

        )


        # ========================================================
        # 19. FPS
        # ========================================================

        cv2.putText(

            annotated_frame,

            f"FPS: {fps:.1f}",

            (20, 75),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.75,

            (0, 255, 0),

            2

        )


        # ========================================================
        # 20. VOICE STATUS
        # ========================================================

        cv2.putText(

            annotated_frame,

            "VOICE: ON",

            (20, 110),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 255, 0),

            2

        )


        # ========================================================
        # 21. SAFETY STATUS
        # ========================================================

        if len(danger_objects) > 0:

            safety_status = "DANGER"

        elif len(close_objects) > 0:

            safety_status = "CLOSE"

        elif len(nearby_objects) > 0:

            safety_status = "NEARBY"

        else:

            safety_status = "NORMAL"


        cv2.putText(

            annotated_frame,

            f"Safety: {safety_status}",

            (20, 145),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 255, 255),

            2

        )


        # ========================================================
        # 22. SHOW CAMERA WINDOW
        # ========================================================

        cv2.imshow(

            "Smart YOLO Assistive Vision System",

            annotated_frame

        )


        # ========================================================
        # 23. QUIT
        # ========================================================

        key = cv2.waitKey(1) & 0xFF


        if key == ord("q"):
            break


# ============================================================
# 24. CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()


print()
print("============================================")
print(" System stopped.")
print("============================================")