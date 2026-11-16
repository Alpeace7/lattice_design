import numpy as np
import at
from copy import deepcopy
import pickle

with open('candidates/n01_02_01_01/ring.pkl', 'rb') as file:
    TDR_1 = pickle.load(file)

geometry = TDR_1.get_geometry(at.End)[0] # The required endpoint geometry


def replace_family(ring: at.Lattice, FamName: str, replacement: at.Lattice, pad=True, alternate=False):
    """Replaces all instances of a family with a replacement.

    Consecutive instances of ``FamName`` are treated as a single group.
    If ``pad=True``, a drift is appended to the replacement such that the
    total length of the replaced section is preserved.

    Parameters
    ----------
    ring : at.Lattice
        Lattice to modify.
    FamName : str
        Family name to replace.
    replacement : at.Lattice
        Lattice used as the replacement.
    pad : bool, optional
        If True, preserve the length of each replaced section with a drift.
    alternate : bool, optional
        If true, reverse the longitudinal field profile of every other section. 

    Returns
    -------
    at.Lattice
        Modified copy of the input lattice.
    """

    # Guarantee no side effects
    ring = deepcopy(ring)
    replacement = deepcopy(replacement)

    # Guarantee replacement is an at.Lattice
    if type(replacement) != at.Lattice:
        replacement = at.Lattice([replacement], energy=ring.energy)

    index = ring.get_uint32_index(FamName)

    if len(index) == 0:
        return ring

    # Split into consecutive groups
    splits = np.where(np.diff(index) != 1)[0] + 1
    index_grouped = np.split(index, splits)

    L_replacement = replacement.get_s_pos()[-1]

    # Build replacement sections
    ring_parts = []
    index = 0

    order = 1
    for group in index_grouped:
        # Add elements before this group
        ring_parts.append(ring[index:group[0]])

        # Padding
        L = ring[group].get_s_pos()[-1]
        L_pad = (L - L_replacement)/2
        name = 'strx' + f'{L_pad:.3f}'.removeprefix('0').replace('.', '')
        drift = at.Drift(name, L_pad)
        if np.isclose(L_pad, 0): pad = False
        
        # Append replacement (with padding if appropriate)
        if pad: ring_parts.append([drift])
        ring_parts.append(replacement[::order])
        if pad: ring_parts.append([drift])

        if alternate: order *= -1

        index = group[-1] + 1

    # Add remaining elements
    ring_parts.append(ring[index:])

    # Concatenate into a new lattice
    ring = at.Lattice(
        [elem for part in ring_parts for elem in part],
        energy=ring.energy,
        periodicity=ring.periodicity
    )

    return ring

def set_PolynomB_scale(scaling, ring, refpts, PolynomB0):
    """"""
    assert PolynomB0 != None

    for element, PolynomB in zip(ring[refpts], PolynomB0):
        element.PolynomB = scaling * PolynomB

def get_PolynomB_scale(ring, refpts, PolynomB0):
    scaling = []
    for element, PolynomB in zip(ring[refpts], PolynomB0):
        scaling = element.PolynomB / PolynomB

    return np.nanmean(scaling)

def get_length(lattice: at.Lattice|at.Element):
    """ The total length of the elements in a lattice. Does not account for periodicity. """
    if type(lattice) == at.Lattice:
        return lattice.get_s_pos()[-1]
    else:
        return lattice.Length

def summary(ring):
    """ Print a short summary of relevant design parameters. """
    # TODO: Add more parameters
    emittance = at.radiation_parameters(ring).emittances[0]
    Qx, Qy = at.get_tune(ring, get_integer=True)
    mcf = at.get_mcf(ring, fit_order=3, n_step=9)
    D1_angle = np.degrees(np.sum([e.BendingAngle for e in ring if 'D1' in e.FamName]))/2
    s_cro = np.mean([ring.get_s_pos('GE')[0], ring.get_s_pos('GS')[1]]) # TODO: Check s coordinate
    sep_cro = -np.interp(s_cro, ring.get_s_pos(), ring.get_geometry()[0].y)

    print(f'Emittance                  : {1e12*emittance:.1f} pm.rad')
    print(f'Tunes                      : [{Qx:.3f}, {Qy:.3f}]')
    print(f'Momentum compaction        : {mcf[0]:.2e} d {mcf[1]:+.2e} d^2 {mcf[2]:+.2e} d^3')
    print(f'D1 angle                   : {D1_angle:.3f} degrees')
    print(f'Crotch absorber separation : {1e3*sep_cro:.2f} mm')

