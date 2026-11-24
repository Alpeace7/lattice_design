import numpy as np
import at 
from . import at as u_at

from scipy.optimize import NonlinearConstraint
from IPython.display import clear_output

def callback(intermediate_result):
    clear_output(wait=True)
    print('Running...')
    print(intermediate_result)

def get_index(ring, names):
    """Return unique lattice indices for elements whose FamName is in names."""
    names = set(names)
    indices = []

    for i, element in enumerate(ring):
        if element.FamName not in names:
            continue

        # Skip repeated references to the same underlying element.
        if any(element is ring[j] for j in indices):
            continue

        indices.append(i)

    return np.asarray(indices, dtype=np.uint32)


def set_x(ring, x, index_rho, index_K):
    # Unpack
    L = x[0]
    rho_inv = x[1:len(index_rho)+1]
    K = x[len(index_rho)+1:]

    for e in ring['strx203']: e.Length = L
    for i, e in enumerate(ring[index_rho]): e.BendingAngle = e.Length * rho_inv[i]
    for i, e in enumerate(ring[index_K]): e.K = K[i]


def get_x(ring, index_rho, index_K):
    L = ring['strx203'][0].Length

    rho_inv = [ring[i].BendingAngle/ring[i].Length for i in index_rho]
    K       = [ring[i].K                           for i in index_K]

    return np.array([L] + rho_inv + K)


def emittance(x, ring, index_rho, index_K, invalid=1e4):
    # Set fields
    set_x(ring, x, index_rho, index_K)

    try:
        emittance = 1e12 * ring.radiation_parameters().emittances[0]
    except Exception as e:
        emittance = invalid

    return emittance


def ID_constraints(ring, index_rho, index_K, lb=0, ub=0):
    """Constrain ID geometry and dispersion values."""
    def values(x):
        set_x(ring, x, index_rho, index_K)

        geometry = ring.get_geometry(at.End)[0]
        x_end = geometry.x[0] - u_at.geometry.x[0]
        theta_UC = geometry.angle[0] - u_at.geometry.angle[0]

        elemdata = at.linopt2(ring, at.All, orbit=np.zeros(6))[2]
        D0, Dp0 = elemdata.dispersion[0, 0:2]

        return np.array([x_end, theta_UC, D0, Dp0])

    return NonlinearConstraint(values, lb=lb, ub=ub)


def tune_constraints(ring, index_rho, index_K, lb=-np.inf, ub=np.inf):
    """Constrain the full-ring tunes."""
    def values(x):
        set_x(ring, x, index_rho, index_K)
        elemdata = at.linopt2(ring, at.All, orbit=np.zeros(6))[2]
        return 20 * elemdata.mu[-1] / (2 * np.pi)

    return NonlinearConstraint(values, lb=lb, ub=ub)


def UC_constraints(ring, index_rho, index_K, lb=[0.399, 0.099], ub=[0.401, 0.101]):
    """Constrain the phase advances for each unit cell."""
    index_UC = ring.get_uint32_index('UCborder')
    
    def values(x):
        set_x(ring, x, index_rho, index_K)
        elemdata = at.linopt2(ring, index_UC, orbit=np.zeros(6))[2]
        return np.diff(elemdata.mu, axis=0).flatten() / (2 * np.pi)

    return NonlinearConstraint(values, lb=np.tile(lb, 5), ub=np.tile(ub, 5))

def mcf_constraints(ring, index_rho, index_K, lb=-np.inf, ub=np.inf):
    """Constrain the linear momentum compaction factor."""
    def values(x):
        set_x(ring, x, index_rho, index_K)
        return ring.get_mcf()

    return NonlinearConstraint(values, lb=lb, ub=ub)


def D1_constraints(ring, index_rho, index_K, lb=-np.inf, ub=np.inf):
    """Constrain the total D1 bending angle in degrees."""
    def values(x):
        set_x(ring, x, index_rho, index_K)
        return np.degrees(sum(e.BendingAngle for e in ring if hasattr(e, "BendingAngle") and e.FamName.startswith("D1_"))) / 2

    return NonlinearConstraint(values, lb=lb, ub=ub)


def D1_constraints(ring, index_rho, index_K, lb=-np.inf, ub=np.inf):
    """Constrain the total D1 bending angle in degrees."""

    def values(x):
        set_x(ring, x, index_rho, index_K)
        return np.degrees(sum(
            e.BendingAngle for e in ring
            if hasattr(e, "BendingAngle") and e.FamName.startswith("D1_")
        )) / 2

    return NonlinearConstraint(values, lb=lb, ub=ub)

def get_bounds(ring, index_rho, index_K, **family_bounds):
    """Build optimizer bounds for [L, rho_inv..., K...].

    Family overrides use (rho_min, rho_max, K_min, K_max).
    """
    bounds = [(None, None)] * (1 + len(index_rho) + len(index_K))

    for i, index in enumerate(index_rho, start=1):
        fam_name = ring[index].FamName
        for family, (rho_min, rho_max, _, _) in family_bounds.items():
            if family in fam_name:
                bounds[i] = (rho_min, rho_max)
                break

    k_offset = 1 + len(index_rho)
    for i, index in enumerate(index_K, start=k_offset):
        fam_name = ring[index].FamName
        for family, (_, _, k_min, k_max) in family_bounds.items():
            if family in fam_name:
                bounds[i] = (k_min, k_max)
                break

    return bounds