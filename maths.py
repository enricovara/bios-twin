import numpy as np
from scipy.integrate import solve_ivp

def bioreactor_odes(t, y, params):
    X, S, P = y
    μ = params['μ_max'] * S / (params['K_s'] + S)
    dX = (μ - params['k_d']) * X
    dS = -(1 / params['Y_xs']) * μ * X
    dP = params['Y_px'] * μ * X
    return [dX, dS, dP]

def stop_when_target(t, y, params):
    return y[2] - params['P_target']
stop_when_target.terminal = True
stop_when_target.direction = 1

def simulate_bioreactor(params):
    y0 = [params['X0'], params['S0'], 0.0]
    sol = solve_ivp(
        lambda t, y: bioreactor_odes(t, y, params),
        t_span=(0, params['t_end']),
        y0=y0,
        events=lambda t, y: stop_when_target(t, y, params),
        dense_output=True,
        max_step=0.5
    )
    # Add print statements for debugging
    print(f"--- Simulation Debug ---")
    print(f"Solver status: {sol.status}, message: {sol.message}")
    print(f"Number of time points: {sol.t.shape[0]}")
    if sol.t.shape[0] > 0:
        print(f"Time range: {sol.t.min():.2f} to {sol.t.max():.2f}")
        print(f"Final concentrations: X={sol.y[0, -1]:.2f}, S={sol.y[1, -1]:.2f}, P={sol.y[2, -1]:.2f}")
        print(f"Concentration shapes: X:{sol.y[0].shape}, S:{sol.y[1].shape}, P:{sol.y[2].shape}")
    else:
        print("Simulation returned no time points.")
    print(f"------------------------")
        
    return sol.t, sol.y

# Class to represent a model equation for UI display
class ModelEquation:
    def __init__(self, name, equation_str, parameters):
        self.name = name  # e.g., "Growth Rate (μ)"
        self.equation_str = equation_str # e.g., "μ = μ_max * S / (K_s + S)"
        self.parameters = parameters # List of strings, e.g., ["μ_max: ...", "S: ..."]

# Define the specific equations
growth_eq = ModelEquation(
    name='Growth Rate (μ)',
    equation_str=r'\mu = \frac{\mu_{max} \cdot S}{K_s + S}',
    parameters=[
        r'\mu_{max}: Maximum specific growth rate (h^{-1})',
        'S: Substrate concentration (g/L)',
        'K_s: Half-saturation constant (g/L)'
    ]
)

biomass_eq = ModelEquation(
    name='Biomass (X)',
    equation_str=r'\frac{dX}{dt} = (\mu - k_d) \cdot X',
    parameters=[
        'k_d: Cell death rate (h^{-1})',
        'X: Biomass concentration (g/L)'
    ]
)

substrate_eq = ModelEquation(
    name='Substrate (S)',
    equation_str=r'\frac{dS}{dt} = -\frac{1}{Y_{xs}} \cdot \mu \cdot X',
    parameters=[
        'Y_{xs}: Biomass yield on substrate (g/g)'
    ]
)

product_eq = ModelEquation(
    name='Product (P)',
    equation_str=r'\frac{dP}{dt} = Y_{px} \cdot \mu \cdot X',
    parameters=[
        'Y_{px}: Product yield on biomass (g/g)'
    ]
)

# List containing all equation objects
model_equations = [growth_eq, biomass_eq, substrate_eq, product_eq] 