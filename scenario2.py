"""
Module scenario2.py
Simulation du scenario 2 : reforme parametrique.
- depart minimum 63 ans, decision annuelle jusqu'a 70 ans (depart obligatoire a 70).
- avancement +10% en 2028/2030/2032/2034.
- cotisation employe + employeur.
- recrutements 300-600 par an.
"""

from distributions import (
    AGES_EMBAUCHE,
    SALAIRES_EMBAUCHE,
    bernoulli,
    tirer_intervalle,
    tirer_sexe,
    tirer_uniforme_int,
)
from indicateurs import (
    calculer_totcotis_s2,
    calculer_totpens,
    compter_employes,
    compter_plus63,
    compter_retraites,
)
from initialisation import (
    generer_employes,
    generer_retraites,
    RESERVE_INIT,
)

ANNEES = list(range(2026, 2036))
AGE_MIN_DEPART = 63
AGE_MAX_DEPART = 70
ANNEES_AVANCEMENT_S2 = {2028, 2030, 2032, 2034}
TAUX_AVANCEMENT_S2 = 0.10


def prob_prolonger(emp):
    """
    Probabilite annuelle qu'un employe decide de prolonger (de ne PAS partir
    a la retraite) en fonction de son sexe, de son salaire et de son age.
    L'employe a deja atteint AGE_MIN_DEPART. age_eff = age - 63 (>=0).
    """
    age_eff = max(0, int(emp['age']) - AGE_MIN_DEPART)
    s = emp['salaire']
    if emp['sexe'] == 'H':
        if s >= 30000:
            p0, d = 0.70, 0.05
        elif s >= 10000:
            p0, d = 0.50, 0.04
        elif s >= 5000:
            p0, d = 0.30, 0.02
        else:
            p0, d = 0.10, 0.01
    else:
        if s >= 30000:
            p0, d = 0.50, 0.04
        elif s >= 10000:
            p0, d = 0.30, 0.02
        elif s >= 5000:
            p0, d = 0.15, 0.01
        else:
            p0, d = 0.05, 0.01

    p = p0 - d * age_eff
    if p < 0.0:
        p = 0.0
    if p > 1.0:
        p = 1.0
    return p


def simuler_scenario2(IX, IY, IZ):
    """
    Execute une simulation complete du scenario 2 sur 2026-2035.
    Retourne (dict resultats par annee, IX, IY, IZ).
    """
    employes, IX, IY, IZ = generer_employes(IX, IY, IZ, age_depart_default=AGE_MIN_DEPART)
    retraites, IX, IY, IZ = generer_retraites(IX, IY, IZ)

    reserve = RESERVE_INIT
    next_emp_id = len(employes)
    next_ret_id = len(retraites)

    resultats = {}

    for annee in ANNEES:
        # 1) Avancement salarial
        if annee in ANNEES_AVANCEMENT_S2:
            for emp in employes:
                if emp['en_activite']:
                    emp['salaire'] *= (1.0 + TAUX_AVANCEMENT_S2)

        # 2) Vieillissement
        for emp in employes:
            if emp['en_activite']:
                emp['age'] += 1.0

        # 3) Indicateurs financiers
        totcotis = calculer_totcotis_s2(employes)
        totpens = calculer_totpens(retraites)
        reserve = reserve + totcotis - totpens

        # 4) Decision de depart en retraite :
        #    - age >= 70 -> depart obligatoire
        #    - 63 <= age < 70 -> tirage selon prob_prolonger
        nouv_ret_list = []
        for emp in employes:
            if not emp['en_activite']:
                continue
            if emp['age'] >= AGE_MAX_DEPART:
                part = True
            elif emp['age'] >= AGE_MIN_DEPART:
                p = prob_prolonger(emp)
                prolonge, IX, IY, IZ = bernoulli(p, IX, IY, IZ)
                part = not prolonge
            else:
                part = False

            if part:
                nat = max(0.0, emp['age'] - emp['age_embauche'])
                dsar = emp['salaire']
                pension = (nat * 2.0 / 100.0) * dsar
                nouv_ret_list.append({'emp_id': emp['id'], 'pension': pension})

        nouv_ret = len(nouv_ret_list)

        # 5) Nouveaux recrutes : entre 300 et 600
        nb_rec, IX, IY, IZ = tirer_uniforme_int(300, 600, IX, IY, IZ)
        nouv_rec_list = []
        for _ in range(nb_rec):
            age_emb, IX, IY, IZ = tirer_intervalle(AGES_EMBAUCHE, IX, IY, IZ)
            sal_emb, IX, IY, IZ = tirer_intervalle(SALAIRES_EMBAUCHE, IX, IY, IZ)
            sexe, IX, IY, IZ = tirer_sexe(IX, IY, IZ)
            nouv_rec_list.append({
                'age': age_emb,
                'age_embauche': age_emb,
                'salaire': sal_emb,
                'salaire_embauche': sal_emb,
                'sexe': sexe,
                'annee_embauche': annee + 1,
            })

        # 6) Indicateurs Plus63
        plus63_t, plus63_h, plus63_f = compter_plus63(employes)

        resultats[annee] = {
            'TotEmp': compter_employes(employes),
            'Plus63': plus63_t,
            'Plus63H': plus63_h,
            'Plus63F': plus63_f,
            'TotRet': compter_retraites(retraites),
            'TotCotis': totcotis,
            'TotPens': totpens,
            'Reserve': reserve,
            'NouvRet': nouv_ret,
            'NouvRec': nb_rec,
        }

        # 7) Transitions au 1er janvier suivant
        ids_partants = {nr['emp_id'] for nr in nouv_ret_list}
        for emp in employes:
            if emp['id'] in ids_partants:
                emp['en_activite'] = False
        for nr in nouv_ret_list:
            retraites.append({
                'id': next_ret_id,
                'pension_mensuelle': nr['pension'],
                'vivant': True,
            })
            next_ret_id += 1

        for nr in nouv_rec_list:
            employes.append({
                'id': next_emp_id,
                'age': nr['age'],
                'salaire': nr['salaire'],
                'sexe': nr['sexe'],
                'annee_embauche': nr['annee_embauche'],
                'age_embauche': nr['age_embauche'],
                'salaire_embauche': nr['salaire_embauche'],
                'en_activite': True,
                'age_depart_retraite': AGE_MIN_DEPART,
            })
            next_emp_id += 1

    return resultats, IX, IY, IZ
