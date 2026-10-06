import cv2
from ultralytics import YOLO

# Load YOLO
model = YOLO("yolo11n.pt")

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

if not cap.isOpened():
    print("Could not open webcam")
    exit()

print("Stand approximately 1 meter from the camera.")
print("Press Q to quit.")

while True:

    ret, frame = cap.read()

    if not ret:
        print("Could not read frame")
        break

    # YOLO detection
    results = model(
        frame,
        conf=0.50,
        verbose=False
    )

    result = results[0]

    # Look for person
    if result.boxes is not None:

        for box in result.boxes:

            class_id = int(box.cls[0])

            object_name = model.names[class_id]

            if object_name == "person":

                # Get bounding box
                x1, y1, x2, y2 = box.xyxy[0]

                x1 = int(x1)
                y1 = int(y1)
                x2 = int(x2)
                y2 = int(y2)

                # Calculate pixel height
                pixel_height = y2 - y1

                print(
                    "Person pixel height:",
                    pixel_height
                )

    # Draw detections
    annotated_frame = result.plot()

    cv2.imshow(
        "Camera Calibration",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()