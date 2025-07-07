# Demeter - Climate Intelligence for Agriculture

Demeter is a web application that translates raw weather forecast data into simple, actionable insights for farmers. Instead of just showing temperature and rain predictions, it provides specific alerts for optimal spraying windows and fungal disease risks.

This MVP was developed to solve a specific problem: generic weather forecasts aren't enough to make critical, time-sensitive decisions on a farm.

## Features

- **Interactive Map:** Select your farm's precise location by clicking on a map.
- **Spraying Window Alerts:** Identifies the best continuous time window (e.g., 48 hours) for spraying, based on wind speed and precipitation forecasts.
- **Fungal Risk Alerts:** Warns you if the combination of temperature and humidity in the upcoming days is favorable for the development of common fungal diseases.
- **Decoupled Architecture:** A modern frontend built with Svelte communicates with a powerful Python backend API.

## Tech Stack

- **Backend:** Python 3, FastAPI, Uvicorn
- **Frontend:** Svelte, Vite, TypeScript, Leaflet.js
- **Data Source:** OpenWeatherMap 5-day/3-hour Forecast API

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js and npm (or a compatible package manager)

### 1. Backend Setup

From the project root directory (`demeter/`):

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Create an environment file from the example
# (On Windows, use `copy` instead of `cp`)
cp .env.example .env

# Next, you need to get a free API key from [OpenWeatherMap](https://openweathermap.org/).
# 3. Open the `.env` file and paste your API key into it:
OPENWEATHER_API_KEY=YOUR_API_KEY_HERE
```

### 2. Frontend Setup

Navigate to the frontend directory and install the Node.js dependencies:

```bash
# 1. Go to the frontend directory
cd frontend

# 2. Install dependencies
npm install
```

## Running the Application

You will need two separate terminals to run both the backend and frontend servers.

**Terminal 1: Start the Backend**

From the project root directory (`demeter/`):

```bash
python -m uvicorn app.main:app --reload
```
The API will be running at `http://127.0.0.1:8000`.

**Terminal 2: Start the Frontend**

From the `frontend/` directory:

```bash
npm run dev
```
The frontend development server will start, usually at `http://localhost:5173`.

## How to Use

1.  Open the frontend URL (e.g., `http://localhost:5173`) in your browser.
2.  The application will display a map centered on Brazil.
3.  Click anywhere on the map to place a marker on your desired location.
4.  Click the "Analisar Clima" button.
5.  The application will call the backend, process the forecast, and display the recommendation cards for spraying and fungal risk.