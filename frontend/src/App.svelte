<script lang="ts">
  import Map from './lib/Map.svelte';
  import Results from './lib/Results.svelte';

  let latitudeInput: string = '';
  let longitudeInput: string = '';
  let selectedCoords: { lat: number; lon: number } | null = null;
  let isLoading = false;
  let apiResponse: any = null;
  let errorMessage: string | null = null;

  // Variáveis para os limiares configuráveis (com valores padrão)
  let windSpeedThresholdMs: number = 2.8; // Pulverização
  let precipitationProbThreshold: number = 0.1; // Pulverização
  let fungalRiskHumidity: number = 80; // Risco Fúngico
  let fungalRiskTempMin: number = 18; // Risco Fúngico
  let fungalRiskTempMax: number = 26; // Risco Fúngico
  let frostTempThreshold: number = 2; // Geada
  let heatStressTempThreshold: number = 32; // Estresse por Calor
  let plantingTempMin: number = 18; // Plantio
  let plantingTempMax: number = 30; // Plantio
  let plantingRainProbThreshold: number = 0.3; // Plantio
  let harvestRainProbThreshold: number = 0.1; // Colheita
  let harvestHumidityThreshold: number = 70; // Colheita
  let irrigationNoRainThreshold: number = 0.05; // Irrigação
  let irrigationTempThreshold: number = 25; // Irrigação
  let irrigationMinHours: number = 24; // Irrigação
  let minWindowHours: number = 12; // Geral

  // Novo: Perfil de cultura selecionado
  let selectedCropProfile: string = 'default';

  // Novo: Mapeamento de perfis de cultura (deve ser sincronizado com o backend)
  const CROP_PROFILES: { [key: string]: any } = {
    "default": {
        windSpeedThresholdMs: 2.8,
        precipitationProbThreshold: 0.1,
        fungalRiskHumidity: 80,
        fungalRiskTempMin: 18,
        fungalRiskTempMax: 26,
        frostTempThreshold: 2,
        heatStressTempThreshold: 32,
        plantingTempMin: 18,
        plantingTempMax: 30,
        plantingRainProbThreshold: 0.3,
        harvestRainProbThreshold: 0.1,
        harvestHumidityThreshold: 70,
        irrigationNoRainThreshold: 0.05,
        irrigationTempThreshold: 25,
        irrigationMinHours: 24,
        minWindowHours: 12,
    },
    "soja": {
        windSpeedThresholdMs: 3.5,
        precipitationProbThreshold: 0.15,
        fungalRiskHumidity: 75,
        fungalRiskTempMin: 20,
        fungalRiskTempMax: 28,
        frostTempThreshold: 0,
        heatStressTempThreshold: 30,
        plantingTempMin: 20,
        plantingTempMax: 32,
        plantingRainProbThreshold: 0.4,
        harvestRainProbThreshold: 0.05,
        harvestHumidityThreshold: 65,
        irrigationNoRainThreshold: 0.1,
        irrigationTempThreshold: 28,
        irrigationMinHours: 36,
        minWindowHours: 18,
    },
    "milho": {
        windSpeedThresholdMs: 4.0,
        precipitationProbThreshold: 0.2,
        fungalRiskHumidity: 85,
        fungalRiskTempMin: 22,
        fungalRiskTempMax: 30,
        frostTempThreshold: -1,
        heatStressTempThreshold: 35,
        plantingTempMin: 16,
        plantingTempMax: 30,
        plantingRainProbThreshold: 0.3,
        harvestRainProbThreshold: 0.15,
        harvestHumidityThreshold: 75,
        irrigationNoRainThreshold: 0.15,
        irrigationTempThreshold: 26,
        irrigationMinHours: 24,
        minWindowHours: 12,
    },
    "algodao": {
        windSpeedThresholdMs: 3.0,
        precipitationProbThreshold: 0.1,
        fungalRiskHumidity: 70,
        fungalRiskTempMin: 25,
        fungalRiskTempMax: 35,
        frostTempThreshold: 5,
        heatStressTempThreshold: 38,
        plantingTempMin: 20,
        plantingTempMax: 35,
        plantingRainProbThreshold: 0.2,
        harvestRainProbThreshold: 0.05,
        harvestHumidityThreshold: 60,
        irrigationNoRainThreshold: 0.05,
        irrigationTempThreshold: 30,
        irrigationMinHours: 48,
        minWindowHours: 12,
    },
    "arroz": {
        windSpeedThresholdMs: 2.5,
        precipitationProbThreshold: 0.3,
        fungalRiskHumidity: 90,
        fungalRiskTempMin: 20,
        fungalRiskTempMax: 30,
        frostTempThreshold: 0,
        heatStressTempThreshold: 32,
        plantingTempMin: 20,
        plantingTempMax: 30,
        plantingRainProbThreshold: 0.5,
        harvestRainProbThreshold: 0.2,
        harvestHumidityThreshold: 80,
        irrigationNoRainThreshold: 0.05,
        irrigationTempThreshold: 25,
        irrigationMinHours: 24,
        minWindowHours: 12,
    }
  };

  // Função para aplicar o perfil selecionado
  function applyCropProfile() {
    const profile = CROP_PROFILES[selectedCropProfile];
    if (profile) {
      windSpeedThresholdMs = profile.windSpeedThresholdMs;
      precipitationProbThreshold = profile.precipitationProbThreshold;
      fungalRiskHumidity = profile.fungalRiskHumidity;
      fungalRiskTempMin = profile.fungalRiskTempMin;
      fungalRiskTempMax = profile.fungalRiskTempMax;
      frostTempThreshold = profile.frostTempThreshold;
      heatStressTempThreshold = profile.heatStressTempThreshold;
      plantingTempMin = profile.plantingTempMin;
      plantingTempMax = profile.plantingTempMax;
      plantingRainProbThreshold = profile.plantingRainProbThreshold;
      harvestRainProbThreshold = profile.harvestRainProbThreshold;
      harvestHumidityThreshold = profile.harvestHumidityThreshold;
      irrigationNoRainThreshold = profile.irrigationNoRainThreshold;
      irrigationTempThreshold = profile.irrigationTempThreshold;
      irrigationMinHours = profile.irrigationMinHours;
      minWindowHours = profile.minWindowHours;
    }
  }

  // Reage à mudança do perfil selecionado
  $: selectedCropProfile, applyCropProfile();

  const API_URL = 'http://127.0.0.1:8000/insights/';

  function handleLocationSelect(event: CustomEvent) {
    const { lat, lon } = event.detail;
    selectedCoords = { lat, lon };
    latitudeInput = lat.toFixed(6); // Atualiza o input com a lat do mapa
    longitudeInput = lon.toFixed(6); // Atualiza o input com a lon do mapa
  }

  // Reage a mudanças nos inputs de latitude/longitude
  $: {
    const lat = parseFloat(latitudeInput);
    const lon = parseFloat(longitudeInput);
    if (!isNaN(lat) && !isNaN(lon)) {
      selectedCoords = { lat, lon };
    } else {
      selectedCoords = null; // Invalida as coordenadas se os inputs não forem números válidos
    }
  }

  async function handleAnalyzeClick() {
    if (!selectedCoords) {
      alert('Por favor, insira coordenadas válidas ou clique no mapa para selecionar uma localização.');
      return;
    }

    isLoading = true;
    apiResponse = null;
    errorMessage = null;

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: selectedCoords.lat,
          lon: selectedCoords.lon,
          crop_profile: selectedCropProfile === 'default' ? null : selectedCropProfile, // Envia o perfil selecionado
          wind_speed_threshold_ms: windSpeedThresholdMs,
          precipitation_prob_threshold: precipitationProbThreshold,
          fungal_risk_humidity: fungalRiskHumidity,
          fungal_risk_temp_min: fungalRiskTempMin,
          fungal_risk_temp_max: fungalRiskTempMax,
          frost_temp_threshold: frostTempThreshold,
          heat_stress_temp_threshold: heatStressTempThreshold,
          planting_temp_min: plantingTempMin,
          planting_temp_max: plantingTempMax,
          planting_rain_prob_threshold: plantingRainProbThreshold,
          harvest_rain_prob_threshold: harvestRainProbThreshold,
          harvest_humidity_threshold: harvestHumidityThreshold,
          irrigation_no_rain_threshold: irrigationNoRainThreshold,
          irrigation_temp_threshold: irrigationTempThreshold,
          irrigationMinHours: irrigationMinHours,
          min_window_hours: minWindowHours,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ocorreu um erro na API.');
      }

      apiResponse = await response.json();
    } catch (err: any) {
      errorMessage = err.message;
    } finally {
      isLoading = false;
    }
  }
