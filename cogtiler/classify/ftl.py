import os
import csv
from time import perf_counter
import logging
import numpy as np

# TODO: make the logger work when running uvicorn on developer machine
logger = logging.getLogger("gunicorn.error")

unknown = (0xff, 0x00, 0x00, 0xff)
mask_color = (0x0, 0x0, 0x0, 0x0)


def prepare_m1m2_lookup_table():
    m1_m2 = (255,211,127,255)
    table = {
        14: m1_m2
    }
    # 500 indicates it's m1/m2 - the last two digits represent percentage conifer
    for i in range(500, 600):
        table[i] = m1_m2
    return table

def prepare_lookup_table():
    filename = os.path.join(os.path.dirname(__file__), 'bc_fbp_fuel_type_lookup_table.csv')
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        grid_value = header.index('grid_value')
        r = header.index('r')
        g = header.index('g')
        b = header.index('b')
        a = header.index('a')
        table = {}
        for line in reader:
            table[int(line[grid_value])] = (int(line[r]), int(line[g]), int(line[b]), int(line[a]))
    return table

lookup_table = prepare_lookup_table()
m1m2_lookup = prepare_m1m2_lookup_table()

def lookup(value, filter):
    """
    not a particularly good filter implemntation, just want to show it's possible.
    """
    if filter == 'm1/m2':
        return m1m2_lookup.get(int(value), mask_color)
    else:
        return lookup_table.get(int(value), unknown)

def classify(data, filter=None):
    """
    Given a numpy array, with a single band, classify the values into RGB and mask tuples.

    NOTE: This is probably a very slow way of doing it - there shouldn't be a way of doing
    this without enumerating. I'm just not a numpy expert.
    see: https://numpy.org/doc/stable/reference/generated/numpy.take.html
    """
    start = perf_counter()
    r, g, b = 0, 1, 2
    rgb = np.empty((3, data.shape[1], data.shape[2]), np.uint8)
    mask = np.empty(data.shape[1:], np.uint8)
    for band in data:
        for y, row in enumerate(band):
            for x, col in enumerate(row):
                rgb[r][y][x], rgb[g][y][x], rgb[b][y][x], mask[y][x] = lookup(col, filter)
    end = perf_counter()
    delta = end - start
    logger.info('ftl classify took %s seconds', delta)
    return rgb, mask