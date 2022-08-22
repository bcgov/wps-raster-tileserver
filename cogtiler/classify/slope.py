import numpy as np

def classify(data):
    """ Not sure exactly about what slope value we're getting from SFMS - but it looks like
    some value between 0 and 180.
    So if we have a tile of 256x256 of slope values, we're just returning a 256x256 array of
    unsigned integers normalized to 0-255.
    """
    rgb = np.empty((1, data.shape[1], data.shape[2]), np.uint8)
    mask = np.empty(data.shape[1:], np.uint8)
    for band in data:
        for y, row in enumerate(band):
            rgb[0][y] = np.where(row < 0, 0, row / 180 * 255)
            mask[y] = np.where(row == -1000000.0, 0, 255)
    return rgb, mask
