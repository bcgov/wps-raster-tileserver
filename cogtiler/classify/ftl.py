from time import perf_counter
import logging
import numpy as np

logger = logging.getLogger("gunicorn.error")

unknown = (0xff, 0x00, 0x00, 0xff)

def prepare_lookup_table():
    mask_color = (0x0, 0x0, 0x0, 0x0)
    non_fuel = mask_color
    c1 = (48,18,59,0xff)
    c2 = (65,67,167,0xff)
    c3 = (71,113,233,0xff)
    c4 = (62,156,254,0xff)
    c5 = (33,198,225,0xff)
    c6 = (27,229,181,0xff)
    c7 = (72,248,130,0xff)
    d1_d2 = (137,0xff,77,0xff)
    s1 = (187,245,52,0xff)
    s2 = (226,220,56,0xff)
    s3 = (251,185,56,0xff)
    o1a = (253,139,38,0xff)
    m1_m2 = (239,89,17,0xff)
    table = {
        -10000: non_fuel,
        1: c1,
        2: c2,
        3: c3,
        4: c4,
        5: c5,
        6: c6,
        7: c7,
        8: d1_d2,
        9: s1,
        10: s2,
        11: s3,
        12: o1a,
        14: m1_m2,
        99: non_fuel,
        102: non_fuel,
        65535: mask_color,    
    }
    # 500 indicates it's m1/m2 - the last two digits represent percentage conifer
    for i in range(500, 600):
        table[i] = m1_m2
    return table

lookup_table = prepare_lookup_table()

def lookup(value):
    """
    TODO: We need FTL lookup table! What are the types, and what colours do they match to?
    """
    return lookup_table.get(int(value), unknown)

def classify(data):
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
                rgb[r][y][x], rgb[g][y][x], rgb[b][y][x], mask[y][x] = lookup(col)
    end = perf_counter()
    delta = end - start
    logger.info('ftl classify took %s seconds', delta)
    return rgb, mask