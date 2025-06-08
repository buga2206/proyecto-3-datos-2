// Obtiene la URL correcta del servidor (localhost o IP de la LAN)
function getServerURL() {
  return `http://${window.location.hostname}:8000`;
}

// Conectar / Desconectar
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
  await fetch(getServerURL() + '/api/disconnect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  document.getElementById('status').innerHTML = 'Estado: <span class="red">Desconectado</span>';
}

// Helper: convierte base64 a Blob
function b64toBlob(b64Data, contentType = '', sliceSize = 512) {
  const byteCharacters = atob(b64Data);
  const byteArrays = [];
  for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    const slice = byteCharacters.slice(offset, offset + sliceSize);
    const byteNumbers = new Array(slice.length);
    for (let i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }
    byteArrays.push(new Uint8Array(byteNumbers));
  }
  return new Blob(byteArrays, { type: contentType });
}

// Subir PDF
document.getElementById('btnUpload').addEventListener('click', () => {
  const fileInput = document.getElementById('uploadFile');
  const file = fileInput.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async () => {
    const base64Data = reader.result.split(',')[1];
    const payload = {
      cmd: 'upload',
      name: file.name,
      data: base64Data
    };
    const res = await fetch(getServerURL() + '/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    alert(json.msg || 'Subida completada');
  };
  reader.readAsDataURL(file);
});

// Eliminar PDF
document.getElementById('btnDelete').addEventListener('click', async () => {
  const name = document.getElementById('deleteName').value.trim();
  if (!name) return;

  const res = await fetch(getServerURL() + '/api/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cmd: 'delete', name })
  });
  const json = await res.json();
  alert(json.msg || 'Eliminación completada');
});

// Descargar PDF
document.getElementById('btnDownload').addEventListener('click', async () => {
  const name = document.getElementById('downloadName').value.trim();
  if (!name) return;

  const res = await fetch(getServerURL() + '/api/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cmd: 'download', name })
  });
  const json = await res.json();
  if (json.status === 'ok' && json.data) {
    const blob = b64toBlob(json.data, 'application/pdf');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } else {
    alert(json.msg || 'Error al descargar');
  }
});

// Listar PDFs
document.getElementById('btnList').addEventListener('click', async () => {
  const res = await fetch(getServerURL() + '/api/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cmd: 'list' })
  });
  const json = await res.json();
  if (json.status === 'ok' && Array.isArray(json.files)) {
    alert('Archivos PDF:\n' + json.files.join('\n'));
  } else {
    alert(json.msg || 'No se pudo listar');
  }
});
