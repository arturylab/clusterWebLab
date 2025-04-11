from flask import Flask, render_template, request, jsonify, session
import sys
import os
import uuid  # Import the uuid library
import shutil  # Import shutil to delete directories
sys.path.append(os.path.join(os.path.dirname(__file__), 'static/src'))
from static.src.rnd_xyz import parse_atom_sequence, generate_random_coordinates
from static.src.optimizer import optimize_structure
from flask import Flask, render_template, request, jsonify, session
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/get_user_uuid', methods=['GET'])
def get_user_uuid():
    """
    Retrieve the unique user ID from the session.

    Returns:
        JSON response containing the user ID if it exists in the session,
        or an error message if the user is not identified.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    return jsonify({'user_id': session['user_id']})

@app.route('/')
def home():
    """
    Render the home page and initialize a unique user session.

    Creates a unique directory for the user and copies example files
    to the user's temporary directory.

    Returns:
        Rendered HTML template for the home page.
    """
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    user_id = session['user_id']

    user_tmp_dir = os.path.join(app.root_path, 'static', 'tmp', user_id)
    os.makedirs(user_tmp_dir, exist_ok=True)

    source_file = os.path.join(app.root_path, 'static', 'examples', 'pd12pt1.xyz')
    destination_file = os.path.join(user_tmp_dir, 'input.xyz')

    opt_source_file = os.path.join(app.root_path, 'static', 'examples', 'pd12pt1.xyz')
    opt_destination_file = os.path.join(user_tmp_dir, 'opt-input.xyz')

    try:
        if os.path.exists(source_file):
            with open(source_file, 'r') as src, open(destination_file, 'w') as dest:
                dest.write(src.read())
            print(f"File successfully copied from {source_file} to {destination_file}")
        else:
            print(f"Source file not found: {source_file}")

        if os.path.exists(opt_source_file):
            with open(opt_source_file, 'r') as src, open(opt_destination_file, 'w') as dest:
                dest.write(src.read())
            print(f"File successfully copied from {opt_source_file} to {opt_destination_file}")
        else:
            print(f"Source file not found: {opt_source_file}")

    except Exception as e:
        print(f"Error copying the file: {str(e)}")

    return render_template('index.html')

@app.route('/upload_xyz', methods=['POST'])
def upload_xyz():
    """
    Upload an XYZ file content and save it to the user's temporary directory.

    Returns:
        JSON response indicating success or failure.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    user_id = session['user_id']

    data = request.json
    xyz_content = data.get('xyz_content')

    if not xyz_content:
        return jsonify({'error': 'XYZ content is required'}), 400

    try:
        user_tmp_dir = os.path.join('static', 'tmp', user_id)
        os.makedirs(user_tmp_dir, exist_ok=True)

        input_file_path = os.path.join(user_tmp_dir, 'input.xyz')
        with open(input_file_path, 'w') as input_file:
            input_file.write(xyz_content)

        return jsonify({'message': f"File successfully saved to {input_file_path}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_cluster', methods=['POST'])
def generate_cluster():
    """
    Generate a cluster based on the provided configuration.

    Parses the atom sequence, generates random coordinates, and saves
    the resulting XYZ content to the user's temporary directory.

    Returns:
        JSON response containing the generated XYZ content and file path,
        or an error message in case of failure.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    user_id = session['user_id']

    data = request.json
    cluster_config = data.get('cluster_config')

    if not cluster_config:
        return jsonify({'error': 'Cluster configuration is required'}), 400

    try:
        atoms = parse_atom_sequence(cluster_config)
        coords = generate_random_coordinates(len(atoms))

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

@app.route('/optimize', methods=['POST'])
def optimize():
    """
    Optimize the structure of the uploaded XYZ content.

    Uses the specified optimization method and saves the optimized
    structure to the user's temporary directory.

    Returns:
        JSON response containing the optimized XYZ content and execution time,
        or an error message in case of failure.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User not identified'}), 400
    user_id = session['user_id']

    data = request.json
    xyz_content = data.get('xyz_content')
    method = data.get('method', 'L-BFGS-B')

    if not xyz_content:
        return jsonify({'error': 'XYZ content is required'}), 400

    try:
        user_tmp_dir = os.path.join('static', 'tmp', user_id)
        os.makedirs(user_tmp_dir, exist_ok=True)

        temp_file_path = os.path.join(user_tmp_dir, 'input.xyz')

        if not os.path.exists(temp_file_path):
            return jsonify({'error': f"File not found: {temp_file_path}"}), 400

        print(f"Optimizing structure using file: {temp_file_path} and method: {method}")
        _, execution_time = optimize_structure(temp_file_path, method=method)

        optimized_file_source = os.path.join('opt-input.xyz')
        optimized_file_destination = os.path.join(user_tmp_dir, 'opt-input.xyz')
        os.rename(optimized_file_source, optimized_file_destination)

        with open(optimized_file_destination, 'r') as optimized_file:
            optimized_xyz_content = optimized_file.read()

        success_message = f"Optimization successful. Executed in {execution_time:.4f} seconds."
        print(success_message)
        return jsonify({'optimized_xyz_content': optimized_xyz_content, 'message': success_message})
    except Exception as e:
        print(f"Error during optimization: {str(e)}")
        return jsonify({'error': str(e)}), 500

def delete_all_temp_files():
    """
    Deletes all temporary files in the 'static/tmp' directory.
    """
    tmp_dir = os.path.join(app.root_path, 'static', 'tmp')
    if os.path.exists(tmp_dir):
        try:
            # Remove all subdirectories and files in 'static/tmp'
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

# Configure the scheduler to run the task every Sunday at 12:00 AM
scheduler = BackgroundScheduler()
scheduler.add_job(delete_all_temp_files, 'cron', day_of_week='sun', hour=0, minute=0)
scheduler.start()

# Ensure the scheduler shuts down when the application exits
import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True)