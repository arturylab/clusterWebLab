import numpy as np

def read_xyz_file(path: str) -> tuple[list[str], np.ndarray]:
    """
    Read an xyz file and return atoms types and the coordinates.

    Args:
        file: path to the xyz file.

    Returns:
        A tuple containing the coordinates (np.ndarray) and atom types (list[str]).
    """
    atoms = []
    coordinates = []
    with open(path, "r") as file:
        for i, line in enumerate(file):
            if i < 2:
                continue
            atom, *xyz = line.split()
            atoms.append(atom)
            coordinates.append(xyz)
    
    return atoms, np.array(coordinates, dtype=float)
