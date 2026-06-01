"""
Module main.py
Point d'entree CLI de la simulation discrete de la caisse de retraite.
"""

import os
import sys

# Forcer UTF-8 sur stdout/stderr (utile sur Windows pour les caracteres de tableau).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(it, **kwargs):
        return it

from alea import valider_germes, germes_simulation_i
from scenario1 import simuler_scenario1, ANNEES
from scenario2 import simuler_scenario2
from statistiques import (
    aggreger_simulations,
    intervalle_confiance,
    ic_par_annee,
    moyennes_par_annee,
)
from affichage import (
    tableau_scenario1,
    tableau_scenario2,
    tableau_40sim_annee,
    tableau_reserve_40sim,
    tableau_ic,
    tableau_comparatif_reserves,
    tableau_ic_compare,
    tableau_plus63_40sim,
)
from graphiques import generer_tous_graphiques

DOSSIER_RESULTATS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultats")
N_SIMULATIONS = 40

INDIC_S1 = ['TotEmp', 'TotRet', 'TotCotis', 'TotPens', 'Reserve', 'NouvRet', 'NouvRec']
INDIC_S2 = ['TotEmp', 'Plus63', 'Plus63H', 'Plus63F', 'TotRet', 'TotCotis', 'TotPens', 'Reserve', 'NouvRet', 'NouvRec']


# ---------------------------------------------------------------------------
# Lecture parametres
# ---------------------------------------------------------------------------

def lire_int(prompt, mini=None, maxi=None, defaut=None):
    while True:
        s = input(prompt).strip()
        if s == "" and defaut is not None:
            return defaut
        try:
            v = int(s)
        except ValueError:
            print("Veuillez entrer un entier.")
            continue
        if mini is not None and v < mini:
            print(f"Valeur minimale = {mini}")
            continue
        if maxi is not None and v > maxi:
            print(f"Valeur maximale = {maxi}")
            continue
        return v


def lire_parametres():
    print("=" * 60)
    print("=== SIMULATION DISCRETE - CAISSE DE RETRAITE ===")
    print("=" * 60)
    print("Entrez les parametres de simulation :")
    IX = lire_int("  Germe IX (1-30000) [defaut 1000] : ", 1, 30000, 1000)
    IY = lire_int("  Germe IY (1-30000) [defaut 2000] : ", 1, 30000, 2000)
    IZ = lire_int("  Germe IZ (1-30000) [defaut 3000] : ", 1, 30000, 3000)
    scenario = lire_int("  Scenario (1=Actuel, 2=Reforme, 3=Les deux) [defaut 3] : ", 1, 3, 3)
    mode = lire_int("  Mode (1=Simulation unique, 2=40 simulations) [defaut 2] : ", 1, 2, 2)
    valider_germes(IX, IY, IZ)
    return IX, IY, IZ, scenario, mode


# ---------------------------------------------------------------------------
# Orchestration des simulations
# ---------------------------------------------------------------------------

def executer_n_simulations(simul_fn, IX0, IY0, IZ0, n=N_SIMULATIONS, label=""):
    """Execute n simulations independantes et retourne la liste des resultats."""
    liste = []
    for i in tqdm(range(1, n + 1), desc=f"Simulations {label}", ncols=80):
        IXi, IYi, IZi = germes_simulation_i(IX0, IY0, IZ0, i)
        res, _, _, _ = simul_fn(IXi, IYi, IZi)
        liste.append(res)
    return liste


# ---------------------------------------------------------------------------
# Generation des rapports texte
# ---------------------------------------------------------------------------

def rapport_scenario1_unique(resultats, IX, IY, IZ, chemin):
    titre = f"=== SCENARIO 1 - SIMULATION UNIQUE (IX={IX}, IY={IY}, IZ={IZ}) ==="
    contenu = titre + "\n\n" + tableau_scenario1(resultats) + "\n"
    if any(resultats[a]['Reserve'] < 0 for a in ANNEES):
        annee_faillite = next(a for a in ANNEES if resultats[a]['Reserve'] < 0)
        contenu += f"\n*** ATTENTION : FAILLITE EN ANNEE {annee_faillite} ***\n"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    return contenu


def rapport_scenario2_unique(resultats, IX, IY, IZ, chemin):
    titre = f"=== SCENARIO 2 - SIMULATION UNIQUE (IX={IX}, IY={IY}, IZ={IZ}) ==="
    contenu = titre + "\n\n" + tableau_scenario2(resultats) + "\n"
    if any(resultats[a]['Reserve'] < 0 for a in ANNEES):
        annee_faillite = next(a for a in ANNEES if resultats[a]['Reserve'] < 0)
        contenu += f"\n*** ATTENTION : FAILLITE EN ANNEE {annee_faillite} ***\n"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    return contenu


