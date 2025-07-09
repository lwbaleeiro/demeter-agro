<script lang="ts">
    export let insights: any; // The full API response
    export let satelliteAnalysisStatus: 'idle' | 'processing' | 'completed' | 'failed';
    export let satelliteAnalysisResult: any; // O resultado final da análise de satélite

    function getCardClass(alert: any, type: 'spraying' | 'fungal' | 'frost' | 'heat_stress' | 'planting_window' | 'harvesting_window' | 'irrigation_recommendation' | 'gdd_insight' | 'satellite') {
        if (type === 'spraying') {
            return alert.ideal_window_found ? 'positive' : 'negative';
        }
        if (type === 'fungal') {
            const level = alert.risk_level.toLowerCase();
            if (level === 'baixo') return 'positive';
            if (level === 'moderado') return 'warning';
            if (level === 'alto') return 'negative';
            if (level === 'severo') return 'severe';
            return '';
        }
        if (type === 'frost') {
            return !alert.frost_risk_found ? 'positive' : 'negative';
        }
        if (type === 'heat_stress') {
            return !alert.heat_stress_found ? 'positive' : 'negative';
        }
        if (type === 'planting_window') {
            return alert.planting_window_found ? 'positive' : 'negative';
        }
        if (type === 'harvesting_window') {
            return alert.harvesting_window_found ? 'positive' : 'negative';
        }
        if (type === 'irrigation_recommendation') {
            return !alert.irrigation_recommended ? 'positive' : 'negative';
        }
        if (type === 'gdd_insight') {
            return 'info'; // GDD is informational
        }
        if (type === 'satellite') {
            if (satelliteAnalysisStatus === 'processing') return 'info';
            if (satelliteAnalysisStatus === 'completed') {
                if (insights.ndvi_insight) {
                    const level = insights.ndvi_insight.level;
                    if (level === 'success') return 'positive';
                    if (level === 'warning') return 'warning';
                    if (level === 'danger') return 'negative';
                }
                return 'info'; // Default if ndvi_insight is not yet available
            }
            if (satelliteAnalysisStatus === 'failed') return 'negative';
            return '';
        }
        return '';
    }

    function getRiskColor(score: number): string {
        if (score < 25) return '#4CAF50'; // Verde
        if (score < 50) return '#FFC107'; // Amarelo
        if (score < 75) return '#FF9800'; // Laranja
        return '#F44336'; // Vermelho
    }

    function formatIrrigationDetails(details: any[]) {
        if (!details || details.length === 0) return '';
        let formatted = '';
        details.forEach((window, index) => {
            const start = window[0].time;
            const end = window[window.length - 1].time;
            const duration = window.length * 3;
            formatted += `<li>${start} a ${end} (${duration}h) - Temp: ${window[0].temp}°C, Chuva: ${(window[0].rain_prob * 100).toFixed(0)}%</li>`;
        });
        return formatted;
    }
</script>

