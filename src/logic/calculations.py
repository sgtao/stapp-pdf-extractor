# calculations.py
import numpy as np


def calculate_spiral(num_points, num_turns):
    indices = np.linspace(0, 1, num_points)
    theta = 2 * np.pi * num_turns * indices
    radius = indices

    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    return x, y, indices
