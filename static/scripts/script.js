// Variables for the viewer
const radius = 0.1; // Radius for stick representation
const scale = 0.5; // Scale for sphere representation

// Select the element with the id "left-section"
const element = document.querySelector('#left-section');
const config = { backgroundColor: 0xf5f5f5 }; // Viewer background color configuration

// Initialize the 3Dmol.js viewer
const viewer = $3Dmol.createViewer(element, config);

// Utility function to load a model into the viewer
function loadModelIntoViewer(data, colorscheme = "Jmol") {
    viewer.removeAllModels(); // Clear any existing models in the viewer
    viewer.addModel(data, "xyz"); // Add the new model in XYZ format
    viewer.setStyle({}, {
        stick: { radius: radius, colorscheme: colorscheme }, // Apply stick style
        sphere: { scale: scale, colorscheme: colorscheme } // Apply sphere style
    });
    viewer.zoomTo(); // Adjust the view to fit the model
    viewer.render(); // Render the viewer
    console.log("Model loaded successfully.");

    // Handle resizing of the viewer when the window is resized
    window.addEventListener('resize', () => {
        viewer.resize();
        viewer.render();
    });
}

// Load the default XYZ file on page load
fetchAndLoadFile("/static/examples/pd12pt1.xyz");

// Utility function to fetch and load a file into the viewer
function fetchAndLoadFile(filePath, colorscheme = "Jmol") {
    jQuery.ajax({
        url: filePath,
        dataType: "text",
        success: function (data) {
            loadModelIntoViewer(data, colorscheme); // Load the fetched data into the viewer
            console.log(`File successfully loaded from ${filePath}`);
        },
        error: function (error) {
            console.error(`Error loading file from ${filePath}:`, error);
        }
    });

    // Clear the viewer and re-render in case of re-fetch
    viewer.removeAllModels();
    viewer.render();
}

// Add event listener to the "Change Color Scheme" radio buttons
document.querySelectorAll('input[name="color-schema"]').forEach(input => {
    input.addEventListener('change', (event) => {
        const selectedScheme = event.target.value; // Get the selected color scheme
        viewer.setStyle({}, {
            stick: { radius: radius, colorscheme: selectedScheme },
            sphere: { scale: scale, colorscheme: selectedScheme }
        });
        viewer.render(); // Re-render the viewer with the new color scheme
        console.log(`Color scheme changed to ${selectedScheme}.`);
    });
});

// Add event listener to the "Download PNG" button
document.getElementById('download-png').addEventListener('click', () => {
    if (viewer) {
        const pngURI = viewer.pngURI(); // Generate PNG URI from the viewer
        const link = document.createElement('a');
        link.href = pngURI;
        link.download = 'cluster_viewer.png'; // Set the download file name
        document.body.appendChild(link);
        link.click(); // Trigger the download
        document.body.removeChild(link);
        console.log("PNG image downloaded successfully.");
    } else {
        console.error("Viewer is not initialized. Cannot download PNG.");
    }
});

// Utility function to generate XYZ content from the viewer's model
function generateXYZContent() {
    const model = viewer.getModel(); // Get the current model from the viewer
    if (!model) {
        console.error("No model found in the viewer.");
        return null;
    }
    const atoms = model.selectedAtoms(); // Get all selected atoms in the model
    if (atoms.length === 0) {
        console.error("No atoms found in the model.");
        return null;
    }
    // Generate XYZ content with atom count, blank line, and atom coordinates
    return `${atoms.length}\n\n` + atoms.map(atom =>
        `${atom.elem} ${atom.x.toFixed(4)} ${atom.y.toFixed(4)} ${atom.z.toFixed(4)}`
    ).join('\n');
}

// Add event listener to the "Download XYZ" button
document.getElementById('download-xyz').addEventListener('click', () => {
    const xyzContent = generateXYZContent(); // Generate XYZ content from the viewer
    if (xyzContent) {
        const blob = new Blob([xyzContent], { type: 'text/plain' }); // Create a blob for the file
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'cluster_viewer.xyz'; // Set the download file name
        document.body.appendChild(link);
        link.click(); // Trigger the download
        document.body.removeChild(link);
        console.log("XYZ file downloaded successfully.");
    }
});

