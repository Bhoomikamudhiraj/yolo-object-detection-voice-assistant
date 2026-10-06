import cv2
from ultralytics import YOLO

# ============================================================
# LOAD YOLO
# ============================================================

model = YOLO("yolo11n.pt")


# ============================================================
# OPEN WEBCAM
# ============================================================

cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    exit()


print("======================================")
print(" OBJECT DISTANCE CALIBRATION")
print("======================================")
print()
print("Place ONE object exactly 1 meter away.")
print()
print("Supported objects:")
print("Bottle")
print("Laptop")
print("Chair")
print()
print("Do NOT press Q until you have recorded")
print("the pixel measurement.")
print()


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Could not read camera frame.")
        break


    # --------------------------------------------------------
    # YOLO DETECTION
    # --------------------------------------------------------

    results = model(
        frame,
        conf=0.30,
        verbose=False
    )

    result = results[0]


    # --------------------------------------------------------
    # DETECT OBJECTS
    # --------------------------------------------------------

    found_object = False

    for box in result.boxes:

        class_id = int(box.cls[0])

        object_name = model.names[class_id]

        confidence = float(box.conf[0])


        # Bounding box

        x1, y1, x2, y2 = box.xyxy[0]

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)


        width = x2 - x1

        height = y2 - y1


        # ----------------------------------------------------
        # ONLY OUR CALIBRATION OBJECTS
        # ----------------------------------------------------

        if object_name in ["bottle", "laptop", "chair"]:

            found_object = True


            print(
                f"OBJECT: {object_name} | "
                f"Confidence: {confidence:.2f} | "
                f"Width: {width} px | "
                f"Height: {height} px"
            )


            # ------------------------------------------------
            # DRAW BOUNDING BOX
            # ------------------------------------------------

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )


            # ------------------------------------------------
            # OBJECT + CONFIDENCE
            # ------------------------------------------------

            label = (
                f"{object_name} "
                f"{confidence:.2f}"
            )


            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 25)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )


            # ------------------------------------------------
            # PIXEL HEIGHT
            # ------------------------------------------------

            cv2.putText(
                frame,
                f"Height: {height}px",
                (x1, y2 + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )


            # ------------------------------------------------
            # PIXEL WIDTH
            # ------------------------------------------------

            cv2.putText(
                frame,
                f"Width: {width}px",
                (x1, y2 + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )


    # ========================================================
    # STATUS ON SCREEN
    # ========================================================

    if found_object:

        status = "OBJECT DETECTED"

    else:

        status = "Waiting for bottle/laptop/chair..."


    cv2.putText(
        frame,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


    cv2.putText(
        frame,
        "Place object exactly 1 meter away",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )


    cv2.putText(
        frame,
        "Press Q to quit",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )


    # ========================================================
    # SHOW CAMERA
    # ========================================================

    cv2.imshow(
        "Object Calibration",
        frame
    )


    # ========================================================
    # QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

print()
print("Calibration stopped.")