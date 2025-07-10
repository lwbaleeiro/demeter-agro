# SmartAgroClima - Climate Intelligence for Agriculture

```
python -m uvicorn app.main:app --reload
python -m arq app.worker.WorkerSettings
```

SmartAgroClima is a web application that translates raw weather forecast data into simple, actionable insights for farmers. Instead of just showing temperature and rain predictions, it provides specific alerts for optimal spraying windows and fungal disease risks.

This MVP was developed to solve a specific problem: generic weather forecasts aren't enough to make critical, time-sensitive decisions on a farm.

## Features

- **Interactive Map:** Select your farm's precise location by clicking on a map.
- **Spraying Window Alerts:** Identifies the best continuous time window (e.g., 48 hours) for spraying, based on wind speed and precipitation forecasts.
- **Fungal Risk Alerts:** Warns you if the combination of temperature and humidity in the upcoming days is favorable for the development of common fungal diseases.
- **PDF Report Generation:** Generate a printable PDF report of the analysis insights.
- **Decoupled Architecture:** A modern frontend built with Svelte communicates with a powerful Python backend API.

## Tech Stack

- **Backend:** Python 3, FastAPI, Uvicorn
- **Frontend:** Svelte, Vite, TypeScript, Leaflet.js, jsPDF
- **Data Source:** OpenWeatherMap 5-day/3-hour Forecast API
- **Containerization:** Docker, Docker Compose

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- An OpenWeatherMap API Key (set as `OPENWEATHER_API_KEY` environment variable in your `.env` file)

### 1. Environment Variables

Create a `.env` file in the project root directory (`demeter/`) and add your OpenWeatherMap API key:

```
OPENWEATHER_API_KEY="YOUR_API_KEY_HERE"
```

Remember to replace `"YOUR_API_KEY_HERE"` with your actual key.

### 2. Build and Run with Docker Compose

From the project root directory (`demeter/`), run the following commands:

```bash
# Build the Docker images for both backend and frontend
docker-compose build

# Start the containers in detached mode
docker-compose up -d
```

This will build the necessary Docker images and start both the backend (FastAPI) and frontend (Nginx serving Svelte) services.

- The backend will be accessible at `http://localhost:8000`.
- The frontend will be accessible at `http://localhost:80`.

### Stopping the Application

To stop the running containers, from the project root directory:

```bash
docker-compose down
```

## How to Use

1.  Open the frontend URL (e.g., `http://localhost:80`) in your browser.
2.  The application will display a map centered on Brazil.
3.  Click anywhere on the map to place a marker on your desired location.
4.  Click the "Analisar Clima" button.
5.  The application will call the backend, process the forecast, and display the recommendation cards for spraying and fungal risk.
6.  After analysis, click the "Imprimir Relatório (PDF)" button to generate a PDF report of the insights.
