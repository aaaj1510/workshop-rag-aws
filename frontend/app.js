// Configuración - WORKSHOP RAG
const CONFIG = {
    // 🔄 PASO 5.2: CAMBIAR ESTA URL POR LA DE TU API GATEWAY
    // Copiar desde: CloudFormation → Outputs → QueryEndpoint
    QUERY_ENDPOINT: 'https://abc123.execute-api.us-east-1.amazonaws.com/prod/query',
    UPLOAD_BUCKET: 'rag-workshop-{tu-nombre}-docs-{account-id}'
};

// NOTA: Este workshop usa simulación para demostrar conceptos RAG
// En producción, conectarías con endpoints reales de AWS

// Estado de la aplicación
let documentsUploaded = false;

// Elementos del DOM
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const messages = document.getElementById('messages');
const queryInput = document.getElementById('queryInput');
const sendBtn = document.getElementById('sendBtn');

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    showStatus('Sube un documento para comenzar', 'info');
});

function setupEventListeners() {
    // Upload area drag & drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // File input
    fileInput.addEventListener('change', handleFileSelect);
    
    // Chat
    sendBtn.addEventListener('click', sendQuery);
    queryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !sendBtn.disabled) {
            sendQuery();
        }
    });
}

// Manejo de drag & drop
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// Procesar archivo
function handleFile(file) {
    // Aceptar tanto PDF como TXT para el workshop
    if (file.type !== 'application/pdf' && file.type !== 'text/plain' && !file.name.endsWith('.txt')) {
        showStatus('Por favor selecciona un archivo PDF o TXT', 'error');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        showStatus('El archivo es demasiado grande. Máximo 10MB', 'error');
        return;
    }
    
    uploadFile(file);
}

// Subir archivo (simulado para el workshop)
async function uploadFile(file) {
    showStatus('Subiendo y procesando documento...', 'info');
    
    try {
        // Simular upload y procesamiento
        await simulateUpload(file);
        
        documentsUploaded = true;
        queryInput.disabled = false;
        sendBtn.disabled = false;
        
        showStatus(`✅ Documento "${file.name}" procesado exitosamente`, 'success');
        addMessage('assistant', `Perfecto! He procesado tu documento "${file.name}". Ahora puedes hacerme preguntas sobre su contenido.`);
        
    } catch (error) {
        showStatus(`Error procesando documento: ${error.message}`, 'error');
    }
}

// Simular upload para el workshop
function simulateUpload(file) {
    return new Promise((resolve) => {
        // Simular tiempo de procesamiento
        setTimeout(() => {
            resolve();
        }, 2000);
    });
}



// Simular consulta RAG para el workshop
async function simulateQuery(query) {
    // Simular tiempo de procesamiento
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Respuestas simuladas basadas en palabras clave
    const responses = {
        'vacaciones': 'Según el documento, los empleados tienen derecho a 15 días hábiles de vacaciones anuales, que pueden tomarse previa solicitud con 30 días de anticipación.',
        'beneficios': 'Los beneficios incluyen: seguro médico completo, seguro dental, plan de pensiones con contribución del 5% del salario, y descuentos en productos de la empresa.',
        'política': 'Las políticas de la empresa están diseñadas para crear un ambiente de trabajo inclusivo y productivo. Incluyen códigos de conducta, procedimientos de recursos humanos y protocolos de seguridad.',
        'horario': 'El horario laboral estándar es de lunes a viernes de 9:00 AM a 6:00 PM, con flexibilidad para trabajo remoto hasta 2 días por semana.',
        'capacitación': 'La empresa ofrece un presupuesto anual de $2,000 por empleado para capacitación y desarrollo profesional, incluyendo cursos, certificaciones y conferencias.',
        'remoto': 'Sí, puedes trabajar desde casa. Según las políticas: trabajo remoto hasta 2 días por semana previa aprobación del supervisor. También hay flexibilidad de horario de ±2 horas con aprobación y trabajo híbrido disponible para roles elegibles.',
        'casa': 'Sí, puedes trabajar desde casa. Según las políticas: trabajo remoto hasta 2 días por semana previa aprobación del supervisor. También hay flexibilidad de horario de ±2 horas con aprobación y trabajo híbrido disponible para roles elegibles.',
        'trabajo': 'El horario estándar es de lunes a viernes, 9:00 AM - 6:00 PM. Trabajo remoto: hasta 2 días por semana previa aprobación del supervisor. Flexibilidad de horario: ±2 horas con aprobación. Trabajo híbrido disponible para roles elegibles.'
    };
    
    // Buscar respuesta basada en palabras clave
    const queryLower = query.toLowerCase();
    for (const [keyword, response] of Object.entries(responses)) {
        if (queryLower.includes(keyword)) {
            return response;
        }
    }
    
    // Respuesta genérica
    return `He analizado tu consulta "${query}". Basándome en el documento procesado, puedo ayudarte con información específica. ¿Podrías ser más específico sobre qué aspecto te interesa conocer?`;
}

// Agregar mensaje al chat
function addMessage(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = content;
    
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Mostrar estado
function showStatus(message, type) {
    uploadStatus.innerHTML = `<div class="status ${type}">${message}</div>`;
    
    // Auto-hide después de 5 segundos para mensajes de éxito
    if (type === 'success') {
        setTimeout(() => {
            uploadStatus.innerHTML = '';
        }, 5000);
    }
}

// Función para conectar con Lambda Function URL
async function realQuery(query) {
    const response = await fetch(CONFIG.QUERY_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
    });
    
    if (!response.ok) {
        throw new Error('Error en la consulta');
    }
    
    const data = await response.json();
    return data.response;
}

// Enviar consulta - MODO REAL CON FALLBACK
async function sendQuery() {
    const query = queryInput.value.trim();
    if (!query) return;
    
    addMessage('user', query);
    queryInput.value = '';
    sendBtn.disabled = true;
    
    try {
        // INTENTAR API REAL PRIMERO
        if (CONFIG.QUERY_ENDPOINT.includes('execute-api')) {
            const response = await realQuery(query);
            addMessage('assistant', response);
        } else {
            // FALLBACK A SIMULACIÓN
            const response = await simulateQuery(query);
            addMessage('assistant', response);
        }
        
    } catch (error) {
        console.error('Error details:', error);
        // FALLBACK A SIMULACIÓN SI FALLA API
        try {
            const response = await simulateQuery(query);
            addMessage('assistant', `[Modo simulación] ${response}`);
        } catch (simError) {
            addMessage('assistant', `Error: ${error.message}`);
        }
    } finally {
        sendBtn.disabled = false;
    }
}