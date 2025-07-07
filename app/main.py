from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import FarmLocation, DemeterInsight, AnalysisConfig
from . import services
from . import logic

app = FastAPI(
    title="Demeter - Inteligência Climática para o Agro",
    description="API para traduzir dados climáticos em insights acionáveis para agricultores.",
    version="0.1.0"
)

# --- Configuração do CORS ---
# Permite que o frontend (rodando em qualquer origem) se comunique com a API.
# Para produção, seria mais restritivo (ex: origins=["http://demeter.app"])
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Demeter"}


@app.post("/insights/", response_model=DemeterInsight)
async def get_demeter_insights(location: FarmLocation, config: AnalysisConfig = Depends(AnalysisConfig)):
    """
    Endpoint principal. Recebe a localização e retorna os insights acionáveis.
    Permite configurar os limiares de análise.
    """
    forecast_data = await services.get_forecast_data(lat=location.lat, lon=location.lon)
    
    if forecast_data.get("error"):
        raise HTTPException(status_code=500, detail=forecast_data.get("error"))

    insights = logic.analyze_forecast(forecast_data, config.model_dump())
    
    if insights.get("error"):
        raise HTTPException(status_code=500, detail=insights.get("error"))

    return insights


@app.post("/weather-data/")
async def get_raw_weather_data(location: FarmLocation):
    """
    Endpoint de depuração para obter os dados brutos da API de clima.
    """
    weather_data = await services.get_forecast_data(lat=location.lat, lon=location.lon)
    if weather_data.get("error"):
        raise HTTPException(status_code=500, detail=weather_data.get("error"))
    return weather_data
