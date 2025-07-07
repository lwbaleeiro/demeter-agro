<script lang="ts">
    import { onMount, createEventDispatcher, afterUpdate } from 'svelte';
    import 'leaflet/dist/leaflet.css';
    import L from 'leaflet';

    // Props para receber as coordenadas do componente pai
    export let currentLat: number | null = null;
    export let currentLon: number | null = null;

    // Leaflet's default icon path is broken in Vite, so we fix it manually.
    import iconUrl from 'leaflet/dist/images/marker-icon.png';
    import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
    import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

    const dispatch = createEventDispatcher();

    let mapContainer: HTMLElement;
    let map: L.Map;
    let marker: L.Marker | null = null;

    onMount(() => {
        // Fix for default marker icon
        const DefaultIcon = L.icon({
            iconUrl,
            iconRetinaUrl,
            shadowUrl,
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            tooltipAnchor: [16, -28],
            shadowSize: [41, 41]
        });
        L.Marker.prototype.options.icon = DefaultIcon;

        // Initialize the map, centered on a sample location in Brazil
        map = L.map(mapContainer).setView([-14.235, -51.925], 4);

        // Add the OpenStreetMap tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Handle map clicks
        map.on('click', (e: L.LeafletMouseEvent) => {
            const { lat, lng } = e.latlng;
            if (marker) {
                marker.setLatLng(e.latlng);
            } else {
                marker = L.marker(e.latlng).addTo(map);
            }
            // Dispatch an event with the selected coordinates
            dispatch('locationselect', { lat, lon: lng });
        });

        // Se já houver coordenadas iniciais, adicione o marcador e centralize
        if (currentLat !== null && currentLon !== null) {
            const initialLatLng = L.latLng(currentLat, currentLon);
            marker = L.marker(initialLatLng).addTo(map);
            map.setView(initialLatLng, 10); // Zoom maior para a localização específica
        }

        return () => {
            map.remove();
        };
    });

    // Reage a mudanças nas props currentLat/currentLon
    afterUpdate(() => {
        if (map && currentLat !== null && currentLon !== null) {
            const newLatLng = L.latLng(currentLat, currentLon);
            if (marker) {
                marker.setLatLng(newLatLng);
            } else {
                marker = L.marker(newLatLng).addTo(map);
            }
            // Apenas move o mapa se a nova localização estiver fora da visualização atual
            if (!map.getBounds().contains(newLatLng)) {
                map.setView(newLatLng, map.getZoom() || 10);
            }
        }
    });
</script>

<div class="map-container" bind:this={mapContainer}></div>

<style>
    .map-container {
        height: 400px;
        width: 100%;
        border-radius: 8px;
        margin-top: 1rem;
    }
</style>
