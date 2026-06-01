"""
Module initialisation.py
Generation des populations initiales : 10 000 employes et 3 000 retraites.
"""

from distributions import (
    SALAIRES_ACTUELS,
    AGES_ACTUELS,
    AGES_EMBAUCHE,
    tirer_intervalle,
    tirer_sexe,
    tirer_uniforme_float,
)

ANNEE_DEBUT = 2026
N_EMPLOYES_INIT = 10_000
N_RETRAITES_INIT = 3_000
RESERVE_INIT = 200_000_000.0  # 200 Mdhs


def generer_employes(IX, IY, IZ, age_depart_default=63):
    """
    Genere la liste des employes initiaux.
    Retourne (liste_employes, IX, IY, IZ).
    """
    employes = []
    for idx in range(N_EMPLOYES_INIT):
        # Age actuel
        age, IX, IY, IZ = tirer_intervalle(AGES_ACTUELS, IX, IY, IZ)
        # Salaire actuel
        salaire, IX, IY, IZ = tirer_intervalle(SALAIRES_ACTUELS, IX, IY, IZ)
        # Sexe
        sexe, IX, IY, IZ = tirer_sexe(IX, IY, IZ)
        # Age d'embauche : on tire selon la distribution mais on s'assure
        # qu'il soit <= age actuel. Sinon on prend min(age, age_embauche_max).
        age_emb, IX, IY, IZ = tirer_intervalle(AGES_EMBAUCHE, IX, IY, IZ)
        if age_emb > age:
            # L'employe est plus jeune que l'age d'embauche tire : on cale
            # son age d'embauche a min(age, 21) ou a (age - 1) si age < 22.
            age_emb = max(21.0, age - 1.0)
            if age_emb > age:
                age_emb = age

        annee_embauche = ANNEE_DEBUT - int(round(age - age_emb))

        # Salaire d'embauche : on retient une fraction du salaire actuel,
        # en supposant une progression d'environ 3% par an entre embauche
        # et aujourd'hui. (utilise uniquement pour la coherence du dict).
        nb_ans = max(0.0, age - age_emb)
        salaire_emb = salaire / ((1.03) ** nb_ans)

        employes.append({
            'id': idx,
            'age': age,
            'salaire': salaire,
            'sexe': sexe,
            'annee_embauche': annee_embauche,
            'age_embauche': age_emb,
            'salaire_embauche': salaire_emb,
            'en_activite': True,
            'age_depart_retraite': age_depart_default,
        })
    return employes, IX, IY, IZ


def generer_retraites(IX, IY, IZ):
    """
    Genere les 3 000 retraites initiaux avec une pension fictive coherente.
    PR = (NAT * 2 / 100) * DSAR, NAT uniforme [20, 40].
    Retourne (liste_retraites, IX, IY, IZ).
    """
    retraites = []
    for idx in range(N_RETRAITES_INIT):
        dsar, IX, IY, IZ = tirer_intervalle(SALAIRES_ACTUELS, IX, IY, IZ)
        nat, IX, IY, IZ = tirer_uniforme_float(20.0, 40.0, IX, IY, IZ)
        pension = (nat * 2.0 / 100.0) * dsar
        retraites.append({
            'id': idx,
            'pension_mensuelle': pension,
            'vivant': True,
        })
    return retraites, IX, IY, IZ