def rapport_40sim_scenario(liste, scenario, chemin):
    parties = [f"=== SCENARIO {scenario} - {N_SIMULATIONS} SIMULATIONS ==="]
    for an in (2026, 2030, 2035):
        parties.append(f"\n--- Resultats {an} ---")
        parties.append(tableau_40sim_annee(liste, an, scenario))
    parties.append("\n--- Evolution de la Reserve (Mdhs) sur 10 ans ---")
    parties.append(tableau_reserve_40sim(liste))

    indicateurs = INDIC_S1 if scenario == 1 else INDIC_S2
    agg = aggreger_simulations(liste, ANNEES, indicateurs)
    ic_data = []
    for an in (2026, 2030, 2035):
        m, inf, sup, larg = intervalle_confiance(agg['Reserve'][an])
        ic_data.append(("Reserve (DH)", an, m, inf, sup, larg))
    if scenario == 2:
        for ind in ('Plus63', 'Plus63H', 'Plus63F'):
            for an in (2026, 2030, 2035):
                m, inf, sup, larg = intervalle_confiance(agg[ind][an])
                ic_data.append((ind, an, m, inf, sup, larg))
    parties.append("\n--- Intervalles de confiance a 95% ---")
    parties.append(tableau_ic(ic_data))

    if scenario == 2:
        parties.append("\n--- Plus63 sur 40 simulations x 10 ans (T/H/F) ---")
        parties.append(tableau_plus63_40sim(liste))

    contenu = "\n".join(parties) + "\n"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    return contenu


def rapport_compare(liste_s1, liste_s2, chemin):
    agg1 = aggreger_simulations(liste_s1, ANNEES, ['Reserve'])
    agg2 = aggreger_simulations(liste_s2, ANNEES, ['Reserve'])
    moy1 = moyennes_par_annee(agg1, 'Reserve', ANNEES)
    moy2 = moyennes_par_annee(agg2, 'Reserve', ANNEES)
    ic1_list = ic_par_annee(agg1, 'Reserve', ANNEES)
    ic2_list = ic_par_annee(agg2, 'Reserve', ANNEES)
    ic1 = {a: ic1_list[i] for i, a in enumerate(ANNEES)}
    ic2 = {a: ic2_list[i] for i, a in enumerate(ANNEES)}

    parties = ["=== COMPARAISON DES 2 SCENARIOS ==="]
    parties.append("\n--- Reserve moyenne par annee ---")
    parties.append(tableau_comparatif_reserves(moy1, moy2))
    parties.append("\n--- IC a 95% sur la Reserve - comparaison ---")
    parties.append(tableau_ic_compare(ic1, ic2))

    contenu = "\n".join(parties) + "\n"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    return contenu


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main():
    os.makedirs(DOSSIER_RESULTATS, exist_ok=True)
    try:
        IX, IY, IZ, scenario, mode = lire_parametres()
    except (EOFError, KeyboardInterrupt):
        print("\nEntree interrompue.")
        return

    rapport_global = []

    # -------- Simulation unique --------
    if mode == 1:
        if scenario in (1, 3):
            print("\nExecution Scenario 1 (unique)...")
            res1, _, _, _ = simuler_scenario1(IX, IY, IZ)
            txt = rapport_scenario1_unique(res1, IX, IY, IZ,
                                           os.path.join(DOSSIER_RESULTATS, "resultats_scenario1.txt"))
            print(txt)
            rapport_global.append(txt)

        if scenario in (2, 3):
            print("\nExecution Scenario 2 (unique)...")
            res2, _, _, _ = simuler_scenario2(IX, IY, IZ)
            txt = rapport_scenario2_unique(res2, IX, IY, IZ,
                                           os.path.join(DOSSIER_RESULTATS, "resultats_scenario2.txt"))
            print(txt)
            rapport_global.append(txt)

    # -------- 40 simulations --------
    else:
        liste_s1 = liste_s2 = None
        if scenario in (1, 3):
            print("\nExecution Scenario 1 (40 simulations)...")
            liste_s1 = executer_n_simulations(simuler_scenario1, IX, IY, IZ, label="S1")
            txt = rapport_40sim_scenario(liste_s1, 1,
                                         os.path.join(DOSSIER_RESULTATS, "resultats_scenario1.txt"))
            print(txt)
            rapport_global.append(txt)

        if scenario in (2, 3):
            print("\nExecution Scenario 2 (40 simulations)...")
            liste_s2 = executer_n_simulations(simuler_scenario2, IX, IY, IZ, label="S2")
            txt = rapport_40sim_scenario(liste_s2, 2,
                                         os.path.join(DOSSIER_RESULTATS, "resultats_scenario2.txt"))
            print(txt)
            rapport_global.append(txt)

        if scenario == 3 and liste_s1 and liste_s2:
            txt = rapport_compare(liste_s1, liste_s2,
                                  os.path.join(DOSSIER_RESULTATS, "comparaison_scenarios.txt"))
            print(txt)
            rapport_global.append(txt)

            print("\nGeneration des graphiques...")
            generer_tous_graphiques(liste_s1, liste_s2, DOSSIER_RESULTATS)
            print(f"Graphiques sauvegardes dans : {DOSSIER_RESULTATS}")

    # Rapport global consolidé
    with open(os.path.join(DOSSIER_RESULTATS, "rapport_resultats.txt"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(rapport_global))

    print("\nTermine. Fichiers disponibles dans :", DOSSIER_RESULTATS)


if __name__ == "__main__":
    main()
