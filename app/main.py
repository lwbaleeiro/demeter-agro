from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .schemas import FarmLocation, DemeterInsight, AnalysisConfig, SatelliteAnalysis
from . import services
from . import logic
from .config import settings
import asyncio
import json
from arq import create_pool
from arq.connections import RedisSettings

app = FastAPI(
    title="Demeter - Inteligência Climática para o Agro",
    description="API para traduzir dados climáticos em insights acionáveis para agricultores.",
    version="0.3.0" # Versão atualizada para refletir a integração com GEE e ARQ
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

# --- ARQ Redis Pool ---
redis_pool = None

@app.on_event("startup")
async def startup_event():
    global redis_pool
    redis_settings = RedisSettings.from_dsn(settings.REDIS_DSN)
    redis_pool = await create_pool(redis_settings)
    # print("ARQ Redis pool initialized.")
    # print(f"Type of redis_pool: {type(redis_pool)}")
    # print(f"Dir of redis_pool: {dir(redis_pool)}")

@app.on_event("shutdown")
async def shutdown_event():
    if redis_pool:
        await redis_pool.close()
        print("ARQ Redis pool closed.")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Demeter"}


@app.post("/insights/", response_model=DemeterInsight)
async def get_demeter_insights(location: FarmLocation, config: AnalysisConfig = Depends(AnalysisConfig)):
    """
    Endpoint principal. Recebe a localização e retorna os insights acionáveis.
    Agora busca tanto a previsão do tempo quanto dados históricos em paralelo.
    A análise de satélite é submetida como uma tarefa de fundo.
    """
    if not redis_pool:
        raise HTTPException(status_code=500, detail="Redis pool not initialized.")

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

    # Submete a tarefa de análise de satélite para o ARQ
    # O resultado inicial da análise de satélite indica que está sendo processado
    try:
        job = await redis_pool.enqueue_job(
            "analyze_satellite_image", 
            lat=location.lat, 
            lon=location.lon,
            _job_id=f"satellite_analysis_{location.lat}_{location.lon}" # ID customizado para fácil recuperação
        )
        satellite_analysis_initial = SatelliteAnalysis(
            available=False,
            message="Análise de satélite em processamento...",
            ndvi_value=None,
            image_url=None,
            task_id=job.job_id # Adiciona o ID da tarefa para o frontend acompanhar
        )
    except Exception as e:
        print(f"Erro ao enfileirar tarefa de satélite: {e}")
        satellite_analysis_initial = SatelliteAnalysis(
            available=False,
            message="Erro ao iniciar análise de satélite.",
            ndvi_value=None,
            image_url=None,
            task_id=None
        )

    # A função de análise agora recebe ambos os conjuntos de dados
    insights = logic.analyze_forecast(forecast_data, historical_data, config.model_dump() | {"lat": location.lat, "lon": location.lon}, satellite_analysis_initial.model_dump())
    
    if insights.get("error"):
        raise HTTPException(status_code=500, detail=insights.get("error"))

    # A análise de satélite já está incluída nos insights retornados por logic.analyze_forecast

    return insights


@app.get("/satellite/result/{task_id}", response_model=SatelliteAnalysis)
async def get_satellite_analysis_result(task_id: str):
    """
    Endpoint para verificar o status e obter o resultado de uma tarefa de análise de satélite.
    """
    if not redis_pool:
        raise HTTPException(status_code=500, detail="Redis pool not initialized.")

    print(f"Received task_id: {task_id}")
    result_json = await redis_pool.get(task_id)
    print(f"Result from Redis for {task_id}: {result_json}")

    if not result_json:
        # If the job is not yet finished, or if it failed and the result was not stored
        # We can't check job.is_finished or job.is_failed directly with arq 0.26.3
        # So we assume it's still processing if no result is found.
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Análise em processamento.")

    # The result of the job is a JSON string that needs to be deserialized
    try:
        result_data = json.loads(result_json)
        return SatelliteAnalysis(
            available=True,
            message="Análise de satélite concluída.",
            ndvi_value=result_data.get("ndvi_value"),
            image_url=result_data.get("image_url")
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erro ao decodificar resultado da tarefa.")


@app.post("/weather-data/")
async def get_raw_weather_data(location: FarmLocation):
    """
    Endpoint de depuração para obter os dados brutos da API de clima.
    """
    weather_data = await services.get_forecast_data(lat=location.lat, lon=location.lon)
    if weather_data.get("error"):
        raise HTTPException(status_code=500, detail=weather_data.get("error"))
    return weather_data