<script lang="ts">
  import Map from './lib/Map.svelte';
  import Results from './lib/Results.svelte';
  import { jsPDF } from 'jspdf';

  let latitudeInput: string = '';
  let longitudeInput: string = '';
  let selectedCoords: { lat: number; lon: number } | null = null;
  let isLoading = false;
  let apiResponse: any = null;
  let errorMessage: string | null = null;
  let lastAnalysisParams: { lat: string; lon: string; profile: string } | null = null;
  let isSameAsLastAnalysis = false;

  // Variáveis para o polling da análise de satélite
  let satelliteAnalysisTaskId: string | null = null;
  let satelliteAnalysisStatus: 'idle' | 'processing' | 'completed' | 'failed' = 'idle';
  let satelliteAnalysisResult: any = null;
  let pollingInterval: any = null;

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

  let selectedCropProfile: string = 'livre';

  function handleCoordinateInput(event: Event) {
    const input = event.target as HTMLInputElement;
    // Permite apenas números, um ponto decimal e um sinal de negativo no início.
    input.value = input.value.replace(/[^-0-9.]/g, '')
                               .replace(/(\..*)\./g, '$1')
                               .replace(/(?!^)-/g, '');
  }

  // Novo: Mapeamento de perfis de cultura (deve ser sincronizado com o backend)
  const CROP_PROFILES: { [key: string]: any } = {
    "livre": {
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
        harvestRainProbThreshold: 0.05,
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

  const API_BASE_URL = 'http://127.0.0.1:8000';

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

    // Verifica se os parâmetros atuais são os mesmos da última análise
    if (lastAnalysisParams) {
      isSameAsLastAnalysis = 
        latitudeInput === lastAnalysisParams.lat &&
        longitudeInput === lastAnalysisParams.lon &&
        selectedCropProfile === lastAnalysisParams.profile;
    } else {
      isSameAsLastAnalysis = false;
    }
  }

  async function handlePrintReport() {
    if (!apiResponse) {
      alert('Nenhum dado de análise para imprimir.');
      return;
    }

    const doc = new jsPDF();
    const bottomMargin = 20;
    const pageHeight = doc.internal.pageSize.getHeight();

    // Função para carregar imagem e converter para Base64
    const loadImageAsBase64 = (url: string) => {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = 'Anonymous';
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx!.drawImage(img, 0, 0);
                resolve(canvas.toDataURL('image/jpeg'));
            };
            img.onerror = (err) => reject(err);
            img.src = url;
        });
    };

    doc.setFontSize(18);
    doc.text('Relatório de Análise Climática', 14, 22);

    doc.setFontSize(12);
    doc.text(`Localização: Latitude ${selectedCoords?.lat.toFixed(6)}, Longitude ${selectedCoords?.lon.toFixed(6)}`, 14, 32);
    doc.text(`Perfil da Cultura: ${selectedCropProfile.charAt(0).toUpperCase() + selectedCropProfile.slice(1)}`, 14, 39);

    let y = 50;

    const addText = (text: string, x: number, y: number, maxWidth: number) => {
      const splitText = doc.splitTextToSize(text, maxWidth);
      doc.text(splitText, x, y);
      return y + (splitText.length * doc.getLineHeight() / doc.internal.scaleFactor);
    };

    // 1. Análise de Satélite (NDVI)
    if (apiResponse.satellite_analysis && apiResponse.satellite_analysis.image_url) {
        doc.setFontSize(14);
        doc.text('1. Análise de Satélite (NDVI)', 14, y);
        y += 7;

        try {
            const imageDataUrl = await loadImageAsBase64(apiResponse.satellite_analysis.image_url);
            doc.addImage(imageDataUrl, 'JPEG', 14, y, 80, 80); // Adiciona a imagem
            y += 85; // Espaço para a imagem
        } catch (e) {
            console.error("Erro ao carregar imagem para o PDF:", e);
            doc.setFontSize(10);
            y = addText('Não foi possível carregar a imagem de satélite.', 14, y, 180);
        }

        doc.setFontSize(10);
        if (apiResponse.ndvi_insight && apiResponse.ndvi_insight.ndvi_value) {
            y = addText(`NDVI: ${apiResponse.ndvi_insight.ndvi_value.toFixed(4)}`, 14, y, 180);
        }
        y = addText(apiResponse.ndvi_insight.message, 14, y, 180);
        y += 10;
    }

    // 2. Graus-Dia (GDD)
    if (apiResponse.gdd_insight) {
        doc.setFontSize(14);
        doc.text('2. Graus-Dia Acumulados (GDD)', 14, y);
        y += 7;
        doc.setFontSize(10);
        y = addText(apiResponse.gdd_insight.message, 14, y, 180);
        if (apiResponse.gdd_insight.gdd_calculated) {
            y = addText(`GDD Acumulado (5 dias): ${apiResponse.gdd_insight.total_gdd?.toFixed(2)}`, 18, y, 180);
        }
        y += 10;
    }

    // 3. Alerta de Pulverização
    doc.setFontSize(14);
    doc.text('3. Alerta de Pulverização', 14, y);
    y += 7;
    doc.setFontSize(10);
    y = addText(apiResponse.spraying_alert.message, 14, y, 180);
    if (apiResponse.spraying_alert.ideal_window_found) {
      y = addText(`Início: ${apiResponse.spraying_alert.start_time}`, 18, y, 180);
      y = addText(`Fim: ${apiResponse.spraying_alert.end_time}`, 18, y, 180);
      y = addText(`Condições: ${apiResponse.spraying_alert.conditions}`, 18, y, 180);
    }
    y += 10;

    // 4. Risco Fúngico
    doc.setFontSize(14);
    doc.text('4. Risco Fúngico', 14, y);
    y += 7;
    doc.setFontSize(10);
    y = addText(apiResponse.fungal_risk_alert.message, 14, y, 180);
    if (apiResponse.fungal_risk_alert.risk_found && apiResponse.fungal_risk_alert.details) {
      y = addText(`Detalhes: ${apiResponse.fungal_risk_alert.details}`, 18, y, 180);
    }
    y += 10;

    // Adicionar nova página se necessário
    if (y > pageHeight - bottomMargin) {
      doc.addPage();
      y = 20;
    }

    // 5. Alerta de Geada
    doc.setFontSize(14);
    doc.text('5. Alerta de Geada', 14, y);
    y += 7;
    doc.setFontSize(10);
    y = addText(apiResponse.frost_alert.message, 14, y, 180);
    if (apiResponse.frost_alert.frost_risk_found && apiResponse.frost_alert.details) {
      y = addText('Períodos de risco:', 18, y, 180);
      apiResponse.frost_alert.details.forEach((period: any) => {
        y = addText(`- ${period.time}: ${period.temp_min}°C`, 22, y, 180);
      });
    }
    y += 10;

    // Necessário adicionar nova página
    doc.addPage();
    y = 20;

    // 6. Estresse por Calor
    doc.setFontSize(14);
    doc.text('6. Estresse por Calor', 14, y);
    y += 7;
    doc.setFontSize(10);
    y = addText(apiResponse.heat_stress_alert.message, 14, y, 180);
    if (apiResponse.heat_stress_alert.heat_stress_found && apiResponse.heat_stress_alert.details) {
      y = addText('Períodos de risco:', 18, y, 180);
      apiResponse.heat_stress_alert.details.forEach((period: any) => {
        y = addText(`- ${period.time}: ${period.temp_max}°C`, 22, y, 180);
      });
    }
    y += 10;

    // // Adicionar nova página se necessário
    // if (y > pageHeight - bottomMargin) {
    //   doc.addPage();
    //   y = 20;
    // }

    // 7. Janela de Plantio/Semeadura
    doc.setFontSize(14);
    doc.text('7. Janela de Plantio/Semeadura', 14, y);
    y += 7;
    doc.setFontSize(10);
    y = addText(apiResponse.planting_window_alert.message, 14, y, 180);
    if (apiResponse.planting_window_alert.planting_window_found && apiResponse.planting_window_alert.details) {
      y = addText('Períodos ideais:', 18, y, 180);
      apiResponse.planting_window_alert.details.forEach((period: any) => {
        y = addText(`- ${period.time}: ${period.temp}°C, Chuva: ${(period.rain_prob * 100).toFixed(0)}%`, 22, y, 180);
      });
    }
    y += 10;

    // 8. Janela de Colheita
    doc.setFontSize(14);
    doc.text('8. Janela de Colheita', 14, y);
    y += 7;
    doc.setFontSize(10);
    y = addText(apiResponse.harvesting_window_alert.message, 14, y, 180);
    if (apiResponse.harvesting_window_alert.harvesting_window_found && apiResponse.harvesting_window_alert.details) {
      y = addText('Períodos ideais:', 18, y, 180);
      apiResponse.harvesting_window_alert.details.forEach((window_period: any) => {
        y = addText(`- ${window_period[0].time} a ${window_period[window_period.length - 1].time} (${window_period.length * 3}h)`, 22, y, 180);
      });
    }
    y += 10;

    // Adicionar nova página se necessário
    if (y > pageHeight - bottomMargin) {
      doc.addPage();
      y = 20;
    }

    // 9. Recomendação de Irrigação
    doc.setFontSize(14);
    doc.text('9. Recomendação de Irrigação', 14, y);
    y += 7;
    doc.setFontSize(10);
    y = addText(apiResponse.irrigation_recommendation.message, 14, y, 180);
    if (apiResponse.irrigation_recommendation.irrigation_recommended && apiResponse.irrigation_recommendation.details) {
      y = addText('Períodos de possível necessidade:', 18, y, 180);
      apiResponse.irrigation_recommendation.details.forEach((window: any) => {
        y = addText(`- ${window[0].time} a ${window[window.length - 1].time} (${window.length * 3}h) - Temp: ${window[0].temp}°C, Chuva: ${(window[0].rain_prob * 100).toFixed(0)}%`, 22, y, 180);
      });
    }
    y += 10;

    // Adicionar rodapé em todas as páginas ANTES de salvar
    const pageCount = doc.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150);
      doc.text(
        'Smart Agro Clima - Inteligência Climática para o Agro',
        doc.internal.pageSize.getWidth() / 2,
        doc.internal.pageSize.getHeight() - 12,
        { align: 'center' }
      );
    }

    doc.save('relatorio_smart_agro_clima.pdf');
  }

  async function handleAnalyzeClick() {
    if (!selectedCoords) {
      alert('Por favor, insira coordenadas válidas ou clique no mapa para selecionar uma localização.');
      return;
    }

    isLoading = true;
    apiResponse = null;
    errorMessage = null;
    satelliteAnalysisStatus = 'idle';
    satelliteAnalysisResult = null;
    satelliteAnalysisTaskId = null;
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/insights/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: selectedCoords.lat,
          lon: selectedCoords.lon,
          crop_profile: selectedCropProfile === 'livre' ? null : selectedCropProfile,
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

      // Armazena os parâmetros da última análise bem-sucedida para evitar repetições
      lastAnalysisParams = {
        lat: latitudeInput,
        lon: longitudeInput,
        profile: selectedCropProfile,
      };

      // Inicia o polling para a análise de satélite se um task_id for retornado
      if (apiResponse.satellite_analysis && apiResponse.satellite_analysis.task_id) {
        satelliteAnalysisTaskId = apiResponse.satellite_analysis.task_id;
        satelliteAnalysisStatus = 'processing';
        pollingInterval = setInterval(pollSatelliteAnalysis, 3000); // Polling a cada 3 segundos
      } else {
        satelliteAnalysisStatus = 'completed'; // Não há tarefa de satélite, considera como concluído
        satelliteAnalysisResult = apiResponse.satellite_analysis; // Usa o resultado inicial (simulado)
      }

    } catch (err: any) {
      errorMessage = err.message;
      satelliteAnalysisStatus = 'failed';
    } finally {
      isLoading = false;
    }
  }

  function generateNdviInsight(satelliteData: any) {
    const ndvi_value = satelliteData?.ndvi_value;

    if (ndvi_value === null || ndvi_value === undefined) {
        return { message: "Análise de satélite em processamento...", level: "info" };
    }

    let message = "";
    let level = "info";

    if (ndvi_value >= 0.7) {
        message = "NDVI muito alto. Indica vegetação extremamente vigorosa e saudável. Excelente!";
        level = "success";
    } else if (ndvi_value >= 0.5) {
        message = "NDVI alto. Indica vegetação saudável e bom desenvolvimento da cultura.";
        level = "success";
    } else if (ndvi_value >= 0.3) {
        message = "NDVI moderado. A vegetação está presente, mas pode indicar estresse leve ou fase inicial de desenvolvimento.";
        level = "warning";
    } else if (ndvi_value >= 0.1) {
        message = "NDVI baixo. Sugere vegetação esparsa, estresse significativo ou solo exposto. Requer investigação.";
        level = "danger";
    } else {
        message = "NDVI muito baixo ou negativo. Indica ausência de vegetação ou áreas com problemas graves. Urge investigação.";
        level = "danger";
    }

    return {
        message: message,
        level: level,
        ndvi_value: ndvi_value,
        explanation_text: "O Índice de Vegetação por Diferença Normalizada (NDVI) é um indicador gráfico que pode ser usado para analisar imagens de satélite e avaliar se a área contém vegetação verde e em que estágio de saúde ela se encontra. Valores de NDVI variam de -1 a +1. Valores mais altos (próximos de +1) indicam vegetação densa e saudável, enquanto valores mais baixos (próximos de -1 ou 0) podem indicar solo exposto, água ou vegetação estressada/morta."
    };
  }

  async function pollSatelliteAnalysis() {
    if (!satelliteAnalysisTaskId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/satellite/result/${satelliteAnalysisTaskId}`);
      
      if (response.status === 202) {
        // Análise ainda em processamento
        console.log("Análise de satélite ainda em processamento...");
        return;
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao obter resultado da análise de satélite.');
      }

      // Análise concluída com sucesso
      const fetchedSatelliteResult = await response.json();
      satelliteAnalysisResult = fetchedSatelliteResult;
      satelliteAnalysisStatus = 'completed';
      clearInterval(pollingInterval);
      pollingInterval = null;

      // Gera o novo insight do NDVI com base nos resultados do satélite
      const newNdviInsight = generateNdviInsight(fetchedSatelliteResult);

      // Atualiza o apiResponse principal com os resultados reais
      apiResponse = {
        ...apiResponse,
        satellite_analysis: fetchedSatelliteResult, // Substitui toda a chave
        ndvi_insight: newNdviInsight, // Substitui o insight antigo pelo novo
      };

    } catch (err: any) {
      console.error("Erro no polling da análise de satélite:", err);
      satelliteAnalysisStatus = 'failed';
      errorMessage = `Erro na análise de satélite: ${err.message}`;
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  }

  // --- Variáveis e Funções para o Feedback ---
  let showFeedbackModal = false;
  let feedbackName = '';
  let feedbackEmail = '';
  let feedbackMessage = '';
  let statusMessage = '';

  async function handleFeedbackSubmit() {
    statusMessage = 'Enviando...';
    try {
      const response = await fetch(`${API_BASE_URL}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          name: feedbackName,
          email: feedbackEmail,
          message: feedbackMessage 
        }),
      });

      if (response.ok) {
        statusMessage = 'Obrigado pelo seu feedback!';
        setTimeout(() => {
          showFeedbackModal = false;
          feedbackName = '';
          feedbackEmail = '';
          feedbackMessage = '';
          statusMessage = '';
        }, 2000);
      } else {
        const error = await response.json();
        statusMessage = `Erro: ${error.detail || 'Não foi possível enviar.'}`;
      }
    } catch (error) {
      statusMessage = 'Erro de conexão. Tente novamente.';
    }
  }