{#if insights}
    <div class="insights-grid">
        <!-- Satellite Analysis Card (Featured) -->
        <div class="insight-card satellite-card {getCardClass(insights.satellite_analysis, 'satellite')}">
            <h3>Análise de Satélite (NDVI)</h3>
            {#if satelliteAnalysisStatus === 'processing'}
                <div class="loading-spinner small"></div>
                <p>Processando imagem de satélite...</p>
            {:else if satelliteAnalysisStatus === 'completed' && satelliteAnalysisResult && satelliteAnalysisResult.available}
                <div class="satellite-content">
                    <div class="satellite-image-container">
                        <img src={satelliteAnalysisResult.image_url} alt="Imagem de Satélite da Área" class="satellite-image"/>
                    </div>
                    <div class="satellite-details">
                        <p class="ndvi-value">NDVI: {satelliteAnalysisResult.ndvi_value?.toFixed(4)}</p>
                        <p>{insights.ndvi_insight?.message}
                            {#if insights.ndvi_insight?.explanation_text}
                                <span class="info-icon" title={insights.ndvi_insight.explanation_text}>&#9432;</span>
                            {/if}
                        </p>
                    </div>
                </div>
            {:else if satelliteAnalysisStatus === 'failed'}
                <p class="error-message">Erro ao carregar análise de satélite. Tente novamente.</p>
            {:else}
                <p>Análise de satélite não disponível ou não iniciada.</p>
            {/if}
        </div>

        <!-- GDD Insight Card (Featured) -->
        {#if insights.gdd_insight && insights.gdd_insight.gdd_calculated}
            <div class="insight-card gdd-card {getCardClass(insights.gdd_insight, 'gdd_insight')}">
                <h3>Graus-Dia Acumulados (GDD)</h3>
                <p>{insights.gdd_insight.message}</p>
                <div class="gdd-total">
                    {insights.gdd_insight.total_gdd?.toFixed(2)}
                </div>
                <p class="details">GDD é uma medida do acúmulo de calor, essencial para prever estágios de desenvolvimento da cultura.</p>
                <p class="details"><strong>Detalhes por dia:</strong></p>
                <ul>
                    {#each insights.gdd_insight.details as period}
                        <li>{new Date(period.date + 'T00:00:00').toLocaleDateString('pt-BR', {day: '2-digit', month: '2-digit'})}: <strong>{period.gdd_value?.toFixed(2)} GDD</strong></li>
                    {/each}
                </ul>
            </div>
        {/if}

        <!-- Fungal Risk Card -->
        <div class="insight-card {getCardClass(insights.fungal_risk_alert, 'fungal')}">
            <h3>Risco Fúngico: <span class="risk-level">{insights.fungal_risk_alert.risk_level}</span></h3>
            <div class="risk-bar-container">
                <div 
                    class="risk-bar"
                    style="width: {insights.fungal_risk_alert.risk_score}%; background-color: {getRiskColor(insights.fungal_risk_alert.risk_score)};"
                ></div>
            </div>
            <p>{insights.fungal_risk_alert.message}</p>
            <p class="details">{insights.fungal_risk_alert.details}</p>
        </div>

        <!-- Spraying Alert Card -->
        <div class="insight-card {getCardClass(insights.spraying_alert, 'spraying')}">
            <h3>Alerta de Pulverização</h3>
            <p>{insights.spraying_alert.message}</p>
            {#if insights.spraying_alert.ideal_window_found}
                <p class="details"><strong>Início:</strong> {insights.spraying_alert.start_time}</p>
                <p class="details"><strong>Fim:</strong> {insights.spraying_alert.end_time}</p>
                <p class="details"><strong>Condições:</strong> {insights.spraying_alert.conditions}</p>
            {/if}
        </div>

        <!-- Frost Alert Card -->
        <div class="insight-card {getCardClass(insights.frost_alert, 'frost')}">
            <h3>Alerta de Geada</h3>
            <p>{insights.frost_alert.message}</p>
            {#if insights.frost_alert.frost_risk_found && insights.frost_alert.details}
                <p class="details">Períodos de risco:</p>
                <ul>
                    {#each insights.frost_alert.details as period}
                        <li>{period.time}: {period.temp_min}°C</li>
                    {/each}
                </ul>
            {/if}
        </div>

        <!-- Heat Stress Alert Card -->
        <div class="insight-card {getCardClass(insights.heat_stress_alert, 'heat_stress')}">
            <h3>Alerta de Estresse por Calor</h3>
            <p>{insights.heat_stress_alert.message}</p>
            {#if insights.heat_stress_alert.heat_stress_found && insights.heat_stress_alert.details}
                <p class="details">Períodos de risco:</p>
                <ul>
                    {#each insights.heat_stress_alert.details as period}
                        <li>{period.time}: {period.temp_max}°C</li>
                    {/each}
                </ul>
            {/if}
        </div>

        <!-- Planting Window Alert Card -->
        <div class="insight-card {getCardClass(insights.planting_window_alert, 'planting_window')}">
            <h3>Janela de Plantio/Semeadura</h3>
            <p>{insights.planting_window_alert.message}</p>
            {#if insights.planting_window_alert.planting_window_found && insights.planting_window_alert.details}
                <p class="details">Períodos ideais:</p>
                <ul>
                    {#each insights.planting_window_alert.details as period}
                        <li>{period.time}: {period.temp}°C, Chuva: {(period.rain_prob * 100).toFixed(0)}%</li>
                    {/each}
                </ul>
            {/if}
        </div>

        <!-- Harvesting Window Alert Card -->
        <div class="insight-card {getCardClass(insights.harvesting_window_alert, 'harvesting_window')}">
            <h3>Janela de Colheita</h3>
            <p>{insights.harvesting_window_alert.message}</p>
            {#if insights.harvesting_window_alert.harvesting_window_found && insights.harvesting_window_alert.details}
                <p class="details">Períodos ideais:</p>
                <ul>
                    {#each insights.harvesting_window_alert.details as window_period}
                        <li>{window_period[0].time} a {window_period[window_period.length - 1].time} ({window_period.length * 3}h)</li>
                    {/each}
                </ul>
            {/if}
        </div>

        <!-- Irrigation Recommendation Card -->
        <div class="insight-card {getCardClass(insights.irrigation_recommendation, 'irrigation_recommendation')}">
            <h3>Recomendação de Irrigação</h3>
            <p>{insights.irrigation_recommendation.message}</p>
            {#if insights.irrigation_recommendation.irrigation_recommended && insights.irrigation_recommendation.details}
                <p class="details">Períodos de possível necessidade:</p>
                <ul>
                    {@html formatIrrigationDetails(insights.irrigation_recommendation.details)}
                </ul>
            {/if}
        </div>
    </div>
{/if}

<style>
    .insights-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }

    .insight-card {
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
    }

    .insight-card.positive { background-color: #e8f5e9; border-left: 5px solid #4CAF50; }
    .insight-card.warning { background-color: #fffde7; border-left: 5px solid #FFC107; }
    .insight-card.negative { background-color: #fff3e0; border-left: 5px solid #FF9800; }
    .insight-card.severe { background-color: #ffebee; border-left: 5px solid #F44336; }
    .insight-card.info { background-color: #e3f2fd; border-left: 5px solid #2196F3; }

    .gdd-card, .satellite-card {
        grid-column: 1 / -1; 
    }

    .satellite-content {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }

    .satellite-image-container {
        flex: 1;
        max-width: 40%;
    }

    .satellite-image {
        width: 100%;
        height: auto;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .satellite-details {
        flex: 1.5;
    }

    .ndvi-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2196F3;
    }

    .gdd-total {
        font-size: 3rem;
        font-weight: 700;
        color: #2196F3;
        margin: 1rem 0;
    }

    .insight-card h3 {
        margin-top: 0;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .risk-level {
        font-weight: 700;
    }

    .risk-bar-container {
        width: 100%;
        height: 10px;
        background-color: #e0e0e0;
        border-radius: 5px;
        margin-bottom: 1rem;
        overflow: hidden;
    }

    .risk-bar {
        height: 100%;
        border-radius: 5px;
        transition: width 0.5s ease-out;
    }

    .insight-card p {
        margin-bottom: 0.5rem;
    }

    .details {
        font-size: 0.9rem;
        opacity: 0.8;
    }

    .info-icon {
        cursor: help;
        margin-left: 5px;
        color: #2196F3; /* Material Blue */
        font-weight: bold;
    }

    ul {
        list-style-type: none;
        padding: 0;
        margin-top: 0.5rem;
    }

    li {
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }

    @media (max-width: 768px) {
        .satellite-content {
            flex-direction: column;
        }
        .satellite-image-container {
            max-width: 100%;
        }
    }
</style>
