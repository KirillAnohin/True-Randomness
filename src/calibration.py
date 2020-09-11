import cv2
import json
import numpy as np
from src import config
from functools import partial

def save(saved_colors, filters, color):
    saved_colors[color] = filters

    with open("colors.json", "w") as f:
        f.write(json.dumps(saved_colors))

def update_range(edge, channel, filters, value):
    # edge = "min" or "max"
    # channel = 0, 1, 2 (H, S, V)
    # value = new slider value
    filters[edge][channel] = value
