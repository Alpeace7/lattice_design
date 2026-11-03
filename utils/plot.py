import numpy as np
import at
import matplotlib.pyplot as plt

import pickle

""" Helper functions """
def align_twin(ax, twin, padding=0.05):
    """ Aligns the zeroes of a main and twin axes. """
    # Get data limits with padding
    y1_min, y1_max = ax.dataLim.intervaly
    y2_min, y2_max = twin.dataLim.intervaly

    p1 = padding * (y1_max - y1_min)
    p2 = padding * (y2_max - y2_min)
    y1_min, y1_max = y1_min - p1, y1_max + p1
    y2_min, y2_max = y2_min - p2, y2_max + p2

    # Fraction of axis height below zero
    f = np.clip(max(
        -y1_min / (y1_max - y1_min),
        -y2_min / (y2_max - y2_min),
    ), 0, 1)

    # Expand limits to align zeroes
    span1 = max(
        y1_max / (1 - f) if f < 1 else 0,
        -y1_min / f if f > 0 else 0,
    )
    span2 = max(
        y2_max / (1 - f) if f < 1 else 0,
        -y2_min / f if f > 0 else 0,
    )

    ax.set_ylim(-f * span1, (1 - f) * span1)
    twin.set_ylim(-f * span2, (1 - f) * span2)


def meshgrid_extent(X, Y, origin='lower'):
    """
    Return an imshow extent that centers pixels on meshgrid coordinates.
    """
    x = X[0, :]
    y = Y[:, 0]

    dx = np.diff(x)
    dy = np.diff(y)

    if not np.allclose(dx, dx[0]) or not np.allclose(dy, dy[0]):
        raise ValueError("Meshgrids must be evenly spaced.")

    dx = dx[0]/2
    dy = dy[0]/2

    extent = np.array([x.min() - dx, x.max() + dx, y.min() - dy, y.max() + dy])

    if origin == 'lower':
        extent[[2, 3]] = extent[[3, 2]]
    elif origin != 'upper':
        raise ValueError("origin must be 'lower' or 'upper'.")

    return extent


""" Standard plots """
def linear(ring: at.lattice, ring0='TDR-1', ax=None, twin=None, UC_tunes=True, **kwargs):
    if ax is None:
        fig, ax = plt.subplots()

    if twin is None:
        twin = ax.twinx()

    """ Calculation """
    elemdata = at.linopt4(ring, at.All)[2]
    s = elemdata.s_pos

    """ Plotting """
    ax.plot(s, elemdata.beta[:, 0], c='tab:blue', **kwargs)
    ax.plot(s, elemdata.beta[:, 1], c='tab:orange', **kwargs)
    twin.plot(s, elemdata.dispersion[:, 0], c='tab:green', **kwargs)

    ax.set_xlabel(r'$s$ [m]')
    ax.set_ylabel(r'$\beta$ [m]')
    twin.set_ylabel(r'$D_x$ [m]')

    """ Unit cell tunes """
    index_UC = at.get_uint32_index(ring, 'UCborder')
    if 0 not in index_UC:
        index_UC = np.array([0, *index_UC])
    if len(ring) not in index_UC:
        index_UC = np.array([*index_UC, len(ring)])

    if UC_tunes and len(index_UC) >= 2:
        for i, index in enumerate(index_UC[:-1]):
            Q_UC = np.round((elemdata.mu[index] - elemdata.mu[index_UC[i-1]])/(2*np.pi), 3)
            
            s_mid = np.mean(s[index_UC[i-1:i+1]])
            ax.text(s_mid, ax.get_ylim()[1], f'{Q_UC[0]}\n{Q_UC[1]}', ha='center', va='top')
            plt.axvline(s[index], linewidth=1, color='black')
   
        Q = 20*elemdata.mu[-1]/(2*np.pi)
        s_mid = np.mean(s[index_UC[-2:]])
        plt.axvline(s[index], linewidth=1, color='black')
        ax.text(s_mid, ax.get_ylim()[1], f'$Q_x={Q[0]:.3f}$\n$Q_y={Q[1]:.3f}$', ha='center', va='top')

    # Axis limits
    ax.set_xlim(s.min(), s.max())
    align_twin(ax, twin)

    """ Plot baseline """
    if ring0 is not None:
        if ring0 == 'TDR-1':
            with open('candidates/n01_02_01_01/ring.pkl', 'rb') as file:
                ring0 = pickle.load(file)

        linear(ring0, None, ax, twin, UC_tunes=False, ls='--')

    return ax, twin

def plot_magnet(lattice, axs=None):
    """Plot the longitudinal field profile of a """
    if axs is None:
        fig, axs = plt.subplots(2, 1)

    if type(lattice) != at.Lattice:
        lattice = at.Lattice([lattice], energy=3000000000.0)
    s_D2 = at.get_s_pos(lattice)

    angle_dist = [e.BendingAngle/e.Length if hasattr(e, 'BendingAngle') else 0 for e in lattice]
    K_dist = [e.PolynomB[1] if hasattr(e, 'PolynomB') else 0 for e in lattice]

    axs[0].stairs(angle_dist, s_D2)
    axs[1].stairs(K_dist, s_D2)

    axs[0].set_ylabel('Bending strength [$^{-1}$]')
    axs[1].set_ylabel('K [m$^{-2}$]')
    axs[1].set_xlabel('$s$ [m]')