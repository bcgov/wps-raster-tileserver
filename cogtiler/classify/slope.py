import numpy as np

def classify(data):
    rgb = np.empty((1, data.shape[1], data.shape[2]), np.uint8)
    mask = np.empty(data.shape[1:], np.uint8)
    for band in data:
        for y, row in enumerate(band):
            rgb[0][y] = np.where(row < 0, 0, row / 180 * 255)
            mask[y] = np.where(row == -1000000.0, 0, 255)
    return rgb, mask
