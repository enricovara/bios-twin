from flask import Flask
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc

# Import refactored components
from params import default_params
from maths import simulate_bioreactor
from layout import layout # Import the layout variable

# Initialize Flask app
server = Flask(__name__)

# Initialize Dash app
app = Dash(__name__, server=server, url_base_pathname='/')

# Assign the layout
app.layout = layout

# Add custom CSS for tooltips
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .tooltip-icon {
                font-size: 14px;
                color: #6c757d;
            }
            .tooltip-icon:hover {
                color: #0d6efd;
            }
            .dash-tooltip {
                max-width: 300px !important;
                white-space: normal !important;
                background-color: rgba(255, 255, 255, 0.95) !important;
                border: 1px solid #dee2e6 !important;
                border-radius: 4px !important;
                padding: 8px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                z-index: 1000 !important;
                color: #212529 !important;
            }
            .dash-tooltip .tooltip-inner {
                max-width: 300px !important;
                white-space: normal !important;
                text-align: left !important;
                background-color: rgba(255, 255, 255, 0.95) !important;
                color: #212529 !important;
            }
            /* Add styles for slider tooltips */
            .rc-slider-tooltip {
                max-width: 300px !important;
                white-space: normal !important;
                background-color: rgba(255, 255, 255, 0.95) !important;
                border: 1px solid #dee2e6 !important;
                border-radius: 4px !important;
                padding: 8px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                z-index: 1000 !important;
            }
            .rc-slider-tooltip-inner {
                max-width: 300px !important;
                white-space: normal !important;
                text-align: left !important;
                background-color: rgba(255, 255, 255, 0.95) !important;
                color: #212529 !important;
            }
            /* Info icon tooltip styles */
            .tooltiptext {
                display: none;
                background-color: white;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.15);
                width: 250px;
                position: absolute;
                z-index: 1000;
                top: 125%;
                left: 50%;
                transform: translateX(-50%);
            }
            .info-icon-container {
                position: relative;
                display: inline-block;
            }
            .info-icon-container:hover .tooltiptext {
                display: block;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define callbacks
@app.callback(
    [Output('bioreactor-plot', 'figure'),
     Output('output-container', 'children'),
     Output('V-value', 'children'),
     Output('X0-value', 'children'),
     Output('S0-value', 'children'),
     Output('μ_max-value', 'children'),
     Output('K_s-value', 'children'),
     Output('k_d-value', 'children')],
    [Input('V-slider', 'value'),
     Input('X0-slider', 'value'),
     Input('S0-slider', 'value'),
     Input('μ_max-slider', 'value'),
     Input('K_s-slider', 'value'),
     Input('k_d-slider', 'value')]
)
def update_plot(V, X0, S0, μ_max, K_s, k_d):
    params = {
        'V': V,
        'X0': X0,
        'S0': S0,
        'μ_max': μ_max,
        'K_s': K_s,
        'k_d': k_d,
        # Include other parameters from default_params needed for simulation
        'Y_xs': default_params['Y_xs'], 
        'Y_px': default_params['Y_px'],
        'P_target': default_params['P_target'],
        't_end': default_params['t_end']
    }
    
    time, concentrations = simulate_bioreactor(params)
    X, S, P = concentrations
    # Convert numpy arrays to Python lists for plotting and debugging
    x_vals = time.tolist() if hasattr(time, 'tolist') else time
    X_vals = X.tolist() if hasattr(X, 'tolist') else X
    S_vals = S.tolist() if hasattr(S, 'tolist') else S
    P_vals = P.tolist() if hasattr(P, 'tolist') else P
    
    # Create the figure using Plotly Go
    fig = go.Figure()
    
    if len(x_vals) > 0:
        print(f"Plotting {len(x_vals)} data points for each species")
        fig.add_trace(go.Scatter(x=x_vals, y=X_vals, mode='lines', name='Biomass (X) g/L'))
        fig.add_trace(go.Scatter(x=x_vals, y=S_vals, mode='lines', name='Substrate (S) g/L'))
        fig.add_trace(go.Scatter(x=x_vals, y=P_vals, mode='lines', name='Product (P) g/L'))
        
        batch_time = x_vals[-1]
        final_product = P_vals[-1]
        productivity = final_product / batch_time if batch_time > 0 else 0
        
        metrics = html.Div([
            html.H3('Batch Performance Metrics'),
            html.P(f'Batch Duration: {batch_time:.1f} hours'),
            html.P(f'Final Product Concentration: {final_product:.2f} g/L'),
            html.P(f'Productivity: {productivity:.3f} g/L/h')
        ])
        
        title = 'Bioreactor Simulation Results'
    else:
        # Handle case with no simulation results
        metrics = html.P('Simulation did not run or produced no results.')
        title = 'Bioreactor Simulation - No Data'
        batch_time = 0
        final_product = 0
        productivity = 0
        
    fig.update_layout(
        title=title,
        xaxis_title='Time (h)',
        yaxis_title='Concentration (g/L)',
        legend_title='Species',
        hovermode="x unified"
    )
    
    # Update slider value displays
    v_text = f'{V:,} L'
    x0_text = f'{X0:.2f} g/L'
    s0_text = f'{S0} g/L'
    mu_max_text = f'{μ_max:.2f} h⁻¹'
    ks_text = f'{K_s:.1f} g/L'
    kd_text = f'{k_d:.3f} h⁻¹'
    
    print("Figure data traces:", fig.data)
    return fig, metrics, v_text, x0_text, s0_text, mu_max_text, ks_text, kd_text

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True) 