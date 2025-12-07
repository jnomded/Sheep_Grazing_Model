import pygame
import numpy as np
import random
import os

from config_loader import get_all_params
from sheep_model import step_eueler, functional_response

# Sheep status global

COLOR_SHEEP_OK = np.array([255, 255, 255])
COLOR_SHEEP_BAD = np.array([255, 0, 0])
COLOR_TEXT = (255, 255, 255)

class Sheep:
    """Visual representation of a sheep on the grid."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, grid_size):
        """Random walk movement."""
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
        dx, dy = random.choice(moves)
        self.x = max(0, min(grid_size - 1, self.x + dx))
        self.y = max(0, min(grid_size - 1, self.y + dy))
