import asyncio
import ee
from arq.connections import RedisSettings
from .config import settings

async def initialize_goolge_earth_engine(ctx):
    """Autentica e inicializa a sessão com o Google Earth Engine."""
    try:
        # A autenticação acontece automaticamente se a variável de ambiente
        # GOOGLE_APPLICATION_CREDENTIALS estiver configurada com o caminho para o seu JSON.
        ee.Initialize(project=settings.GOOGLE_PROJECT_ID)
        print("Google Earth Engine inicializado com sucesso.")
    except Exception as e:
        print(f"Falha ao inicializar o Google Earth Engine: {e}")
        print("Certifique-se de que suas credenciais (GOOGLE_APPLICATION_CREDENTIALS) e o ID do projeto (GOOGLE_PROJECT_ID) estão configurados corretamente.")

async def analyze_satellite_image(ctx, lat: float, lon: float):
    """
    Tarefa de fundo (ARQ) para analisar a imagem de satélite.
    """
    await initialize_goolge_earth_engine(ctx)

    # Lógica para buscar a imagem e calcular o NDVI
    # (Esta é uma implementação de exemplo e pode precisar de ajustes)
    point = ee.Geometry.Point(lon, lat)
    
    # Usar a coleção de imagens do Sentinel-2
    collection = (
        ee.ImageCollection('COPERNICUS/S2_SR')
        .filterBounds(point)
        .filterDate('2023-01-01', '2023-12-31') # Exemplo de intervalo de datas
        .sort('CLOUDY_PIXEL_PERCENTAGE')
        .limit(1)
    )
    
    image = ee.Image(collection.first())
    
    # Calcular NDVI
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    
    # Extrair o valor médio de NDVI na região
    ndvi_value = ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point.buffer(100), # Buffer de 100 metros ao redor do ponto
        scale=10
    ).get('NDVI').getInfo()

    # Simulação de uma URL de imagem (em um caso real, você geraria e armazenaria a imagem)
    image_url = image.getThumbUrl({
        'bands': ['B4', 'B3', 'B2'], # RGB
        'min': 0,
        'max': 3000,
        'region': point.buffer(500).bounds().getInfo()['coordinates']
    })

    result = {
        "ndvi_value": round(ndvi_value, 4) if ndvi_value else None,
        "image_url": image_url
    }

    # Armazenar o resultado no Redis usando o job_id como chave
    await ctx['redis'].set(ctx['job_id'], str(result), ex=3600) # Expira em 1 hora
    return result


class WorkerSettings:
    functions = [analyze_satellite_image]
    on_startup = initialize_goolge_earth_engine
    redis_settings = RedisSettings.from_dsn(settings.REDIS_DSN)
