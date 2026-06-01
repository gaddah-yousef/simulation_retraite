# Simulation discrete - Caisse de retraite marocaine

Simulation discrete sur 10 ans (2026-2035) comparant 2 scenarios :
- **Scenario 1 :** situation actuelle (depart 63 ans fixe).
- **Scenario 2 :** reforme parametrique (depart 63-70 ans, decision annuelle).

## Installation

```bash
pip install -r requirements.txt
```

Python 3.10+ recommande.

## Execution

### Mode CLI (terminal)
```bash
python main.py
```

### Mode interface graphique (Streamlit, navigateur)
```bash
streamlit run app.py
```
Une page s'ouvre dans le navigateur. Reglez les germes / scenario / mode dans la
barre laterale, cliquez sur **Lancer la simulation**, puis explorez les onglets
(tableaux, graphiques, comparaisons, IC 95%).

Le programme demande :
- germes `IX`, `IY`, `IZ` (entiers entre 1 et 30000),
- le scenario a simuler (1, 2 ou 3 = les deux),
- le mode (1 = simulation unique, 2 = 40 simulations).

Pour reproduire les memes resultats, utiliser les memes germes.

## Sortie

Tout est ecrit dans le dossier `resultats/` :
- `resultats_scenario1.txt`
- `resultats_scenario2.txt`
- `comparaison_scenarios.txt`
- `rapport_resultats.txt`
- `graphique_*.png` (courbes Reserve, IC, comparaisons, boxplot, histogramme...).

## Structure

```
simulation_retraite/
├── main.py            # Interface CLI et orchestration
├── alea.py            # Generateur pseudo-aleatoire impose
├── distributions.py   # Tables et tirages
├── initialisation.py  # 10 000 employes + 3 000 retraites de depart
├── indicateurs.py     # Taux de cotisation, calcul des indicateurs
├── scenario1.py       # Logique du scenario 1
├── scenario2.py       # Logique du scenario 2
├── statistiques.py    # Moyenne, ecart-type, IC 95%
├── affichage.py       # Tableaux formates (tabulate)
├── graphiques.py      # Matplotlib (PNG haute resolution)
└── resultats/         # Sorties generees a l'execution
```

## Hypotheses

- Generateur Wichmann-Hill (fonction `alea` imposee).
- Germes pour la i-eme simulation : `IXi = IX0 + (i-1)*3`, idem +5/+7 pour IY/IZ
  (ramenes dans [1, 30000] par modulo si necessaire).
- Pension mensuelle : `PR = (NAT * 2 / 100) * DSAR` (NAT = annees travaillees,
  DSAR = dernier salaire avant la retraite, mensuel).
- Pas de mortalite des retraites (gestion simplifiee, conformement au sujet).
- Mesures effectuees chaque fin decembre.
