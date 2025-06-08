from flask import Flask, render_template, request, jsonify, session
import sys
import os
import uuid
import shutil
sys.path.append(os.path.join(os.path.dirname(__file__), 'static/src'))
from static.src.rnd_xyz import parse_atom_sequence, generate_random_coordinates
from static.src.optimizer import optimize_structure
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Route to retrieve the unique user ID from the session
@app.route('/get_user_uuid', methods=['GET'])
def get_user_uuid():
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    return jsonify({'user_id': session['user_id']})

# Route to render the home page and initialize user session
@app.route('/')
def home():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    user_id = session['user_id']

    # Create a unique temporary directory for the user
    user_tmp_dir = os.path.join(app.root_path, 'static', 'tmp', user_id)
    os.makedirs(user_tmp_dir, exist_ok=True)

    # Copy example files to the user's temporary directory
    source_file = os.path.join(app.root_path, 'static', 'examples', 'pd12pt1.xyz')
    destination_file = os.path.join(user_tmp_dir, 'input.xyz')

    opt_source_file = os.path.join(app.root_path, 'static', 'examples', 'pd12pt1.xyz')
    opt_destination_file = os.path.join(user_tmp_dir, 'opt-input.xyz')

    try:
        if os.path.exists(source_file):
            with open(source_file, 'r') as src, open(destination_file, 'w') as dest:
                dest.write(src.read())
        if os.path.exists(opt_source_file):
            with open(opt_source_file, 'r') as src, open(opt_destination_file, 'w') as dest:
                dest.write(src.read())
    except Exception as e:
        print(f"Error copying the file: {str(e)}")

    return render_template('index.html')

# Route to upload XYZ file content
@app.route('/upload_xyz', methods=['POST'])
def upload_xyz():
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    user_id = session['user_id']

    data = request.json
    xyz_content = data.get('xyz_content')

    if not xyz_content:
        return jsonify({'error': 'XYZ content is required'}), 400

    try:
        # Save the uploaded XYZ content to the user's temporary directory
        user_tmp_dir = os.path.join('static', 'tmp', user_id)
        os.makedirs(user_tmp_dir, exist_ok=True)

        input_file_path = os.path.join(user_tmp_dir, 'input.xyz')
        with open(input_file_path, 'w') as input_file:
            input_file.write(xyz_content)

        return jsonify({'message': f"File successfully saved to {input_file_path}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to generate a cluster based on user configuration
@app.route('/generate_cluster', methods=['POST'])
def generate_cluster():
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    user_id = session['user_id']

    data = request.json
    cluster_config = data.get('cluster_config')

    if not cluster_config:
        return jsonify({'error': 'Cluster configuration is required'}), 400

    try:
        # Parse atom sequence and generate random coordinates
        atoms = parse_atom_sequence(cluster_config)
        coords = generate_random_coordinates(len(atoms))

        # Create XYZ content and save it to the user's temporary directory
        xyz_content = f"{len(atoms)}\n\n"
        for atom, coord in zip(atoms, coords):
            xyz_content += f"{atom} {coord[0]:.4f} {coord[1]:.4f} {coord[2]:.4f}\n"

        user_tmp_dir = os.path.join('static', 'tmp', user_id)
        os.makedirs(user_tmp_dir, exist_ok=True)

        temp_file_path = os.path.join(user_tmp_dir, 'input.xyz')
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(xyz_content)

        return jsonify({'xyz_content': xyz_content, 'file_path': temp_file_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to optimize the structure of the uploaded XYZ content
@app.route('/optimize', methods=['POST'])
def optimize():
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    user_id = session['user_id']

    data = request.json
    xyz_content = data.get('xyz_content')
    method = data.get('method', 'L-BFGS-B')

    if not xyz_content:
        return jsonify({'error': 'XYZ content is required'}), 400

    try:
        # Perform optimization and save the optimized structure
        user_tmp_dir = os.path.join('static', 'tmp', user_id)
        os.makedirs(user_tmp_dir, exist_ok=True)

        temp_file_path = os.path.join(user_tmp_dir, 'input.xyz')

        if not os.path.exists(temp_file_path):
            return jsonify({'error': f"File not found: {temp_file_path}"}), 400

        # Guardar el contenido XYZ actual para asegurar que estamos optimizando
        # el modelo correcto en cada reoptimización
        with open(temp_file_path, 'w') as f:
            f.write(xyz_content)

        # Ahora realiza la optimización con el archivo actualizado
        (energy_values, execution_time) = optimize_structure(temp_file_path, method=method)
        old_energy, new_energy = energy_values

        optimized_file_source = os.path.join('opt-input.xyz')
        optimized_file_destination = os.path.join(user_tmp_dir, 'opt-input.xyz')
        os.rename(optimized_file_source, optimized_file_destination)

        with open(optimized_file_destination, 'r') as optimized_file:
            optimized_xyz_content = optimized_file.read()

        success_message = f"✅ Optimization executed {execution_time:.4f} sec.<br>⚡️ Old energy: {old_energy:.4f} eV<br>⚡️ New energy: {new_energy:.4f} eV"
        return jsonify({'optimized_xyz_content': optimized_xyz_content, 'message': success_message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Function to delete all temporary files in the 'static/tmp' directory
def delete_all_temp_files():
    tmp_dir = os.path.join(app.root_path, 'static', 'tmp')
    if (os.path.exists(tmp_dir)):
        try:
            for item in os.listdir(tmp_dir):
                item_path = os.path.join(tmp_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            print(f"[{datetime.now()}] All temporary files deleted successfully.")
        except Exception as e:
            print(f"[{datetime.now()}] Error deleting temporary files: {str(e)}")
    else:
        print(f"[{datetime.now()}] Temporary directory does not exist.")

# Configure the scheduler to run the cleanup task every Sunday at 12:00 AM
scheduler = BackgroundScheduler()
scheduler.add_job(delete_all_temp_files, 'cron', day_of_week='sun', hour=0, minute=0)
scheduler.start()

# Ensure the scheduler shuts down when the application exits
import atexit
atexit.register(lambda: scheduler.shutdown())

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=5003)
