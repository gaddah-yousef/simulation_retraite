"""
Module affichage.py
Mise en forme des tableaux pour affichage terminal / fichier texte.
"""

from tabulate import tabulate

ANNEES = list(range(2026, 2036))


def _M(val):
    """Formatage : convertit en millions de DH, arrondi 2 decimales."""
    return round(val / 1_000_000.0, 2)


def tableau_scenario1(resultats):
    """
    resultats : dict { annee : { indicateur : valeur } }.
    Retourne une chaine formatee.
    """
    headers = ["Annee", "TotEmp", "TotRet", "TotCotis(M)", "TotPens(M)", "Reserve(M)", "NouvRet", "NouvRec"]
    rows = []
    for a in ANNEES:
        r = resultats[a]
        rows.append([a, r['TotEmp'], r['TotRet'], _M(r['TotCotis']), _M(r['TotPens']), _M(r['Reserve']), r['NouvRet'], r['NouvRec']])
    return tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="right", numalign="right")


def tableau_scenario2(resultats):
    headers = ["Annee", "TotEmp", "Plus63", "Plus63H", "Plus63F", "TotRet", "TotCotis(M)", "TotPens(M)", "Reserve(M)", "NouvRet", "NouvRec"]
    rows = []
    for a in ANNEES:
        r = resultats[a]
        rows.append([a, r['TotEmp'], r['Plus63'], r['Plus63H'], r['Plus63F'], r['TotRet'], _M(r['TotCotis']), _M(r['TotPens']), _M(r['Reserve']), r['NouvRet'], r['NouvRec']])
    return tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="right", numalign="right")


def tableau_40sim_annee(liste_resultats, annee, scenario):
    """Tableau des 40 simulations pour une annee donnee (sce 1 ou 2)."""
    if scenario == 1:
        headers = ["Sim", "TotEmp", "TotRet", "TotCotis(M)", "TotPens(M)", "Reserve(M)", "NouvRet", "NouvRec"]
        rows = []
        for i, res in enumerate(liste_resultats, start=1):
            r = res[annee]
            rows.append([i, r['TotEmp'], r['TotRet'], _M(r['TotCotis']), _M(r['TotPens']), _M(r['Reserve']), r['NouvRet'], r['NouvRec']])
        # ligne moyenne
        n = len(liste_resultats)
        moy = ["MOY",
               round(sum(res[annee]['TotEmp'] for res in liste_resultats) / n, 1),
               round(sum(res[annee]['TotRet'] for res in liste_resultats) / n, 1),
               round(sum(_M(res[annee]['TotCotis']) for res in liste_resultats) / n, 2),
               round(sum(_M(res[annee]['TotPens']) for res in liste_resultats) / n, 2),
               round(sum(_M(res[annee]['Reserve']) for res in liste_resultats) / n, 2),
               round(sum(res[annee]['NouvRet'] for res in liste_resultats) / n, 1),
               round(sum(res[annee]['NouvRec'] for res in liste_resultats) / n, 1)]
        rows.append(moy)
    else:
        headers = ["Sim", "TotEmp", "Plus63", "TotRet", "TotCotis(M)", "TotPens(M)", "Reserve(M)", "NouvRet", "NouvRec"]
        rows = []
        for i, res in enumerate(liste_resultats, start=1):
            r = res[annee]
            rows.append([i, r['TotEmp'], r['Plus63'], r['TotRet'], _M(r['TotCotis']), _M(r['TotPens']), _M(r['Reserve']), r['NouvRet'], r['NouvRec']])
        n = len(liste_resultats)
        moy = ["MOY",
               round(sum(res[annee]['TotEmp'] for res in liste_resultats) / n, 1),
               round(sum(res[annee]['Plus63'] for res in liste_resultats) / n, 1),
               round(sum(res[annee]['TotRet'] for res in liste_resultats) / n, 1),
               round(sum(_M(res[annee]['TotCotis']) for res in liste_resultats) / n, 2),
               round(sum(_M(res[annee]['TotPens']) for res in liste_resultats) / n, 2),
               round(sum(_M(res[annee]['Reserve']) for res in liste_resultats) / n, 2),
               round(sum(res[annee]['NouvRet'] for res in liste_resultats) / n, 1),
               round(sum(res[annee]['NouvRec'] for res in liste_resultats) / n, 1)]
        rows.append(moy)
    return tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="right", numalign="right")


