import autograd.numpy as np
from autograd import elementwise_grad as egrad
from autograd import hessian as hess


parameters = {
    # A, XI: Coehesive energy (eV)
    # P, Q: Indepent elastic constants
    # R0: Lattice parameter (Å)
    #         A         XI       P        Q        R0
    "Fe-Fe": (0.13315, 1.6179,  10.5000, 2.6000,  2.5530),
    "Fe-Co": (0.11246, 1.5515,  11.0380, 2.4379,  2.5248),
    "Co-Fe": (0.11246, 1.5515,  11.0380, 2.4379,  2.5248),
    "Fe-Ni": (0.07075, 1.3157,  13.3599, 1.7582,  2.5213),
    "Ni-Fe": (0.07075, 1.3157,  13.3599, 1.7582,  2.5213),
    "Co-Co": (0.09500, 1.4880,  11.6040, 2.2860,  2.4970),
    "Co-Ni": (0.05970, 1.2618,  14.0447, 1.6486,  2.4934),
    "Ni-Co": (0.05970, 1.2618,  14.0447, 1.6486,  2.4934),
    "Ni-Ni": (0.03760, 1.0700,  16.9990, 1.1890,  2.4900),
    "Cu-Cu": (0.08550, 1.2240,  10.9600, 2.2780,  2.5562),
    "Cu-Pd": (0.13005, 1.4710,  10.9135, 3.0100,  2.65235),
    "Pd-Cu": (0.13005, 1.4710,  10.9135, 3.0100,  2.65235),
    "Cu-Ag": (0.09800, 1.2274,  10.7000, 2.8050,  2.7224),
    "Ag-Cu": (0.09800, 1.2274,  10.7000, 2.8050,  2.7224),
    "Cu-Pt": (0.16000, 1.8200,  10.7860, 3.1410,  2.6660),
    "Pt-Cu": (0.16000, 1.8200,  10.7860, 3.1410,  2.6660),
    "Cu-Au": (0.15390, 1.5605,  11.0500, 3.0475,  2.5562),
    "Au-Cu": (0.15390, 1.5605,  11.0500, 3.0475,  2.5562),
    "Pd-Pd": (0.17460, 1.7180,  10.8670, 3.7420,  2.7485),
    "Pd-Ag": (0.16100, 1.5597,  10.8950, 3.4920,  2.8185),
    "Ag-Pd": (0.16100, 1.5597,  10.8950, 3.4920,  2.8185),
    "Pd-Pt": (0.23000, 2.2000,  10.7400, 3.8700,  2.7600),
    "Pt-Pd": (0.23000, 2.2000,  10.7400, 3.8700,  2.7600),
    "Pd-Au": (0.19000, 1.7500,  10.5400, 3.8900,  2.8160),
    "Au-Pd": (0.19000, 1.7500,  10.5400, 3.8900,  2.8160),
    "Ag-Ag": (0.10280, 1.1780,  10.9280, 3.1390,  2.8885),
    "Ag-Pt": (0.17500, 1.7900,  10.7300, 3.5900,  2.8330),
    "Pt-Ag": (0.17500, 1.7900,  10.7300, 3.5900,  2.8330),
    "Ag-Au": (0.14900, 1.4874,  10.4940, 3.6070,  2.8864),
    "Au-Ag": (0.14900, 1.4874,  10.4940, 3.6070,  2.8864),
    "Pt-Pt": (0.29750, 2.6950,  10.6120, 4.0040,  2.7747),
    "Pt-Au": (0.25000, 2.2000,  10.4200, 4.0200,  2.8300),
    "Au-Pt": (0.25000, 2.2000,  10.4200, 4.0200,  2.8300),
    "Au-Au": (0.20610, 1.7900,  10.2290, 4.0360,  2.8843),
    # "Al-Al": (0.07690, 1.1280,  15.1194, 1.9300,  0.9787)  # TODO: Fix parameters for Al-Al interaction
}


