# Bioreactor Digital Twin Web Application

This is a web-based digital twin of a bioreactor system, built with Flask and Plotly Dash. It allows interactive exploration of bioreactor parameters and their effects on the process.

## Features

- Interactive sliders for key bioreactor parameters
- Real-time visualization of concentration profiles
- Performance metrics calculation
- Responsive web interface

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:8050`

## Deployment to PythonAnywhere

1. Log in to your PythonAnywhere account
2. Create a new web app
3. Upload the following files:
   - `app.py`
   - `requirements.txt`
4. In the PythonAnywhere console:
   ```bash
   pip install -r requirements.txt
   ```
5. Configure the web app to use `app.py` as the WSGI file
6. Reload the web app

## Parameters

The application allows you to adjust:
- Working Volume (L)
- Initial Biomass Concentration (g/L)
- Initial Substrate Concentration (g/L)
- Maximum Growth Rate (h⁻¹)
- Half-Saturation Constant (g/L)
- Cell Death Rate (h⁻¹)

## License

MIT License 