</script>

<div class="app-container">
  <div class="hero-section">
    <div class="hero-content">
      <h1 class="hero-title">SmartAgroClima</h1>
      <p class="hero-subtitle">Inteligência Climática para Decisões Agrícolas</p>
    </div>
  </div>

  <div class="main-content">
    <div class="content-wrapper">
      <!-- Seção de Localização -->
      <div class="section-card">
        <div class="section-header">
          <h2>Selecione a Localização</h2>
          <p>Insira as coordenadas ou clique no mapa para selecionar</p>
        </div>
        
        <div class="location-inputs">
          <div class="input-group">
            <input 
              type="text" 
              placeholder="Latitude" 
              bind:value={latitudeInput}
              on:input={handleCoordinateInput}
              class="location-input"
            />
            <input 
              type="text" 
              placeholder="Longitude" 
              bind:value={longitudeInput}
              on:input={handleCoordinateInput}
              class="location-input"
            />
          </div>
        </div>

        <div class="map-container">
          <Map 
            on:locationselect={handleLocationSelect} 
            currentLat={selectedCoords?.lat} 
            currentLon={selectedCoords?.lon} 
          />
        </div>
      </div>

      <!-- Seção de Configuração -->
      <div class="section-card">
        <div class="section-header">
          <h2>Configure os Parâmetros</h2>
          <p>Ajuste os limiares de análise para sua cultura</p>
        </div>

        <div class="config-content">
          <div class="crop-profile-section">
            <label for="cropProfile" class="profile-label">Perfil da Cultura:</label>
            <select id="cropProfile" bind:value={selectedCropProfile} class="profile-select">
              {#each Object.keys(CROP_PROFILES) as profileName}
                <option value={profileName}>
                  {profileName.charAt(0).toUpperCase() + profileName.slice(1)}
                </option>
              {/each}
            </select>
          </div>

          <div class="config-grid">
            <div class="config-item">
              <label for="windSpeedThresholdMs">Vento Pulverização (m/s)</label>
              <input 
                id="windSpeedThresholdMs"
                type="number" 
                bind:value={windSpeedThresholdMs} 
                step="0.1" 
                min="0" 
                max="10"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="precipitationProbThreshold">Chuva Pulverização (%)</label>
              <input 
                id="precipitationProbThreshold"
                type="number" 
                bind:value={precipitationProbThreshold} 
                step="0.01" 
                min="0" 
                max="1"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="fungalRiskHumidity">Umidade Risco Fúngico (%)</label>
              <input 
                id="fungalRiskHumidity"
                type="number" 
                bind:value={fungalRiskHumidity} 
                step="1" 
                min="0" 
                max="100"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="fungalRiskTempMin">Temp. Mín. Risco Fúngico (°C)</label>
              <input 
                id="fungalRiskTempMin"
                type="number" 
                bind:value={fungalRiskTempMin} 
                step="1" 
                min="-10" 
                max="50"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="fungalRiskTempMax">Temp. Máx. Risco Fúngico (°C)</label>
              <input 
                id="fungalRiskTempMax"
                type="number" 
                bind:value={fungalRiskTempMax} 
                step="1" 
                min="-10" 
                max="50"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="frostTempThreshold">Temp. Geada (°C)</label>
              <input 
                id="frostTempThreshold"
                type="number" 
                bind:value={frostTempThreshold} 
                step="1" 
                min="-20" 
                max="10"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="heatStressTempThreshold">Temp. Estresse Calor (°C)</label>
              <input 
                id="heatStressTempThreshold"
                type="number" 
                bind:value={heatStressTempThreshold} 
                step="1" 
                min="20" 
                max="60"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="plantingTempMin">Temp. Mín. Plantio (°C)</label>
              <input 
                id="plantingTempMin"
                type="number" 
                bind:value={plantingTempMin} 
                step="1" 
                min="0" 
                max="40"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="plantingTempMax">Temp. Máx. Plantio (°C)</label>
              <input 
                id="plantingTempMax"
                type="number" 
                bind:value={plantingTempMax} 
                step="1" 
                min="0" 
                max="40"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="plantingRainProbThreshold">Chuva Plantio (%)</label>
              <input 
                id="plantingRainProbThreshold"
                type="number" 
                bind:value={plantingRainProbThreshold} 
                step="0.01" 
                min="0" 
                max="1"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="harvestRainProbThreshold">Chuva Colheita (%)</label>
              <input 
                id="harvestRainProbThreshold"
                type="number" 
                bind:value={harvestRainProbThreshold} 
                step="0.01" 
                min="0" 
                max="1"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="harvestHumidityThreshold">Umidade Colheita (%)</label>
              <input 
                id="harvestHumidityThreshold"
                type="number" 
                bind:value={harvestHumidityThreshold} 
                step="1" 
                min="0" 
                max="100"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="irrigationNoRainThreshold">Chuva Irrigação (%)</label>
              <input 
                id="irrigationNoRainThreshold"
                type="number" 
                bind:value={irrigationNoRainThreshold} 
                step="0.01" 
                min="0" 
                max="1"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="irrigationTempThreshold">Temp. Irrigação (°C)</label>
              <input 
                id="irrigationTempThreshold"
                type="number" 
                bind:value={irrigationTempThreshold} 
                step="1" 
                min="0" 
                max="50"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="irrigationMinHours">Min. Horas Irrigação</label>
              <input 
                id="irrigationMinHours"
                type="number" 
                bind:value={irrigationMinHours} 
                step="3" 
                min="0" 
                max="72"
                class="config-input"
              />
            </div>

            <div class="config-item">
              <label for="minWindowHours">Min. Horas Janela</label>
              <input 
                id="minWindowHours"
                type="number" 
                bind:value={minWindowHours} 
                step="3" 
                min="0" 
                max="72"
                class="config-input"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Seção de Ação -->
      <div class="action-section">
        <button 
          on:click={handleAnalyzeClick} 
          disabled={!selectedCoords || isLoading || isSameAsLastAnalysis}
          class="analyze-button"
          title={isSameAsLastAnalysis ? 'Altere os parâmetros para uma nova análise' : 'Analisar Clima'}
        >
          {#if isLoading}
            <span class="loading-spinner"></span>
            Analisando...
          {:else}
            Analisar Clima
          {/if}
        </button>

        {#if apiResponse}
          <button 
            on:click={handlePrintReport} 
            class="print-button"
            disabled={satelliteAnalysisStatus !== 'completed' && satelliteAnalysisStatus !== 'failed'}
            title={satelliteAnalysisStatus === 'processing' ? 'Aguarde a conclusão da análise de satélite' : 'Gerar Relatório em PDF'}
          >
            Gerar Relatório PDF
          </button>
        {/if}
      </div>

      <!-- Seção de Resultados -->
      {#if isLoading}
        <div class="loading-section">
          <div class="loading-spinner large"></div>
          <p>Processando dados climáticos...</p>
        </div>
      {/if}

      {#if errorMessage}
        <div class="error-section">
          <div class="error-icon">⚠️</div>
          <p>{errorMessage}</p>
        </div>
      {/if}

      {#if apiResponse}
        <div class="results-section">
          <div class="section-header">
            <h2>Recomendações para os Próximos 5 Dias</h2>
            <p>Análise detalhada das condições climáticas</p>
          </div>
          <Results 
            insights={apiResponse} 
            satelliteAnalysisStatus={satelliteAnalysisStatus}
            satelliteAnalysisResult={satelliteAnalysisResult}
          />
        </div>
      {/if}
    </div>
  </div>

  <footer class="app-footer">
    <div class="footer-content">
      <p>Smart Agro Clima - Inteligência Climática para o Agro</p>
    </div>
  </footer>

  <!-- Botão de Feedback Flutuante -->
  <button class="feedback-button" on:click={() => showFeedbackModal = true}>
    Feedback
  </button>

  {#if showFeedbackModal}
    <div
      class="modal-backdrop"
      on:click={() => showFeedbackModal = false}
      on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') showFeedbackModal = false; }}
      role="button"
      tabindex="0"
    >
      <div class="modal-content" on:click|stopPropagation role="dialog" aria-modal="true">
        <h2>Deixe seu Feedback</h2>
        <p>Encontrou um problema ou tem uma sugestão? Nos avise!</p>
        <form on:submit|preventDefault={handleFeedbackSubmit}>
          <input
            type="text"
            bind:value={feedbackName}
            placeholder="Seu nome (opcional)"
            class="feedback-input"
          />
          <input
            type="email"
            bind:value={feedbackEmail}
            placeholder="Seu e-mail (opcional)"
            class="feedback-input"
          />
          <textarea
            bind:value={feedbackMessage}
            rows="5"
            placeholder="Sua mensagem aqui..."
            required
          ></textarea>
          <div class="modal-actions">
            <button type="button" on:click={() => showFeedbackModal = false}>Cancelar</button>
            <button type="submit">Enviar</button>
          </div>
        </form>
        {#if statusMessage}
          <p class="status-message">{statusMessage}</p>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  /* Estilos gerais e do container */
  .app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    font-family: 'Arial', sans-serif;
    background-color: #f0f2f5;
  }

  .hero-section {
    background: linear-gradient(to right, #4CAF50, #8BC34A);
    color: white;
    padding: 40px 20px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .hero-title {
    font-size: 3em;
    margin-bottom: 10px;
  }

  .hero-subtitle {
    font-size: 1.2em;
    opacity: 0.9;
  }

  .main-content {
    flex-grow: 1;
    padding: 20px;
    display: flex;
    justify-content: center;
  }

  .content-wrapper {
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 100%;
    max-width: 1200px;
  }

  .section-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
  }

  .section-header {
    margin-bottom: 20px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
  }

  .section-header h2 {
    font-size: 1.8em;
    color: #333;
    margin-bottom: 5px;
  }

  .section-header p {
    color: #666;
    font-size: 0.9em;
  }

  .location-inputs {
    margin-bottom: 20px;
  }

  .input-group {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
  }

  .location-input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1em;
  }

  .map-container {
    height: 400px;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #ddd;
  }

  .config-content {
    margin-top: 10px;
  }

  .crop-profile-section {
    margin-bottom: 20px;
  }

  .profile-label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
    color: #555;
  }

  .profile-select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #fff;
    font-size: 1em;
  }

  .config-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
  }

  .config-item label {
    display: block;
    margin-bottom: 5px;
    font-size: 0.9em;
    color: #666;
  }

  .config-input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9em;
  }

  .action-section {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 20px;
    margin-bottom: 20px;
  }

  .analyze-button, .print-button {
    background-color: #28a745;
    color: white;
    padding: 12px 25px;
    border: none;
    border-radius: 5px;
    font-size: 1.1em;
    cursor: pointer;
    transition: background-color 0.3s ease;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .analyze-button:hover:not(:disabled), .print-button:hover:not(:disabled) {
    background-color: #218838;
  }

  .analyze-button:disabled, .print-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }

  .loading-spinner {
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid #fff;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
  }

  .loading-spinner.large {
    width: 40px;
    height: 40px;
    border-width: 6px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .loading-section, .error-section {
    text-align: center;
    padding: 20px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
  }

  .error-section {
    color: #dc3545;
    background-color: #f8d7da;
    border-color: #f5c6cb;
  }

  .error-icon {
    font-size: 2em;
    margin-bottom: 10px;
  }

  .results-section {
    margin-top: 20px;
  }

  .app-footer {
    background-color: #333;
    color: white;
    text-align: center;
    padding: 20px;
    margin-top: 20px;
  }

  .footer-content p {
    margin: 5px 0;
    font-size: 0.9em;
    opacity: 0.8;
  }

  /* Botão de Feedback Flutuante */
  .feedback-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 50px;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    z-index: 1000;
  }

  /* Estilos do Modal */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1001;
  }

  .modal-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  }

  .feedback-input {
    width: 100%;
    padding: 10px;
    margin-bottom: 10px; /* Adicionado para espaçamento entre os inputs */
    border-radius: 4px;
    border: 1px solid #ccc;
  }

  textarea {
    width: 100%;
    padding: 10px;
    margin-top: 0px; /* Ajustado para não ter margem superior extra */
    border-radius: 4px;
    border: 1px solid #ccc;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
  }
  
  .status-message {
    margin-top: 15px;
    color: #333;
  }
</style>
