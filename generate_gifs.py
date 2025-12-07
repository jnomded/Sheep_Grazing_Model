import os
import argparse
import numpy as np
from PIL import Image

from config_loader import get_all_params
from sheep_sim import run_simulation

def frames_to_gif(frames, output_path, fps=30, loop=0):
    """
    Convert a list of numpy array frames to a GIF.
    
    Parameters:
        frames: list of numpy arrays (H, W, C)
        output_path: path to save the GIF
        fps: frames per second
        loop: number of loops (0 = infinite)
    """
    if not frames:
        print("No frames to save!")
        return
    
    # Convert frames to PIL Images
    pil_frames = [Image.fromarray(frame.astype('uint8')) for frame in frames]
    
    # Calculate duration in milliseconds
    duration = int(1000 / fps)
    
    # Save as GIF
    pil_frames[0].save(
        output_path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=duration,
        loop=loop
    )
    print(f"Saved GIF to {output_path} ({len(frames)} frames)")


def generate_simulation_gif(params, output_path):
    """Generate GIF from pygame simulation."""
    print("Generating simulation GIF...")
    
    fps = params["FPS"]
    t_max = params["T_MAX"]
    sim_speed = params["SIM_SPEED"]
    dt = params["DT"]
    
    # Calculate max frames based on t_max
    sim_time_per_frame = sim_speed * dt
    max_frames = int(t_max / sim_time_per_frame) + 1
    
    # Run simulation and capture frames
    frames = run_simulation(params, record_frames=True, max_frames=max_frames)
    
    if frames:
        frames_to_gif(frames, output_path, fps=fps)
    else:
        print("No frames captured from simulation")


def main():
    parser = argparse.ArgumentParser(description='Generate GIFs from sheep grazing model')
    parser.add_argument('--config', type=str, default=None, help='Path to config file')
    parser.add_argument('--output-dir', type=str, default='output', help='Output directory for GIFs')
    parser.add_argument('--run-sim', action='store_true', help='Only generate simulation GIF')

    args = parser.parse_args()

    #load config
    params = get_all_params(args.config)

    # create output directory if not exists
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")


    #reproducibility
    if params.get("seed") is not None:
        np.random.seed(params["seed"])

    response_mode = params["response_mode"]
    h0 = params["H0"]
    initial_p_frac = params.get("INITIAL_P_FRAC", None)
    suffix = f"_c{response_mode}_H{h0}_P{initial_p_frac}"  


    sim_path = os.path.join(output_dir, f"simulation{suffix}.gif")
    generate_simulation_gif(params, sim_path)

    print("\nDone!")


if __name__ == "__main__":
    main()
