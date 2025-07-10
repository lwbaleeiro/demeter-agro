# SmartAgroClima - Technical Vision and Future Roadmap

This document outlines the current technical state of the SmartAgroClima project and a strategic vision for its future development.

## Current Architecture (MVP v2)

The application is architected as a decoupled system, consisting of a backend API and a separate frontend client. This separation allows for independent development, scaling, and technology evolution.

### Backend

- **Framework:** **FastAPI** on Python 3. It was chosen for its high performance, asynchronous capabilities (leveraging `asyncio` and `httpx`), and automatic data validation with Pydantic.
- **Core Logic:** The backend is responsible for three main tasks:
    1.  **Data Fetching (`services.py`):** Interfaces with the external OpenWeatherMap API to get raw forecast data.
    2.  **Data Processing (`logic.py`):** Contains the core business rules. It iterates through the forecast data to identify patterns based on predefined thresholds (e.g., wind speed, humidity, temperature).
    3.  **Serving Insights (`main.py`):** Exposes a simple `/insights` endpoint that takes geographic coordinates and returns the processed, actionable alerts.
- **Configuration:** API keys and other settings are managed via a `.env` file, loaded by `pydantic-settings` for type-safe configuration management.
- **CORS:** `CORSMiddleware` is configured to allow the frontend client (running on a different port) to communicate with the API, with a permissive policy for development.

### Frontend

- **Framework:** **Svelte 4** with **Vite**. This stack was chosen to provide a modern, reactive user experience while maintaining a simple and highly performant codebase. Svelte's compile-time approach minimizes runtime overhead.
- **Mapping:** **Leaflet.js** is used for the interactive map. It was chosen over alternatives like Google Maps API to avoid the need for API key management and billing setup, making the project simpler to set up and run for new developers.
- **Structure:** The frontend is component-based:
    - `Map.svelte`: An encapsulated component that handles all map interactions and emits an event with the selected coordinates.
    - `Results.svelte`: A presentational component that receives the API response and displays it in formatted cards.
    - `App.svelte`: The main application component that manages state (loading, errors, API responses) and orchestrates the interaction between the map and the results.
- **TypeScript:** The entire frontend codebase uses TypeScript for improved code quality, maintainability, and developer experience.

## Future Roadmap & Technical Vision

The current MVP is a solid foundation. The following steps outline a vision for evolving SmartAgroClima into a more powerful and robust platform.

### Phase 1: Refinement and Production Readiness

1.  **Containerization:** Dockerize both the FastAPI backend and the Svelte frontend using `docker-compose`. This will standardize the development environment and simplify deployment immensely.
2.  **Robust Testing:**
    - **Backend:** Implement a comprehensive test suite using `pytest`. This should include unit tests for the logic in `logic.py` (mocking the forecast data) and integration tests for the API endpoints.
    - **Frontend:** Implement component tests using Vitest to ensure UI components render and behave correctly.
3.  **Configuration for Production:** Refine the CORS policy to be more restrictive, allowing only the specific domain of the deployed frontend.
4.  **User Authentication:** Implement a simple user authentication system (e.g., using JWT) to allow users to save and manage multiple farm locations.

### Phase 2: Advanced Agronomic Insights

1.  **Historical Weather Data:** Integrate a service (like Open-Meteo) to fetch historical weather data for the selected location. This is the foundation for more advanced analytics.
2.  **Growing Degree Days (GDD) Calculation:** With historical data, calculate the GDD for the current season, a critical metric for predicting crop development stages.
3.  **Pest and Disease Modeling:** Evolve the simple "fungal risk" alert into more sophisticated models. This could involve:
    - Using academic or industry-standard models for specific diseases (e.g., soybean rust, wheat leaf rust).
    - Incorporating historical data and GDD to predict pest life cycles.
4.  **Satellite Imagery Integration:** As originally envisioned, integrate with a geospatial data provider.
    - **Google Earth Engine:** For non-commercial or research-focused expansion, its powerful analysis capabilities could be used to calculate NDVI (Normalized Difference Vegetation Index) to assess crop health remotely.
    - **Commercial Provider (e.g., Planet.com):** For a commercial-grade product, use high-resolution satellite imagery to detect stress, irrigation issues, or pest damage.

### Phase 3: Platform and Scalability

1.  **Database Integration:** Add a database (e.g., PostgreSQL with PostGIS for geographic data) to store user information, farm locations, historical analysis, and sensor data.
2.  **Asynchronous Task Queue:** For long-running analyses (like processing satellite imagery or running complex models), implement a task queue like Celery or ARQ to process jobs in the background without blocking the API.
3.  **IoT Integration:** Allow users to connect on-site weather stations or soil moisture sensors to provide hyper-local, real-time data, dramatically improving the accuracy of the recommendations.
4.  **Multi-Language Support:** Internationalize the frontend to support multiple languages and expand the user base.
