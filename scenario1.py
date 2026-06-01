"""
Module scenario1.py
Simulation du scenario 1 : situation actuelle (depart 63 ans, avancement +5% en 2026/2030/2034).
"""

from distributions import (
    AGES_EMBAUCHE,
    SALAIRES_EMBAUCHE,
    tirer_intervalle,
    tirer_sexe,
    tirer_uniforme_int,
)
from indicateurs import (
    calculer_totcotis_s1,
    calculer_totpens,
    compter_employes,
    compter_retraites,
)
from initialisation import (
    generer_employes,
    generer_retraites,
    RESERVE_INIT,
    ANNEE_DEBUT,
)

ANNEES = list(range(2026, 2036))  # 2026 a 2035
AGE_DEPART_S1 = 63
ANNEES_AVANCEMENT_S1 = {2026, 2030, 2034}
TAUX_AVANCEMENT_S1 = 0.05


def simuler_scenario1(IX, IY, IZ):
    """
    Execute une simulation complete du scenario 1 sur 2026-2035.
    Retourne un dict { annee : { indicateur : valeur } } et les germes finales.
    """
    employes, IX, IY, IZ = generer_employes(IX, IY, IZ, age_depart_default=AGE_DEPART_S1)
    retraites, IX, IY, IZ = generer_retraites(IX, IY, IZ)

    reserve = RESERVE_INIT
    next_emp_id = len(employes)
    next_ret_id = len(retraites)

    resultats = {}

    for annee in ANNEES:
        # 1) Integrer les recrues / nouveaux retraites decides en fin d'annee precedente
        #    (deja appliques en fin de boucle precedente sur les listes).

        # 2) Avancement salarial en janvier si applicable
        if annee in ANNEES_AVANCEMENT_S1:
            for emp in employes:
                if emp['en_activite']:
                    emp['salaire'] *= (1.0 + TAUX_AVANCEMENT_S1)

        # 3) Vieillissement d'un an (en cours d'annee)
        for emp in employes:
            if emp['en_activite']:
                emp['age'] += 1.0

        # 4) Calcul des indicateurs financiers sur l'annee
        totcotis = calculer_totcotis_s1(employes)
        totpens = calculer_totpens(retraites)
        reserve = reserve + totcotis - totpens

        # 5) Identifier les nouveaux retraites de l'annee (ceux qui atteignent 63 ans)
        nouv_ret_list = []
        for emp in employes:
            if emp['en_activite'] and emp['age'] >= emp['age_depart_retraite']:
                nat = max(0.0, emp['age'] - emp['age_embauche'])
                dsar = emp['salaire']
                pension = (nat * 2.0 / 100.0) * dsar
                nouv_ret_list.append({'dsar': dsar, 'nat': nat, 'pension': pension, 'emp_id': emp['id']})

        nouv_ret = len(nouv_ret_list)

        # 6) Tirer le nombre de nouveaux recrutes
        nb_rec, IX, IY, IZ = tirer_uniforme_int(250, 400, IX, IY, IZ)
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

        # 7) Enregistrer les indicateurs (avant les transitions effectives au 1er janvier suivant)
        resultats[annee] = {
            'TotEmp': compter_employes(employes),
            'TotRet': compter_retraites(retraites),
            'TotCotis': totcotis,
            'TotPens': totpens,
            'Reserve': reserve,
            'NouvRet': nouv_ret,
            'NouvRec': nb_rec,
        }

        # 8) Transitions au 1er janvier de l'annee suivante :
        #    - les nouveaux retraites quittent les employes et integrent les retraites
        #    - les nouveaux recrutes integrent les employes
        for nr in nouv_ret_list:
            for emp in employes:
                if emp['id'] == nr['emp_id']:
                    emp['en_activite'] = False
                    break
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
                'age_depart_retraite': AGE_DEPART_S1,
            })
            next_emp_id += 1

    return resultats, IX, IY, IZ
