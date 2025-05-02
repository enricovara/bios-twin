import dash_bootstrap_components as dbc
from dash import html, dcc
from params import default_params
from maths import model_equations

# Function to generate HTML for a single equation
def create_equation_div(eq):
    # Wrap equation string and parameters with Markdown for LaTeX rendering
    equation_markdown = dcc.Markdown(f'${eq.equation_str}$', mathjax=True, style={'textAlign': 'center', 'fontSize': '1.3em'}) # Increased font size
    
    # Process parameters: Wrap if they contain LaTeX symbols (_ or \), otherwise use plain text
    parameter_elements = []
    for param in eq.parameters:
        param_parts = param.split(':', 1)
        name_part = param_parts[0].strip()
        desc_part = f': {param_parts[1].strip()}' if len(param_parts) == 2 else ''

        # Check if the name part needs LaTeX rendering (contains _ or \)
        # Handles raw strings like r'\mu_{max}' by checking original name_part
        needs_render = ('_' in name_part) or ('\\' in name_part)

        if needs_render:
            # Clean the name part (e.g., remove r'...' if present)
            clean_name = name_part
            if clean_name.startswith("r'") and clean_name.endswith("'"):
                 clean_name = clean_name[2:-1]
            
            # Wrap the potentially LaTeX name part in $...$
            latex_markdown = dcc.Markdown(f'${clean_name}$', mathjax=True, style={'display': 'inline-block', 'marginRight':'5px'}) # Add small margin
            parameter_elements.append(html.Li([latex_markdown, desc_part], style={'whiteSpace':'normal','overflowWrap':'break-word','wordBreak':'break-word'}))
        else:
            # Keep the whole parameter string as plain text
            parameter_elements.append(html.Li(param, style={'whiteSpace':'normal','overflowWrap':'break-word','wordBreak':'break-word'}))

    # Style the individual equation box for flex layout
    box_style = {
        'flex': '1 1 45%',       # Grow, shrink, basis 45% (allows 2 columns)
        'minWidth': '350px',     # Minimum width before wrapping
        'margin': '10px',        # Spacing between boxes
        'padding': '15px',        # Internal padding
        'border': '1px solid #ddd',
        'borderRadius': '8px',
        'backgroundColor': '#fff', # White background for each box
        'overflowWrap': 'break-word', # Allow breaking long words
        'wordBreak': 'break-word',    # Ensure words wrap
    }

    return html.Div([
        html.H3(eq.name, style={'textAlign': 'center'}),
        equation_markdown, # Use the Markdown component
        html.P('Where:', style={'marginTop': '15px'}),
        html.Ul(parameter_elements, style={'whiteSpace': 'normal', 'overflowWrap': 'break-word','wordBreak':'break-word','width':'100%'}) # Ensure wrapping of bullet text and full-width list
    ], style=box_style)

# Function to generate HTML for a single slider
def create_slider(param_id, label, tooltip_text, min_val, max_val, step, value, marks_config):
    """
    Create a slider component with standard formatting
    
    Parameters:
    -----------
    param_id : str
        The parameter ID used for both the slider and value display
    label : str
        The display label for the parameter
    tooltip_text : str
        The explanation text shown in the tooltip
    min_val : float or int
        Minimum value for the slider
    max_val : float or int
        Maximum value for the slider
    step : float or int
        Step size for the slider
    value : float or int
        Default value for the slider
    marks_config : dict
        Dictionary defining the tick marks for the slider
    
    Returns:
    --------
    html.Div
        The complete slider component with label, value display, and tooltip
    """
    # Slider wrapper style - consistent for all sliders
    slider_style = {
        'flex': '1 1 30%', 
        'minWidth': '300px', 
        'padding': '20px',
        'boxSizing': 'border-box'
    }
    
    return html.Div([
        # Label row with value display and tooltip
        html.Div([
            html.Label(label),
            html.Span(id=f'{param_id}-value', style={'marginLeft': '10px', 'fontWeight': 'bold'}),
            html.Div([
                html.Span('ⓘ', 
                    id=f'{param_id}-tooltip',
                    style={'marginLeft': '10px', 'cursor': 'pointer'},
                    className='tooltip-icon'
                ),
                html.Div(
                    tooltip_text,
                    className='tooltiptext'
                )
            ], className='info-icon-container'),
        ], style={'display': 'flex', 'alignItems': 'center'}),
        
        # The slider itself
        dcc.Slider(
            id=f'{param_id}-slider',
            min=min_val,
            max=max_val,
            step=step,
            value=value,
            marks=marks_config,
        ),
    ], style=slider_style)

