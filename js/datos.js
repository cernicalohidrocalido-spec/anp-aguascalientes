// Carga y utilidades compartidas para el sitio de ANP Aguascalientes

async function cargarANPs() {
  const res = await fetch('data/anps.json');
  return res.json();
}

async function cargarGeoJSON() {
  const res = await fetch('data/anp_poligonos.geojson');
  return res.json();
}

function nivelBadgeClass(nivel) {
  const n = (nivel || '').toLowerCase();
  if (n.includes('federal')) return 'badge-federal';
  if (n.includes('estatal')) return 'badge-estatal';
  if (n.includes('municipal')) return 'badge-municipal';
  return 'badge-todo';
}

function esTodo(valor) {
  return typeof valor === 'string' && valor.trim().toUpperCase().startsWith('TODO');
}

function formatoHectareas(ha) {
  if (ha === null || ha === undefined) return '—';
  return ha.toLocaleString('es-MX', { maximumFractionDigits: 2 }) + ' ha';
}

function agregarCapasBase(map, colapsado) {
  const calles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
  });
  const satelite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community',
    maxZoom: 19
  });
  calles.addTo(map);
  L.control.layers({ 'Calles': calles, 'Satélite': satelite }, null, { position: 'topright', collapsed: !!colapsado }).addTo(map);
}

function nombreDoc(clave) {
  const nombres = {
    decreto: 'Decreto',
    decreto_federal: 'Decreto federal',
    programa_manejo: 'Programa de manejo',
    certificacion: 'Certificación',
    recategorizacion: 'Recategorización',
    decretos_abril_2021: 'Decretos abril 2021',
    decreto_federal_cadnr043: 'Decreto federal CADNR 043',
  };
  return nombres[clave] || clave;
}