// Add event listener to the "Upload XYZ" file input
document.getElementById('file-upload').addEventListener('change', (event) => {
    const file = event.target.files[0]; // Get the uploaded file
    if (file && file.name.endsWith('.xyz')) { // Validate file extension
        const reader = new FileReader();
        reader.onload = function (e) {
            const xyzData = e.target.result; // Read the file content
            loadModelIntoViewer(xyzData); // Load the content into the viewer
            fetch('/upload_xyz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ xyz_content: xyzData }), // Send the content to the server
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
        reader.readAsText(file); // Read the file as text
    } else {
        console.error("Please upload a valid .xyz file.");
    }
});

// Add event listener to the "Generate Cluster" button
document.getElementById('generate-button').addEventListener('click', () => {
    const clusterInput = document.getElementById('cluster-input').value.trim(); // Get cluster configuration
    if (!clusterInput) {
        console.error("Cluster configuration is required.");
        return;
    }
    fetch('/generate_cluster', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cluster_config: clusterInput }), // Send the configuration to the server
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error generating cluster:", data.error);
            } else {
                loadModelIntoViewer(data.xyz_content); // Load the generated cluster into the viewer
                console.log("Cluster generated and loaded successfully.");
            }
        })
        .catch(error => console.error("Error:", error));
});

// Add event listener to the "Optimize Structure" button
document.getElementById('optimize-button').addEventListener('click', () => {
    const xyzContent = generateXYZContent(); // Generate XYZ content from the viewer
    if (!xyzContent) return;

    const selectedMethod = document.querySelector('input[name="optimization-method"]:checked').value; // Get selected optimization method

    const overlayText = document.querySelector('.overlay-text'); // Select the overlay-text element
    overlayText.textContent = "⚙️ Optimization in progress..."; // Display progress message

    fetch('/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ xyz_content: xyzContent, method: selectedMethod }), // Send optimization request
    })
        .then(response => response.json())
        .then(async (data) => {
            // Ensure the message is displayed for at least 1 second
            setTimeout(async () => {
                if (data.error) {
                    overlayText.textContent = "Error optimizing structure."; // Display error message
                    console.error("Error optimizing structure:", data.error);
                } else {
                    overlayText.textContent = data.message; // Display success message
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
            // Ensure the message is displayed for at least 1 second in case of error
            setTimeout(() => {
                overlayText.textContent = "Error optimizing structure."; // Display error message
                console.error("Error:", error);
            }, 1000);
        });
});

// Add event listener to the "Energy" button
document.getElementById('get_energy').addEventListener('click', async () => {
    const overlayText = document.querySelector('.overlay-text');
    overlayText.textContent = "⚡️ Energy calculation in progress...";

    try {
        // Fetch the user's UUID to locate the optimized file
        const response = await fetch('/get_user_uuid');
        if (!response.ok) {
            throw new Error('Failed to fetch user UUID');
        }
        const data = await response.json();
        const userId = data.user_id;

        // Path to the optimized file
        const optimizedFilePath = `/static/tmp/${userId}/opt-input.xyz`;
        console.log("File path sent to server:", optimizedFilePath);

        const energyResponse = await fetch('/calculate_energy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: optimizedFilePath }), // Send the file path to the server
        });

        if (!energyResponse.ok) {
            throw new Error('Failed to calculate energy');
        }

        const energyData = await energyResponse.json();
        if (energyData.error) {
            throw new Error(energyData.error);
        }

        // Ensure the message is displayed for at least 1 second
        setTimeout(() => {
            overlayText.textContent = `⚡️ Energy: ${energyData.energy}`; // Display the calculated energy
        }, 1000);
    } catch (error) {
        console.error('Error calculating energy:', error);
        setTimeout(() => {
            overlayText.textContent = "Error calculating energy."; // Display error message
        }, 1000);
    }
});
// Function to update the viewer's background color
function updateViewerBackgroundColor(isDarkMode) {
    config.backgroundColor = isDarkMode ? 0x121212 : 0xf5f5f5; // Change color based on mode
    viewer.setBackgroundColor(config.backgroundColor); // Update the viewer's background color
    viewer.render(); // Re-render the viewer
}

// Listener for the dark mode toggle
document.getElementById('dark-mode-toggle').addEventListener('change', (event) => {
    const isDarkMode = event.target.checked;
    document.body.classList.toggle('dark-mode', isDarkMode); // Toggle dark mode class on the body
    updateViewerBackgroundColor(isDarkMode); // Update the viewer's background color
    console.log(isDarkMode ? "Dark mode activated." : "Dark mode deactivated.");
});
