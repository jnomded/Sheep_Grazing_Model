import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config(config_path=None):

    """Load configuration from a YAML file."""
    if config_path is None:
        config_path = CONFIG_PATH
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config


def get_model_params(config):
    """Extract model parameters from the configuration dictionary."""
    model = config["model"]
    return {
        "K_CAPACITY": float(model["K_CAPACITY"]),
        "GROWTH_RATE": float(model["GROWTH_RATE"]),
        "A_CONST": float(model["A_CONST"]),
        "B_CONST": float(model["B_CONST"]),
        "response_mode": int(model["response_mode"]),
    }

def get_scenario_params(config):
    """Extract scenario parameters from the configuration dictionary."""
    scenario = config["scenario"]
    return {
        "INITIAL_BIOMASS": float(scenario["INITIAL_BIOMASS"]),
        "TIME_STEP": float(scenario["TIME_STEP"]),
        "TOTAL_TIME": float(scenario["TOTAL_TIME"]),
    }

def get_sustainability_params(config):
    """Extract sustainability parameters from config."""
    sust = config["sustainability"]
    return {
        "MALNOURISH_FRAC": float(sust["MALNOURISH_FRAC"]),
        "freeze_on_unsustainable": bool(sust["freeze_on_unsustainable"]),
    }

def get_randomness_params(config):
    """Extract randomness parameters from config."""
    rand = config["randomness"]
    seed = rand.get("seed")
    return {
        "seed": int(seed) if seed is not None else None,
    }

def get_visualization_params(config):
    """Extract visualization parameters from config."""
    vis = config["visualization"]
    return {
        "WINDOW_SIZE": int(vis["WINDOW_SIZE"]),
        "PASTURE_SIZE": int(vis["PASTURE_SIZE"]),
        "FPS": int(vis["FPS"]),
        "SIM_SPEED": int(vis["SIM_SPEED"]),
    }

def get_all_params(config_path=None):
    """Load config and return all parameters as a flat dictionary."""
    config = load_config(config_path)
    
    params = {}
    params.update(get_model_params(config))
    params.update(get_scenario_params(config))
    params.update(get_sustainability_params(config))
    params.update(get_randomness_params(config))
    params.update(get_visualization_params(config))
    
    return params


if __name__ == "__main__":
    # Test loading
    params = get_all_params()
    print("Loaded configuration:")
    for key, value in params.items():
        print(f"  {key}: {value}")