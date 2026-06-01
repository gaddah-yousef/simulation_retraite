"""
Module statistiques.py
Moyennes, ecart-types et intervalles de confiance a 95%.
"""

import math

Z = 1.96  # quantile 97.5% loi normale


def moyenne(valeurs):
    return sum(valeurs) / len(valeurs) if valeurs else 0.0


def ecart_type(valeurs):
    """Ecart-type empirique (non biaise, n-1)."""
    n = len(valeurs)
    if n < 2:
        return 0.0
    m = moyenne(valeurs)
    return math.sqrt(sum((x - m) ** 2 for x in valeurs) / (n - 1))


def intervalle_confiance(valeurs, z=Z):
    """
    Calcule l'IC a 95% : [m - z*s/sqrt(n), m + z*s/sqrt(n)].
    Retourne (m, ic_inf, ic_sup, largeur).
    """
    n = len(valeurs)
    m = moyenne(valeurs)
    s = ecart_type(valeurs)
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0
    demi = z * s / math.sqrt(n)
    return m, m - demi, m + demi, 2 * demi


def aggreger_simulations(liste_resultats, annees, indicateurs):
    """
    A partir d'une liste de dicts { annee : { indicateur : valeur } },
    retourne un dict { indicateur : { annee : [val_sim1, val_sim2, ...] } }.
    """
    out = {ind: {a: [] for a in annees} for ind in indicateurs}
    for res in liste_resultats:
        for a in annees:
            for ind in indicateurs:
                out[ind][a].append(res[a][ind])
    return out


def moyennes_par_annee(aggregat, indicateur, annees):
    """Liste de moyennes [moy(annee_1), moy(annee_2), ...]."""
    return [moyenne(aggregat[indicateur][a]) for a in annees]


def ic_par_annee(aggregat, indicateur, annees):
    """Liste [(m, inf, sup, larg), ...] pour chaque annee."""
    return [intervalle_confiance(aggregat[indicateur][a]) for a in annees]
