<script lang="ts">
    export let insights: any; // The full API response

    function getCardClass(alert: any, type: 'spraying' | 'fungal' | 'frost' | 'heat_stress' | 'planting_window' | 'harvesting_window' | 'irrigation_recommendation' | 'gdd_insight') {
        if (type === 'spraying') {
            return alert.ideal_window_found ? 'positive' : 'negative';
        }
        if (type === 'fungal') {
            return !alert.risk_found ? 'positive' : 'negative';
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
            return alert.gdd_calculated ? 'positive' : 'negative'; // GDD calculado é sempre positivo
        }
        return '';
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

        <!-- Fungal Risk Card -->
        <div class="insight-card {getCardClass(insights.fungal_risk_alert, 'fungal')}">
            <h3>Risco Fúngico</h3>
            <p>{insights.fungal_risk_alert.message}</p>
            {#if insights.fungal_risk_alert.risk_found}
                <p class="details">{insights.fungal_risk_alert.details}</p>
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

        <!-- GDD Insight Card -->
        <div class="insight-card {getCardClass(insights.gdd_insight, 'gdd_insight')}">
            <h3>Graus-Dia (GDD)</h3>
            <p>{insights.gdd_insight.message}</p>
            {#if insights.gdd_insight.gdd_calculated}
                <p class="details">GDD Acumulado (5 dias): {insights.gdd_insight.total_gdd?.toFixed(2)}</p>
                <p class="details">Detalhes por período:</p>
                <ul>
                    {#each insights.gdd_insight.details as period}
                        <li>{period.date}: {period.gdd_value?.toFixed(2)} GDD</li>
                    {/each}
                </ul>
            {/if}
        </div>
    </div>
{/if}

<style>
    .insights-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-top: 2rem;
    }

    .insight-card {
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid;
    }

    .insight-card.positive {
        background-color: #e8f5e9;
        border-color: #4CAF50;
    }

    .insight-card.negative {
        background-color: #fff3e0;
        border-color: #ff9800;
    }

    .insight-card h3 {
        margin-top: 0;
        font-size: 1.2rem;
    }

    .insight-card p {
        margin-bottom: 5px;
    }

    .details {
        font-size: 0.9rem;
        opacity: 0.8;
    }

    ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }

    li {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-bottom: 3px;
    }

    @media (max-width: 700px) {
        .insights-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
