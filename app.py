"""
Interface graphique Streamlit pour la simulation discrete de la caisse de retraite.
Design : dashboard sombre style fintech, palette teal/coral, KPI cards, charts unifies.

Lancement :
    streamlit run app.py
"""

import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from alea import valider_germes, germes_simulation_i
from scenario1 import simuler_scenario1, ANNEES
from scenario2 import simuler_scenario2
from statistiques import (
    aggreger_simulations,
    intervalle_confiance,
    ic_par_annee,
    moyennes_par_annee,
)


# ============================================================================
# DESIGN SYSTEM
# ============================================================================

# Palette
COLOR_BG = "#0E1419"
COLOR_PANEL = "#161D26"
COLOR_PANEL_LIGHT = "#1F2832"
COLOR_BORDER = "#2A3441"
COLOR_TEXT = "#E6EDF3"
COLOR_TEXT_MUTED = "#8B949E"
COLOR_PRIMARY = "#00D4A6"       # teal vif (positif)
COLOR_DANGER = "#FF6B6B"        # corail (negatif / faillite)
COLOR_WARNING = "#FFB454"       # ambre
COLOR_S1 = "#5B8FF9"            # bleu scenario 1
COLOR_S2 = "#FF9F40"            # orange scenario 2
COLOR_ACCENT = "#A78BFA"        # violet (pour Plus63)

