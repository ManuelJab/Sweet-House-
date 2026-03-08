/**
 * Buscador de dirección con mapa - Nominatim + Leaflet
 * El cliente busca o selecciona en el mapa y la dirección se llena automáticamente.
 */
function initAddressMap() {
  const addressInput = document.getElementById('id_address_map');
  const latInput = document.getElementById('id_address_lat');
  const lngInput = document.getElementById('id_address_lng');
  const mapContainer = document.getElementById('address-map-container');
  const searchInput = document.getElementById('address-search-input');
  const searchBtn = document.getElementById('address-search-btn');
  const resultsList = document.getElementById('address-search-results');

  if (!mapContainer || !searchInput || !searchBtn) return;

  // Centro por defecto: Cartagena, Colombia
  const defaultLat = 10.39972;
  const defaultLng = -75.51444;

  let map = null;
  let marker = null;

  // Inicializar mapa Leaflet (el contenedor debe estar visible para calcular dimensiones)
  function initMap() {
    if (typeof L === 'undefined') return;

    map = L.map('address-map').setView([defaultLat, defaultLng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap'
    }).addTo(map);

    // Forzar recálculo de dimensiones tras renderizado
    setTimeout(function () {
      if (map) map.invalidateSize();
    }, 100);

    map.on('click', function (e) {
      const { lat, lng } = e.latlng;
      setLocation(lat, lng);
      reverseGeocode(lat, lng);
    });
  }

  function setMarker(lat, lng) {
    if (!map) return;
    if (marker) map.removeLayer(marker);
    marker = L.marker([lat, lng]).addTo(map);
    map.setView([lat, lng], 16);
  }

  function setLocation(lat, lng) {
    if (latInput) latInput.value = lat;
    if (lngInput) lngInput.value = lng;
    setMarker(lat, lng);
  }

  function setAddress(addr) {
    const inp = document.getElementById('id_address_map');
    if (inp) inp.value = addr;
  }

  // Búsqueda con Nominatim
  function searchAddress(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    const q = searchInput.value.trim();
    if (!q || q.length < 2) {
      showResults([], 'Escribe al menos 2 caracteres para buscar.');
      return;
    }

    searchBtn.disabled = true;
    searchBtn.innerHTML = '<span>Buscando...</span>';

    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&addressdetails=1&limit=5&countrycodes=co`;
    fetch(url, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Accept': 'application/json',
        'Accept-Language': 'es',
        'User-Agent': 'StimanDessert/1.0 (pedidos@stimandessert.com)'
      }
    })
      .then(r => r.json())
      .then(data => {
        showResults(data);
      })
      .catch(function (err) {
        showResults([], 'Error al buscar. Intenta de nuevo.');
      })
      .finally(() => {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="bi bi-search"></i> Buscar';
      });
  }

  function showResults(results, emptyMessage) {
    if (!resultsList) return;
    resultsList.innerHTML = '';
    resultsList.style.display = 'block';

    if (!results || results.length === 0) {
      resultsList.innerHTML = '<div class="address-result-empty">' + (emptyMessage || 'No se encontraron resultados. Intenta con otra dirección.') + '</div>';
      return;
    }

    results.forEach(r => {
      const item = document.createElement('button');
      item.type = 'button';
      item.className = 'address-result-item';
      item.textContent = r.display_name;
      item.addEventListener('click', () => {
        const lat = parseFloat(r.lat);
        const lng = parseFloat(r.lon);
        setLocation(lat, lng);
        setAddress(r.display_name);
        resultsList.innerHTML = '';
        resultsList.style.display = 'none';
      });
      resultsList.appendChild(item);
    });
  }

  // Reverse geocode: coordenadas → dirección
  function reverseGeocode(lat, lng) {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`;
    fetch(url, {
      headers: {
        'Accept-Language': 'es',
        'User-Agent': 'StimanDessert/1.0 (pedidos@stimandessert.com)'
      }
    })
      .then(r => r.json())
      .then(data => {
        const addr = data.display_name || `${lat}, ${lng}`;
        setAddress(addr);
      })
      .catch(() => setAddress(`${lat}, ${lng}`));
  }

  // Eventos
  searchBtn.addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    searchAddress(e);
  });
  if (searchInput) {
    searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        searchAddress();
      }
    });
  }

  // Cargar Leaflet y luego inicializar
  function loadLeaflet(cb) {
    if (typeof L !== 'undefined') {
      cb();
      return;
    }
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    link.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    link.crossOrigin = '';
    document.head.appendChild(link);

    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    script.crossOrigin = '';
    script.onload = cb;
    document.body.appendChild(script);
  }

  // Mostrar contenedor PRIMERO para que tenga dimensiones, luego iniciar mapa
  const toggleMapBtn = document.getElementById('toggle-map-btn');
  mapContainer.classList.add('open');
  if (toggleMapBtn) toggleMapBtn.innerHTML = '<i class="bi bi-map-fill"></i> Ocultar mapa';

  if (toggleMapBtn) {
    toggleMapBtn.addEventListener('click', () => {
      mapContainer.classList.toggle('open');
      toggleMapBtn.innerHTML = mapContainer.classList.contains('open')
        ? '<i class="bi bi-map-fill"></i> Ocultar mapa'
        : '<i class="bi bi-map-fill"></i> Ver mapa para seleccionar ubicación';
      if (map && mapContainer.classList.contains('open')) {
        setTimeout(function () { map.invalidateSize(); }, 150);
      }
    });
  }

  loadLeaflet(() => {
    requestAnimationFrame(() => {
      initMap();
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAddressMap);
} else {
  initAddressMap();
}
