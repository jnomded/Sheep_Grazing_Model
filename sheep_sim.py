import pygame
import numpy as np
import random
import os

from config_loader import get_all_params
from sheep_model import functional_response, step_euler

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


    #logic
    while running:
        #termination conditions
        if record_frames:
            if max_frames and frame_count >= max_frames:
                running = False
                continue
            if current_time >= t_max:
                running = False
                continue
        
        # Event handling
        if not record_frames:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
        else:
            pygame.event.pump()
        
        # Physics loop (1D ODE)
        for _ in range(sim_speed):
            cP = functional_response(P, a, b, current_response)
            grazing_frac = (cP / a) if a > 0 else 0.0
            
            # Check malnourishment
            malnourished = grazing_frac < malnourish_frac
            
            # Check sustainability
            if freeze_on_unsustainable and grazing_frac < 0.01:
                frozen = True
            
            # Only update biomass and move sheep if not frozen
            if not frozen:
                P_old = P
                P = step_euler(P, H0, K, r, a, b, current_response, dt)
                
                delta_P_frac = (P - P_old) / K
                
                # Distribute the change across all the pixels and update to according match delta in patchy way
                if delta_P_frac < 0:
                    # Grazing: remove from pixels in patchy clusters
                    total_available = pixel_grid.sum()
                    if total_available > 0:
                        amount_to_remove = -delta_P_frac * total_pixels

                        # Work on a copy so we can iteratively carve patches
                        remaining = amount_to_remove
                        while remaining > 0:
                            # Random grazing center
                            cx = np.random.randint(0, pasture_size)
                            cy = np.random.randint(0, pasture_size)

                            # Random patch radius (in pixels)
                            radius = np.random.randint(2, 6)

                            # Define patch bounds
                            x_min = max(0, cx - radius)
                            x_max = min(pasture_size, cx + radius + 1)
                            y_min = max(0, cy - radius)
                            y_max = min(pasture_size, cy + radius + 1)

                            patch = pixel_grid[x_min:x_max, y_min:y_max]

                            # Only graze where there is grass
                            mask = patch > 0
                            if not mask.any():
                                continue
                            
                            # Amount to remove in this patch (small chunk)
                            local_target = min(remaining, radius * radius * 0.5)
                            local_available = patch[mask].sum()
                            if local_available <= 0:
                                continue
                            
                            # Remove proportionally inside this patch
                            frac = min(1.0, local_target / local_available)
                            patch[mask] = np.maximum(0.0, patch[mask] * (1.0 - frac))

                            remaining -= local_target
                else:
                    # Regrowth: add to pixels in small, local patches
                    total_room = (1.0 - pixel_grid).sum()
                    if total_room > 0:
                        amount_to_add = delta_P_frac * total_pixels
                        remaining = amount_to_add
                
                        # Limit number of patches so we don't loop forever when growth is tiny
                        max_patches = 200
                
                        patches_done = 0
                        while remaining > 0 and patches_done < max_patches:
                            # Random center, but bias toward existing grass so it thickens/spreads
                            if np.random.rand() < 0.7 and pixel_grid.sum() > 0:
                                # Sample a grass pixel as center
                                grass_indices = np.argwhere(pixel_grid > 0.01)
                                cx, cy = grass_indices[np.random.randint(len(grass_indices))]
                            else:
                                # Completely random center
                                cx = np.random.randint(0, pasture_size)
                                cy = np.random.randint(0, pasture_size)
                
                            radius = np.random.randint(2, 6)
                            x_min = max(0, cx - radius)
                            x_max = min(pasture_size, cx + radius + 1)
                            y_min = max(0, cy - radius)
                            y_max = min(pasture_size, cy + radius + 1)
                
                            patch = pixel_grid[x_min:x_max, y_min:y_max]
                
                            # Can only grow where there's room
                            room = 1.0 - patch
                            mask = room > 0.001
                            if not mask.any():
                                patches_done += 1
                                continue
                            
                            # Target a small chunk for this patch
                            local_target = min(remaining, radius * radius * 0.5)
                            local_room = room[mask].sum()
                            if local_room <= 0:
                                patches_done += 1
                                continue
                            
                            # Add proportionally to available room
                            frac = min(1.0, local_target / local_room)
                            patch[mask] = np.minimum(1.0, patch[mask] + room[mask] * frac)
                
                            remaining -= local_target
                            patches_done += 1
                
                # Move sheep
                for sheep in sheep_list:
                    sheep.move(pasture_size)
            
            current_time += dt
        
        # --- RENDER SECTION (UPDATED FOR 7 DISTINCT PATCH COLORS) ---
        
        # 1. Digitize the grid: Map saturation values (0.0-1.0) to bin indices (0-6) based on thresholds.
        # Values < 0.15 become index 0, values > 0.90 become index 6.
        bin_indices = np.digitize(pixel_grid, THRESHOLDS)

        # 2. Map indices to colors using numpy indexing.
        # This creates an (N, N, 3) RGB grid efficiently.
        rgb_grid = PALETTE[bin_indices]

        # Draw sheep based on status
        sheep_color = COLOR_SHEEP_BAD if (frozen or malnourished) else COLOR_SHEEP_OK
        for sheep in sheep_list:
            # Ensure coordinates are within bounds just in case
            sx = min(sheep.x, pasture_size-1)
            sy = min(sheep.y, pasture_size-1)
            rgb_grid[sx, sy] = sheep_color
        
        # Create surface
        surface = pygame.surfarray.make_surface(rgb_grid)
        scaled_surface = pygame.transform.scale(surface, (window_size, window_size))
        screen.blit(scaled_surface, (0, 0))
        
        # Stats text (top)
        label = (f"Mode: c{current_response} | Sheep (H0): {H0} | "
                 f"P: {P:.1f}/{K:.0f} | Grazing: {100*grazing_frac:.1f}% | t: {current_time:.1f}")
        text_surf = font.render(label, True, COLOR_TEXT)
        screen.blit(text_surf, (10, 10))
        
        # Status display (bottom middle)
        if frozen:
            status = "STARVED"
            status_color = (255, 0, 0)
        elif malnourished:
            status = "MALNOURISHED"
            status_color = (255, 165, 0)
        else:
            status = "OK"
            status_color = COLOR_TEXT
        status_surf = font.render(status, True, status_color)
        status_rect = status_surf.get_rect(center=(window_size // 2, window_size - 30))
        screen.blit(status_surf, status_rect)
        
        if record_frames:
            frame_array = pygame.surfarray.array3d(screen)
            frame_array = np.transpose(frame_array, (1, 0, 2))
            frames.append(frame_array.copy())
        else:
            pygame.display.flip()
        
        clock.tick(fps)
        frame_count += 1
    
    pygame.quit()
    
    if record_frames:
        return frames
    return None


def main():
    """Run the simulation standalone, not recommended"""
    import argparse
    # get args
    parser = argparse.ArgumentParser(description='Run sheep grazing simulation')
    parser.add_argument('--config', type=str, default=None, help='Path to config file')
    
    args = parser.parse_args()
    
    params = get_all_params(args.config)
    run_simulation(params, record_frames=False)


if __name__ == "__main__":
    main()