st.set_page_config(
    page_title="Caisse Retraite | Dashboard",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css():
    st.markdown(f"""
        <style>
        /* Police */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"], .stApp {{
            font-family: 'Inter', -apple-system, sans-serif;
        }}

        .stApp {{
            background: linear-gradient(180deg, {COLOR_BG} 0%, #0A0F14 100%);
        }}

        /* Header hero */
        .hero {{
            background: linear-gradient(135deg, #161D26 0%, #1A2530 100%);
            border: 1px solid {COLOR_BORDER};
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }}
        .hero::before {{
            content: "";
            position: absolute;
            top: -50%; right: -10%;
            width: 400px; height: 400px;
            background: radial-gradient(circle, {COLOR_PRIMARY}22 0%, transparent 70%);
            pointer-events: none;
        }}
        .hero-title {{
            font-size: 32px;
            font-weight: 800;
            color: {COLOR_TEXT};
            margin: 0;
            letter-spacing: -0.5px;
        }}
        .hero-subtitle {{
            color: {COLOR_TEXT_MUTED};
            font-size: 15px;
            margin-top: 6px;
            font-weight: 400;
        }}
        .hero-badge {{
            display: inline-block;
            background: {COLOR_PRIMARY}1A;
            color: {COLOR_PRIMARY};
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 12px;
            border: 1px solid {COLOR_PRIMARY}33;
        }}

        /* KPI Cards */
        .kpi-card {{
            background: {COLOR_PANEL};
            border: 1px solid {COLOR_BORDER};
            border-radius: 12px;
            padding: 18px 20px;
            transition: all 0.2s ease;
            height: 100%;
        }}
        .kpi-card:hover {{
            border-color: {COLOR_PRIMARY}66;
            transform: translateY(-2px);
        }}
        .kpi-label {{
            color: {COLOR_TEXT_MUTED};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 8px;
        }}
        .kpi-value {{
            color: {COLOR_TEXT};
            font-size: 26px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            line-height: 1.1;
        }}
        .kpi-delta {{
            font-size: 12px;
            font-weight: 500;
            margin-top: 6px;
        }}
        .kpi-positive {{ color: {COLOR_PRIMARY}; }}
        .kpi-negative {{ color: {COLOR_DANGER}; }}
        .kpi-neutral  {{ color: {COLOR_TEXT_MUTED}; }}

        /* Section header */
        .section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 32px 0 14px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid {COLOR_BORDER};
        }}
        .section-header h3 {{
            color: {COLOR_TEXT};
            font-size: 17px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.2px;
        }}
        .section-marker {{
            width: 4px;
            height: 18px;
            background: {COLOR_PRIMARY};
            border-radius: 2px;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: {COLOR_PANEL};
            border-right: 1px solid {COLOR_BORDER};
        }}
        section[data-testid="stSidebar"] .stMarkdown h2 {{
            color: {COLOR_TEXT};
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: {COLOR_TEXT_MUTED};
        }}

        /* Boutons */
        .stButton > button {{
            background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, #00B894 100%);
            color: #0E1419;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            font-size: 14px;
            padding: 12px 20px;
            transition: all 0.2s;
            box-shadow: 0 4px 12px {COLOR_PRIMARY}33;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 18px {COLOR_PRIMARY}55;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            background: transparent;
            border-bottom: 1px solid {COLOR_BORDER};
        }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            color: {COLOR_TEXT_MUTED};
            border-radius: 8px 8px 0 0;
            font-weight: 500;
            padding: 10px 18px;
        }}
        .stTabs [aria-selected="true"] {{
            background: {COLOR_PANEL_LIGHT};
            color: {COLOR_PRIMARY};
            border-bottom: 2px solid {COLOR_PRIMARY};
        }}

        /* Dataframe */
        [data-testid="stDataFrame"] {{
            border: 1px solid {COLOR_BORDER};
            border-radius: 10px;
            overflow: hidden;
        }}

        /* Alertes */
        [data-testid="stAlert"] {{
            border-radius: 10px;
            border: 1px solid {COLOR_BORDER};
        }}

        /* Footer caption */
        .footer-caption {{
            text-align: center;
            color: {COLOR_TEXT_MUTED};
            font-size: 12px;
            padding: 24px 0 12px 0;
            border-top: 1px solid {COLOR_BORDER};
            margin-top: 40px;
        }}

        /* Cache la barre de menu Streamlit */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)


def style_matplotlib():
    """Style global matplotlib coherent avec le dashboard sombre."""
    plt.rcParams.update({
        "figure.facecolor": COLOR_PANEL,
        "axes.facecolor": COLOR_PANEL,
        "axes.edgecolor": COLOR_BORDER,
        "axes.labelcolor": COLOR_TEXT,
        "axes.titlecolor": COLOR_TEXT,
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": COLOR_TEXT_MUTED,
        "ytick.color": COLOR_TEXT_MUTED,
        "grid.color": COLOR_BORDER,
        "grid.linewidth": 0.6,
        "grid.alpha": 0.4,
        "text.color": COLOR_TEXT,
        "legend.facecolor": COLOR_PANEL_LIGHT,
        "legend.edgecolor": COLOR_BORDER,
        "legend.labelcolor": COLOR_TEXT,
        "legend.fontsize": 10,
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Segoe UI", "Arial"],
        "figure.dpi": 110,
    })


inject_css()
style_matplotlib()


# ============================================================================
# Constantes metier
# ============================================================================

INDIC_S1 = ['TotEmp', 'TotRet', 'TotCotis', 'TotPens', 'Reserve', 'NouvRet', 'NouvRec']
INDIC_S2 = ['TotEmp', 'Plus63', 'Plus63H', 'Plus63F', 'TotRet', 'TotCotis', 'TotPens', 'Reserve', 'NouvRet', 'NouvRec']
N_SIM_DEFAUT = 40
DOSSIER_RESULTATS = os.path.join(BASE_DIR, "resultats")
os.makedirs(DOSSIER_RESULTATS, exist_ok=True)


# ============================================================================
# Composants UI
# ============================================================================

def section(titre):
    st.markdown(f"""
        <div class="section-header">
            <div class="section-marker"></div>
            <h3>{titre}</h3>
        </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, delta=None, delta_kind="neutral", help_text=None):
    delta_class = {
        "positive": "kpi-positive",
        "negative": "kpi-negative",
        "neutral": "kpi-neutral",
    }.get(delta_kind, "kpi-neutral")

    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    title_attr = f'title="{help_text}"' if help_text else ""

    st.markdown(f"""
        <div class="kpi-card" {title_attr}>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def hero():
    st.markdown(f"""
        <div class="hero">
            <div class="hero-badge">◈ Simulation discrete · 2026-2035</div>
            <h1 class="hero-title">Caisse de retraite marocaine</h1>
            <p class="hero-subtitle">
                Etude d'impact d'une reforme parametrique
                · Scenario actuel vs reforme · 40 simulations pseudo-aleatoires (Wichmann-Hill)
            </p>
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# Helpers calcul
# ============================================================================

def _M(v):
    return v / 1_000_000.0


def fmt_M(v, decimals=1):
    return f"{_M(v):,.{decimals}f}".replace(",", " ")


def fmt_int(v):
    return f"{int(v):,}".replace(",", " ")


def lancer_n_simulations(simul_fn, IX0, IY0, IZ0, n, progress_bar=None, label=""):
    liste = []
    for i in range(1, n + 1):
        IXi, IYi, IZi = germes_simulation_i(IX0, IY0, IZ0, i)
        res, _, _, _ = simul_fn(IXi, IYi, IZi)
        liste.append(res)
        if progress_bar is not None:
            progress_bar.progress(i / n, text=f"{label} · simulation {i}/{n}")
    return liste


# ============================================================================
# Visualisations
# ============================================================================

def fig_reserve_ic(liste, scenario, color):
    agg = aggreger_simulations(liste, ANNEES, ['Reserve'])
    ic = ic_par_annee(agg, 'Reserve', ANNEES)
    moy = [c[0] / 1e6 for c in ic]
    inf = [c[1] / 1e6 for c in ic]
    sup = [c[2] / 1e6 for c in ic]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(ANNEES, moy, marker='o', label='Moyenne', color=color, linewidth=2.5, markersize=7)
    ax.fill_between(ANNEES, inf, sup, alpha=0.18, color=color, label='IC 95%')
    ax.axhline(0, color=COLOR_DANGER, linestyle='--', alpha=0.6, linewidth=1)
    ax.set_title(f"Evolution de la Reserve · Scenario {scenario}")
    ax.set_xlabel("Annee")
    ax.set_ylabel("Reserve (Mdhs)")
    ax.legend(loc='upper left')
    fig.tight_layout()
    return fig


def fig_double_courbe(liste, indic_a, indic_b, titre, ylabel, color_a, color_b, en_M=False):
    agg = aggreger_simulations(liste, ANNEES, [indic_a, indic_b])
    a = moyennes_par_annee(agg, indic_a, ANNEES)
    b = moyennes_par_annee(agg, indic_b, ANNEES)
    if en_M:
        a = [x / 1e6 for x in a]
        b = [x / 1e6 for x in b]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(ANNEES, a, marker='o', label=indic_a, color=color_a, linewidth=2.2, markersize=6)
    ax.plot(ANNEES, b, marker='s', label=indic_b, color=color_b, linewidth=2.2, markersize=6)
    ax.set_title(titre)
    ax.set_xlabel("Annee")
    ax.set_ylabel(ylabel)
    ax.legend()
    fig.tight_layout()
    return fig


def fig_plus63(liste):
    agg = aggreger_simulations(liste, ANNEES, ['Plus63', 'Plus63H', 'Plus63F'])
    t = moyennes_par_annee(agg, 'Plus63', ANNEES)
    h = moyennes_par_annee(agg, 'Plus63H', ANNEES)
    f = moyennes_par_annee(agg, 'Plus63F', ANNEES)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(ANNEES, t, marker='o', label='Total', color=COLOR_ACCENT, linewidth=2.5, markersize=7)
    ax.plot(ANNEES, h, marker='s', label='Hommes', color=COLOR_S1, linewidth=2, markersize=6)
    ax.plot(ANNEES, f, marker='^', label='Femmes', color=COLOR_S2, linewidth=2, markersize=6)
    ax.set_title("Employes > 63 ans (prolongation)")
    ax.set_xlabel("Annee")
    ax.set_ylabel("Nombre moyen")
    ax.legend()
    fig.tight_layout()
    return fig


def fig_compare_reserve(liste_s1, liste_s2, avec_ic=True):
    agg1 = aggreger_simulations(liste_s1, ANNEES, ['Reserve'])
    agg2 = aggreger_simulations(liste_s2, ANNEES, ['Reserve'])
    ic1 = ic_par_annee(agg1, 'Reserve', ANNEES)
    ic2 = ic_par_annee(agg2, 'Reserve', ANNEES)
    m1 = [c[0] / 1e6 for c in ic1]
    m2 = [c[0] / 1e6 for c in ic2]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ANNEES, m1, marker='o', label='Scenario 1 (actuel)', color=COLOR_S1, linewidth=2.5, markersize=7)
    ax.plot(ANNEES, m2, marker='s', label='Scenario 2 (reforme)', color=COLOR_S2, linewidth=2.5, markersize=7)
    if avec_ic:
        ax.fill_between(ANNEES, [c[1]/1e6 for c in ic1], [c[2]/1e6 for c in ic1],
                        alpha=0.15, color=COLOR_S1)
        ax.fill_between(ANNEES, [c[1]/1e6 for c in ic2], [c[2]/1e6 for c in ic2],
                        alpha=0.15, color=COLOR_S2)
    ax.axhline(0, color=COLOR_DANGER, linestyle='--', alpha=0.6, linewidth=1, label='Seuil faillite')
    ax.set_title("Reserve comparee" + (" avec IC 95%" if avec_ic else ""))
    ax.set_xlabel("Annee")
    ax.set_ylabel("Reserve (Mdhs)")
    ax.legend(loc='best')
    fig.tight_layout()
    return fig


def fig_boxplot(liste_s2):
    annees_box = [2026, 2030, 2035]
    data = [[res[a]['Reserve'] / 1e6 for res in liste_s2] for a in annees_box]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bp = ax.boxplot(data, labels=[str(a) for a in annees_box], patch_artist=True,
                    medianprops=dict(color=COLOR_BG, linewidth=2),
                    boxprops=dict(facecolor=COLOR_S2 + "80", edgecolor=COLOR_S2, linewidth=1.5),
                    whiskerprops=dict(color=COLOR_TEXT_MUTED, linewidth=1.2),
                    capprops=dict(color=COLOR_TEXT_MUTED, linewidth=1.2),
                    flierprops=dict(marker='o', markerfacecolor=COLOR_DANGER,
                                    markeredgecolor='none', markersize=6))
    ax.set_title("Distribution de la Reserve · Scenario 2")
    ax.set_ylabel("Reserve (Mdhs)")
    fig.tight_layout()
    return fig


def fig_hist_reserve(liste_s2, annee=2035):
    vals = [res[annee]['Reserve'] / 1e6 for res in liste_s2]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.hist(vals, bins=12, color=COLOR_ACCENT + "B0", edgecolor=COLOR_ACCENT, linewidth=1.2)
    ax.axvline(np.mean(vals), color=COLOR_PRIMARY, linestyle='--', linewidth=2,
               label=f"Moyenne : {np.mean(vals):.1f}")
    ax.set_title(f"Distribution de la Reserve en {annee} · Scenario 2")
    ax.set_xlabel("Reserve (Mdhs)")
    ax.set_ylabel("Frequence")
    ax.legend()
    fig.tight_layout()
    return fig


def fig_nouvret_nouvrec(liste, scenario):
    agg = aggreger_simulations(liste, ANNEES, ['NouvRet', 'NouvRec'])
    nr = moyennes_par_annee(agg, 'NouvRet', ANNEES)
    rc = moyennes_par_annee(agg, 'NouvRec', ANNEES)
    x = np.arange(len(ANNEES))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(x - w/2, nr, width=w, label='Nouveaux retraites', color=COLOR_DANGER, edgecolor='none')
    ax.bar(x + w/2, rc, width=w, label='Nouveaux recrutes', color=COLOR_PRIMARY, edgecolor='none')
    ax.set_xticks(x)
    ax.set_xticklabels(ANNEES)
    ax.set_title(f"Flux annuels · Scenario {scenario}")
    ax.set_ylabel("Nombre moyen")
    ax.legend()
    fig.tight_layout()
    return fig


# ============================================================================
# SIDEBAR - Parametres
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙ Configuration")
    st.markdown("")

    st.markdown("**Germes du generateur**")
    g1, g2, g3 = st.columns(3)
    with g1:
        IX = st.number_input("IX", min_value=1, max_value=30000, value=1000, step=1, label_visibility="visible")
    with g2:
        IY = st.number_input("IY", min_value=1, max_value=30000, value=2000, step=1, label_visibility="visible")
    with g3:
        IZ = st.number_input("IZ", min_value=1, max_value=30000, value=3000, step=1, label_visibility="visible")
    st.caption("Entiers entre 1 et 30 000. Memes germes → memes resultats.")

    st.markdown("---")

    scenario_choix = st.radio(
        "**Scenario(s) a simuler**",
        options=["Scenario 1 seul", "Scenario 2 seul", "Les deux (comparaison)"],
        index=2,
    )

    mode_choix = st.radio(
        "**Mode**",
        options=["Simulation unique", "N simulations (etude statistique)"],
        index=1,
    )

    n_sim = N_SIM_DEFAUT
    if "N simulations" in mode_choix:
        n_sim = st.slider("Nombre de simulations", min_value=5, max_value=100,
                          value=N_SIM_DEFAUT, step=5)

    st.markdown("---")
    lancer = st.button("▶  LANCER LA SIMULATION", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 11px; color: {COLOR_TEXT_MUTED}; line-height: 1.6">
    <strong style="color:{COLOR_TEXT}">Sorties</strong><br>
    Tableaux + graphiques sauvegardes dans <code>resultats/</code>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN PAGE
# ============================================================================

hero()


def afficher_kpis_simulation_unique(res, scenario):
    """KPIs pour une simulation unique : valeurs finales (2035)."""
    r_init = 200.0  # Mdhs
    r_2035 = _M(res[2035]['Reserve'])
    r_2026 = _M(res[2026]['Reserve'])
    evol = r_2035 - r_init

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Reserve 2035", f"{r_2035:,.1f} M".replace(",", " "),
                 delta=f"{'+' if evol >= 0 else ''}{evol:,.1f} M depuis 2026".replace(",", " "),
                 delta_kind="positive" if evol >= 0 else "negative")
    with cols[1]:
        kpi_card("Employes 2035", fmt_int(res[2035]['TotEmp']))
    with cols[2]:
        kpi_card("Retraites 2035", fmt_int(res[2035]['TotRet']))
    with cols[3]:
        ratio = res[2035]['TotEmp'] / max(1, res[2035]['TotRet'])
        kpi_card("Ratio Actifs/Retraites", f"{ratio:.2f}",
                 delta="Soutenable" if ratio >= 2 else "Tension demographique",
                 delta_kind="positive" if ratio >= 2 else "negative")

    if scenario == 2:
        cols2 = st.columns(4)
        with cols2[0]:
            kpi_card("Plus63 (T) 2035", fmt_int(res[2035]['Plus63']))
        with cols2[1]:
            kpi_card("Plus63 Hommes", fmt_int(res[2035]['Plus63H']))
        with cols2[2]:
            kpi_card("Plus63 Femmes", fmt_int(res[2035]['Plus63F']))
        with cols2[3]:
            total_cotis = sum(res[a]['TotCotis'] for a in ANNEES)
            kpi_card("Cotis cumulees", f"{_M(total_cotis):,.0f} M".replace(",", " "))


def afficher_simulation_unique(IX, IY, IZ, faire_s1, faire_s2):
    onglet_names = []
    if faire_s1: onglet_names.append("◐ Scenario 1")
    if faire_s2: onglet_names.append("◑ Scenario 2")
    onglets = st.tabs(onglet_names) if onglet_names else []

    idx = 0
    if faire_s1:
        with onglets[idx]:
            t0 = time.time()
            res1, _, _, _ = simuler_scenario1(IX, IY, IZ)
            st.caption(f"Execute en {time.time()-t0:.2f}s · Germes ({IX}, {IY}, {IZ})")

            section("Indicateurs cles")
            afficher_kpis_simulation_unique(res1, 1)

            faillite = next((a for a in ANNEES if res1[a]['Reserve'] < 0), None)
            if faillite:
                st.error(f"⚠ **FAILLITE DETECTEE EN {faillite}** · Reserve devient negative.")

            section("Tableau detaille")
            rows = [{
                "Annee": a,
                "TotEmp": fmt_int(res1[a]['TotEmp']),
                "TotRet": fmt_int(res1[a]['TotRet']),
                "TotCotis (Mdhs)": round(_M(res1[a]['TotCotis']), 2),
                "TotPens (Mdhs)": round(_M(res1[a]['TotPens']), 2),
                "Reserve (Mdhs)": round(_M(res1[a]['Reserve']), 2),
                "NouvRet": res1[a]['NouvRet'],
                "NouvRec": res1[a]['NouvRec'],
            } for a in ANNEES]
            st.dataframe(rows, use_container_width=True, hide_index=True)

            section("Evolution de la Reserve")
            fig, ax = plt.subplots(figsize=(10, 4.5))
            vals = [_M(res1[a]['Reserve']) for a in ANNEES]
            ax.plot(ANNEES, vals, marker='o', color=COLOR_S1, linewidth=2.5, markersize=8)
            ax.fill_between(ANNEES, vals, 0,
                            where=[v >= 0 for v in vals], alpha=0.2, color=COLOR_PRIMARY)
            ax.fill_between(ANNEES, vals, 0,
                            where=[v < 0 for v in vals], alpha=0.2, color=COLOR_DANGER)
            ax.axhline(0, color=COLOR_DANGER, linestyle='--', alpha=0.5)
            ax.set_title("Reserve de la caisse · Scenario 1")
            ax.set_xlabel("Annee"); ax.set_ylabel("Mdhs")
            fig.tight_layout()
            st.pyplot(fig)
        idx += 1

    if faire_s2:
        with onglets[idx]:
            t0 = time.time()
            res2, _, _, _ = simuler_scenario2(IX, IY, IZ)
            st.caption(f"Execute en {time.time()-t0:.2f}s · Germes ({IX}, {IY}, {IZ})")

            section("Indicateurs cles")
            afficher_kpis_simulation_unique(res2, 2)

            faillite = next((a for a in ANNEES if res2[a]['Reserve'] < 0), None)
            if faillite:
                st.error(f"⚠ **FAILLITE DETECTEE EN {faillite}**")

            section("Tableau detaille")
            rows = [{
                "Annee": a,
                "TotEmp": fmt_int(res2[a]['TotEmp']),
                "Plus63": res2[a]['Plus63'],
                "+H": res2[a]['Plus63H'],
                "+F": res2[a]['Plus63F'],
                "TotRet": fmt_int(res2[a]['TotRet']),
                "TotCotis (Mdhs)": round(_M(res2[a]['TotCotis']), 2),
                "TotPens (Mdhs)": round(_M(res2[a]['TotPens']), 2),
                "Reserve (Mdhs)": round(_M(res2[a]['Reserve']), 2),
                "NouvRet": res2[a]['NouvRet'],
                "NouvRec": res2[a]['NouvRec'],
            } for a in ANNEES]
            st.dataframe(rows, use_container_width=True, hide_index=True)

            section("Evolution de la Reserve")
            fig, ax = plt.subplots(figsize=(10, 4.5))
            vals = [_M(res2[a]['Reserve']) for a in ANNEES]
            ax.plot(ANNEES, vals, marker='o', color=COLOR_S2, linewidth=2.5, markersize=8)
            ax.fill_between(ANNEES, vals, 0, alpha=0.2, color=COLOR_S2)
            ax.axhline(0, color=COLOR_DANGER, linestyle='--', alpha=0.5)
            ax.set_title("Reserve de la caisse · Scenario 2")
            ax.set_xlabel("Annee"); ax.set_ylabel("Mdhs")
            fig.tight_layout()
            st.pyplot(fig)


def afficher_kpis_n_sim(liste, scenario):
    agg = aggreger_simulations(liste, ANNEES, ['Reserve', 'TotEmp', 'TotRet'])
    moy_r_2035 = sum(agg['Reserve'][2035]) / len(liste)
    moy_r_2026 = sum(agg['Reserve'][2026]) / len(liste)
    moy_emp = sum(agg['TotEmp'][2035]) / len(liste)
    moy_ret = sum(agg['TotRet'][2035]) / len(liste)
    n_faillite = sum(1 for res in liste if any(res[a]['Reserve'] < 0 for a in ANNEES))
    evol = _M(moy_r_2035 - moy_r_2026)

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Reserve moy. 2035", f"{_M(moy_r_2035):,.1f} M".replace(",", " "),
                 delta=f"{'+' if evol >= 0 else ''}{evol:,.1f} M vs 2026".replace(",", " "),
                 delta_kind="positive" if evol >= 0 else "negative")
    with cols[1]:
        kpi_card("Employes moy. 2035", fmt_int(moy_emp))
    with cols[2]:
        kpi_card("Retraites moy. 2035", fmt_int(moy_ret))
    with cols[3]:
        pct = 100 * n_faillite / len(liste)
        kpi_card("Simulations en faillite",
                 f"{n_faillite}/{len(liste)}",
                 delta=f"{pct:.0f}% des simulations",
                 delta_kind="negative" if pct > 0 else "positive")


