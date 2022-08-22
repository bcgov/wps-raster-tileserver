import numpy as np

def classify(data):
    """ Given a multidimensional numpy array of elevation values, return a monochrome RGB array and a mask array.

    Elevation is going to be a number between 0 and 3954 (highst point in BC), but we want a number between 0 and 255
    for a nice monochrome elevation map.
    """
    # e.g. if the input is 512x512, the output will be 512x512 - of unsigned integers.
    rgb = np.empty((1, data.shape[1], data.shape[2]), np.uint8)
    mask = np.empty(data.shape[1:], np.uint8)
    max_height = 3954
    for band in data:
        for y, row in enumerate(band):
            # normalise the elevation values to 0-255
            rgb[0][y] = row / max_height * 255
            # if altitude is below 0, then mask it.
            mask[y] = np.where(row< 0, 0, 255)
    return rgb, mask
    