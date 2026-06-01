"""
Module graphiques.py
Generation des graphiques matplotlib et sauvegarde au format PNG.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from statistiques import (
    aggreger_simulations,
    moyennes_par_annee,
    ic_par_annee,
)

ANNEES = list(range(2026, 2036))
INDIC_S1 = ['TotEmp', 'TotRet', 'TotCotis', 'TotPens', 'Reserve', 'NouvRet', 'NouvRec']
INDIC_S2 = ['TotEmp', 'Plus63', 'Plus63H', 'Plus63F', 'TotRet', 'TotCotis', 'TotPens', 'Reserve', 'NouvRet', 'NouvRec']


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _en_M(values):
    return [v / 1_000_000.0 for v in values]


def graph_reserve_ic(liste_resultats, scenario, path):
    """Courbe moyenne + bande IC 95% pour la reserve."""
    agg = aggreger_simulations(liste_resultats, ANNEES, ['Reserve'])
    ic = ic_par_annee(agg, 'Reserve', ANNEES)
    moy = [c[0] / 1e6 for c in ic]
    inf = [c[1] / 1e6 for c in ic]
    sup = [c[2] / 1e6 for c in ic]

    plt.figure(figsize=(10, 6))
    plt.plot(ANNEES, moy, marker='o', color='steelblue', label='Moyenne')
    plt.fill_between(ANNEES, inf, sup, alpha=0.25, color='steelblue', label='IC 95%')
    plt.title(f"Reserve - Scenario {scenario} (40 simulations)")
    plt.xlabel("Annee")
    plt.ylabel("Reserve (Mdhs)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def graph_totemp_totret(liste_resultats, scenario, path):
    agg = aggreger_simulations(liste_resultats, ANNEES, ['TotEmp', 'TotRet'])
    moy_emp = moyennes_par_annee(agg, 'TotEmp', ANNEES)
    moy_ret = moyennes_par_annee(agg, 'TotRet', ANNEES)

    plt.figure(figsize=(10, 6))
    plt.plot(ANNEES, moy_emp, marker='o', label='TotEmp (adherents)')
    plt.plot(ANNEES, moy_ret, marker='s', label='TotRet (retraites)')
    plt.title(f"Effectifs adherents vs retraites - Scenario {scenario}")
    plt.xlabel("Annee")
    plt.ylabel("Nombre")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def graph_cotis_pens(liste_resultats, scenario, path):
    agg = aggreger_simulations(liste_resultats, ANNEES, ['TotCotis', 'TotPens'])
    moy_c = _en_M(moyennes_par_annee(agg, 'TotCotis', ANNEES))
    moy_p = _en_M(moyennes_par_annee(agg, 'TotPens', ANNEES))

    plt.figure(figsize=(10, 6))
    plt.plot(ANNEES, moy_c, marker='o', label='TotCotis')
    plt.plot(ANNEES, moy_p, marker='s', label='TotPens')
    plt.title(f"Cotisations vs Pensions - Scenario {scenario}")
    plt.xlabel("Annee")
    plt.ylabel("Millions DH/an")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def graph_nouvret_nouvrec(liste_resultats, scenario, path):
    agg = aggreger_simulations(liste_resultats, ANNEES, ['NouvRet', 'NouvRec'])
    moy_r = moyennes_par_annee(agg, 'NouvRet', ANNEES)
    moy_c = moyennes_par_annee(agg, 'NouvRec', ANNEES)
    x = np.arange(len(ANNEES))
    w = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x - w / 2, moy_r, width=w, label='NouvRet', color='salmon')
    plt.bar(x + w / 2, moy_c, width=w, label='NouvRec', color='lightseagreen')
    plt.xticks(x, ANNEES)
    plt.title(f"Nouveaux retraites / Nouveaux recrutes - Scenario {scenario}")
    plt.xlabel("Annee")
    plt.ylabel("Nombre")
    plt.grid(True, axis='y', alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def graph_plus63(liste_resultats_s2, path):
    agg = aggreger_simulations(liste_resultats_s2, ANNEES, ['Plus63', 'Plus63H', 'Plus63F'])
    t = moyennes_par_annee(agg, 'Plus63', ANNEES)
    h = moyennes_par_annee(agg, 'Plus63H', ANNEES)
    f = moyennes_par_annee(agg, 'Plus63F', ANNEES)

    plt.figure(figsize=(10, 6))
    plt.plot(ANNEES, t, marker='o', label='Plus63 (Total)')
    plt.plot(ANNEES, h, marker='s', label='Plus63 Hommes')
    plt.plot(ANNEES, f, marker='^', label='Plus63 Femmes')
    plt.title("Employes ages de plus de 63 ans - Scenario 2")
    plt.xlabel("Annee")
    plt.ylabel("Nombre")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def graph_reserve_comparee(liste_s1, liste_s2, path):
    agg1 = aggreger_simulations(liste_s1, ANNEES, ['Reserve'])
    agg2 = aggreger_simulations(liste_s2, ANNEES, ['Reserve'])
    moy1 = _en_M(moyennes_par_annee(agg1, 'Reserve', ANNEES))
    moy2 = _en_M(moyennes_par_annee(agg2, 'Reserve', ANNEES))

    plt.figure(figsize=(10, 6))
    plt.plot(ANNEES, moy1, marker='o', label='Scenario 1')
    plt.plot(ANNEES, moy2, marker='s', label='Scenario 2')
    plt.title("Reserve moyenne comparee (Mdhs)")
    plt.xlabel("Annee")
    plt.ylabel("Reserve (Mdhs)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def graph_reserve_ic_comparee(liste_s1, liste_s2, path):
    agg1 = aggreger_simulations(liste_s1, ANNEES, ['Reserve'])
    agg2 = aggreger_simulations(liste_s2, ANNEES, ['Reserve'])
    ic1 = ic_par_annee(agg1, 'Reserve', ANNEES)
    ic2 = ic_par_annee(agg2, 'Reserve', ANNEES)
    m1 = [c[0] / 1e6 for c in ic1]
    i1 = [c[1] / 1e6 for c in ic1]
    s1 = [c[2] / 1e6 for c in ic1]
    m2 = [c[0] / 1e6 for c in ic2]
    i2 = [c[1] / 1e6 for c in ic2]
    s2 = [c[2] / 1e6 for c in ic2]

    plt.figure(figsize=(10, 6))
    plt.plot(ANNEES, m1, marker='o', color='steelblue', label='Scenario 1 (moy)')
    plt.fill_between(ANNEES, i1, s1, alpha=0.2, color='steelblue', label='IC 95% S1')
    plt.plot(ANNEES, m2, marker='s', color='darkorange', label='Scenario 2 (moy)')
    plt.fill_between(ANNEES, i2, s2, alpha=0.2, color='darkorange', label='IC 95% S2')
    plt.title("Reserve - comparaison avec IC 95%")
    plt.xlabel("Annee")
    plt.ylabel("Reserve (Mdhs)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def graph_indicateur_compare(liste_s1, liste_s2, indicateur, titre, ylabel, path, en_millions=False):
    """Graphique comparatif pour un indicateur entre les 2 scenarios."""
    agg1 = aggreger_simulations(liste_s1, ANNEES, [indicateur])
    agg2 = aggreger_simulations(liste_s2, ANNEES, [indicateur])
    m1 = moyennes_par_annee(agg1, indicateur, ANNEES)
    m2 = moyennes_par_annee(agg2, indicateur, ANNEES)
    if en_millions:
        m1 = _en_M(m1)
        m2 = _en_M(m2)

    plt.figure(figsize=(10, 6))
    plt.plot(ANNEES, m1, marker='o', label='Scenario 1')
    plt.plot(ANNEES, m2, marker='s', label='Scenario 2')
    plt.title(titre)
    plt.xlabel("Annee")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def graph_boxplot_reserve(liste_resultats_s2, path):
    """Boites a moustaches de la Reserve en 2026, 2030, 2035."""
    annees_box = [2026, 2030, 2035]
    data = [[res[a]['Reserve'] / 1e6 for res in liste_resultats_s2] for a in annees_box]

    plt.figure(figsize=(10, 6))
    plt.boxplot(data, labels=[str(a) for a in annees_box], patch_artist=True)
    plt.title("Distribution de la Reserve - Scenario 2 (40 simulations)")
    plt.ylabel("Reserve (Mdhs)")
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def graph_hist_reserve_2035(liste_resultats_s2, path):
    """Histogramme de la Reserve en 2035 sur 40 simulations."""
    vals = [res[2035]['Reserve'] / 1e6 for res in liste_resultats_s2]
    plt.figure(figsize=(10, 6))
    plt.hist(vals, bins=10, color='mediumpurple', edgecolor='black')
    plt.title("Distribution de la Reserve en 2035 - Scenario 2 (40 simulations)")
    plt.xlabel("Reserve (Mdhs)")
    plt.ylabel("Frequence")
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def generer_tous_graphiques(liste_s1, liste_s2, dossier):
    """Sauvegarde tous les graphiques attendus dans `dossier`."""
    _ensure_dir(dossier)

    # Scenario 1
    graph_reserve_ic(liste_s1, 1, os.path.join(dossier, "graphique_02_reserve_ic_scenario1.png"))
    graph_totemp_totret(liste_s1, 1, os.path.join(dossier, "graphique_04_totemp_totret_s1.png"))
    graph_cotis_pens(liste_s1, 1, os.path.join(dossier, "graphique_06_cotis_pens_s1.png"))
    graph_nouvret_nouvrec(liste_s1, 1, os.path.join(dossier, "graphique_11_nouvret_nouvrec_s1.png"))

    # Scenario 2
    graph_reserve_ic(liste_s2, 2, os.path.join(dossier, "graphique_03_reserve_ic_scenario2.png"))
    graph_totemp_totret(liste_s2, 2, os.path.join(dossier, "graphique_05_totemp_totret_s2.png"))
    graph_cotis_pens(liste_s2, 2, os.path.join(dossier, "graphique_07_cotis_pens_s2.png"))
    graph_plus63(liste_s2, os.path.join(dossier, "graphique_08_plus63_evolution.png"))
    graph_nouvret_nouvrec(liste_s2, 2, os.path.join(dossier, "graphique_12_nouvret_nouvrec_s2.png"))

    # Comparaisons croisees
    graph_reserve_comparee(liste_s1, liste_s2, os.path.join(dossier, "graphique_01_reserve_comparee.png"))
    graph_reserve_ic_comparee(liste_s1, liste_s2, os.path.join(dossier, "graphique_10_comparaison_croisee.png"))
    graph_indicateur_compare(liste_s1, liste_s2, 'TotEmp', "TotEmp compare", "Nombre",
                             os.path.join(dossier, "graphique_13_totemp_compare.png"))
    graph_indicateur_compare(liste_s1, liste_s2, 'TotRet', "TotRet compare", "Nombre",
                             os.path.join(dossier, "graphique_14_totret_compare.png"))
    graph_indicateur_compare(liste_s1, liste_s2, 'TotCotis', "TotCotis compare", "Mdhs",
                             os.path.join(dossier, "graphique_15_totcotis_compare.png"), en_millions=True)
    graph_indicateur_compare(liste_s1, liste_s2, 'TotPens', "TotPens compare", "Mdhs",
                             os.path.join(dossier, "graphique_16_totpens_compare.png"), en_millions=True)

    # Specifique scenario 2
    graph_boxplot_reserve(liste_s2, os.path.join(dossier, "graphique_09_boxplot_reserve.png"))
    graph_hist_reserve_2035(liste_s2, os.path.join(dossier, "graphique_17_hist_reserve_2035.png"))
