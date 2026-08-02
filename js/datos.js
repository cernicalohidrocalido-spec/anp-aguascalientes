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
