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

def run_simulation(params, record_frames=False, max_frames=None):
    # Extract parameters
    K = params["K_CAPACITY"]
    r = params["GROWTH_RATE"]
    a = params["A_CONST"]
    b = params["B_CONST"]
    response_mode = params["response_mode"]
    H0 = params["H0"]
    P0 = params["INITIAL_P"]
    dt = params["DT"]
    t_max = params["T_MAX"]
    malnourish_frac = params["MALNOURISH_FRAC"]
    freeze_on_unsustainable = params["freeze_on_unsustainable"]
    seed = params["seed"]
    
    window_size = params["WINDOW_SIZE"]
    pasture_size = params["PASTURE_SIZE"]
    fps = params["FPS"]
    sim_speed = params["SIM_SPEED"]
    
    # Set random seed
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Initialize pygame
    pygame.init()

    if record_frames:
        screen = pygame.Surface((window_size, window_size))
    else:
        screen = pygame.display.set_mode((window_size, window_size))
        pygame.display.set_caption(f"Sheep Sim (1D model) | Speed: {sim_speed}x")
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    # Initialize state
    P = P0
    current_response = response_mode
    frozen = False
    malnourished = False
    grazing_frac = 1.0
    current_time = 0.0
    
    # Initialize pixel grid where each pixel has its own saturation (0.0 to 1.0)
    initial_saturation = P0 / K
    pixel_grid = np.full((pasture_size, pasture_size), initial_saturation, dtype=np.float64)
    total_pixels = pasture_size * pasture_size
    
    #sheep for visualization 
    sheep_list = [
        Sheep(random.randint(0, pasture_size - 1),
              random.randint(0, pasture_size - 1))
        for _ in range(H0)
    ]
    
    frames = []
    running = True
    frame_count = 0
    


    #Distinc patch palettes for each saturation level of the pixels
    PALETTE = np.array([
        [101,  67,  33],  # 0: Very bare dirt
        [124,  80,  34],  # 1: Sparse dry
        [139, 100,  35],  # 2: Very dry
        [160, 130,  40],  # 3: Dry-medium
        [180, 160,  50],  # 4: Dry (yellow-green)
        [170, 180,  55],  # 5: Medium-dry light
        [154, 205,  50],  # 6: Medium-dry
        [130, 175,  45],  # 7: Medium
        [120, 160,  40],  # 8: Medium-green
        [107, 142,  35],  # 9: Medium-lush
        [80,  130,  35],  # 10: Lush-medium
        [60,  120,  34],  # 11: Lush-dark
        [34,  139,  34],  # 12: Lush
        [0,   120,   0],  # 13: Very lush (lighter)
        [0,   110,   0],  # 14: Very lush dark
    ], dtype=np.uint8)
    
    # Threshold boundaries between the 7 states
    THRESHOLDS = [
    0.05, 0.10, 0.15, 0.20,
    0.30, 0.40, 0.50, 0.60,
    0.65, 0.70, 0.75, 0.80,
    0.85, 0.90
    ]

def main():
    run_simulation(get_all_params(), record_frames=False)
