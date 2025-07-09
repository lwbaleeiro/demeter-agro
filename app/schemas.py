from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class FarmLocation(BaseModel):
    lat: float
    lon: float

class AnalysisConfig(BaseModel):
    crop_profile: Optional[str] = None

    # Pulverização
    wind_speed_threshold_ms: float = Field(2.8, description="Limite de velocidade do vento para pulverização em m/s (aprox. 10 km/h)")
    precipitation_prob_threshold: float = Field(0.1, description="Probabilidade máxima de chuva para pulverização (0.0 a 1.0)")

    # Risco Fúngico
    fungal_risk_humidity: float = Field(80, description="Umidade relativa mínima para risco fúngico (%)")
    fungal_risk_temp_min: float = Field(18, description="Temperatura mínima para risco fúngico (°C)")
    fungal_risk_temp_max: float = Field(26, description="Temperatura máxima para risco fúngico (°C)")

    # Geada
    frost_temp_threshold: float = Field(2, description="Temperatura limite para alerta de geada (°C)")

    # Estresse por Calor
    heat_stress_temp_threshold: float = Field(32, description="Temperatura limite para estresse por calor (°C)")

    # Plantio
    planting_temp_min: float = Field(18, description="Temperatura mínima ideal para plantio (°C)")
    planting_temp_max: float = Field(30, description="Temperatura máxima ideal para plantio (°C)")
    planting_rain_prob_threshold: float = Field(0.3, description="Probabilidade mínima de chuva para plantio (0.0 a 1.0)")

    # Colheita
    harvest_rain_prob_threshold: float = Field(0.1, description="Probabilidade máxima de chuva para colheita (0.0 a 1.0)")
    harvest_humidity_threshold: float = Field(70, description="Umidade máxima para colheita (%)")

    # Irrigação
    irrigation_no_rain_threshold: float = Field(0.05, description="Probabilidade máxima de chuva para recomendação de irrigação (0.0 a 1.0)")
    irrigation_temp_threshold: float = Field(25, description="Temperatura mínima para recomendação de irrigação (°C)")
    irrigation_min_hours: float = Field(24, description="Duração mínima em horas para recomendação de irrigação")

    # GDD
    gdd_base_temp: float = Field(10, description="Temperatura base para cálculo de Graus-Dia (°C)")

    # Geral
    min_window_hours: float = Field(12, description="Duração mínima em horas para uma janela ser considerada válida (geral)")


# --- Modelos para a Resposta dos Insights ---

class SprayingAlert(BaseModel):
    ideal_window_found: bool
    message: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    conditions: Optional[str] = None

class FungalRiskAlert(BaseModel):
    risk_level: str 
    risk_score: float
    message: str
    total_risk_hours: int
    details: Optional[str] = None

class FrostPeriod(BaseModel):
    time: str
    temp_min: float

class FrostAlert(BaseModel):
    frost_risk_found: bool
    message: str
    details: Optional[List[FrostPeriod]] = None

class HeatStressPeriod(BaseModel):
    time: str
    temp_max: float

class HeatStressAlert(BaseModel):
    heat_stress_found: bool
    message: str
    details: Optional[List[HeatStressPeriod]] = None

class PlantingPeriod(BaseModel):
    time: str
    temp: float
    rain_prob: float

class PlantingWindowAlert(BaseModel):
    planting_window_found: bool
    message: str
    details: Optional[List[PlantingPeriod]] = None

class HarvestingPeriod(BaseModel):
    time: str
    temp: float
    humidity: float
    wind_speed: float

class HarvestingWindowAlert(BaseModel):
    harvesting_window_found: bool
    message: str
    details: Optional[List[List[HarvestingPeriod]]] = None

class IrrigationPeriod(BaseModel):
    time: str
    temp: float
    rain_prob: float

class IrrigationRecommendation(BaseModel):
    irrigation_recommended: bool
    message: str
    details: Optional[List[List[IrrigationPeriod]]] = None

class GDDInsight(BaseModel):
    gdd_calculated: bool
    message: str
    total_gdd: Optional[float] = None
    details: Optional[List[Dict[str, Any]]] = None

class SatelliteAnalysis(BaseModel):
    available: bool
    message: str
    ndvi_value: Optional[float] = None
    image_url: Optional[str] = None
    task_id: Optional[str] = None

class NDVIInsight(BaseModel):
    message: str
    level: str
    ndvi_value: Optional[float] = None
    explanation_text: Optional[str] = None

class DemeterInsight(BaseModel):
    spraying_alert: SprayingAlert
    fungal_risk_alert: FungalRiskAlert
    frost_alert: FrostAlert
    heat_stress_alert: HeatStressAlert
    planting_window_alert: PlantingWindowAlert
    harvesting_window_alert: HarvestingWindowAlert
    irrigation_recommendation: IrrigationRecommendation
    gdd_insight: GDDInsight
    satellite_analysis: SatelliteAnalysis
    ndvi_insight: NDVIInsight
