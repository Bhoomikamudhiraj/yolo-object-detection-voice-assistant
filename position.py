def get_position(x1, x2, frame_width):
    """
    Determine whether an object is on the
    left, center, or right side of the frame.
    """

    object_center = (x1 + x2) / 2

    left_boundary = frame_width / 3
    right_boundary = (frame_width * 2) / 3

    if object_center < left_boundary:

        return "left"

    elif object_center > right_boundary:

        return "right"

    else:

        return "center"