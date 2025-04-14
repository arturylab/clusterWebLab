# Script to optimize atomic structures from an XYZ file using the Gupta potential
import argparse
import scipy.optimize as spo
from autograd import elementwise_grad as egrad
from potentials.gupta import Gupta
from read_xyz import read_xyz_file
from write_xyz import write_xyz_file
from static.src.timer import timeit
from typing import Tuple

@timeit
def optimize_structure(file_path: str, method: str = "L-BFGS-B") -> Tuple[float, float]:
    """
    Optimize the atomic structure from an XYZ file using the Gupta potential.

    Args:
        file_path (str): Path to the input XYZ file containing atomic structure.
        method (str): Optimization method to use. Options are "L-BFGS-B" or "basinhopping".
                      Default is "L-BFGS-B".

    Returns:
        Tuple[float, float]: A tuple containing the old energy and the new energy of the structure.
    """
    # Read atomic data and coordinates from the XYZ file
    atoms, coords = read_xyz_file(file_path)
    
    # Initialize the Gupta potential with the atomic data
    gupta = Gupta(atoms)
    
    # Define the potential energy function
    potential = lambda x: gupta.potential(x.reshape(len(coords), 3))
    
    # Calculate the initial energy of the structure
    old_energy = potential(coords.flatten())
    
    # Perform optimization based on the selected method
    if method == "L-BFGS-B":
        # Use the L-BFGS-B optimization method
        sol = spo.minimize(
            potential,
            coords.flatten(),
            method='L-BFGS-B',
            jac=egrad(potential),  # Gradient of the potential
            options={
                "gtol": 1e-8,  # Gradient tolerance
                "maxiter": 1000,  # Maximum number of iterations
                "disp": False,  # Suppress output
            })
    elif method == 'basinhopping':
        # Use the basinhopping optimization method
        sol = spo.basinhopping(
                potential,
                coords.flatten(),
                minimizer_kwargs={
                    "method": "L-BFGS-B",
                    "jac": egrad(potential),
                },
                niter=250,  # Number of iterations for basinhopping
                disp=False)  # Suppress output
        
    # Extract the optimized coordinates and energy
    new_coords = sol.x.reshape(-1, 3)
    new_energy = sol.fun
    
    # Generate the output file name and save the optimized structure
    output_file = f"opt-{file_path.split('/')[-1]}"
    write_xyz_file(output_file, atoms, new_coords, new_energy)
    
    # Print the results of the optimization
    print(f"Old energy: {old_energy} eV | New energy: {new_energy} eV")
    print(f"Optimization complete. Output saved to {output_file}")
    
    return (old_energy, new_energy)

if __name__ == "__main__":
    try:
        # Set up argument parser for command-line usage
        parser = argparse.ArgumentParser(description="Optimize atomic structure from an XYZ file.")
        parser.add_argument("file", type=str, help="Path to the XYZ file.")
        parser.add_argument("--method", type=str, default="L-BFGS-B", choices=["L-BFGS-B", "basinhopping"],
                            help="Optimization method to use. Default is 'L-BFGS-B'.")
        args = parser.parse_args()
        
        # Ensure a file path is provided
        if not args.file:
            raise ValueError("No file path provided. Please specify the path to an XYZ file.")
        
        # Call the optimization function with the provided arguments
        optimize_structure(args.file, method=args.method)
    except Exception as e:
        # Handle and display any errors that occur
        print(f"Error: {e}")
