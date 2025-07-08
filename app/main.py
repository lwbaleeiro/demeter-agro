from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import FarmLocation, DemeterInsight, AnalysisConfig
from . import services
from . import logic
import asyncio

app = FastAPI(
    title="Demeter - Inteligência Climática para o Agro",
    description="API para traduzir dados climáticos em insights acionáveis para agricultores.",
    version="0.2.0" # Versão atualizada para refletir a nova funcionalidade
)

# --- Configuração do CORS ---
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
    Agora busca tanto a previsão do tempo quanto dados históricos em paralelo.
    """
    # Busca os dados de previsão e históricos em paralelo para mais eficiência
    forecast_task = services.get_forecast_data(lat=location.lat, lon=location.lon)
    historical_task = services.get_historical_weather_data(lat=location.lat, lon=location.lon)
    
    results = await asyncio.gather(forecast_task, historical_task)
    
    forecast_data, historical_data = results
    
    if forecast_data.get("error"):
        raise HTTPException(status_code=500, detail=forecast_data.get("error"))
    
    # O erro nos dados históricos é tratado dentro da lógica para não quebrar a análise principal
    if historical_data.get("error"):
        print(f"Alerta: Não foi possível obter dados históricos. {historical_data.get('error')}")

    # A função de análise agora recebe ambos os conjuntos de dados
    insights = logic.analyze_forecast(forecast_data, historical_data, config.model_dump() | {"lat": location.lat, "lon": location.lon})
    
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