def tableau_reserve_40sim(liste_resultats):
    """Reserve sur 10 ans pour 40 simulations + ligne moyenne (en Mdhs)."""
    headers = ["Sim"] + [str(a) for a in ANNEES]
    rows = []
    for i, res in enumerate(liste_resultats, start=1):
        rows.append([i] + [_M(res[a]['Reserve']) for a in ANNEES])
    n = len(liste_resultats)
    moy = ["MOY"] + [round(sum(_M(res[a]['Reserve']) for res in liste_resultats) / n, 2) for a in ANNEES]
    rows.append(moy)
    return tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="right", numalign="right")


def tableau_ic(ic_data):
    """
    ic_data : liste de tuples (indicateur, annee, m, inf, sup, largeur).
    """
    headers = ["Indicateur", "Annee", "Moyenne", "IC Inf", "IC Sup", "Largeur IC"]
    rows = []
    for ind, an, m, inf, sup, larg in ic_data:
        rows.append([ind, an, round(m, 2), round(inf, 2), round(sup, 2), round(larg, 2)])
    return tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="right", numalign="right")


def tableau_comparatif_reserves(moy_s1, moy_s2):
    """Comparaison moyennes des reserves entre scenarios (en Mdhs)."""
    headers = ["Annee", "Scenario 1 (moy.)", "Scenario 2 (moy.)"]
    rows = []
    for i, a in enumerate(ANNEES):
        rows.append([a, round(moy_s1[i] / 1_000_000.0, 2), round(moy_s2[i] / 1_000_000.0, 2)])
    return tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="right", numalign="right")


def tableau_ic_compare(ic_s1, ic_s2, annees=(2026, 2030, 2035)):
    """
    ic_s1, ic_s2 : dicts {annee : (m, inf, sup, larg)} en valeurs absolues (DH).
    """
    headers = ["Annee", "IC Scenario 1 (Mdhs)", "IC Scenario 2 (Mdhs)"]
    rows = []
    for a in annees:
        m1, i1, s1, _ = ic_s1[a]
        m2, i2, s2, _ = ic_s2[a]
        rows.append([a,
                     f"[{i1/1_000_000:.2f} , {s1/1_000_000:.2f}]",
                     f"[{i2/1_000_000:.2f} , {s2/1_000_000:.2f}]"])
    return tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="right", numalign="right")


def tableau_plus63_40sim(liste_resultats_s2):
    """Tableau Plus63 (T, H, F) sur 40 simulations x 10 ans + ligne CUM et MOY."""
    rows = []
    n = len(liste_resultats_s2)
    headers = ["Sim"] + [f"{a} T/H/F" for a in ANNEES]
    for i, res in enumerate(liste_resultats_s2, start=1):
        row = [i]
        for a in ANNEES:
            r = res[a]
            row.append(f"{r['Plus63']}/{r['Plus63H']}/{r['Plus63F']}")
        rows.append(row)
    cum_row = ["CUM"]
    moy_row = ["MOY"]
    for a in ANNEES:
        t = sum(res[a]['Plus63'] for res in liste_resultats_s2)
        h = sum(res[a]['Plus63H'] for res in liste_resultats_s2)
        f = sum(res[a]['Plus63F'] for res in liste_resultats_s2)
        cum_row.append(f"{t}/{h}/{f}")
        moy_row.append(f"{round(t/n,1)}/{round(h/n,1)}/{round(f/n,1)}")
    rows.append(cum_row)
    rows.append(moy_row)
    return tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="right", numalign="right")
