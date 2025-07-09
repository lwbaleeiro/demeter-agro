from datetime import datetime, timedelta
from typing import List, Dict, Any

# --- Constantes de Análise (valores padrão, serão sobrescritos pela configuração) ---
WIND_SPEED_THRESHOLD_MS = 2.8
PRECIPITATION_PROB_THRESHOLD = 0.1
FUNGAL_RISK_HUMIDITY = 80
FUNGAL_RISK_TEMP_MIN = 18
FUNGAL_RISK_TEMP_MAX = 26
MIN_WINDOW_HOURS = 12
FROST_TEMP_THRESHOLD = 2
HEAT_STRESS_TEMP_THRESHOLD = 32
PLANTING_TEMP_MIN = 18
PLANTING_TEMP_MAX = 30
PLANTING_RAIN_PROB_THRESHOLD = 0.3
HARVEST_RAIN_PROB_THRESHOLD = 0.1
HARVEST_HUMIDITY_THRESHOLD = 70
IRRIGATION_NO_RAIN_THRESHOLD = 0.05
IRRIGATION_TEMP_THRESHOLD = 25
IRRIGATION_MIN_HOURS = 24
GDD_BASE_TEMP = 10 # Temperatura base padrão para GDD

# --- Perfis de Cultura Pré-configurados ---
# Estes valores podem ser ajustados conforme a necessidade de cada cultura
CROP_PROFILES = {
    "default": {
        "wind_speed_threshold_ms": WIND_SPEED_THRESHOLD_MS,
        "precipitation_prob_threshold": PRECIPITATION_PROB_THRESHOLD,
        "fungal_risk_humidity": FUNGAL_RISK_HUMIDITY,
        "fungal_risk_temp_min": FUNGAL_RISK_TEMP_MIN,
        "fungal_risk_temp_max": FUNGAL_RISK_TEMP_MAX,
        "frost_temp_threshold": FROST_TEMP_THRESHOLD,
        "heat_stress_temp_threshold": HEAT_STRESS_TEMP_THRESHOLD,
        "planting_temp_min": PLANTING_TEMP_MIN,
        "planting_temp_max": PLANTING_TEMP_MAX,
        "planting_rain_prob_threshold": PLANTING_RAIN_PROB_THRESHOLD,
        "harvest_rain_prob_threshold": HARVEST_RAIN_PROB_THRESHOLD,
        "harvest_humidity_threshold": HARVEST_HUMIDITY_THRESHOLD,
        "irrigation_no_rain_threshold": IRRIGATION_NO_RAIN_THRESHOLD,
        "irrigation_temp_threshold": IRRIGATION_TEMP_THRESHOLD,
        "irrigation_min_hours": IRRIGATION_MIN_HOURS,
        "min_window_hours": MIN_WINDOW_HOURS,
        "gdd_base_temp": GDD_BASE_TEMP,
    },
    "soja": {
        "wind_speed_threshold_ms": 3.5,  # Soja pode tolerar um pouco mais de vento na pulverização
        "precipitation_prob_threshold": 0.15,
        "fungal_risk_humidity": 75, # Ferrugem asiática é sensível à umidade
        "fungal_risk_temp_min": 20,
        "fungal_risk_temp_max": 28,
        "frost_temp_threshold": 0,   # Mais sensível à geada
        "heat_stress_temp_threshold": 30,
        "planting_temp_min": 20,
        "planting_temp_max": 32,
        "planting_rain_prob_threshold": 0.4,
        "harvest_rain_prob_threshold": 0.05, # Precisa de tempo bem seco para colheita
        "harvest_humidity_threshold": 65,
        "irrigation_no_rain_threshold": 0.1,
        "irrigation_temp_threshold": 28,
        "irrigation_min_hours": 36,
        "min_window_hours": 18,
        "gdd_base_temp": 10, # Exemplo para soja
    },
    "milho": {
        "wind_speed_threshold_ms": 4.0,
        "precipitation_prob_threshold": 0.2,
        "fungal_risk_humidity": 85,
        "fungal_risk_temp_min": 22,
        "fungal_risk_temp_max": 30,
        "frost_temp_threshold": -1,
        "heat_stress_temp_threshold": 35,
        "planting_temp_min": 16,
        "planting_temp_max": 30,
        "planting_rain_prob_threshold": 0.3,
        "harvest_rain_prob_threshold": 0.15,
        "harvest_humidity_threshold": 75,
        "irrigation_no_rain_threshold": 0.15,
        "irrigation_temp_threshold": 26,
        "irrigation_min_hours": 24,
        "min_window_hours": 12,
        "gdd_base_temp": 10, # Exemplo para milho
    },
    "algodao": {
        "wind_speed_threshold_ms": 3.0,
        "precipitation_prob_threshold": 0.1,
        "fungal_risk_humidity": 70,
        "fungal_risk_temp_min": 25,
        "fungal_risk_temp_max": 35,
        "frost_temp_threshold": 5, # Muito sensível ao frio
        "heat_stress_temp_threshold": 38,
        "planting_temp_min": 20,
        "planting_temp_max": 35,
        "planting_rain_prob_threshold": 0.2,
        "harvest_rain_prob_threshold": 0.05,
        "harvest_humidity_threshold": 60, # Precisa de umidade bem baixa para colheita
        "irrigation_no_rain_threshold": 0.05,
        "irrigation_temp_threshold": 30,
        "irrigation_min_hours": 48,
        "min_window_hours": 12,
        "gdd_base_temp": 15, # Exemplo para algodão
    },
    "arroz": {
        "wind_speed_threshold_ms": 2.5,
        "precipitation_prob_threshold": 0.3, # Arroz de sequeiro pode precisar de mais chuva
        "fungal_risk_humidity": 90,
        "fungal_risk_temp_min": 20,
        "fungal_risk_temp_max": 30,
        "frost_temp_threshold": 0,
        "heat_stress_temp_threshold": 32,
        "planting_temp_min": 20,
        "planting_temp_max": 30,
        "planting_rain_prob_threshold": 0.5,
        "harvest_rain_prob_threshold": 0.2,
        "harvest_humidity_threshold": 80,
        "irrigation_no_rain_threshold": 0.05,
        "irrigation_temp_threshold": 25,
        "irrigation_min_hours": 24,
        "min_window_hours": 12,
        "gdd_base_temp": 10, # Exemplo para arroz
    }
}

