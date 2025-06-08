// Obtiene la URL correcta del servidor
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

// Helper base64→Blob (igual)
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

// REFRESCAR LISTA de PDFs en metadata.json
async function refreshFileList() {
  const ul = document.getElementById('fileList');
  ul.innerHTML = '';  // limpiar lista
  const res = await fetch(getServerURL() + '/api/command', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ cmd:'list' })
  });
  const json = await res.json();
  if (json.status==='ok' && Array.isArray(json.files)) {
    json.files.forEach(name => {
      const li = document.createElement('li');
      li.textContent = name;
      li.onclick = () => {
        document.getElementById('downloadName').value = name;
      };
      ul.appendChild(li);
    });
    if (json.files.length===0) {
      const li = document.createElement('li');
      li.textContent = '(no hay archivos aún)';
      ul.appendChild(li);
    }
  } else {
    alert(json.msg || 'No se pudo listar PDFs');
  }
}

// SUBIR PDF (igual)
document.getElementById('btnUpload').addEventListener('click', () => {
  const fileInput = document.getElementById('uploadFile');
  const file = fileInput.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async () => {
    const base64Data = reader.result.split(',')[1];
    const payload = { cmd:'upload', name:file.name, data:base64Data };
    const res = await fetch(getServerURL() + '/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    alert(json.msg || 'Subida completada');
  };
  reader.readAsDataURL(file);
});

// ELIMINAR PDF (igual)
document.getElementById('btnDelete').addEventListener('click', async () => {
  const name = document.getElementById('deleteName').value.trim();
  if (!name) return;
  const res = await fetch(getServerURL() + '/api/command', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ cmd:'delete', name })
  });
  const json = await res.json();
  alert(json.msg || 'Eliminación completada');
});

// LISTAR PDF → sólo al pulsar el botón
document.getElementById('btnList').addEventListener('click', refreshFileList);

// DESCARGAR PDF → usando el campo de texto
document.getElementById('btnDownload').addEventListener('click', async () => {
  const name = document.getElementById('downloadName').value.trim();
  if (!name) return alert('Escriba el nombre exacto del PDF');
  const res = await fetch(getServerURL() + '/api/command', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ cmd:'download', name })
  });
  const json = await res.json();
  if (json.status==='ok' && json.data) {
    const blob = b64toBlob(json.data, 'application/pdf');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } else {
    alert(json.msg || 'Error al descargar');
  }
});
