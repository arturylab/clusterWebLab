# Script to optimize atomic structures from an XYZ file using the Gupta potential
import argparse
import scipy.optimize as spo
from autograd import elementwise_grad as egrad
from potentials.gupta import Gupta
from read_xyz import read_xyz_file
from write_xyz import write_xyz_file
from static.src.timer import timeit

@timeit
def optimize_structure(file_path, method="L-BFGS-B"):
    """Optimize the atomic structure from an XYZ file using the Gupta potential.
    
    Args:
        file_path (str): Path to the input XYZ file.
    
    Returns:
        None: Saves the optimized structure to a new XYZ file.
    """
    atoms, coords = read_xyz_file(file_path)
    
    gupta = Gupta(atoms)
    potential = lambda x: gupta.potential(x.reshape(len(coords), 3))
    
    # If the optimization method is "L-BFGS-B", use the scipy.optimize.minimize function
    if method == "L-BFGS-B":
        sol = spo.minimize(
            potential,  # The potential energy function to minimize
            coords.flatten(),  # Initial guess for the atomic coordinates (flattened)
            method='L-BFGS-B',  # Optimization method
            jac=egrad(potential),  # Gradient of the potential energy function
            options={
                "gtol": 1e-8,  # Gradient tolerance for convergence
                "maxiter": 1000,  # Maximum number of iterations
                "disp": False,  # Suppress output display
            })
    
    # If the optimization method is "basinhopping", use the scipy.optimize.basinhopping function
    elif method == 'basinhopping':
        sol = spo.basinhopping(
                potential,  # The potential energy function to minimize
                coords.flatten(),  # Initial guess for the atomic coordinates (flattened)
                minimizer_kwargs={
                    "method": "L-BFGS-B",  # Local minimization method
                    "jac": egrad(potential),  # Gradient of the potential energy function
                },
                niter=250,  # Number of basin-hopping iterations
                disp=False)  # Suppress output display
        
    new_coords = sol.x.reshape(-1, 3)
    energy = sol.fun
    
    output_file = f"opt-{file_path.split('/')[-1]}"
    write_xyz_file(output_file, atoms, new_coords, energy)
    
    print(f"Optimization complete. Output saved to {output_file}")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Optimize atomic structure from an XYZ file.")
        parser.add_argument("file", type=str, help="Path to the XYZ file.")
        parser.add_argument("--method", type=str, default="L-BFGS-B", choices=["L-BFGS-B", "basinhopping"],
                            help="Optimization method to use. Default is 'L-BFGS-B'.")
        args = parser.parse_args()
        
        if not args.file:
            raise ValueError("No file path provided. Please specify the path to an XYZ file.")
        
        optimize_structure(args.file, method=args.method)
    except Exception as e:
        print(f"Error: {e}")
