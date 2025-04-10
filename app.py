from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'static/src'))
from static.src.rnd_xyz import parse_atom_sequence, generate_random_coordinates
from static.src.optimizer import optimize_structure

app = Flask(__name__)

@app.route('/')
def home():
    # Define the source and destination paths for input.xyz
    source_file = os.path.join(app.root_path, 'static', 'examples', 'pd12pt1.xyz')
    destination_dir = os.path.join(app.root_path, 'static', 'tmp')
    destination_file = os.path.join(destination_dir, 'input.xyz')

    # Define the source and destination paths for opt-input.xyz
    opt_source_file = os.path.join(app.root_path, 'static', 'examples', 'pd12pt1.xyz')  # Example file to copy
    opt_destination_file = os.path.join(destination_dir, 'opt-input.xyz')

    try:
        # Ensure the /static/tmp/ directory exists
        os.makedirs(destination_dir, exist_ok=True)

        # Copy the file from /static/examples/ to /static/tmp/ as input.xyz
        if os.path.exists(source_file):
            with open(source_file, 'r') as src, open(destination_file, 'w') as dest:
                dest.write(src.read())
            print(f"File copied successfully from {source_file} to {destination_file}")
        else:
            print(f"Source file not found: {source_file}")

        # Copy the file from /static/examples/ to /static/tmp/ as opt-input.xyz
        if os.path.exists(opt_source_file):
            with open(opt_source_file, 'r') as src, open(opt_destination_file, 'w') as dest:
                dest.write(src.read())
            print(f"File copied successfully from {opt_source_file} to {opt_destination_file}")
        else:
            print(f"Source file not found: {opt_source_file}")

    except Exception as e:
        print(f"Error copying file: {str(e)}")

    return render_template('index.html')

@app.route('/upload_xyz', methods=['POST'])
def upload_xyz():
    data = request.json
    xyz_content = data.get('xyz_content')

    if not xyz_content:
        return jsonify({'error': 'XYZ content is required'}), 400

    try:
        # Ensure the /static/tmp/ directory exists
        tmp_dir = os.path.join('static', 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Save the XYZ content to input.xyz in /static/tmp/
        input_file_path = os.path.join(tmp_dir, 'input.xyz')
        with open(input_file_path, 'w') as input_file:
            input_file.write(xyz_content)

        return jsonify({'message': f"File saved successfully at {input_file_path}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_cluster', methods=['POST'])
def generate_cluster():
    data = request.json
    cluster_config = data.get('cluster_config')

    if not cluster_config:
        return jsonify({'error': 'Cluster configuration is required'}), 400

    try:
        # Parse the atom sequence and generate random coordinates
        atoms = parse_atom_sequence(cluster_config)
        coords = generate_random_coordinates(len(atoms))

        # Generate the XYZ content
        xyz_content = f"{len(atoms)}\n\n"
        for atom, coord in zip(atoms, coords):
            xyz_content += f"{atom} {coord[0]:.4f} {coord[1]:.4f} {coord[2]:.4f}\n"

        # Ensure the /static/tmp/ directory exists
        tmp_dir = os.path.join('static', 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Save the XYZ content to a file in /static/tmp/
        temp_file_path = os.path.join(tmp_dir, 'input.xyz')
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(xyz_content)

        return jsonify({'xyz_content': xyz_content, 'file_path': temp_file_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    xyz_content = data.get('xyz_content')
    method = data.get('method', 'L-BFGS-B')  # Default to "L-BFGS-B" if not provided

    if not xyz_content:
        return jsonify({'error': 'XYZ content is required'}), 400

    try:
        # Define the path to the existing input.xyz file in /static/tmp/
        tmp_dir = os.path.join('static', 'tmp')
        temp_file_path = os.path.join('static', 'tmp', 'input.xyz')

        # Ensure the file exists
        if not os.path.exists(temp_file_path):
            return jsonify({'error': f"File not found: {temp_file_path}"}), 400

        # Optimize the structure with the selected method
        print(f"Optimizing structure using input file: {temp_file_path} and method: {method}")
        
        # Call optimize_structure and get the execution time
        _, execution_time = optimize_structure(temp_file_path, method=method)

        # Move the optimized file to the /static/tmp/ directory
        optimized_file_source = os.path.join('opt-input.xyz')
        optimized_file_destination = os.path.join(tmp_dir, 'opt-input.xyz')
        os.rename(optimized_file_source, optimized_file_destination)
        
        # Define the expected output file path
        optimized_file_path = os.path.join(tmp_dir, 'opt-input.xyz')

        if not os.path.exists(optimized_file_path):
            print(f"Optimization failed. File not found: {optimized_file_path}")
            return jsonify({'error': 'Optimization failed. No output file generated.'}), 500

        # Read the optimized content
        with open(optimized_file_path, 'r') as optimized_file:
            optimized_xyz_content = optimized_file.read()

        # Send success message with execution time
        success_message = f"Optimization successful. Executed in {execution_time:.4f} seconds."
        print(success_message)
        return jsonify({'optimized_xyz_content': optimized_xyz_content, 'message': success_message})
    except Exception as e:
        print(f"Error during optimization: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)
