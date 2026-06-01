"""
Module alea.py
Generateur de nombres pseudo-aleatoires impose par le projet.
"""


def alea(IX, IY, IZ):
    """
    Generateur de nombres pseudo-aleatoires base sur trois germes (Wichmann-Hill).

    Parametres
    ----------
    IX, IY, IZ : int
        Germes courants, doivent etre compris entre 1 et 30000.

    Retourne
    --------
    u : float
        Nombre pseudo-aleatoire dans [0, 1).
    IX, IY, IZ : int
        Nouveaux germes pour le prochain appel.
    """
    IX = 171 * (IX % 177) - 2 * (IX // 177)
    IY = 172 * (IY % 176) - 35 * (IY // 176)
    IZ = 170 * (IZ % 178) - 63 * (IZ // 178)

    if IX < 0:
        IX += 30269
    if IY < 0:
        IY += 30307
    if IZ < 0:
        IZ += 30323

    u = (IX / 30269.0 + IY / 30307.0 + IZ / 30323.0) % 1.0
    return u, IX, IY, IZ


def valider_germes(IX, IY, IZ):
    """Verifie que les germes sont valides (entre 1 et 30000)."""
    for nom, val in (("IX", IX), ("IY", IY), ("IZ", IZ)):
        if not (1 <= val <= 30000):
            raise ValueError(f"La germe {nom}={val} doit etre entre 1 et 30000.")
    return True


def germes_simulation_i(IX0, IY0, IZ0, i):
    """
    Calcule les germes pour la i-eme simulation (i >= 1).
    Regle : IXi = IX0 + (i-1)*3, IYi = IY0 + (i-1)*5, IZi = IZ0 + (i-1)*7
    Les valeurs sont ramenees dans [1, 30000] par modulo si necessaire.
    """
    IXi = ((IX0 + (i - 1) * 3 - 1) % 30000) + 1
    IYi = ((IY0 + (i - 1) * 5 - 1) % 30000) + 1
    IZi = ((IZ0 + (i - 1) * 7 - 1) % 30000) + 1
    return IXi, IYi, IZi