class Gupta:
    '''Python implementation of the Gupta potential for transition metals systems [1].
    
    Supports interactions between the following atomic pairs:
    - Fe, Co, and Ni
    - Cu, Pd, Ag, Pt, and Au.
    - Al # TODO: Fix parameters for Al-Al interaction
    
    Args:
        atoms: (list[str]) List of atomic symbols.
        
    Example:
        Variables:
            atoms = ["Fe", "Co", "Ni"]
            coord = np.array([[1.0, 0.0, 0.0],
                              [0.0, 1.0, 0.0],
                              [0.0, 0.0, 1.0]])
        Instance:
            gupta = Gupta(atoms)
        Methods:
            potential = gupta.potential(coord) # Calculate the potential energy (float)
            gradient = gupta.gradient(coord) # Calculate the gradient vector (np.ndarray)
            hessian = gupta.hessian(coord) # Calculate the hessian matrix (np.ndarray)
    '''

    def __init__(self, atoms: list[str]) -> None:
        self.atoms = atoms
        
        n = len(atoms)
        idx_ij = []
        atom_ij = []

        # https://docs.scipy.org/doc/scipy/reference/spatial.distance.html also
        # uses this ordering
        for i in range(n - 1):
            for j in range(i + 1, n):
                idx_ij.append([i, j])
                atom_ij.append((atoms[i], atoms[j]))
        
        arr_ij = np.array(idx_ij, dtype=int)
        self.ai = arr_ij[:, 0]
        self.aj = arr_ij[:, 1]

        # Access parameters using a more readable format with tuples
        self.A, self.XI, self.P, self.Q, self.R0 = zip(*[
            parameters[f"{aij[0]}-{aij[1]}"] for aij in atom_ij
        ])

        # Convert to numpy arrays for calculations
        self.A = np.array(self.A, dtype=float)
        self.XI = np.array(self.XI, dtype=float)
        self.P = np.array(self.P, dtype=float)
        self.Q = np.array(self.Q, dtype=float)
        self.R0 = np.array(self.R0, dtype=float)

        # Calculate these once instead of every time in potential
        self.XI2 = self.XI**2
        self.nP = -self.P
        self.nQ2 = -self.Q * 2

        # Ensure i < j for correct position in the upper triangular matrix
        def idx(i, j):
            if j < i:
                i, j = j, i
            return n * i + j - ((i + 2) * (i + 1)) // 2
        
        # Create a pairwise interaction matrix
        self.pairwise = np.array([[idx(i, j) for j in range(n) if i != j] for i in range(n)])

        # Precompute the gradient and hessian functions of the potential
        self.gradient = egrad(self.potential)
        self.hessian = hess(self.potential)


    def potential(self, coords: np.ndarray) -> float:
        """
        Calculate the potential energy of the system based on the given coordinates.

        Args:
            coords: A matrix with shape (n, 3) (np.ndarray).

        Returns:
            The calculated potential energy (float).

        Reference:
            [1] Raju P. Gupta
                Lattice relaxation at a metal surface
                Phys. Rev. B 23, 6265 - Published 15 June 1981
                https://doi.org/10.1103/PhysRevB.23.6265
        """
        dist = np.linalg.norm(coords[self.ai] - coords[self.aj], axis=1)
        norm = dist / self.R0 - 1.0
        Ub = self.XI2 * np.exp(self.nQ2 * norm)
        Ur = self.A * np.exp(self.nP * norm)
        U: float = 2.0 * np.sum(Ur)
        U -= np.sum(np.sqrt(np.sum(Ub[self.pairwise], axis=1)))
        return U
    

    def gradient(self, coords: np.ndarray) -> np.ndarray:
        """
        Compute the gradient of the potential with respect to atomic coordinates.

        Args:
            coords: A matrix with shape (n, 3) (np.ndarray).

        Returns:
            The gradient matrix of the potential with shape (n, 3) (np.ndarray).
        """
        return egrad(self.potential)(coords)


    def hessian(self, coords: np.ndarray) -> np.ndarray:
        """
        Calculate the Hessian matrix of the potential at the given coordinates.

        Args:
            coords: A matrix with shape (3n, 3n) (np.ndarray).

        Returns:
            The Hessian matrix of the potential with shape (3n, 3n) (np.ndarray).
        """
        return hess(self.potential)(coords)
