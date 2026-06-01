# Rapport LaTeX - Simulation discrete caisse de retraite

## Compilation

### Avec latexmk (recommande)
```bash
cd rapport
latexmk -pdf rapport.tex
```

### Avec pdflatex (manuelle, 2 passes pour la table des matieres)
```bash
cd rapport
pdflatex rapport.tex
pdflatex rapport.tex
```

### Avec MikTeX / TeX Live sous Windows
Ouvrir `rapport.tex` dans TeXstudio / TeXmaker / Overleaf et compiler avec
le moteur **pdfLaTeX**.

### Sur Overleaf
1. Creer un nouveau projet vide.
2. Uploader `rapport.tex` et le dossier `../resultats/` (pour les figures).
3. Mettre le moteur sur **pdfLaTeX**.
4. Cliquer sur Recompile.

## Figures

Le fichier cherche les images dans deux dossiers :
- `../resultats/` : graphiques generes par la simulation (graphique_01..17.png)
- `figures/` : a creer si vous voulez ajouter des captures d'ecran de l'interface
  Streamlit (`dashboard.png`) ou un logo (`logo.png`).

Si une figure manque, commenter la ligne `\includegraphics` ou la remplacer
par `\fbox{\rule{0pt}{6cm}\rule{12cm}{0pt}}` (placeholder).

## Structure

- Page de garde
- Remerciements, Resume (FR), Abstract (EN)
- Table des matieres, listes des figures et tableaux
- Introduction Generale
- **Chapitre 1 :** Contexte general
- **Chapitre 2 :** Specifications fonctionnelles et techniques
- **Chapitre 3 :** Realisation et resultats experimentaux
- Conclusion Generale
- Bibliographie

## Personnalisation

- Remplacer `[Nom de l'encadrant]` et `[Nom Etudiant N]` sur la page de garde.
- Ajouter votre logo dans `figures/logo.png` (ou commenter la ligne).
- Ajouter une capture d'ecran du dashboard dans `figures/dashboard.png`.
