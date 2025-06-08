// Obtiene la URL correcta del servidor (localhost o IP de la LAN)
function getServerURL() {
    return `http://${window.location.hostname}:8000`;
  }
  
  async function connect() {
    const res = await fetch(getServerURL() + '/api/connect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    if (data.status === 'ok') {
      document.getElementById('status').innerHTML = 'Estado: <span class="green">Conectado</span>';
    } else {
      alert(data.msg);
    }
  }
  
  async function disconnect() {
    const res = await fetch(getServerURL() + '/api/disconnect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    await res.json();
    document.getElementById('status').innerHTML = 'Estado: <span class="red">Desconectado</span>';
  }
  
  // Botones aún inactivos hasta que definamos sus rutas
  
  document.getElementById('btnUpload').addEventListener('click', () => {
    const file = document.getElementById('uploadFile').files[0];
    if (!file) return;
    // Aquí irá el fetch de /api/command con cmd: 'upload'
  });
  
  document.getElementById('btnDelete').addEventListener('click', () => {
    const name = document.getElementById('deleteName').value.trim();
    if (!name) return;
    // Aquí irá el fetch de /api/command con cmd: 'delete', name
  });
  
  document.getElementById('btnDownload').addEventListener('click', () => {
    const name = document.getElementById('downloadName').value.trim();
    if (!name) return;
    // Aquí irá el fetch de /api/command con cmd: 'download', name
  });
  
  document.getElementById('btnList').addEventListener('click', () => {
    // Siempre activo, envía cmd: 'list'
    // Aquí irá el fetch de /api/command con cmd: 'list'
  });