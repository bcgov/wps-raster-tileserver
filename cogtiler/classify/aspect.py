import numpy as np

def classify(data):
    rgb = np.empty((3, data.shape[1], data.shape[2]), np.uint8)
    mask = np.empty(data.shape[1:], np.uint8)
    for band in data:
        for y, row in enumerate(band):
            mask[y] = np.where(row == -1000000.0, 0, 255)

            row = row % 360
            north = np.where((row >= 315) | (row < 45), 1, 0)
            east = np.where((row >= 45) & (row < 135), 1, 0)
            south = np.where((row >= 135) & (row < 225), 1, 0)
            west = np.where((row >= 225) & (row < 315), 1, 0)

            rgb[0][y] = np.where(south == 1, 255, 0)
            rgb[1][y] = np.where((north == 1) | (west == 1), 255, 0)
            rgb[2][y] = np.where((east == 1) | (west == 1), 255, 0)
    return rgb, mask
