# ============================================================
# OBJECT DISTANCE CALIBRATION
# ============================================================
#
# Calibration means:
# "How many pixels does this object appear as
#  when it is exactly 1 meter away?"
#
# Distance is estimated using:
#
# Distance = Calibration_Pixels / Current_Pixels
#
# ============================================================


CALIBRATION_DISTANCE = 1.0


OBJECT_CALIBRATION = {

    # Person
    # Your actual measurement:
    "person": {
        "dimension": "height",
        "pixels_at_1m": 187
    },


    # Bottle
    # Your measured value:
    "bottle": {
        "dimension": "height",
        "pixels_at_1m": 259
    },


    # Laptop
    # We will replace this after you measure it.
    "laptop": {
        "dimension": "width",
        "pixels_at_1m": None
    },


    # Chair
    # We will replace this after you measure it.
    "chair": {
        "dimension": "height",
        "pixels_at_1m": None
    }

}