def afficher_section_scenario(liste, scenario):
    section("Indicateurs cles")
    afficher_kpis_n_sim(liste, scenario)

    section("Resultats moyens annuels")
    indicateurs = INDIC_S1 if scenario == 1 else INDIC_S2
    agg = aggreger_simulations(liste, ANNEES, indicateurs)
    rows = []
    for a in ANNEES:
        row = {"Annee": a}
        for ind in indicateurs:
            vals = agg[ind][a]
            moy = sum(vals) / len(vals)
            if ind in ("TotCotis", "TotPens", "Reserve"):
                row[f"{ind} (Mdhs)"] = round(moy / 1e6, 2)
            else:
                row[ind] = round(moy, 1)
        rows.append(row)
    st.dataframe(rows, use_container_width=True, hide_index=True)

    section("Reserve sur 10 ans · toutes simulations")
    rows = []
    for idx, res in enumerate(liste, start=1):
        rows.append({"Sim": idx, **{str(a): round(res[a]['Reserve']/1e6, 2) for a in ANNEES}})
    rows.append({"Sim": "MOY",
                 **{str(a): round(sum(r[a]['Reserve'] for r in liste)/len(liste)/1e6, 2)
                    for a in ANNEES}})
    st.dataframe(rows, use_container_width=True, hide_index=True, height=380)

    section("Visualisations")
    color = COLOR_S1 if scenario == 1 else COLOR_S2

    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(fig_reserve_ic(liste, scenario, color))
        st.pyplot(fig_double_courbe(liste, 'TotEmp', 'TotRet', "Effectifs (employes vs retraites)",
                                    "Nombre", COLOR_PRIMARY, COLOR_DANGER))
    with c2:
        st.pyplot(fig_double_courbe(liste, 'TotCotis', 'TotPens',
                                    "Cotisations vs Pensions", "Mdhs",
                                    COLOR_PRIMARY, COLOR_DANGER, en_M=True))
        st.pyplot(fig_nouvret_nouvrec(liste, scenario))

    if scenario == 2:
        section("Specifique Scenario 2")
        c3, c4 = st.columns(2)
        with c3:
            st.pyplot(fig_plus63(liste))
            st.pyplot(fig_boxplot(liste))
        with c4:
            st.pyplot(fig_hist_reserve(liste))


