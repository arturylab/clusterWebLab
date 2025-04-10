# Generate random coordinates for a given number of atoms and create an xyz file.
# script.py
import sys
import re
import numpy as np
from write_xyz import write_xyz_file

def parse_atom_sequence(sequence: str) -> list[str]:
    """
    Parse an atom sequence like Fe2Co10Ni or FeCoNi into a list of atoms.
    
    Args:
        sequence: input sequence (e.g., Fe2Co10Ni).
    Returns:
        List of atoms (e.g., ['Fe', 'Fe', 'Co', 'Co', ..., 'Ni']).
    """
    # Regex to match atom symbols and optional counts
    pattern = re.compile(r"([A-Z][a-z]?)(\d*)")
    atoms = []
    for match in pattern.finditer(sequence):
        atom = match.group(1)  # Atom symbol (e.g., Fe, Co, Ni)
        count = match.group(2)  # Optional count (e.g., 2, 10)
        count = int(count) if count else 1  # Default to 1 if no count is provided
        atoms.extend([atom] * count)  # Add the atom 'count' times to the list
    return atoms

def generate_random_coordinates(num_atoms: int) -> np.ndarray:
    """
    Generate random coordinates for a given number of atoms.
    
    Args:
        num_atoms: number of atoms.
    Returns:
        Array of random coordinates.
    """
    return np.random.uniform(low=-5.0, high=5.0, size=(num_atoms, 3))

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <atom_sequence>")
        print("Example: python script.py Fe2Co10Ni")
        sys.exit(1)
    
    atom_sequence = sys.argv[1]
    atoms = parse_atom_sequence(atom_sequence)
    num_atoms = len(atoms)
    
    # Generate random coordinates
    coords = generate_random_coordinates(num_atoms)
    
    # Create the output file name
    output_file = f"rnd-{atom_sequence.lower()}.xyz"
    
    # Create the xyz file
    write_xyz_file(output_file, atoms, coords, comment="Randomly generated coordinates")
    
    print(f"XYZ file '{output_file}' created successfully with {num_atoms} atoms.")

if __name__ == "__main__":
    main()