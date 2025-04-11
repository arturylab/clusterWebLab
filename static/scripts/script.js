// Variables for the viewer
const radius = 0.1;
const scale = 0.5;

// Select the element with the id "left-section"
const element = document.querySelector('#left-section');
const config = { backgroundColor: 0xf5f5f5 };

// Initialize the 3Dmol.js viewer
const viewer = $3Dmol.createViewer(element, config);

// Utility function to load a model into the viewer
function loadModelIntoViewer(data, colorscheme = "Jmol") {
    viewer.removeAllModels(); // Remove existing models
    viewer.addModel(data, "xyz");
    viewer.setStyle({}, {
        stick: { radius: radius, colorscheme: colorscheme },
        sphere: { scale: scale, colorscheme: colorscheme }
    });
    viewer.zoomTo();
    viewer.render();
    console.log("Model loaded successfully.");

    // Handle resizing
    window.addEventListener('resize', () => {
        viewer.resize();
        viewer.render();
    });
}

// Utility function to fetch and load a file into the viewer
function fetchAndLoadFile(filePath, colorscheme = "Jmol") {
    jQuery.ajax({
        url: filePath,
        dataType: "text",
        success: function (data) {
            loadModelIntoViewer(data, colorscheme);
        },
        error: function (xhr, status, error) {
            console.error(`Error loading file from ${filePath}:`, error);
        }
    });
}

// Load the default XYZ file on page load
fetchAndLoadFile("/static/examples/pd12pt1.xyz");

// Add event listener to the "Change Color Scheme" radio buttons
document.querySelectorAll('input[name="color-schema"]').forEach(input => {
    input.addEventListener('change', (event) => {
        const selectedScheme = event.target.value;
        viewer.setStyle({}, {
            stick: { radius: radius, colorscheme: selectedScheme },
            sphere: { scale: scale, colorscheme: selectedScheme }
        });
        viewer.render();
        console.log(`Color scheme changed to ${selectedScheme}.`);
    });
});

// Add event listener to the "Download PNG" button
document.getElementById('download-png').addEventListener('click', () => {
    if (viewer) {
        const pngURI = viewer.pngURI();
        const link = document.createElement('a');
        link.href = pngURI;
        link.download = 'cluster_viewer.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log("PNG image downloaded successfully.");
    } else {
        console.error("Viewer is not initialized. Cannot download PNG.");
    }
});

// Utility function to generate XYZ content from the viewer's model
function generateXYZContent() {
    const model = viewer.getModel();
    if (!model) {
        console.error("No model found in the viewer.");
        return null;
    }
    const atoms = model.selectedAtoms();
    if (atoms.length === 0) {
        console.error("No atoms found in the model.");
        return null;
    }
    return `${atoms.length}\n\n` + atoms.map(atom =>
        `${atom.elem} ${atom.x.toFixed(4)} ${atom.y.toFixed(4)} ${atom.z.toFixed(4)}`
    ).join('\n');
}

// Add event listener to the "Download XYZ" button
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
        console.log("XYZ file downloaded successfully.");
    }
});

// Add event listener to the "Upload XYZ" file input
document.getElementById('file-upload').addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.xyz')) {
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
                        console.error("Error saving file on server:", data.error);
                    } else {
                        console.log("File saved successfully on server:", data.message);
                    }
                })
                .catch(error => console.error("Error:", error));
        };
        reader.readAsText(file);
    } else {
        console.error("Please upload a valid .xyz file.");
    }
});

// Add event listener to the "Generate Cluster" button
document.getElementById('generate-button').addEventListener('click', () => {
    const clusterInput = document.getElementById('cluster-input').value.trim();
    if (!clusterInput) {
        console.error("Cluster configuration is required.");
        return;
    }
    fetch('/generate_cluster', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cluster_config: clusterInput }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error generating cluster:", data.error);
            } else {
                loadModelIntoViewer(data.xyz_content);
                console.log("Cluster generated and loaded successfully.");
            }
        })
        .catch(error => console.error("Error:", error));
});

// Add event listener to the "Optimize Structure" button
document.getElementById('optimize-button').addEventListener('click', () => {
    const xyzContent = generateXYZContent();
    if (!xyzContent) return;

    const selectedMethod = document.querySelector('input[name="optimization-method"]:checked').value;

    // Display "Optimization in progress..." message
    const optimizerSection = document.querySelector('.optimizer');
    let progressMessage = document.createElement('p');
    progressMessage.textContent = "Optimization in progress . . .";
    progressMessage.style.color = 'blue';
    optimizerSection.insertBefore(progressMessage, document.getElementById('optimize-button'));

    fetch('/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ xyz_content: xyzContent, method: selectedMethod }),
    })
        .then(response => response.json())
        .then(data => {
            // Remove the progress message
            progressMessage.remove();

            if (data.error) {
                console.error("Error optimizing structure:", data.error);
            } else {
                const messageContainer = document.createElement('p');
                messageContainer.textContent = data.message;
                messageContainer.style.color = 'green';
                optimizerSection.insertBefore(messageContainer, document.getElementById('optimize-button'));
                console.log(data.message);
            }
        })
        .catch(error => {
            // Remove the progress message in case of error
            progressMessage.remove();
            console.error("Error:", error);
        });
});

// Add event listener to the "Load Optimized Structure" button
document.getElementById('load-opt-button').addEventListener('click', async () => {
    const messageContainer = document.querySelector('.optimizer p');
    if (messageContainer) {
        messageContainer.remove();
    }

    try {
        // Fetch the user's UUID from the server
        const response = await fetch('/get_user_uuid');
        if (!response.ok) {
            throw new Error('Failed to fetch user UUID');
        }
        const data = await response.json();
        const userId = data.user_id;

        // Construct the path to the optimized file
        const optimizedFilePath = `/static/tmp/${userId}/opt-input.xyz`;

        // Load the optimized file into the viewer
        fetchAndLoadFile(optimizedFilePath);
        console.log(`Optimized file loaded from ${optimizedFilePath}`);
    } catch (error) {
        console.error('Error loading optimized structure:', error);
    }
});

// Add event listener to the "Load Default File" button
document.getElementById('load-file-button').addEventListener('click', async () => {
    try {
        // Fetch the user's UUID from the server
        const response = await fetch('/get_user_uuid');
        if (!response.ok) {
            throw new Error('Failed to fetch user UUID');
        }
        const data = await response.json();
        const userId = data.user_id;

        // Construct the path to the default file
        const defaultFilePath = `/static/tmp/${userId}/input.xyz`;

        // Load the default file into the viewer
        fetchAndLoadFile(defaultFilePath);
        console.log(`Default file loaded from ${defaultFilePath}`);
    } catch (error) {
        console.error('Error loading default file:', error);
    }
});