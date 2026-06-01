"""
Module indicateurs.py
Calcul des indicateurs annuels (7 pour scenario 1, 10 pour scenario 2).
"""


def taux_cotisation_s1(salaire):
    """Taux de cotisation employe (scenario 1)."""
    if salaire < 5000:
        return 0.05
    if salaire <= 7000:
        return 0.06
    if salaire <= 10000:
        return 0.08
    return 0.10


def taux_cotisation_s2(salaire):
    """
    Taux de cotisation (employe ET employeur, chacun) pour le scenario 2.
    Retourne (taux_employe, taux_employeur). Les deux sont egaux.
    Pour salaire > 10000, i = salaire // 10000 ; taux = (10 + (i-1)*2)% plafonne a 30%.
    """
    if salaire < 5000:
        return 0.06, 0.06
    if salaire <= 7000:
        return 0.07, 0.07
    if salaire <= 10000:
        return 0.08, 0.08
    # salaire > 10000
    i = int(salaire // 10000)
    if i < 1:
        i = 1
    taux = min(0.30, (10 + (i - 1) * 2) / 100.0)
    return taux, taux


def calculer_totcotis_s1(employes):
    """Somme annuelle des cotisations pour le scenario 1."""
    total = 0.0
    for emp in employes:
        if emp['en_activite']:
            t = taux_cotisation_s1(emp['salaire'])
            total += emp['salaire'] * t * 12.0
    return total


def calculer_totcotis_s2(employes):
    """Somme annuelle des cotisations pour le scenario 2 (employe + employeur)."""
    total = 0.0
    for emp in employes:
        if emp['en_activite']:
            te, tr = taux_cotisation_s2(emp['salaire'])
            total += emp['salaire'] * (te + tr) * 12.0
    return total


def calculer_totpens(retraites):
    """Somme annuelle des pensions versees."""
    return sum(r['pension_mensuelle'] * 12.0 for r in retraites if r['vivant'])


def compter_employes(employes):
    """Nombre d'employes en activite."""
    return sum(1 for e in employes if e['en_activite'])


def compter_retraites(retraites):
    """Nombre de retraites vivants."""
    return sum(1 for r in retraites if r['vivant'])


def compter_plus63(employes):
    """Retourne (total, hommes, femmes) des employes en activite ages de plus de 63 ans."""
    total = 0
    hommes = 0
    femmes = 0
    for e in employes:
        if e['en_activite'] and e['age'] > 63:
            total += 1
            if e['sexe'] == 'H':
                hommes += 1
            else:
                femmes += 1
    return total, hommes, femmes
