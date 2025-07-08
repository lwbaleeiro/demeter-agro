import httpx
from .config import settings
from datetime import datetime, timedelta

# Documentação da API 5 day / 3 hour: https://openweathermap.org/forecast5
FORECAST_API_URL = "http://api.openweathermap.org/data/2.5/forecast"
HISTORICAL_API_URL = "https://api.open-meteo.com/v1/forecast"


async def get_forecast_data(lat: float, lon: float) -> dict:
    """
    Busca dados de previsão do tempo (5 dias, de 3 em 3 horas) da API OpenWeatherMap.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "pt_br",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(FORECAST_API_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Erro ao chamar a API do OpenWeatherMap: {e}")
            # O erro 401 especificamente pode ser um problema de chave ou de plano
            if e.response.status_code == 401:
                return {"error": "Chave de API inválida ou não autorizada. Verifique o arquivo .env e as permissões da sua chave no site do OpenWeatherMap."}
            return {"error": f"Não foi possível obter os dados do tempo (Erro: {e.response.status_code})."}
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            return {"error": "Ocorreu um erro inesperado no servidor."}

async def get_historical_weather_data(lat: float, lon: float, days: int = 5) -> dict:
    """
    Busca dados históricos de temperatura (máx e mín) dos últimos 'days' dias.
    Usa a API Open-Meteo, que não requer chave.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "past_days": days,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HISTORICAL_API_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Erro ao chamar a API do Open-Meteo: {e}")
            return {"error": f"Não foi possível obter os dados históricos do tempo (Erro: {e.response.status_code})."}
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao buscar dados históricos: {e}")
            return {"error": "Ocorreu um erro inesperado no servidor ao buscar dados históricos."}
