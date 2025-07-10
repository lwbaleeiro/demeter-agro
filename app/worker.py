import ee
import os
import json
from datetime import datetime, timedelta
from arq.connections import RedisSettings
from ee import ServiceAccountCredentials
from .config import settings

async def analyze_satellite_image(ctx, lat: float, lon: float):
    """
    Tarefa de fundo (ARQ) para analisar a imagem de satélite.
    """
    try:
        print("Attempting to initialize Earth Engine...")
        credentials = ServiceAccountCredentials(
            email=os.environ["GOOGLE_SERVICE_ACCOUNT_EMAIL"],
            key_file=os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        )
        ee.Initialize(credentials, project=os.environ["GOOGLE_PROJECT_ID"])
        print("Earth Engine initialized successfully.")
    except Exception as e:
        print(f"Error initializing Earth Engine: {e}")
        # Se a inicialização falhar, retorne um erro para o cliente.
        result = {
            "error": "Falha ao inicializar o Google Earth Engine.",
            "details": str(e)
        }
        await ctx['redis'].set(ctx['job_id'], json.dumps(result), ex=3600)
        return result

    point = ee.Geometry.Point(lon, lat)
    
    # Definir o período de busca (últimos 30 dias)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    print(f"Searching for images from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Usar a coleção de imagens do Sentinel-2
    collection = (
        ee.ImageCollection('COPERNICUS/S2_SR')
        .filterBounds(point)
        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        .sort('CLOUDY_PIXEL_PERCENTAGE')
        .limit(1)
    )
    
    image = collection.first()

    if not image:
        print("No image found for the given criteria.")
        result = {
            "ndvi_value": None,
            "image_url": None,
            "message": "Nenhuma imagem de satélite encontrada para a área e período especificados."
        }
        await ctx['redis'].set(ctx['job_id'], json.dumps(result), ex=3600)
        return result

    print("Image found. Calculating NDVI...")
    
    # Calcular NDVI
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    
    # Extrair o valor médio de NDVI na região
    ndvi_value = ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point.buffer(100), # Buffer de 100 metros ao redor do ponto
        scale=10
    ).get('NDVI').getInfo()

    print(f"NDVI calculated: {ndvi_value}")

    # Gerar URL da imagem de thumbnail
    image_url = image.getThumbUrl({
        'bands': ['B4', 'B3', 'B2'], # RGB
        'min': 0,
        'max': 3000,
        'region': point.buffer(500).bounds().getInfo()
    })

    print(f"Image URL generated: {image_url}")

    result = {
        "ndvi_value": round(ndvi_value, 4) if ndvi_value else None,
        "image_url": image_url
    }

    # Armazenar o resultado no Redis usando o job_id como chave, como JSON
    await ctx['redis'].set(ctx['job_id'], json.dumps(result), ex=3600) # Expira em 1 hora
    print("Result stored in Redis.")
    return result


class WorkerSettings:
    functions = [analyze_satellite_image]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_DSN)
