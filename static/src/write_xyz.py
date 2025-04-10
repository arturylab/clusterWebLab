import numpy as np


def write_xyz_file(path: str, atoms: list[str], coords: np.ndarray, comment: str = "") -> None:
    """
    Write an xyz file with the given atoms and coordinates.
    
    Args:
        path: path to the xyz file.
        atoms: list of atom types.
        coords: array of coordinates.
        comment: optional comment line.
    Returns:
        None
    """
    with open(path, "w") as file:
        file.write(f"{len(atoms)}\n")
        file.write(f"{comment}\n")
        for atom, coord in zip(atoms, coords):
            file.write(f"{atom}   {'   '.join(map(str, coord))}\n")
