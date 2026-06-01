"""
Module distributions.py
Tables de distribution et fonctions de tirage selon ces tables.
Toutes les fonctions utilisent le generateur alea (et propagent IX, IY, IZ).
"""

from alea import alea


# ----------------------------------------------------------------------
# Tables de distribution (intervalle, frequence)
# Les intervalles sont des tuples (borne_inf, borne_sup).
# ----------------------------------------------------------------------

SALAIRES_ACTUELS = [
    ((80001, 120000), 0.01),
    ((40000, 80000), 0.03),
    ((30000, 40000), 0.05),
    ((20000, 30000), 0.05),
    ((15000, 20000), 0.10),
    ((10000, 15000), 0.20),
    ((7500, 10000), 0.20),
    ((5000, 7500), 0.20),
    ((3000, 5000), 0.16),
]

AGES_ACTUELS = [
    ((53, 63), 0.20),
    ((41, 52), 0.30),
    ((31, 40), 0.30),
    ((21, 30), 0.20),
]

AGES_EMBAUCHE = [
    ((21, 24), 0.05),
    ((25, 28), 0.30),
    ((29, 32), 0.30),
    ((33, 36), 0.15),
    ((37, 40), 0.15),
    ((41, 45), 0.05),
]

SALAIRES_EMBAUCHE = [
    ((32000, 50000), 0.02),
    ((24000, 32000), 0.05),
    ((16000, 24000), 0.05),
    ((12000, 16000), 0.10),
    ((8000, 12000), 0.20),
    ((6000, 8000), 0.20),
    ((4000, 6000), 0.20),
    ((3000, 4000), 0.18),
]


def tirer_intervalle(table, IX, IY, IZ):
    """
    Tire un intervalle selon la table de frequences cumulees.
    Puis tire uniformement une valeur reelle dans cet intervalle.

    Retourne (valeur, IX, IY, IZ).
    """
    u, IX, IY, IZ = alea(IX, IY, IZ)
    cum = 0.0
    intervalle = table[-1][0]
    for inter, freq in table:
        cum += freq
        if u <= cum:
            intervalle = inter
            break

    binf, bsup = intervalle
    u2, IX, IY, IZ = alea(IX, IY, IZ)
    valeur = binf + u2 * (bsup - binf)
    return valeur, IX, IY, IZ


def tirer_sexe(IX, IY, IZ, prob_homme=0.55):
    """Tire un sexe : 'H' avec proba 0.55, sinon 'F'."""
    u, IX, IY, IZ = alea(IX, IY, IZ)
    sexe = 'H' if u < prob_homme else 'F'
    return sexe, IX, IY, IZ


def tirer_uniforme_int(binf, bsup, IX, IY, IZ):
    """Tire un entier uniforme dans [binf, bsup] (inclus)."""
    u, IX, IY, IZ = alea(IX, IY, IZ)
    valeur = int(binf + u * (bsup - binf + 1))
    if valeur > bsup:
        valeur = bsup
    return valeur, IX, IY, IZ


def tirer_uniforme_float(binf, bsup, IX, IY, IZ):
    """Tire une valeur reelle uniforme dans [binf, bsup]."""
    u, IX, IY, IZ = alea(IX, IY, IZ)
    valeur = binf + u * (bsup - binf)
    return valeur, IX, IY, IZ


def bernoulli(prob, IX, IY, IZ):
    """Retourne True avec probabilite `prob`."""
    u, IX, IY, IZ = alea(IX, IY, IZ)
    return (u < prob), IX, IY, IZ
