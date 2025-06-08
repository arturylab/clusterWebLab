// ===============================
// VIEWER SETUP (LEFT SECTION)
// ===============================
const radius = 0.1;
const scale = 0.5;

const element = document.querySelector('#left-section');
const config = { backgroundColor: 0xf8fafc };
const viewer = $3Dmol.createViewer(element, config);

// Notification system management
const notificationsContainer = document.getElementById('viewer-notifications');
let notificationCounter = 0;

function showNotification(message, type = 'info', duration = 5000) {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.id = `notification-${++notificationCounter}`;
    
    // Crear el contenido de la notificación con botón de cierre
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-message">${message}</div>
            <button class="notification-close" aria-label="Cerrar notificación">
                ×
            </button>
        </div>
    `;
    
    // Agregar al contenedor
    notificationsContainer.appendChild(notification);
    
    // Mostrar con animación
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto-remove después del duration (guardar el timeoutId para poder cancelarlo)
    const timeoutId = setTimeout(() => {
        removeNotification(notification.id);
    }, duration);
    
    // Guardar el timeoutId en el elemento para poder cancelarlo si se cierra manualmente
    notification.timeoutId = timeoutId;
    
    // Agregar event listener para cerrar al hacer clic en toda la notificación
    notification.addEventListener('click', () => {
        removeNotification(notification.id);
    });
    
    // Limitar el número de notificaciones visibles (máximo 3)
    const notifications = notificationsContainer.querySelectorAll('.notification');
    if (notifications.length > 3) {
        removeNotification(notifications[0].id);
    }
}

function removeNotification(notificationId) {
    const notification = document.getElementById(notificationId);
    if (notification) {
        // Cancelar el timeout automático si existe
        if (notification.timeoutId) {
            clearTimeout(notification.timeoutId);
        }
        
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
}

// Función de compatibilidad con el código existente
function showStatus(message, duration = 5000, type = 'info') {
    showNotification(message, type, duration);
}

function loadModelIntoViewer(data, colorscheme = "Jmol") {
    viewer.removeAllModels();
    viewer.addModel(data, "xyz");
    viewer.setStyle({}, {
        stick: { radius: radius, colorscheme: colorscheme },
        sphere: { scale: scale, colorscheme: colorscheme }
    });
    viewer.zoomTo();
    viewer.render();
    console.log("Model loaded successfully.");

    window.addEventListener('resize', () => {
        viewer.resize();
        viewer.render();
    });
}

function fetchAndLoadFile(filePath, colorscheme = "Jmol") {
    jQuery.ajax({
        url: filePath,
        dataType: "text",
        success: function (data) {
            loadModelIntoViewer(data, colorscheme);
            showNotification("✅ Structure loaded successfully", "success");
            console.log(`File successfully loaded from ${filePath}`);
        },
        error: function (error) {
            showNotification("❌ Error loading structure", "error");
            console.error(`Error loading file from ${filePath}:`, error);
        }
    });

    viewer.removeAllModels();
    viewer.render();
}

// Load default file
fetchAndLoadFile("/static/examples/pd12pt1.xyz");
setTimeout(() => showNotification("🔬 Welcome to ClusterWebLab - Advanced Molecular Analysis Platform", "info", 6000), 1000);

// ===============================
// FILE UPLOAD WITH DRAG & DROP
// ===============================
const fileUploadArea = document.getElementById('file-upload-area');
const fileInput = document.getElementById('file-upload');

fileUploadArea.addEventListener('click', () => fileInput.click());

fileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadArea.classList.add('dragover');
});

fileUploadArea.addEventListener('dragleave', () => {
    fileUploadArea.classList.remove('dragover');
});

fileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

function handleFileUpload(file) {
    if (file && file.name.endsWith('.xyz')) {
        showNotification("📁 Loading structure...", "info", 3000);
        const reader = new FileReader();
        reader.onload = function (e) {
            const xyzData = e.target.result;
            loadModelIntoViewer(xyzData);
            fetch('/upload_xyz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ xyz_content: xyzData }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showNotification("❌ Error saving file", "error");
                    console.error("Error saving file on server:", data.error);
                } else {
                    showNotification("✅ Structure imported successfully", "success");
                    console.log("File saved successfully on server:", data.message);
                }
            })
            .catch(error => {
                showNotification("❌ Upload failed", "error");
                console.error("Error:", error);
            });
        };
        reader.readAsText(file);
    } else {
        showNotification("❌ Please upload a valid .xyz file", "warning");
    }
}

// ===============================
// CLUSTER GENERATOR
// ===============================
document.getElementById('generate-button').addEventListener('click', () => {
    const clusterInput = document.getElementById('cluster-input').value.trim();
    if (!clusterInput) {
        showNotification("❗ Please enter a cluster configuration", "warning");
        return;
    }
    
    const button = document.getElementById('generate-button');
    button.classList.add('loading');
    showNotification("🧬 Generating cluster structure...", "info", 8000);
    
    fetch('/generate_cluster', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cluster_config: clusterInput }),
    })
    .then(response => response.json())
    .then(data => {
        button.classList.remove('loading');
        if (data.error) {
            showNotification("❌ Error generating cluster", "error");
            console.error("Error generating cluster:", data.error);
        } else {
            loadModelIntoViewer(data.xyz_content);
            showNotification("✅ Cluster generated successfully", "success");
            console.log("Cluster generated and loaded successfully.");
        }
    })
    .catch(error => {
        button.classList.remove('loading');
        showNotification("❌ Generation failed", "error");
        console.error("Error:", error);
    });
});

// ===============================
// OPTIMIZER
// ===============================
document.getElementById('optimize-button').addEventListener('click', () => {
    const xyzContent = generateXYZContent();
    if (!xyzContent) return;

    const selectedMethod = document.querySelector('input[name="optimization-method"]:checked').value;
    const button = document.getElementById('optimize-button');
    
    button.classList.add('loading');
    showNotification("⚙️ Optimizing molecular structure...", "info", 15000);

    fetch('/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ xyz_content: xyzContent, method: selectedMethod }),
    })
    .then(response => response.json())
    .then(async (data) => {
        setTimeout(async () => {
            button.classList.remove('loading');
            if (data.error) {
                showNotification(`❌ Error: ${data.error}`, "error", 8000);
                console.error("Error optimizing structure:", data.error);
            } else {
                // Mostrar mensaje de éxito con energías por 15 segundos
                showNotification(data.message, "success", 15000);
                console.log(data.message);

                // Automatically load the optimized structure
                try {
                    const response = await fetch('/get_user_uuid');
                    if (!response.ok) {
                        throw new Error('Failed to fetch user UUID');
                    }
                    const userData = await response.json();
                    const userId = userData.user_id;

                    // Construct the path to the optimized file
                    const optimizedFilePath = `/static/tmp/${userId}/opt-input.xyz`;

                    // Load the optimized file into the viewer
                    fetchAndLoadFile(optimizedFilePath);
                    console.log(`Optimized file loaded from ${optimizedFilePath}`);
                } catch (error) {
                    console.error('Error loading optimized structure:', error);
                }
            }
        }, 1000);
    })
    .catch(error => {
        setTimeout(() => {
            button.classList.remove('loading');
            showNotification("❌ Error optimizing structure", "error");
            console.error("Error:", error);
        }, 1000);
    });
});

// ===============================
// COLOR SCHEMA
// ===============================
document.querySelectorAll('input[name="color-schema"]').forEach(input => {
    input.addEventListener('change', (event) => {
        const selectedScheme = event.target.value;
        viewer.setStyle({}, {
            stick: { radius: radius, colorscheme: selectedScheme },
            sphere: { scale: scale, colorscheme: selectedScheme }
        });
        viewer.render();
        console.log(`Color scheme changed to ${selectedScheme}.`);
        
        // Update radio option selection visual
        document.querySelectorAll('.radio-option').forEach(option => {
            option.classList.remove('selected');
        });
        event.target.closest('.radio-option').classList.add('selected');
    });
});

// ===============================
// DARK MODE TOGGLE
// ===============================
function updateViewerBackgroundColor(isDarkMode) {
    config.backgroundColor = isDarkMode ? 0x121212 : 0xf8fafc;
    viewer.setBackgroundColor(config.backgroundColor);
    viewer.render();
}

document.getElementById('dark-mode-toggle').addEventListener('click', () => {
    const toggle = document.getElementById('dark-mode-toggle');
    const isDarkMode = !toggle.classList.contains('active');
    
    toggle.classList.toggle('active', isDarkMode);
    document.body.classList.toggle('dark-mode', isDarkMode);
    updateViewerBackgroundColor(isDarkMode);
    
    console.log(isDarkMode ? "Dark mode activated." : "Dark mode deactivated.");
});

// ===============================
// DOWNLOAD FUNCTIONS
// ===============================
function generateXYZContent() {
    const model = viewer.getModel();
    if (!model) {
        console.error("No model found in the viewer.");
        showNotification("❌ No structure to download", "warning");
        return null;
    }
    const atoms = model.selectedAtoms();
    if (atoms.length === 0) {
        console.error("No atoms found in the model.");
        showNotification("❌ No atoms in structure", "warning");
        return null;
    }
    return `${atoms.length}\n\n` + atoms.map(atom =>
        `${atom.elem} ${atom.x.toFixed(4)} ${atom.y.toFixed(4)} ${atom.z.toFixed(4)}`
    ).join('\n');
}

document.getElementById('download-xyz').addEventListener('click', () => {
    const xyzContent = generateXYZContent();
    if (xyzContent) {
        const blob = new Blob([xyzContent], { type: 'text/plain' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'cluster_viewer.xyz';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showNotification("✅ XYZ file downloaded", "success");
        console.log("XYZ file downloaded successfully.");
    }
});

document.getElementById('download-png').addEventListener('click', () => {
    if (viewer) {
        const pngURI = viewer.pngURI();
        const link = document.createElement('a');
        link.href = pngURI;
        link.download = 'cluster_viewer.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showNotification("✅ PNG image downloaded", "success");
        console.log("PNG image downloaded successfully.");
    } else {
        showNotification("❌ Viewer not initialized", "error");
        console.error("Viewer is not initialized. Cannot download PNG.");
    }
});

// ===============================
// RADIO BUTTON INTERACTIONS
// ===============================
document.querySelectorAll('input[name="optimization-method"]').forEach(input => {
    input.addEventListener('change', (event) => {
        document.querySelectorAll('input[name="optimization-method"]').forEach(radio => {
            radio.closest('.radio-option').classList.remove('selected');
        });
        event.target.closest('.radio-option').classList.add('selected');
    });
});