def mps_to_kmh(mps: float) -> float:
    """Converte metros por segundo para quilômetros por hora."""
    return mps * 3.6

def analyze_forecast(forecast_data: Dict[str, Any], historical_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analisa os dados de previsão do tempo para gerar insights, usando configurações dinâmicas.
    """
    if "list" not in forecast_data:
        return {"error": "Formato de dados de previsão inválido."}

    forecast_list = forecast_data["list"]

    # Carregar perfil da cultura se especificado
    crop_profile_name = config.get("crop_profile")
    if crop_profile_name and crop_profile_name in CROP_PROFILES:
        profile_config = CROP_PROFILES[crop_profile_name]
        # Sobrescrever configurações padrão com as do perfil
        for key, value in profile_config.items():
            # Apenas sobrescreve se o valor não foi explicitamente fornecido na config
            if key not in config or config[key] is None: 
                config[key] = value

    # Usar valores da configuração ou constantes padrão
    wind_speed_threshold_ms = config.get("wind_speed_threshold_ms", WIND_SPEED_THRESHOLD_MS)
    precipitation_prob_threshold = config.get("precipitation_prob_threshold", PRECIPITATION_PROB_THRESHOLD)
    fungal_risk_humidity = config.get("fungal_risk_humidity", FUNGAL_RISK_HUMIDITY)
    fungal_risk_temp_min = config.get("fungal_risk_temp_min", FUNGAL_RISK_TEMP_MIN)
    fungal_risk_temp_max = config.get("fungal_risk_temp_max", FUNGAL_RISK_TEMP_MAX)
    min_window_hours = config.get("min_window_hours", MIN_WINDOW_HOURS)
    frost_temp_threshold = config.get("frost_temp_threshold", FROST_TEMP_THRESHOLD)
    heat_stress_temp_threshold = config.get("heat_stress_temp_threshold", HEAT_STRESS_TEMP_THRESHOLD)
    planting_temp_min = config.get("planting_temp_min", PLANTING_TEMP_MIN)
    planting_temp_max = config.get("planting_temp_max", PLANTING_TEMP_MAX)
    planting_rain_prob_threshold = config.get("planting_rain_prob_threshold", PLANTING_RAIN_PROB_THRESHOLD)
    harvest_rain_prob_threshold = config.get("harvest_rain_prob_threshold", HARVEST_RAIN_PROB_THRESHOLD)
    harvest_humidity_threshold = config.get("harvest_humidity_threshold", HARVEST_HUMIDITY_THRESHOLD)
    irrigation_no_rain_threshold = config.get("irrigation_no_rain_threshold", IRRIGATION_NO_RAIN_THRESHOLD)
    irrigation_temp_threshold = config.get("irrigation_temp_threshold", IRRIGATION_TEMP_THRESHOLD)
    irrigation_min_hours = config.get("irrigation_min_hours", IRRIGATION_MIN_HOURS)
    gdd_base_temp = config.get("gdd_base_temp", GDD_BASE_TEMP)

    spraying_window = find_spraying_window(forecast_list, wind_speed_threshold_ms, precipitation_prob_threshold, min_window_hours)
    fungal_risk = find_fungal_risk_window(forecast_list, fungal_risk_humidity, fungal_risk_temp_min, fungal_risk_temp_max, min_window_hours)
    frost_alert = find_frost_risk(forecast_list, frost_temp_threshold)
    heat_stress_alert = find_heat_stress_risk(forecast_list, heat_stress_temp_threshold)
    planting_window_alert = find_planting_window(forecast_list, planting_temp_min, planting_temp_max, planting_rain_prob_threshold)
    harvesting_window_alert = find_harvesting_window(forecast_list, harvest_rain_prob_threshold, harvest_humidity_threshold, min_window_hours)
    irrigation_recommendation = find_irrigation_recommendation(forecast_list, irrigation_no_rain_threshold, irrigation_temp_threshold, irrigation_min_hours)
    gdd_insight = calculate_gdd(historical_data, gdd_base_temp)
    return {
        "spraying_alert": spraying_window,
        "fungal_risk_alert": fungal_risk,
        "frost_alert": frost_alert,
        "heat_stress_alert": heat_stress_alert,
        "planting_window_alert": planting_window_alert,
        "harvesting_window_alert": harvesting_window_alert,
        "irrigation_recommendation": irrigation_recommendation,
        "gdd_insight": gdd_insight
    }

def find_spraying_window(forecast_list: List[Dict[str, Any]], wind_speed_threshold_ms: float, precipitation_prob_threshold: float, min_window_hours: float) -> Dict[str, Any]:
    """Encontra a melhor janela contínua para pulverização."""
    best_window = []
    current_window = []

    for forecast in forecast_list:
        wind_speed = forecast["wind"]["speed"]
        rain_prob = forecast.get("pop", 0)
        is_raining = any(w["id"] < 600 for w in forecast["weather"])

        if wind_speed < wind_speed_threshold_ms and rain_prob < precipitation_prob_threshold and not is_raining:
            current_window.append(forecast)
        else:
            if len(current_window) * 3 >= min_window_hours:
                best_window = current_window
                break # Encontramos a primeira janela válida, podemos parar
            current_window = []
    
    # Se não encontrou uma janela e a última janela é a melhor
    if not best_window and len(current_window) * 3 >= min_window_hours:
        best_window = current_window

    duration_hours = len(best_window) * 3
    if duration_hours < min_window_hours:
        return {
            "ideal_window_found": False,
            "message": f"Nenhuma janela ideal para pulverização (mín. {min_window_hours}h) encontrada nos próximos 5 dias."
        }

    start_time = datetime.fromtimestamp(best_window[0]["dt"]).strftime('%d/%m %H:%M')
    end_time = (datetime.fromtimestamp(best_window[-1]["dt"]) + timedelta(hours=3)).strftime('%d/%m %H:%M')
    
    avg_wind = mps_to_kmh(sum(f["wind"]["speed"] for f in best_window) / len(best_window))

    return {
        "ideal_window_found": True,
        "message": f"Janela ideal para pulverização de {duration_hours}h encontrada.",
        "start_time": start_time,
        "end_time": end_time,
        "conditions": f"Vento médio de {avg_wind:.1f} km/h e sem previsão de chuva."
    }


def find_fungal_risk_window(forecast_list: List[Dict[str, Any]], fungal_risk_humidity: float, fungal_risk_temp_min: float, fungal_risk_temp_max: float, min_window_hours: float) -> Dict[str, Any]:
    """Analisa o risco fúngico calculando um escore com base na duração e intensidade das condições."""
    total_risk_hours = 0
    risk_score = 0.0

    # A temperatura ótima para a maioria dos fungos está no meio da faixa de risco.
    optimal_temp_midpoint = (fungal_risk_temp_min + fungal_risk_temp_max) / 2
    temp_range = fungal_risk_temp_max - fungal_risk_temp_min

    for forecast in forecast_list:
        humidity = forecast["main"]["humidity"]
        temp = forecast["main"]["temp"]

        if humidity >= fungal_risk_humidity and fungal_risk_temp_min <= temp <= fungal_risk_temp_max:
            total_risk_hours += 3
            
            # Ponderar o escore pela temperatura: mais pontos para temperaturas ótimas.
            # A pontuação é maior quando a temperatura está mais próxima do ponto médio ótimo.
            distance_from_optimal = abs(temp - optimal_temp_midpoint)
            temp_score_factor = 1.0 - (distance_from_optimal / (temp_range / 2))
            
            # Ponderar pela umidade: umidade mais alta aumenta o risco.
            humidity_score_factor = (humidity - fungal_risk_humidity) / (100 - fungal_risk_humidity)
            
            # O escore por período de 3h é uma combinação dos fatores de temp e umidade.
            # O valor 1.5 é um peso para dar mais impacto às horas de risco.
            risk_score += (1 + temp_score_factor + humidity_score_factor) * 1.5

    # Normalizar o escore para uma escala de 0 a 100
    # O máximo de horas é 120 (5 dias * 24h). O escore máximo teórico é ajustado.
    max_possible_score = 120 / 3 * 3.5 # Ajustado para a fórmula acima
    normalized_score = min(100.0, (risk_score / max_possible_score) * 100)

    # Definir níveis de risco com base no escore normalizado
    if normalized_score >= 75:
        risk_level = "Severo"
        message = f"Risco Severo! {total_risk_hours}h de condições favoráveis para fungos. Aja preventivamente."
    elif normalized_score >= 50:
        risk_level = "Alto"
        message = f"Risco Alto! {total_risk_hours}h de condições favoráveis para fungos. Monitore a lavoura."
    elif normalized_score >= 25:
        risk_level = "Moderado"
        message = f"Risco Moderado. {total_risk_hours}h de condições favoráveis para fungos. Fique atento."
    else:
        risk_level = "Baixo"
        message = "Condições de baixo risco para doenças fúngicas nos próximos 5 dias."

    return {
        "risk_level": risk_level,
        "risk_score": round(normalized_score, 2),
        "message": message,
        "total_risk_hours": total_risk_hours,
        "details": f"Análise baseada em umidade > {fungal_risk_humidity}% e temp. entre {fungal_risk_temp_min}°C e {fungal_risk_temp_max}°C."
    }

def find_frost_risk(forecast_list: List[Dict[str, Any]], frost_temp_threshold: float) -> Dict[str, Any]:
    """Verifica o risco de geada nos próximos 5 dias."""
    frost_periods = []
    for forecast in forecast_list:
        temp_min = forecast["main"]["temp_min"]
        if temp_min <= frost_temp_threshold:
            frost_periods.append({
                "time": datetime.fromtimestamp(forecast["dt"]).strftime('%d/%m %H:%M'),
                "temp_min": temp_min
            })
    
    if not frost_periods:
        return {
            "frost_risk_found": False,
            "message": "Baixo risco de geada nos próximos 5 dias."
        }
    else:
        first_frost_time = frost_periods[0]["time"]
        return {
            "frost_risk_found": True,
            "message": f"Atenção! Risco de geada detectado. Temperatura mínima de {frost_periods[0]["temp_min"]}°C prevista para {first_frost_time}.",
            "details": frost_periods
        }

def find_heat_stress_risk(forecast_list: List[Dict[str, Any]], heat_stress_temp_threshold: float) -> Dict[str, Any]:
    """Verifica o risco de estresse por calor nos próximos 5 dias."""
    heat_stress_periods = []
    for forecast in forecast_list:
        temp_max = forecast["main"]["temp_max"]
        if temp_max >= heat_stress_temp_threshold:
            heat_stress_periods.append({
                "time": datetime.fromtimestamp(forecast["dt"]).strftime('%d/%m %H:%M'),
                "temp_max": temp_max
            })
    
    if not heat_stress_periods:
        return {
            "heat_stress_found": False,
            "message": "Baixo risco de estresse por calor nos próximos 5 dias."
        }
    else:
        first_stress_time = heat_stress_periods[0]["time"]
        return {
            "heat_stress_found": True,
            "message": f"Atenção! Risco de estresse por calor detectado. Temperatura máxima de {heat_stress_periods[0]["temp_max"]}°C prevista para {first_stress_time}.",
            "details": heat_stress_periods
        }

def find_planting_window(forecast_list: List[Dict[str, Any]], planting_temp_min: float, planting_temp_max: float, planting_rain_prob_threshold: float) -> Dict[str, Any]:
    """Encontra a melhor janela para plantio/semeadura."""
    ideal_periods = []
    for i, forecast in enumerate(forecast_list):
        temp = forecast["main"]["temp"]
        rain_prob = forecast.get("pop", 0)
        is_raining = any(w["id"] < 600 for w in forecast["weather"])

        # Verifica se a temperatura está na faixa ideal
        temp_ok = planting_temp_min <= temp <= planting_temp_max

        # Verifica se há chuva no período atual ou nos próximos 2 períodos (6 horas)
        rain_ok = False
        for j in range(i, min(i + 2, len(forecast_list))):
            if forecast_list[j].get("pop", 0) >= planting_rain_prob_threshold or any(w["id"] < 600 for w in forecast_list[j]["weather"]):
                rain_ok = True
                break

        if temp_ok and rain_ok:
            ideal_periods.append({
                "time": datetime.fromtimestamp(forecast["dt"]).strftime('%d/%m %H:%M'),
                "temp": temp,
                "rain_prob": rain_prob
            })
    
    if not ideal_periods:
        return {
            "planting_window_found": False,
            "message": "Nenhuma janela ideal para plantio/semeadura encontrada nos próximos 5 dias."
        }
    else:
        first_ideal_time = ideal_periods[0]["time"]
        return {
            "planting_window_found": True,
            "message": f"Janela ideal para plantio/semeadura detectada. Primeiro período ideal começa em {first_ideal_time}.",
            "details": ideal_periods
        }

def find_harvesting_window(forecast_list: List[Dict[str, Any]], harvest_rain_prob_threshold: float, harvest_humidity_threshold: float, min_window_hours: float) -> Dict[str, Any]:
    """Encontra a melhor janela para colheita."""
    ideal_periods = []
    current_window = []

    for forecast in forecast_list:
        rain_prob = forecast.get("pop", 0)
        is_raining = any(w["id"] < 600 for w in forecast["weather"])
        humidity = forecast["main"]["humidity"]
        temp = forecast["main"]["temp"]
        wind_speed = forecast["wind"]["speed"]

        if rain_prob < harvest_rain_prob_threshold and not is_raining and humidity < harvest_humidity_threshold:
            # Adiciona um dicionário formatado para o modelo HarvestingPeriod
            current_window.append({
                "time": datetime.fromtimestamp(forecast["dt"]).strftime('%d/%m %H:%M'),
                "temp": temp,
                "humidity": humidity,
                "wind_speed": wind_speed
            })
        else:
            if len(current_window) * 3 >= min_window_hours:
                ideal_periods.append(current_window)
            current_window = []
    
    if len(current_window) * 3 >= min_window_hours:
        ideal_periods.append(current_window)

    if not ideal_periods:
        return {
            "harvesting_window_found": False,
            "message": "Nenhuma janela ideal para colheita encontrada nos próximos 5 dias."
        }
    else:
        # O details agora é uma lista de listas de HarvestingPeriod
        # O frontend espera uma lista de listas, então a estrutura já está correta
        first_ideal_time = ideal_periods[0][0]["time"]
        total_ideal_hours = sum(len(p) for p in ideal_periods) * 3
        return {
            "harvesting_window_found": True,
            "message": f"Janela ideal para colheita detectada. Total de {total_ideal_hours}h de condições favoráveis. Primeiro período ideal começa em {first_ideal_time}.",
            "details": ideal_periods
        }

def calculate_gdd(historical_data: Dict[str, Any], base_temp: float) -> Dict[str, Any]:
    """Calcula os Graus-Dia (GDD) acumulados com base nos dados históricos."""
    if not historical_data or 'daily' not in historical_data or not all(k in historical_data['daily'] for k in ['time', 'temperature_2m_max', 'temperature_2m_min']):
        return {
            "gdd_calculated": False,
            "message": "Dados históricos insuficientes ou em formato inválido para calcular GDD."
        }

    total_gdd = 0.0
    gdd_details = []

    dates = historical_data['daily']['time']
    temp_max_list = historical_data['daily']['temperature_2m_max']
    temp_min_list = historical_data['daily']['temperature_2m_min']

    for i, date_str in enumerate(dates):
        temp_max = temp_max_list[i]
        temp_min = temp_min_list[i]

        # Fórmula padrão do GDD
        avg_temp = (temp_max + temp_min) / 2
        gdd_value = max(0.0, avg_temp - base_temp)
        total_gdd += gdd_value
        gdd_details.append({"date": date_str, "gdd_value": gdd_value})

    if total_gdd > 0:
        return {
            "gdd_calculated": True,
            "message": f"GDD acumulado nos últimos {len(dates)} dias: {total_gdd:.2f}.",
            "total_gdd": total_gdd,
            "details": gdd_details
        }
    else:
        return {
            "gdd_calculated": False,
            "message": f"Nenhum GDD acumulado nos últimos {len(dates)} dias (Temp. Base: {base_temp}°C)."
        }



def find_irrigation_recommendation(forecast_list: List[Dict[str, Any]], irrigation_no_rain_threshold: float, irrigation_temp_threshold: float, irrigation_min_hours: float) -> Dict[str, Any]:
    """Verifica a necessidade de irrigação nos próximos 5 dias."""
    irrigation_needed_periods = []
    current_dry_hot_window = []

    for forecast in forecast_list:
        rain_prob = forecast.get("pop", 0)
        is_raining = any(w["id"] < 600 for w in forecast["weather"])
        temp = forecast["main"]["temp"]

        # Condições para possível necessidade de irrigação: sem chuva e quente
        if rain_prob < irrigation_no_rain_threshold and not is_raining and temp >= irrigation_temp_threshold:
            current_dry_hot_window.append({
                "time": datetime.fromtimestamp(forecast["dt"]).strftime('%d/%m %H:%M'),
                "temp": temp,
                "rain_prob": rain_prob
            })
        else:
            if len(current_dry_hot_window) * 3 >= irrigation_min_hours:
                irrigation_needed_periods.append(current_dry_hot_window)
            current_dry_hot_window = []
    
    if len(current_dry_hot_window) * 3 >= irrigation_min_hours:
        irrigation_needed_periods.append(current_dry_hot_window)

    if not irrigation_needed_periods:
        return {
            "irrigation_recommended": False,
            "message": "Baixa necessidade de irrigação nos próximos 5 dias."
        }
    else:
        first_period_time = irrigation_needed_periods[0][0]["time"]
        total_hours = sum(len(p) for p in irrigation_needed_periods) * 3
        return {
            "irrigation_recommended": True,
            "message": f"Atenção! Irrigação pode ser necessária. {total_hours}h de condições secas e quentes. Primeiro período começa em {first_period_time}.",
            "details": irrigation_needed_periods
        }
