import numpy as np

def functional_response(P, a, b, response_type):
    """
    Compute the functional response of our predator to prey, 
    uses 
    Parameters:
        P: biomass level
        a: saturation constant
        b: half-saturation constant
        response_type: 1 for c1 (Type II), 2 for c2 (Type III)
    """
    if response_type == 1:
        # Type II functional response
        return (a * P) / (b + P)
    elif response_type == 2:
        # Type III functional response
        return (a * P**2) / (b**2 + P**2)
    else:
        raise ValueError("Invalid response_type. Use 1 for Type II or 2 for Type III.")
    
def compute_dPdt(P, r, K, a, b, response_type):
    """
    Compute the rate of change of prey biomass.
    
    Parameters:
        P: current prey biomass
    """
    dPdt = compute_dPdt(P, H0, K, r, a, b, response_type)
    P_new = P + dPdt * dt
    return max(0.0, min(K, P_new))        