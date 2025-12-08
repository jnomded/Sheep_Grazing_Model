import numpy as np

def functional_response(P, a, b, response_type):
    """
    Compute the functional response of our predator to prey, 
    given prey biomass P, parameters a and b, and response type.
    """
    if response_type == 1:
        # c1
        return (a * P) / (b + P)
    elif response_type == 2:
        # c2
        return (a * P**2) / (b**2 + P**2)
    else:
        raise ValueError("Invalid response type. Must be 1 or 2.")
    
def compute_dPdt(P, H0, r, K, a, b, response_type):
    """
    Compute the rate of change of prey biomass.
    """
    cP = functional_response(P, a, b, response_type)
    return r * P * (1.0 - P / K) - H0 * cP

def step_euler(P, H0, r, K, a, b, response_type, dt):
    """
    Take one time step using the Euler method.
    """
    dPdt = compute_dPdt(P, H0, r, K, a, b, response_type)
    return P + dPdt * dt