</script>

<main>
  <header>
    <h1>Demeter</h1>
    <p>Inteligência Climática para Decisões Agrícolas</p>
  </header>

  <section>
    <h2>1. Selecione a Localização</h2>
    <div class="input-coords">
      <input type="text" placeholder="Latitude" bind:value={latitudeInput} />
      <input type="text" placeholder="Longitude" bind:value={longitudeInput} />
    </div>
    <p class="or-text">ou clique no mapa:</p>
    <Map on:locationselect={handleLocationSelect} currentLat={selectedCoords?.lat} currentLon={selectedCoords?.lon} />
  </section>

  <section class="config-section">
    <h2>2. Configure os Limiares de Análise</h2>
    <div class="config-item">
      <label for="cropProfile">Perfil da Cultura:</label>
      <select id="cropProfile" bind:value={selectedCropProfile}>
        {#each Object.keys(CROP_PROFILES) as profileName}
          <option value={profileName}>{profileName.charAt(0).toUpperCase() + profileName.slice(1)}</option>
        {/each}
      </select>
    </div>
    <div class="config-grid">
      <div class="config-item">
        <label for="windSpeed">Vento Pulverização (m/s):</label>
        <input type="number" id="windSpeed" bind:value={windSpeedThresholdMs} step="0.1" min="0" max="10">
      </div>
      <div class="config-item">
        <label for="rainProbSpray">Chuva Pulverização (%):</label>
        <input type="number" id="rainProbSpray" bind:value={precipitationProbThreshold} step="0.01" min="0" max="1">
      </div>
      <div class="config-item">
        <label for="fungalHumidity">Umidade Risco Fúngico (%):</label>
        <input type="number" id="fungalHumidity" bind:value={fungalRiskHumidity} step="1" min="0" max="100">
      </div>
      <div class="config-item">
        <label for="fungalTempMin">Temp. Mín. Risco Fúngico (°C):</label>
        <input type="number" id="fungalTempMin" bind:value={fungalRiskTempMin} step="1" min="-10" max="50">
      </div>
      <div class="config-item">
        <label for="fungalTempMax">Temp. Máx. Risco Fúngico (°C):</label>
        <input type="number" id="fungalTempMax" bind:value={fungalRiskTempMax} step="1" min="-10" max="50">
      </div>
      <div class="config-item">
        <label for="frostTemp">Temp. Geada (°C):</label>
        <input type="number" id="frostTemp" bind:value={frostTempThreshold} step="1" min="-20" max="10">
      </div>
      <div class="config-item">
        <label for="heatTemp">Temp. Estresse Calor (°C):</label>
        <input type="number" id="heatTemp" bind:value={heatStressTempThreshold} step="1" min="20" max="60">
      </div>
      <div class="config-item">
        <label for="plantingTempMin">Temp. Mín. Plantio (°C):</label>
        <input type="number" id="plantingTempMin" bind:value={plantingTempMin} step="1" min="0" max="40">
      </div>
      <div class="config-item">
        <label for="plantingTempMax">Temp. Máx. Plantio (°C):</label>
        <input type="number" id="plantingTempMax" bind:value={plantingTempMax} step="1" min="0" max="40">
      </div>
      <div class="config-item">
        <label for="plantingRainProb">Chuva Plantio (%):</label>
        <input type="number" id="plantingRainProb" bind:value={plantingRainProbThreshold} step="0.01" min="0" max="1">
      </div>
      <div class="config-item">
        <label for="harvestRainProb">Chuva Colheita (%):</label>
        <input type="number" id="harvestRainProb" bind:value={harvestRainProbThreshold} step="0.01" min="0" max="1">
      </div>
      <div class="config-item">
        <label for="harvestHumidity">Umidade Colheita (%):</label>
        <input type="number" id="harvestHumidity" bind:value={harvestHumidityThreshold} step="1" min="0" max="100">
      </div>
      <div class="config-item">
        <label for="irrigationNoRain">Chuva Irrigação (%):</label>
        <input type="number" id="irrigationNoRain" bind:value={irrigationNoRainThreshold} step="0.01" min="0" max="1">
      </div>
      <div class="config-item">
        <label for="irrigationTemp">Temp. Irrigação (°C):</label>
        <input type="number" id="irrigationTemp" bind:value={irrigationTempThreshold} step="1" min="0" max="50">
      </div>
      <div class="config-item">
        <label for="irrigationMinHours">Min. Horas Irrigação:</label>
        <input type="number" id="irrigationMinHours" bind:value={irrigationMinHours} step="3" min="0" max="72">
      </div>
      <div class="config-item">
        <label for="minWindowHours">Min. Horas Janela:</label>
        <input type="number" id="minWindowHours" bind:value={minWindowHours} step="3" min="0" max="72">
      </div>
    </div>
  </section>

  <section class="call-to-action">
    <button on:click={handleAnalyzeClick} disabled={!selectedCoords || isLoading}>
      {#if isLoading}
        Analisando...
      {:else}
        Analisar Clima
      {/if}
    </button>
  </section>

  <section class="results-section">
    {#if isLoading}
      <div class="loading-text">Buscando e processando dados...</div>
    {/if}

    {#if errorMessage}
      <div class="error-box">{errorMessage}</div>
    {/if}

    {#if apiResponse}
      <h2>3. Recomendações para os Próximos 5 Dias</h2>
      <Results insights={apiResponse} />
    {/if}
  </section>

  <footer>
    <p>MVP v2 com Svelte e Leaflet.js</p>
  </footer>
</main>

<style>
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background-color: #f0f4f8;
    color: #333;
  }

  main {
    width: 100%;
    max-width: 800px;
    margin: 40px auto;
    padding: 2rem;
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
  }

  header {
    text-align: center;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
  }

  header h1 {
    color: #2c5b2d;
    margin: 0;
    font-weight: 700;
  }

  header p {
    margin: 5px 0 0;
    color: #666;
  }

  section {
    margin-bottom: 2rem;
  }

  h2 {
    color: #333;
    font-weight: 700;
    margin-top: 0;
  }

  .input-coords {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
  }

  .input-coords input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 1rem;
  }

  .or-text {
    text-align: center;
    margin-bottom: 15px;
    color: #666;
  }

  .config-section {
    background-color: #f9f9f9;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
  }

  .config-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
  }

  .config-item {
    display: flex;
    flex-direction: column;
  }

  .config-item label {
    font-size: 0.9rem;
    color: #555;
    margin-bottom: 5px;
  }

  .config-item input[type="number"] {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .call-to-action {
    text-align: center;
  }

  button {
    padding: 15px 30px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.1s ease;
  }

  button:hover:not(:disabled) {
    background-color: #45a049;
  }

  button:active:not(:disabled) {
    transform: scale(0.98);
  }

  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }

  .loading-text {
    text-align: center;
    padding: 2rem;
    font-size: 1.1rem;
    color: #666;
  }

  .error-box {
    text-align: center;
    padding: 1.5rem;
    background-color: #ffebee;
    color: #c62828;
    border: 1px solid #c62828;
    border-radius: 8px;
  }

  footer {
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e0e0e0;
    font-size: 0.9rem;
    color: #999;
  }
</style>
