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

# API endpoint to retrieve the unique user ID stored in the session
@app.route('/get_user_uuid', methods=['GET'])
def get_user_uuid():
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    return jsonify({'user_id': session['user_id']})

# Main route that renders the home page and initializes user session with temporary workspace
@app.route('/')
def home():
    # Generate unique user ID if not already present in session
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    user_id = session['user_id']

    # Create isolated temporary directory structure for each user session
    user_tmp_dir = os.path.join(app.root_path, 'static', 'tmp', user_id)
    os.makedirs(user_tmp_dir, exist_ok=True)

    # Initialize user workspace with default example files (pd12pt1.xyz cluster)
    source_file = os.path.join(app.root_path, 'static', 'examples', 'pd12pt1.xyz')
    destination_file = os.path.join(user_tmp_dir, 'input.xyz')

    opt_source_file = os.path.join(app.root_path, 'static', 'examples', 'pd12pt1.xyz')
    opt_destination_file = os.path.join(user_tmp_dir, 'opt-input.xyz')

    try:
        # Copy example files to user's workspace for immediate visualization
        if os.path.exists(source_file):
            with open(source_file, 'r') as src, open(destination_file, 'w') as dest:
                dest.write(src.read())
        if os.path.exists(opt_source_file):
            with open(opt_source_file, 'r') as src, open(opt_destination_file, 'w') as dest:
                dest.write(src.read())
    except Exception as e:
        print(f"Error copying the file: {str(e)}")

    return render_template('index.html')

# API endpoint to handle user-uploaded XYZ molecular structure files
@app.route('/upload_xyz', methods=['POST'])
def upload_xyz():
    # Validate user session before processing upload
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    user_id = session['user_id']

    data = request.json
    xyz_content = data.get('xyz_content')

    if not xyz_content:
        return jsonify({'error': 'XYZ content is required'}), 400

    try:
        # Save uploaded XYZ content to user's isolated temporary workspace
        user_tmp_dir = os.path.join('static', 'tmp', user_id)
        os.makedirs(user_tmp_dir, exist_ok=True)

        input_file_path = os.path.join(user_tmp_dir, 'input.xyz')
        with open(input_file_path, 'w') as input_file:
            input_file.write(xyz_content)

        return jsonify({'message': f"File successfully saved to {input_file_path}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint to generate random molecular clusters based on user-defined atomic composition
@app.route('/generate_cluster', methods=['POST'])
def generate_cluster():
    # Ensure user is properly identified before cluster generation
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    user_id = session['user_id']

    data = request.json
    cluster_config = data.get('cluster_config')

    if not cluster_config:
        return jsonify({'error': 'Cluster configuration is required'}), 400

    try:
        # Parse atomic sequence and generate randomized 3D coordinates for cluster
        atoms = parse_atom_sequence(cluster_config)
        coords = generate_random_coordinates(len(atoms))

        # Build XYZ file format with atom count header and atomic coordinates
        xyz_content = f"{len(atoms)}\n\n"
        for atom, coord in zip(atoms, coords):
            xyz_content += f"{atom} {coord[0]:.4f} {coord[1]:.4f} {coord[2]:.4f}\n"

        # Save generated cluster to user's temporary workspace
        user_tmp_dir = os.path.join('static', 'tmp', user_id)
        os.makedirs(user_tmp_dir, exist_ok=True)

        temp_file_path = os.path.join(user_tmp_dir, 'input.xyz')
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(xyz_content)

        return jsonify({'xyz_content': xyz_content, 'file_path': temp_file_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint to perform molecular structure optimization using specified algorithms
@app.route('/optimize', methods=['POST'])
def optimize():
    # Validate user session before starting optimization process
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    user_id = session['user_id']

    data = request.json
    xyz_content = data.get('xyz_content')
    method = data.get('method', 'L-BFGS-B')  # Default optimization method

    if not xyz_content:
        return jsonify({'error': 'XYZ content is required'}), 400

    try:
        # Setup user workspace and prepare input file for optimization
        user_tmp_dir = os.path.join('static', 'tmp', user_id)
        os.makedirs(user_tmp_dir, exist_ok=True)

        temp_file_path = os.path.join(user_tmp_dir, 'input.xyz')

        if not os.path.exists(temp_file_path):
            return jsonify({'error': f"File not found: {temp_file_path}"}), 400

        # Update input file with current XYZ content to ensure optimization
        # uses the most recent molecular structure for re-optimization scenarios
        with open(temp_file_path, 'w') as f:
            f.write(xyz_content)

        # Execute structure optimization and capture energy changes with timing metrics
        (energy_values, execution_time) = optimize_structure(temp_file_path, method=method)
        old_energy, new_energy = energy_values

        # Move optimized structure file to user's workspace for retrieval
        optimized_file_source = os.path.join('opt-input.xyz')
        optimized_file_destination = os.path.join(user_tmp_dir, 'opt-input.xyz')
        os.rename(optimized_file_source, optimized_file_destination)

        # Read optimized structure content for client response
        with open(optimized_file_destination, 'r') as optimized_file:
            optimized_xyz_content = optimized_file.read()

        # Format success message with optimization results and performance metrics
        success_message = f"✅ Optimization executed {execution_time:.4f} sec.<br>⚡️ Old energy: {old_energy:.4f} eV<br>⚡️ New energy: {new_energy:.4f} eV"
        return jsonify({'optimized_xyz_content': optimized_xyz_content, 'message': success_message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Background maintenance function to clean up all temporary user files and directories
def delete_all_temp_files():
    tmp_dir = os.path.join(app.root_path, 'static', 'tmp')
    if (os.path.exists(tmp_dir)):
        try:
            # Recursively remove all user directories and files in temporary storage
            for item in os.listdir(tmp_dir):
                item_path = os.path.join(tmp_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Remove user directories
                else:
                    os.remove(item_path)  # Remove standalone files
            print(f"[{datetime.now()}] All temporary files deleted successfully.")
        except Exception as e:
            print(f"[{datetime.now()}] Error deleting temporary files: {str(e)}")
    else:
        print(f"[{datetime.now()}] Temporary directory does not exist.")

# Configure automated cleanup scheduler to run weekly maintenance on Sundays at midnight
scheduler = BackgroundScheduler()
scheduler.add_job(delete_all_temp_files, 'cron', day_of_week='sun', hour=0, minute=0)
scheduler.start()

# Register cleanup handler to ensure scheduler shuts down gracefully on application exit
import atexit
atexit.register(lambda: scheduler.shutdown())

# Application entry point - start Flask development server with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
