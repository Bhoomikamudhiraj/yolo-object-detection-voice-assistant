# ============================================================
# DISTANCE ESTIMATION
# ============================================================

from calibration import OBJECT_CALIBRATION


def calculate_distance(object_name, pixel_width, pixel_height):
    """
    Estimate approximate distance of an object.

    Returns:
        distance in meters
        or None if the object is not calibrated.
    """


    # --------------------------------------------------------
    # Check whether calibration exists
    # --------------------------------------------------------

    if object_name not in OBJECT_CALIBRATION:

        return None


    calibration = OBJECT_CALIBRATION[
        object_name
    ]


    calibrated_pixels = calibration[
        "pixels_at_1m"
    ]


    dimension = calibration[
        "dimension"
    ]


    # --------------------------------------------------------
    # If calibration is not available
    # --------------------------------------------------------

    if calibrated_pixels is None:

        return None


    # --------------------------------------------------------
    # Select current pixel measurement
    # --------------------------------------------------------

    if dimension == "height":

        current_pixels = pixel_height

    else:

        current_pixels = pixel_width


    # --------------------------------------------------------
    # Avoid division by zero
    # --------------------------------------------------------

    if current_pixels <= 0:

        return None


    # --------------------------------------------------------
    # Distance calculation
    # --------------------------------------------------------

    distance = (
        calibrated_pixels
        / current_pixels
    )


    return distance