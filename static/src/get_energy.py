# Script to compute the energy of an atomic structure using the Gupta potential
import argparse
from potentials.gupta import Gupta
from read_xyz import read_xyz_file

def compute_energy(file_path, print_coords=False):
    """Compute the energy of an atomic structure using the Gupta potential.
    
    Args:
        file_path (str): Path to the input XYZ file.
        print_coords (bool): If True, print the coordinates instead of the energy.
    
    Returns:
        None: Prints the energy in eV or the coordinates.
    """
    atoms, coords = read_xyz_file(file_path)
    gupta = Gupta(atoms)
    
    if print_coords:
        print("Coordinates:")
        print(coords)
    else:
        energy = gupta.potential(coords)
        print(f"Energy: {energy:.6f} eV")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Compute energy of an atomic structure from an XYZ file.")
        parser.add_argument("file", type=str, help="Path to the XYZ file.")
        parser.add_argument("--coords", action="store_true", help="If set, print the coordinates instead of energy.")
        args = parser.parse_args()
        
        if not args.file:
            raise ValueError("No file path provided. Please specify the path to an XYZ file.")
        
        compute_energy(args.file, print_coords=args.coords)
    except Exception as e:
        print(f"Error: {e}")