def afficher_comparaison(liste_s1, liste_s2):
    section("Resume executif")
    agg1 = aggreger_simulations(liste_s1, ANNEES, ['Reserve'])
    agg2 = aggreger_simulations(liste_s2, ANNEES, ['Reserve'])
    moy1_2035 = _M(sum(agg1['Reserve'][2035]) / len(liste_s1))
    moy2_2035 = _M(sum(agg2['Reserve'][2035]) / len(liste_s2))
    gap = moy2_2035 - moy1_2035

    cols = st.columns(3)
    with cols[0]:
        kpi_card("Reserve S1 · 2035", f"{moy1_2035:,.1f} M".replace(",", " "),
                 delta_kind="negative" if moy1_2035 < 0 else "positive")
    with cols[1]:
        kpi_card("Reserve S2 · 2035", f"{moy2_2035:,.1f} M".replace(",", " "),
                 delta_kind="positive" if moy2_2035 >= 0 else "negative")
    with cols[2]:
        kpi_card("Gain reforme (S2-S1)", f"+{gap:,.1f} M".replace(",", " "),
                 delta=f"Soit x{(moy2_2035/moy1_2035):.1f}" if moy1_2035 != 0 else "",
                 delta_kind="positive")

    section("Tableau comparatif Reserve")
    moy1 = moyennes_par_annee(agg1, 'Reserve', ANNEES)
    moy2 = moyennes_par_annee(agg2, 'Reserve', ANNEES)
    rows = []
    for i, a in enumerate(ANNEES):
        rows.append({
            "Annee": a,
            "S1 (Mdhs)": round(moy1[i] / 1e6, 2),
            "S2 (Mdhs)": round(moy2[i] / 1e6, 2),
            "Gain S2-S1 (Mdhs)": round((moy2[i] - moy1[i]) / 1e6, 2),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    section("Comparaison visuelle")
    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(fig_compare_reserve(liste_s1, liste_s2, avec_ic=False))
    with c2:
        st.pyplot(fig_compare_reserve(liste_s1, liste_s2, avec_ic=True))


def afficher_ic(liste_s1, liste_s2):
    section("Intervalles de confiance a 95% · Reserve")
    annees_cible = [2026, 2030, 2035]
    rows = []
    for label, liste in (("Scenario 1", liste_s1), ("Scenario 2", liste_s2)):
        if not liste:
            continue
        agg = aggreger_simulations(liste, ANNEES, ['Reserve'])
        for a in annees_cible:
            m, inf, sup, larg = intervalle_confiance(agg['Reserve'][a])
            rows.append({
                "Scenario": label,
                "Annee": a,
                "Moyenne (Mdhs)": round(m / 1e6, 2),
                "IC Inf": round(inf / 1e6, 2),
                "IC Sup": round(sup / 1e6, 2),
                "Largeur": round(larg / 1e6, 2),
            })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    if liste_s2:
        section("IC 95% specifiques Scenario 2 (Plus63)")
        rows = []
        agg = aggreger_simulations(liste_s2, ANNEES, ['Plus63', 'Plus63H', 'Plus63F'])
        for ind in ('Plus63', 'Plus63H', 'Plus63F'):
            for a in annees_cible:
                m, inf, sup, larg = intervalle_confiance(agg[ind][a])
                rows.append({
                    "Indicateur": ind,
                    "Annee": a,
                    "Moyenne": round(m, 1),
                    "IC Inf": round(inf, 1),
                    "IC Sup": round(sup, 1),
                    "Largeur": round(larg, 1),
                })
        st.dataframe(rows, use_container_width=True, hide_index=True)


def afficher_n_simulations(IX, IY, IZ, n, faire_s1, faire_s2):
    liste_s1 = liste_s2 = None

    if faire_s1:
        with st.status(f"Execution Scenario 1 · {n} simulations...", expanded=True) as status:
            bar = st.progress(0.0, text="Initialisation...")
            t0 = time.time()
            liste_s1 = lancer_n_simulations(simuler_scenario1, IX, IY, IZ, n, bar, "S1")
            bar.empty()
            status.update(label=f"✓ Scenario 1 termine en {time.time()-t0:.1f}s", state="complete")

    if faire_s2:
        with st.status(f"Execution Scenario 2 · {n} simulations...", expanded=True) as status:
            bar = st.progress(0.0, text="Initialisation...")
            t0 = time.time()
            liste_s2 = lancer_n_simulations(simuler_scenario2, IX, IY, IZ, n, bar, "S2")
            bar.empty()
            status.update(label=f"✓ Scenario 2 termine en {time.time()-t0:.1f}s", state="complete")

    onglet_names = []
    if liste_s1: onglet_names.append("◐ Scenario 1")
    if liste_s2: onglet_names.append("◑ Scenario 2")
    if liste_s1 and liste_s2: onglet_names.append("⚖ Comparaison")
    onglet_names.append("∑ Intervalles de confiance")

    onglets = st.tabs(onglet_names)
    i = 0
    if liste_s1:
        with onglets[i]: afficher_section_scenario(liste_s1, 1)
        i += 1
    if liste_s2:
        with onglets[i]: afficher_section_scenario(liste_s2, 2)
        i += 1
    if liste_s1 and liste_s2:
        with onglets[i]: afficher_comparaison(liste_s1, liste_s2)
        i += 1
    with onglets[i]: afficher_ic(liste_s1, liste_s2)


# ============================================================================
# ROUTING
# ============================================================================

if lancer:
    try:
        valider_germes(IX, IY, IZ)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    faire_s1 = scenario_choix in ("Scenario 1 seul", "Les deux (comparaison)")
    faire_s2 = scenario_choix in ("Scenario 2 seul", "Les deux (comparaison)")

    if mode_choix == "Simulation unique":
        afficher_simulation_unique(IX, IY, IZ, faire_s1, faire_s2)
    else:
        afficher_n_simulations(IX, IY, IZ, n_sim, faire_s1, faire_s2)
else:
    # Landing page
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">◐ Scenario 1 · Actuel</div>
            <div style="color:{COLOR_TEXT}; font-size:14px; font-weight:500; margin-top:8px; line-height:1.6">
                Depart 63 ans fixe · Avancement +5% (2026/2030/2034)<br>
                Cotisation employe 5-10% · Recrutement 250-400/an
            </div>
        </div>""", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">◑ Scenario 2 · Reforme</div>
            <div style="color:{COLOR_TEXT}; font-size:14px; font-weight:500; margin-top:8px; line-height:1.6">
                Depart flexible 63-70 ans · Avancement +10%<br>
                Cotisation employe + employeur · Recrutement 300-600/an
            </div>
        </div>""", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">⚙ Methodologie</div>
            <div style="color:{COLOR_TEXT}; font-size:14px; font-weight:500; margin-top:8px; line-height:1.6">
                Generateur Wichmann-Hill (alea)<br>
                10 000 employes + 3 000 retraites initiaux<br>
                Periode 2026-2035 · IC a 95%
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    st.info("◀ Configurez les parametres dans la barre laterale puis cliquez sur **LANCER LA SIMULATION**.")

    with st.expander("◈ Methodologie detaillee"):
        st.markdown(f"""
        ##### Generateur pseudo-aleatoire (Wichmann-Hill)
        Trois germes `IX`, `IY`, `IZ` entre 1 et 30 000 alimentent la fonction `alea(IX, IY, IZ)`
        imposee par le sujet. Pour la i-eme simulation : `IXi = IX0 + (i-1)*3`, `IYi = IY0 + (i-1)*5`,
        `IZi = IZ0 + (i-1)*7` (modulo 30 000).

        ##### Formule de pension
        `PR_mensuelle = (NAT × 2 / 100) × DSAR`
        - **NAT** : nombre d'annees travaillees jusqu'au depart en retraite
        - **DSAR** : dernier salaire mensuel avant la retraite

        ##### Reserve de la caisse
        `Reserve(N) = Reserve(N-1) + TotCotis(N) - TotPens(N)`
        Une reserve negative indique une **faillite**.

        ##### Intervalle de confiance a 95%
        Sur N simulations : `IC = [m - 1.96·s/√n , m + 1.96·s/√n]`
        """)

st.markdown(f"""
<div class="footer-caption">
    Simulation discrete · Caisse de retraite marocaine · Periode 2026-2035 · Build {time.strftime("%Y-%m-%d")}
</div>
""", unsafe_allow_html=True)