layout = html.Div([
    html.H1('Bioreactor Digital Twin', style={'textAlign': 'center'}),
    
    # --- Combined Sliders Container --- 
    html.Div([
        # Create all sliders using the create_slider function
        create_slider(
            'V', 'Working Volume (L)',
            "The total volume of the bioreactor in liters. This affects how much product can be produced in a single batch.",
            0, 20000, 100, default_params['V'],
            {i: f'{i:,}' for i in range(0, 20001, 5000)}
        ),
        
        create_slider(
            'X0', 'Initial Biomass (g/L)',
            "The starting concentration of cells in the bioreactor, measured in grams per liter. Higher values can lead to faster production but may require more nutrients.",
            0, 1.0, 0.01, default_params['X0'],
            {0: f'{0:.1f}', **{i/10: f'{i/10:.1f}' for i in range(2, 11, 2)}}
        ),
        
        create_slider(
            'S0', 'Initial Substrate (g/L)',
            "The starting concentration of nutrients (like glucose) in the bioreactor, measured in grams per liter. This is the food source for the cells.",
            0, 100, 5, default_params['S0'],
            {i: str(i) for i in range(0, 101, 20)}
        ),
        
        create_slider(
            'μ_max', 'Max Growth Rate (h⁻¹)',
            "The maximum rate at which cells can grow, measured in doublings per hour. Higher values mean cells can grow and produce product faster.",
            0, 0.5, 0.01, default_params['μ_max'],
            {0: f'{0:.1f}', **{i/10: f'{i/10:.1f}' for i in range(1, 6)}}
        ),
        
        create_slider(
            'K_s', 'Half-Saturation (g/L)',
            "The substrate concentration at which cells grow at half their maximum rate, measured in grams per liter. Lower values mean cells can grow well even with little nutrients.",
            0, 5.0, 0.1, default_params['K_s'],
            {i: f'{i:.1f}' for i in range(0, 6)}
        ),
        
        create_slider(
            'k_d', 'Death Rate (h⁻¹)',
            "The rate at which cells die naturally, measured as a fraction of the population per hour. Higher values mean cells die faster, which can reduce productivity.",
            0, 0.01, 0.001, default_params['k_d'],
            {0: f'{0:.3f}', **{i/1000: f'{i/1000:.3f}' for i in range(2, 11, 2)}}
        ),
    # Style the combined slider container
    ], style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'justifyContent': 'space-around',
        'maxWidth': '1200px',
        'margin': '0 auto'
        }),
    
    # --- Graph --- Wrap in a centering Div
    html.Div([
        dcc.Graph(
            id='bioreactor-plot',
            style={'height': '500px'}, # Width will be handled by parent
            config={'responsive': True},
        )
    ], style={'maxWidth': '1200px', 'margin': '20px auto'}), # Center graph container
    
    # --- Output Container --- Update maxWidth
    html.Div(id='output-container', style={
        'marginTop': '20px', 
        'padding': '20px',
        'maxWidth': '1200px',     # Consistent max-width
        'margin': '20px auto',   
        'textAlign': 'center',   
        'border': '1px solid #ccc', 
        'borderRadius': '8px',   
        'backgroundColor': '#f8f9fa' 
        }),
    
    # --- Equations Container --- Already has maxWidth: 1200px, margin: 0 auto
    html.Div([
        html.H2('Model Equations', style={'textAlign': 'center', 'marginTop': '40px'}),
        html.Div([
            # Iterate through equation objects and create HTML divs
            *[create_equation_div(eq) for eq in model_equations]
        ], style={
              'display': 'flex', 
              'flexWrap': 'wrap', 
              'justifyContent': 'space-around', 
              'maxWidth': '1200px', # Consistent max-width
              'margin': '0 auto', 
              'padding': '20px', 
              'backgroundColor': '#f8f9fa', 
              'borderRadius': '10px',
              'minWidth': 'min-content'  # Prevent container from shrinking below content width
          })
    ])
]) 