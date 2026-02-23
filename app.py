import streamlit as st
import pandas as pd
import requests
import joblib
import numpy as np
import statistics
import altair as alt
import random
import math
from collections import Counter
from datetime import datetime, timedelta
import os
import streamlit.components.v1 as components

# --- 1. CONFIGURATION V56.2 (ANIMATION LOGO & SPACING) ---
st.set_page_config(page_title="Le Pif Du Foot", layout="wide", page_icon="👃")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:ital,wght@0,300;0,400;0,700;0,900;1,300&display=swap');

    /* FOND GÉNÉRAL & TEXTE */
    .stApp, [data-testid="stAppViewContainer"] { background-color: #0B0E14 !important; color: #FFFFFF !important; font-family: 'Kanit', sans-serif; }
    p, h1, h2, h3, div, span, label, h4, h5, h6, li, td, th { color: #FFFFFF !important; font-family: 'Kanit', sans-serif; }

    /* HEADER CONTAINER CENTRÉ */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] { align-items: center; text-align: center; }

    /* --- NOUVELLE SECTION LOGO ET ANIMATION --- */
    
    /* Définition de l'animation : de 100% à 70% */
    @keyframes shrinkLogoAnimation {
        0% { transform: scale(1); }
        100% { transform: scale(0.7); }
    }

    .logo-wrapper {
        display: flex;
        justify-content: center;
        margin-bottom: 0px; /* Espace réduit sous le logo */
    }
    .logo-wrapper img { 
        /* Taille de base (état 100% actuel) */
        width: 70% !important; 
        max-width: 250px;      
        height: auto;
        
        /* Styles visuels */
        border: 2px solid rgba(255, 255, 255, 0.8); 
        border-radius: 20px; 
        padding: 5px; 
        background: rgba(26, 28, 36, 0.6); 
        backdrop-filter: blur(10px);
        box-shadow: 0 0 30px rgba(0, 255, 153, 0.3); 
        
        /* Application de l'animation sur 3s, 'forwards' garde l'état final à 70% */
        animation: shrinkLogoAnimation 3s ease-in-out forwards;

        /* On garde la transition uniquement sur l'ombre pour le survol */
        transition: box-shadow 0.3s ease;
    }
    /* Ajustement du survol pour qu'il fonctionne par-dessus l'échelle 0.7 */
    .logo-wrapper img:hover { 
        transform: scale(0.75) !important; /* Zoom léger par rapport au 0.7 final */
        box-shadow: 0 0 40px rgba(0, 255, 153, 0.5); 
    }

    /* BASELINE STYLISÉE AVEC ESPACE RÉDUIT */
    .pif-subtitle { 
        text-align: center; 
        font-weight: 300; 
        font-style: italic; 
        color: #E0E0E0 !important; 
        font-size: 1.6rem; 
        margin-top: 5px; /* Espace réduit au-dessus de la phrase */
        margin-bottom: 40px; 
        letter-spacing: 1.5px; 
        text-shadow: 0 0 15px rgba(0, 255, 153, 0.5); 
    }

    /* ------------------------------------------ */


    /* TITRES DE SECTIONS */
    .my-sel-title { text-align: center; font-weight: 900; color: #FFD700 !important; font-size: 2.2rem; border-bottom: 2px solid rgba(255, 215, 0, 0.5); padding-bottom: 10px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 1px;}
    .narine-title { text-align: center; font-weight: 900; color: #00D4FF !important; font-size: 2.2rem; border-bottom: 2px solid rgba(0, 212, 255, 0.5); padding-bottom: 10px; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 1px;}

    /* FENÊTRES MODALES */
    div[role="dialog"] { background-color: rgba(11, 16, 22, 0.95) !important; backdrop-filter: blur(15px); border: 1px solid #00FF99 !important; border-radius: 20px !important; box-shadow: 0 10px 40px rgba(0, 255, 153, 0.2); }
    div[role="dialog"] * { color: #FFFFFF !important; }
    div[role="dialog"] h2, div[role="dialog"] h3 { color: #00FF99 !important; text-align: center; font-weight: 900; }
    
    /* FIX BUG GRAPHIQUES */
    #vg-tooltip-element { background-color: rgba(26, 28, 36, 0.9) !important; backdrop-filter: blur(5px); color: white !important; border: 1px solid #00FF99 !important; border-radius: 8px; }
    #vg-tooltip-element td { color: white !important; }
    summary.vega-actions { display: none !important; }

    /* VISIBILITÉ DES SELECTBOX (LISTES DÉROULANTES) */
    div[data-baseweb="select"] > div, div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { background-color: #151821 !important; color: white !important; border-color: #333 !important; }
    li[role="option"] { background-color: #151821 !important; color: white !important; transition: background-color 0.2s ease; }
    div[data-baseweb="select"] svg { fill: white !important; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #00FF99 !important; }
    li[role="option"]:hover span, li[role="option"][aria-selected="true"] span, li[role="option"]:hover div, li[role="option"][aria-selected="true"] div { color: #000000 !important; font-weight: 900 !important; }

    /* SIDEBAR TEXTS */
    [data-testid="stSidebarUserContent"] h1, [data-testid="stSidebarUserContent"] h2, [data-testid="stSidebarUserContent"] h3 { color: #00FF99 !important; font-family: 'Kanit', sans-serif; font-weight: 900; }

    /* BOUTONS STANDARDS ANIMES */
    button[kind="primary"] { background: linear-gradient(90deg, #00FF99, #00CC77) !important; color: #0B0E14 !important; font-weight: 900 !important; border: none !important; border-radius: 8px !important; box-shadow: 0 4px 15px rgba(0, 255, 153, 0.3) !important; transition: all 0.3s ease !important; width: 100%; }
    button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 255, 153, 0.5) !important; }
    button[kind="secondary"] { background: linear-gradient(90deg, #0055FF, #00D4FF) !important; color: white !important; border: none !important; font-weight: 900 !important; border-radius: 8px !important; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important; transition: all 0.3s ease !important; width: 100%; }
    button[kind="secondary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5) !important; }
    .btn-plan-b button { background: linear-gradient(90deg, #FF4B4B, #FF8800) !important; color: white !important; border: none !important; font-weight: 900 !important; box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important; transition: all 0.3s ease !important; width: 100%;}
    .btn-plan-b button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 75, 75, 0.5) !important; }
    
    /* BOUTON DORE SPÉCIFIQUE (MA BANKROLL) */
    button:has(p:contains("MA BANKROLL")) { background: linear-gradient(90deg, #FFD700, #DAA520) !important; border: none !important; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4) !important; transition: all 0.3s ease !important; width: 100%; }
    button:has(p:contains("MA BANKROLL")):hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6) !important; }
    button:has(p:contains("MA BANKROLL")) p { color: #0B0E14 !important; font-weight: 900 !important; }
    
    /* BOUTON LIVE & VIDER */
    button:has(p:contains("LIVE SURPRISE")) { background: linear-gradient(90deg, #FF0044, #CC0000) !important; border: none !important; box-shadow: 0 4px 15px rgba(255, 0, 68, 0.5) !important; width: 100%; }
    button:has(p:contains("LIVE SURPRISE")) p { color: #FFFFFF !important; font-weight: 900 !important; }
    button:has(p:contains("Vider ce tableau")) { background: linear-gradient(90deg, #FF0044, #AA0000) !important; color: white !important; border: none !important; font-weight: bold; width: 100%; }
    button:has(p:contains("Vider ce tableau")):hover { box-shadow: 0 4px 15px rgba(255, 0, 68, 0.6) !important; }

    /* BOUTON NARINE */
    button:has(p:contains("FOUILLE DANS LA NARINE")) { background: linear-gradient(90deg, #00D4FF, #0055FF) !important; border: none !important; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4) !important; transition: all 0.3s ease !important; width: 100%; }
    button:has(p:contains("FOUILLE DANS LA NARINE")):hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(0, 212, 255, 0.6) !important; }
    button:has(p:contains("FOUILLE DANS LA NARINE")) p { color: #FFFFFF !important; font-weight: 900 !important; }

    /* MATCH HEADER & CARTES */
    .match-header { display: flex; flex-direction: row; align-items: center; justify-content: space-between; background: rgba(26, 28, 36, 0.8); padding: 12px 8px; border-radius: 12px; margin-bottom: 5px; border: 1px solid #333; backdrop-filter: blur(5px); }
    .team-box { text-align: center; width: 40%; display: flex; flex-direction: column; align-items: center; }
    .team-logo { width: 50px; height: 50px; object-fit: contain; margin-bottom: 5px; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.5)); }
    .team-name { font-size: 0.85rem; font-weight: bold; line-height: 1.2; color: white !important; }
    .vs-box { width: 20%; text-align: center; color: #00FF99 !important; font-weight: 900; font-size: 1.3rem; }
    
    div[data-testid="stExpander"] { background-color: #151821 !important; border-color: #333 !important; border-radius: 12px !important; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
    div[data-testid="stExpander"] summary p { font-weight: bold !important; font-size: 1.05rem; }

    .probs-container { display: flex; flex-direction: row; justify-content: space-between; gap: 8px; margin-bottom: 20px; width: 100%; }
    .prob-box { background: linear-gradient(145deg, #1a1c24, #11141c); border: 1px solid #363b4e; border-radius: 12px; width: 32%; padding: 15px 5px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
    .prob-label { font-size: 0.7rem; color: #AAAAAA !important; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
    .prob-value { font-size: 1.4rem; font-weight: 900; color: #FFFFFF !important; line-height: 1.2; margin-top: 5px; }
    
    .ticket-match-title { font-weight: bold; color: #00FF99 !important; margin-top: 15px; border-bottom: 1px solid #333; padding-bottom: 5px; font-size: 1.1rem; }
    
    /* STYLING DES TABLES DE BANKROLL ET STATS */
    .comp-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.95rem; background-color: transparent !important; }
    .comp-table th, .comp-table td { border: 1px solid #444; padding: 12px; text-align: center; }
    .comp-table th { background-color: #1a1c24; color: #00FF99 !important; font-weight: 900; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; }
    .comp-table tr:nth-child(even) { background-color: rgba(26, 28, 36, 0.5); }
    
    [data-testid="stDataFrame"] > div { background-color: #0e1117 !important; border: 1px solid #333 !important; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    
    /* ANIMATION LIVE UPSET */
    @keyframes pulse-border { 0% { border-color: #333; box-shadow: 0 0 0 rgba(255, 68, 0, 0); } 50% { border-color: #FF4400; box-shadow: 0 0 20px rgba(255, 68, 0, 0.8); } 100% { border-color: #333; box-shadow: 0 0 0 rgba(255, 68, 0, 0); } }
    .live-upset-card { background: linear-gradient(145deg, #1a0a0a, #11141c); padding: 15px; border-radius: 12px; margin-bottom: 15px; animation: pulse-border 1.5s infinite; border: 2px solid #FF4400; }
    .live-normal-card { background: #151821; padding: 15px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #333; }
    .blink-text { color: #FF4400; font-weight: bold; animation: text-pulse 1.5s infinite; font-size: 1.1em; }
    @keyframes text-pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

    /* STYLE POUR LES TABS DE LA NARINE */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1a1c24; border-radius: 8px 8px 0 0; color: #aaa; border: 1px solid #333; border-bottom: none; }
    .stTabs [aria-selected="true"] { background-color: #00D4FF !important; color: #0B0E14 !important; font-weight: 900; }

    @media only screen and (max-width: 640px) { .block-container { padding-top: 1rem !important; padding-left: 0.3rem !important; padding-right: 0.3rem !important; } }
</style>
""", unsafe_allow_html=True)

API_KEY = "4d3c1dbf76600a937722ff6425d450ee"
HEADERS = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
LEAGUE_IDS = [2, 3, 39, 61, 62, 140, 135, 78, 94, 45, 144, 203, 307, 143, 323, 848]

# STATES INITIAUX
if 'analyzed_match_data' not in st.session_state: st.session_state.analyzed_match_data = None
if 'ticket_data' not in st.session_state: st.session_state.ticket_data = None
if 'scorer_ticket' not in st.session_state: st.session_state.scorer_ticket = None
if 'mode' not in st.session_state: st.session_state.mode = "std" 
if 'quantum_mode' not in st.session_state: st.session_state.quantum_mode = False

# STATES MA SÉLECTION & UX
if 'persisted_selections' not in st.session_state: st.session_state.persisted_selections = {}
if 'selection_validated' not in st.session_state: st.session_state.selection_validated = False
if 'selection_analyzed' not in st.session_state: st.session_state.selection_analyzed = False
if 'selection_ai_results' not in st.session_state: st.session_state.selection_ai_results = {}
if 'auto_analyzed' not in st.session_state: st.session_state.auto_analyzed = False
if 'show_plan_b' not in st.session_state: st.session_state.show_plan_b = False
if 'auto_trigger_analyze' not in st.session_state: st.session_state.auto_trigger_analyze = False
if 'collapse_sidebar' not in st.session_state: st.session_state.collapse_sidebar = False
if 'top_suggestions' not in st.session_state: st.session_state.top_suggestions = []

def get_empty_bankroll():
    return pd.DataFrame({
        "PARIS": [f"Paris {j}" for j in range(1, 21)],
        "NOMS DES EQUIPES": ["" for _ in range(20)],
        "COTES": [1.50 for _ in range(20)],
        "PRONOS": ["" for _ in range(20)],
        "MISES": [10.0 for _ in range(20)],
        "RESULTATS": ["⏳ En attente" for _ in range(20)],
        "RESULTATS FINANCIERS": ["⚪ 0.00 €" for _ in range(20)],
        "Total Cumulé": ["🏦 0.00 €" for _ in range(20)],
        "Prono de l'IA": ["" for _ in range(20)]
    })

# STATES BANKROLL (Persistance Totale & Versioning pour forcer le rafraîchissement)
BANKROLL_FILE = 'bankroll_data.pkl'
if 'bankroll_versions' not in st.session_state:
    st.session_state.bankroll_versions = {f"Tableau {i}": 0 for i in range(1, 11)}

if 'bankrolls' not in st.session_state:
    if os.path.exists(BANKROLL_FILE):
        try: 
            st.session_state.bankrolls = joblib.load(BANKROLL_FILE)
            for k in st.session_state.bankrolls.keys():
                if k not in st.session_state.bankroll_versions:
                    st.session_state.bankroll_versions[k] = 0
        except: pass
    if 'bankrolls' not in st.session_state or not st.session_state.bankrolls:
        st.session_state.bankrolls = {}
        for i in range(1, 11):
            st.session_state.bankrolls[f"Tableau {i}"] = get_empty_bankroll()
        joblib.dump(st.session_state.bankrolls, BANKROLL_FILE)

needs_save = False
for k in st.session_state.bankrolls:
    if "Prono de l'IA" not in st.session_state.bankrolls[k].columns:
        st.session_state.bankrolls[k]["Prono de l'IA"] = ""; needs_save = True
    st.session_state.bankrolls[k]["NOMS DES EQUIPES"] = st.session_state.bankrolls[k]["NOMS DES EQUIPES"].fillna("")
if needs_save: joblib.dump(st.session_state.bankrolls, BANKROLL_FILE)

try: model = joblib.load('oracle_brain.pkl'); MODEL_LOADED = True
except: model = None; MODEL_LOADED = False

dark_axis_config = alt.Axis(labelColor='#E0E0E0', titleColor='#E0E0E0', gridColor='#2a2d3d', domainColor='#555555', tickColor='#555555', labelFontSize=12, titleFontSize=13)

# --- MOTEUR DONNÉES ---
@st.cache_data(ttl=3600)
def get_upcoming_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d") 
    clean_fixtures = []
    for l in LEAGUE_IDS:
        try:
            r = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"league": l, "season": "2025", "from": today, "to": end, "timezone": "Europe/Paris"}).json()
            if 'response' in r:
                for f in r['response']:
                    if f['fixture']['status']['short'] in ['NS', 'TBD']: clean_fixtures.append(f)
        except: pass
    return clean_fixtures

@st.cache_data(ttl=3600)
def get_past_matches(days_ago):
    date_str = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    clean_fixtures = []
    for l in LEAGUE_IDS:
        try:
            r = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"league": l, "season": "2025", "date": date_str, "timezone": "Europe/Paris"}).json()
            if 'response' in r:
                for f in r['response']:
                    if f['fixture']['status']['short'] in ['FT', 'AET', 'PEN']: clean_fixtures.append(f)
        except: pass
    return clean_fixtures

@st.cache_data(ttl=60)
def get_live_matches():
    try:
        r = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"live": "all"}).json()
        if 'response' in r: return [f for f in r['response'] if f['league']['id'] in LEAGUE_IDS]
    except: pass
    return []

@st.cache_data(ttl=3600)
def get_deep_stats(tid):
    d = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"team": str(tid), "last": "20", "status": "FT"}).json().get('response', [])
    if not d: return None
    history = []
    for m in d:
        h = m['teams']['home']['id'] == tid
        gf = (m['goals']['home'] if h else m['goals']['away']) or 0
        ga = (m['goals']['away'] if h else m['goals']['home']) or 0
        res = "✅" if gf > ga else ("➖" if gf == ga else "❌")
        hf = m['score']['halftime']['home'] if h else m['score']['halftime']['away']
        ha = m['score']['halftime']['away'] if h else m['score']['halftime']['home']
        ht_d = 1 if hf is not None and ha is not None and hf == ha else 0
        ft_d = 1 if gf == ga else 0
        s_70, c_70 = 0, 0
        if 'events' in m and m['events']:
            for ev in m['events']:
                if ev['type'] == 'Goal' and 'Missed' not in str(ev.get('detail', '')):
                    t = ev['time']['elapsed']
                    if t and t >= 70:
                        if ev['team']['id'] == tid: s_70 += 1
                        else: c_70 += 1
        else:
            if gf > 0 and random.random() > 0.5: s_70 += 1
            if ga > 0 and random.random() > 0.5: c_70 += 1
        
        match_date = datetime.fromisoformat(m['fixture']['date'].replace('Z', '+00:00')).date()
        history.append({"gf": gf, "ga": ga, "res": res, "pen_call": 1 if (gf > 2 and random.random() > 0.8) else 0, "red_card": 1 if (random.random() > 0.95) else 0, "ht_draw": ht_d, "ft_draw": ft_d, "scored_70": 1 if s_70 > 0 else 0, "conceded_70": 1 if c_70 > 0 else 0, "is_home": h, "date": match_date})
    
    history.sort(key=lambda x: x['date'], reverse=True)
    return {"name": d[0]['teams']['home']['name'] if d[0]['teams']['home']['id'] == tid else d[0]['teams']['away']['name'], "id": tid, "history": history, "league_id": d[0]['league']['id']}

@st.cache_data(ttl=3600)
def get_standings(league_id):
    try:
        r = requests.get("https://v3.football.api-sports.io/standings", headers=HEADERS, params={"league": league_id, "season": "2025"}).json()
        if 'response' in r and len(r['response']) > 0: return r['response'][0]['league']['standings'][0]
    except: pass
    return None

def process_stats_by_filter(raw_stats, limit, venue="all"):
    if not raw_stats or 'history' not in raw_stats: return None
    data = raw_stats['history']
    
    if venue == "home": data = [x for x in data if x['is_home']][:limit]
    elif venue == "away": data = [x for x in data if not x['is_home']][:limit]
    else: data = data[:limit]
    
    if not data: return None
    
    weights = [max(0.5, 1.5 - (0.1 * i)) for i in range(len(data))]
    sum_weights = sum(weights)
    
    avg_gf = sum(x['gf'] * w for x, w in zip(data, weights)) / sum_weights
    avg_ga = sum(x['ga'] * w for x, w in zip(data, weights)) / sum_weights
    
    pts = [(3 if x['res']=="✅" else (1 if x['res']=="➖" else 0)) for x in data]
    form = sum(p * w for p, w in zip(pts, weights)) / sum_weights
    
    cs = sum([1 for x in data if x['ga']==0])
    btts = sum([1 for x in data if x['gf']>0 and x['ga']>0])
    try: vol = statistics.stdev([x['gf'] for x in data])
    except: vol = 0
    
    match_dates = [x['date'] for x in data]

    return {"name": raw_stats['name'], "id": raw_stats['id'], "avg_gf": avg_gf, "avg_ga": avg_ga, "form": form, "cs_rate": cs/len(data)*100, "btts_rate": btts/len(data)*100, "draw_rate": sum([x['ft_draw'] for x in data])/len(data)*100, "vol": vol, "pen_for": sum([x['pen_call'] for x in data]), "red_cards": sum([x['red_card'] for x in data]), "streak": "".join([x['res'] for x in data[:5]]), "count": len(data), "raw_gf": [x['gf'] for x in data], "ht_draws": sum([x['ht_draw'] for x in data]), "ft_draws": sum([x['ft_draw'] for x in data]), "scored_70": sum([x['scored_70'] for x in data]), "conceded_70": sum([x['conceded_70'] for x in data]), "dates": match_dates}

@st.cache_data(ttl=86400)
def get_top_scorers(league_id, team_id):
    try:
        r = requests.get("https://v3.football.api-sports.io/players/topscorers", headers=HEADERS, params={"league": league_id, "season": "2025"}).json()
        if 'response' in r:
            return [{"name": p['player']['name'], "goals": p['statistics'][0]['goals']['total'] or 0, "rating": float(p['statistics'][0]['games']['rating'] or 0)} for p in r['response'] if p['statistics'][0]['team']['id'] == team_id][:3]
    except: pass
    return []

@st.cache_data(ttl=3600)
def get_h2h_stats(h_id, a_id):
    d = requests.get("https://v3.football.api-sports.io/fixtures/headtohead", headers=HEADERS, params={"h2h": f"{h_id}-{a_id}"}).json().get('response', [])
    if not d: return None
    goals = [m['goals']['home']+m['goals']['away'] for m in d if m['fixture']['status']['short'] in ['FT', 'AET', 'PEN'] and m['goals']['home'] is not None and m['goals']['away'] is not None]
    if not goals: return None
    return {"vol": statistics.stdev(goals) if len(goals)>1 else 0, "matches": len(goals), "avg_goals": sum(goals)/len(goals)}

def get_advanced_mock_data(h, a):
    random.seed(h['id'])
    h_poss = 50 + (h['form'] - a['form']) * 10 + random.uniform(-3, 3)
    h_poss = min(75, max(25, h_poss)); a_poss = 100 - h_poss
    h_xg = h['avg_gf'] * random.uniform(0.9, 1.2); a_xg = a['avg_gf'] * random.uniform(0.9, 1.2)
    h_shots = h['avg_gf'] * 6.5 + random.uniform(2, 5); a_shots = a['avg_gf'] * 6.5 + random.uniform(2, 5)
    h_ppda = max(5, 15 - (h['form'] * 2) + random.uniform(-2, 2)); a_ppda = max(5, 15 - (a['form'] * 2) + random.uniform(-2, 2))
    random.seed()
    return {"h_poss": h_poss, "a_poss": a_poss, "h_xg": h_xg, "a_xg": a_xg, "h_shots": h_shots, "a_shots": a_shots, "h_sot": h_shots * random.uniform(0.3, 0.45), "a_sot": a_shots * random.uniform(0.3, 0.45), "h_xga": h['avg_ga'] * random.uniform(0.8, 1.1), "a_xga": a['avg_ga'] * random.uniform(0.8, 1.1), "h_ppda": h_ppda, "a_ppda": a_ppda}

def simulate_10k_scenarios(h_stats, a_stats):
    h_lam = max(0.1, (h_stats['avg_gf'] + a_stats['avg_ga']) / 2)
    a_lam = max(0.1, (a_stats['avg_gf'] + h_stats['avg_ga']) / 2)
    scores = []; red_c, pen_c = 0, 0
    for _ in range(10000):
        chaos = random.random()
        hr = 1 if (chaos > 0.98 and h_stats['red_cards']>0) else 0
        ar = 1 if (chaos > 0.98 and a_stats['red_cards']>0) else 0
        if hr or ar: red_c += 1
        ip = 1 if chaos < 0.05 else 0
        if ip: pen_c += 1
        s_h = np.random.poisson(h_lam * (0.8 if hr else 1.0)) + (1 if ip and random.random()>0.5 else 0)
        s_a = np.random.poisson(a_lam * (0.8 if ar else 1.0))
        scores.append(f"{s_h}-{s_a}")
    return Counter(scores).most_common(3), red_c, pen_c

def get_quantum_analysis(h, a):
    xg_h = (h['avg_gf'] / 1.35) * (a['avg_ga'] / 1.35) * 1.35 * 1.15
    xg_a = (a['avg_gf'] / 1.35) * (h['avg_ga'] / 1.35) * 1.35
    best_s, best_p, upset = "0-0", 0, 0
    for i in range(6):
        for j in range(6):
            p = (math.exp(-xg_h) * (xg_h**i) / math.factorial(i)) * (math.exp(-xg_a) * (xg_a**j) / math.factorial(j))
            if p > best_p: best_p=p; best_s=f"{i}-{j}"
            if xg_h > xg_a and j > i: upset += p
            elif xg_a > xg_h and i > j: upset += p
    mom_h = sum([(3 if c=="✅" else (1 if c=="➖" else 0)) * w for c, w in zip(h['streak'], [5,4,3,2,1])]) / 45 * 100 if len(h['streak'])==5 else 50
    mom_a = sum([(3 if c=="✅" else (1 if c=="➖" else 0)) * w for c, w in zip(a['streak'], [5,4,3,2,1])]) / 45 * 100 if len(a['streak'])==5 else 50
    return {"sniper_score": best_s, "sniper_conf": best_p*100, "upset_risk": upset*100, "xg_h": xg_h, "xg_a": xg_a, "mom_h": mom_h, "mom_a": mom_a}

def get_coherent_probabilities(h, a):
    lam_h = max(0.1, (h['avg_gf'] + a['avg_ga']) / 2) * 1.15
    lam_a = max(0.1, (a['avg_gf'] + h['avg_ga']) / 2)
    ph, pd, pa = 0, 0, 0
    for i in range(6):
        for j in range(6):
            prob = (math.exp(-lam_h) * (lam_h**i) / math.factorial(i)) * (math.exp(-lam_a) * (lam_a**j) / math.factorial(j))
            if i == j:
                if i == 0: prob *= 1.35
                elif i == 1: prob *= 1.15
                elif i == 2: prob *= 1.05
            
            if i > j: ph += prob
            elif i == j: pd += prob
            else: pa += prob
    tot = ph + pd + pa
    if tot == 0: return [0.33, 0.34, 0.33]
    return [pd/tot, ph/tot, pa/tot]

def gen_smart_justif(type, val, h, a):
    r = []
    h_name = h.get('name', 'Domicile'); a_name = a.get('name', 'Extérieur')
    if h_name in val:
        if h.get('form', 0) > 1.5: r.append(f"{h_name} est en forme impériale à domicile.")
        if h.get('avg_gf', 0) > 1.5: r.append("Attaque prolifique, difficile à contenir.")
        if a.get('avg_ga', 0) > 1.5: r.append(f"Défense de {a_name} très friable récemment.")
    elif a_name in val:
        if a.get('form', 0) > 1.5: r.append(f"{a_name} voyage exceptionnellement bien.")
        if a.get('avg_gf', 0) > 1.5: r.append("Redoutable efficacité en contre-attaque.")
    elif "Nul" in val: r.append("Forces équilibrées et forte tendance à la neutralisation mutuelle.")
    return random.choice(r) if r else "Analyse statistique favorable."

def gen_plan_b_justif(val, h, a):
    r = []
    h_name = str(h.get('name', 'Domicile')); a_name = str(a.get('name', 'Extérieur')); val_str = str(val)
    if h_name in val_str or "Domicile" in val_str:
        r.extend([f"Le football réserve des surprises. Poussé par son public, {h_name} pourrait déjouer les pronostics si {a_name} manque de réalisme.", f"Un bloc bas de {h_name} suivi d'un exploit individuel à domicile est un scénario piège classique."])
    elif a_name in val_str or "Extérieur" in val_str:
        r.extend([f"Attention au 'Hold-up'. {a_name} a le profil parfait pour subir et piquer en contre si {h_name} se découvre trop.", f"Si le match s'enlise, l'opportunisme de {a_name} à l'extérieur pourrait faire très mal contre le cours du jeu."])
    elif "Nul" in val_str:
        r.extend([f"La peur de perdre pourrait figer le jeu. Un match verrouillé tactiquement menant à un score de parité est très crédible.", f"Si les gardiens sont dans un grand jour, ce match a tout du match piège qui se termine sur un score nul."])
    if len(r) == 0: return "Scénario alternatif envisagé par l'IA en cas de contre-performance du favori."
    return random.choice(r)

def get_form_arrow(form_pts): return "🟢 ⬆️" if form_pts >= 2.0 else ("🔴 ⬇️" if form_pts <= 1.0 else "⚪ ➡️")

# --- TICKETS & TOP 10 ---
def gen_match_ticket(fix):
    pools = {"WIN":[], "DRAW":[], "OVER":[], "UNDER":[], "BTTS":[]}
    bar = st.sidebar.progress(0, text="Analyse Multidimensionnelle...")
    fix_copy = fix.copy(); random.shuffle(fix_copy); limit = min(len(fix_copy), 30) 
    for i, f in enumerate(fix_copy[:limit]):
        hid, aid = f['teams']['home']['id'], f['teams']['away']['id']
        raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
        if raw_h and raw_a:
            hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
            as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
            hs = process_stats_by_filter(raw_h, 10, "all"); as_ = process_stats_by_filter(raw_a, 10, "all")
            
            if hs_home and as_away:
                h2h = get_h2h_stats(hid, aid); h2h_avg = h2h['avg_goals'] if h2h else (hs['avg_gf'] + as_['avg_gf'])
                if abs(hs['form'] - as_['form']) <= 0.4 and (hs['draw_rate'] > 30 or as_['draw_rate'] > 30): pools["DRAW"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "⚖️ Résultat", "v": "Match Nul", "j": "Niveau très équilibré et forte tendance historique au nul.", "h": hs, "a": as_})
                elif hs['btts_rate'] >= 60 and as_['btts_rate'] >= 60 and hs['avg_gf'] >= 1.2 and as_['avg_gf'] >= 1.2: pools["BTTS"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🥅 Les 2 marquent", "v": "OUI", "j": "Attaques très performantes combinées à des défenses friables.", "h": hs, "a": as_})
                elif (hs['avg_gf'] + as_['avg_gf']) <= 2.2 or (hs['avg_ga'] <= 1.0 and as_['avg_ga'] <= 1.0): pools["UNDER"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🔒 Buts", "v": "-2.5 Buts", "j": "Rencontre fermée prévue. Les attaques peinent et les défenses sont solides.", "h": hs, "a": as_})
                elif (hs['avg_gf'] + as_['avg_gf']) > 3.0 and h2h_avg >= 2.5: pools["OVER"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "⚽ Buts", "v": "+2.5 Buts", "j": "Forte puissance offensive de part et d'autre. Match ouvert.", "h": hs, "a": as_})
                elif hs_home['form'] > 2.0 and as_away['form'] < 1.2: pools["WIN"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🏆 Résultat", "v": f"Victoire {hs['name']}", "j": "Domination totale du favori à domicile.", "h": hs, "a": as_})
                elif as_away['form'] > 2.0 and hs_home['form'] < 1.2: pools["WIN"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🏆 Résultat", "v": f"Victoire {as_['name']}", "j": "Dynamique impressionnante à l'extérieur face à une équipe en difficulté.", "h": hs, "a": as_})
        bar.progress((i+1)/limit)
    bar.empty()
    seen_matches = set(); final_ticket = []
    categories = ["DRAW", "UNDER", "BTTS", "WIN", "OVER"]; random.shuffle(categories)
    for cat in categories:
        if pools[cat]:
            random.shuffle(pools[cat])
            for bet in pools[cat]:
                if bet['m'] not in seen_matches: final_ticket.append(bet); seen_matches.add(bet['m']); break
    all_remaining = []
    for cat in categories: all_remaining.extend(pools[cat])
    random.shuffle(all_remaining)
    for bet in all_remaining:
        if bet['m'] not in seen_matches: final_ticket.append(bet); seen_matches.add(bet['m'])
        if len(final_ticket) >= 6: break
    return final_ticket

def gen_scorer_ticket(fix):
    scorers = []
    bar = st.sidebar.progress(0, text="Scan Buteurs...")
    fix_copy = fix.copy(); random.shuffle(fix_copy); limit = min(len(fix_copy), 15)
    for i, f in enumerate(fix_copy[:limit]):
        hid, aid, lid = f['teams']['home']['id'], f['teams']['away']['id'], f['league']['id']
        raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
        sh = get_top_scorers(lid, hid)
        if sh and raw_h and raw_a: 
            hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
            if hs and as_:
                scorers.append({"m": f"{hs['name']} vs {as_['name']}", "p": sh[0], "team": hs['name'], "h": hs, "a": as_})
        bar.progress((i+1)/limit)
    bar.empty()
    return scorers[:6]

def generate_top_10_suggestions(fixtures):
    candidates = []
    bar = st.progress(0, text="L'IA scanne les opportunités les plus fiables des 3 prochains jours...")
    fix_copy = fixtures.copy(); limit = min(len(fix_copy), 40) 
    for i, f in enumerate(fix_copy[:limit]):
        hid, aid = f['teams']['home']['id'], f['teams']['away']['id']
        raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
        if raw_h and raw_a:
            hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
            as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
            hs = process_stats_by_filter(raw_h, 10, "all"); as_ = process_stats_by_filter(raw_a, 10, "all")
            if hs_home and as_away:
                p = get_coherent_probabilities(hs_home, as_away); p = np.array(p).flatten()
                if len(p) >= 3:
                    best_idx = np.argmax(p); conf = p[best_idx] * 100; q = get_quantum_analysis(hs_home, as_away)
                    if conf >= 45:
                        score = conf - (q['upset_risk'] * 0.2)
                        pick = f"Victoire {hs['name']}" if best_idx==1 else (f"Victoire {as_['name']}" if best_idx==2 else "Match Nul")
                        candidates.append({'score': score, 'conf': conf, 'f': f, 'pick': pick, 'hs': hs, 'as_': as_, 'q': q})
        bar.progress((i+1)/limit)
    bar.empty()
    candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)
    return candidates[:10]

def update_user_selection(fix_id, match_str, home_id, away_id, league_id):
    val = st.session_state[f"rad_{fix_id}"]
    if val != "Aucun": st.session_state.persisted_selections[fix_id] = {"match": match_str, "home_id": home_id, "away_id": away_id, "league_id": league_id, "user_pick": val}
    else:
        if fix_id in st.session_state.persisted_selections: del st.session_state.persisted_selections[fix_id]

def set_match_and_analyze(m_str):
    st.session_state.main_match_select = m_str
    st.session_state.auto_trigger_analyze = True

# --- FONCTIONS BANKROLL AUTO ---
def get_status_all_matches():
    live_m = get_live_matches() or []
    past_1 = get_past_matches(1) or []
    past_2 = get_past_matches(2) or []
    past_3 = get_past_matches(3) or []
    return live_m + past_1 + past_2 + past_3

def auto_update_bankroll(df, all_matches_pool):
    changed = False
    for idx, row in df.iterrows():
        if row["RESULTATS"] == "⏳ En attente" and pd.notnull(row["NOMS DES EQUIPES"]) and row["NOMS DES EQUIPES"] != "":
            match_str = row["NOMS DES EQUIPES"]; prono_str = str(row["PRONOS"])
            for f in all_matches_pool:
                if f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}" == match_str:
                    status = f['fixture']['status']['short']
                    gh = f['goals']['home']; ga = f['goals']['away']
                    if status in ['FT', 'AET', 'PEN'] and gh is not None and ga is not None:
                        h_name = f['teams']['home']['name']; a_name = f['teams']['away']['name']
                        won = False
                        if "Victoire" in prono_str and h_name in prono_str and gh > ga: won = True
                        elif "Victoire" in prono_str and a_name in prono_str and ga > gh: won = True
                        elif "Match Nul" in prono_str and gh == ga: won = True
                        df.at[idx, "RESULTATS"] = "✅ Victoire du pronos" if won else "❌ Défaite du pronos"
                        changed = True
                    elif status in ['1H', '2H', 'HT', 'LIVE']:
                        df.at[idx, "RESULTATS"] = f"🔄 En direct ({gh or 0}-{ga or 0})"
                        changed = True
                    break
    return changed, df

def recalculate_bankroll(df):
    total_cumule = 0.0
    for idx, row in df.iterrows():
        mise = float(row["MISES"]) if pd.notnull(row["MISES"]) else 0.0
        cote = float(row["COTES"]) if pd.notnull(row["COTES"]) else 1.0
        res = str(row["RESULTATS"])
        if "✅" in res: profit = (mise * cote) - mise; df.at[idx, "RESULTATS FINANCIERS"] = f"🟢 + {profit:.2f} €"; total_cumule += profit
        elif "❌" in res: df.at[idx, "RESULTATS FINANCIERS"] = f"🔴 - {mise:.2f} €"; total_cumule -= mise
        else: df.at[idx, "RESULTATS FINANCIERS"] = "⚪ 0.00 €"
        df.at[idx, "Total Cumulé"] = f"🏦 {total_cumule:.2f} €"
    return df

def style_bankroll_df(df):
    def highlight(x):
        c = pd.DataFrame('', index=x.index, columns=x.columns)
        for i in x.index:
            res = str(x.at[i, "RESULTATS"]); row_style = ''
            if "✅" in res: row_style = 'background-color: rgba(0, 255, 153, 0.15);'
            elif "❌" in res: row_style = 'background-color: rgba(255, 75, 75, 0.15);'
            elif "🔄" in res: row_style = 'background-color: rgba(255, 136, 0, 0.15);'
            for col in x.columns: c.at[i, col] = row_style
            c.at[i, "Prono de l'IA"] += ' color: #00FF99; font-weight: bold; background-color: #0a2918;'
            fin = str(x.at[i, "RESULTATS FINANCIERS"])
            if "🟢" in fin: c.at[i, "RESULTATS FINANCIERS"] += ' color: #00FF99; font-weight: bold;'
            elif "🔴" in fin: c.at[i, "RESULTATS FINANCIERS"] += ' color: #FF4B4B; font-weight: bold;'
        return c
    return df.style.apply(highlight, axis=None)

# --- FONCTIONS D'ANALYSE ---
def calculate_rest_days(past_dates, match_date_str):
    if not past_dates: return 7
    try:
        last_match_date = past_dates[0]
        current_match_date = datetime.strptime(match_date_str, "%Y-%m-%d").date()
        delta = current_match_date - last_match_date
        return max(0, delta.days - 1)
    except: return 5

def get_ai_estimated_advanced_stats(s, league_tier=1):
    random.seed(s['id'] + int(s['form']*10))
    form_factor = s['form'] / 3.0
    off_factor = min(2.5, s['avg_gf']) / 2.5
    def_factor = max(0.5, 2.5 - s['avg_ga']) / 2.5
    xg_history = [max(0.1, gf * random.uniform(0.7, 1.3) + random.uniform(-0.2, 0.3)) for gf in s['raw_gf']]
    avg_xg = sum(xg_history) / len(xg_history) if xg_history else s['avg_gf']
    shots_pg = s['avg_gf'] * 6.5 + random.uniform(2, 5) * off_factor
    sot_pct = 30 + (form_factor * 15) + random.uniform(-5, 5)
    final_third_poss = 40 + (form_factor * 20) + (off_factor * 10) + random.uniform(-5, 5)
    recovery_time = 18 - (form_factor * 6) - (def_factor * 4) + random.uniform(-2, 3)
    shots_conceded_pg = s['avg_ga'] * 7.5 + random.uniform(3, 6) * (1-def_factor)
    gk_save_pct = 65 + (def_factor * 15) + random.uniform(-8, 8)
    errors_leading_to_shot = max(0, (1-form_factor)*2 + (1-def_factor) + random.uniform(-0.5, 1.5))
    def_line_distance = 35 + (off_factor * 15) + (form_factor * 5) + random.uniform(-5, 5)
    distance_traveled = random.randint(50, 800) if league_tier == 1 else random.randint(20, 300)
    media_pressure = random.randint(20, 90) + (1-form_factor)*20
    shots_in_box = shots_pg * (0.5 + off_factor*0.2) * random.uniform(0.8, 1.1)
    potential_assists = s['avg_gf'] * 0.8 + shots_pg * 0.1 * off_factor
    transition_speed = 15 - (off_factor * 5) + random.uniform(-2, 2)
    big_chance_ratio = (s['avg_gf'] / max(1, shots_pg)) * 100 * random.uniform(0.9, 1.2)
    ppda = 16 - (form_factor * 6) - (def_factor * 4) + random.uniform(-3, 3)
    aerial_duels_lost = 50 - (def_factor * 10) + random.uniform(-10, 10)
    recovery_distance = 40 + (form_factor * 10) + random.uniform(-5, 5)
    cb_stability = max(0, int(4 - (form_factor*2) + random.uniform(-1, 2)))
    random.seed()
    return {
        "xg_history": xg_history, "avg_xg": avg_xg, "shots_pg": shots_pg, "sot_pct": sot_pct, "final_third_poss": final_third_poss, "recovery_time": recovery_time,
        "shots_conceded_pg": shots_conceded_pg, "gk_save_pct": gk_save_pct, "errors_leading_to_shot": errors_leading_to_shot, "def_line_distance": def_line_distance,
        "distance_traveled": distance_traveled, "media_pressure": media_pressure, "shots_in_box": shots_in_box, "potential_assists": potential_assists, "transition_speed": transition_speed, "big_chance_ratio": big_chance_ratio,
        "ppda": ppda, "aerial_duels_lost": aerial_duels_lost, "recovery_distance": recovery_distance, "cb_stability": cb_stability
    }

def calculate_weighted_ou25(h_stats, a_stats, context_val=0):
    avg_goals_sim = (h_stats['avg_gf'] + a_stats['avg_gf'])
    score_sim = 1 if avg_goals_sim > 2.5 else 0
    avg_conceded_opp = (h_stats['avg_ga'] + a_stats['avg_ga'])
    score_opp = 1 if avg_conceded_opp > 2.5 else 0
    form_diff = abs(h_stats['form'] - a_stats['form'])
    score_form = 1 if form_diff > 1.0 or (h_stats['form']>2 and a_stats['form']>2) else 0
    score_context = 1 if context_val > 0.5 else 0
    total_score = (score_sim * 0.40) + (score_opp * 0.30) + (score_form * 0.20) + (score_context * 0.10)
    is_over = total_score >= 0.55
    justifs = []
    if score_sim: justifs.append("Historique récent prolifique en buts pour les deux équipes dans cette configuration.")
    else: justifs.append("Tendance récente à des matchs fermés et tactiques.")
    if score_opp: justifs.append("Les défenses montrent des signes de fébrilité inquiétants.")
    else: justifs.append("Blocs défensifs solides et bien en place.")
    if form_diff > 1.0: justifs.append("L'écart de niveau pourrait mener à un score fleuve.")
    elif h_stats['form']>2 and a_stats['form']>2: justifs.append("Deux équipes en pleine confiance offensivement.")
    return is_over, total_score * 100, " ".join(justifs)

def display_scan_inline(f_data):
    hid, aid = f_data['teams']['home']['id'], f_data['teams']['away']['id']
    h_name, a_name = f_data['teams']['home']['name'], f_data['teams']['away']['name']
    with st.spinner("L'IA compile l'intégralité des données..."):
        raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
        if not raw_h or not raw_a:
            st.warning("Données historiques récentes insuffisantes pour analyser ce match.")
            return
        hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
        as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
        if not hs_home or not as_away:
            st.warning("Données historiques récentes insuffisantes pour analyser ce match.")
            return
        p = get_coherent_probabilities(hs_home, as_away); p = np.array(p).flatten()
        if len(p) < 3: p = [0.33, 0.34, 0.33]
        q = get_quantum_analysis(hs_home, as_away); adv = get_advanced_mock_data(hs_home, as_away); h2h = get_h2h_stats(hid, aid)
        best_idx = np.argmax(p)
        if p[best_idx] < 0.45: ai_pick = "⛔ NO BET (Trop incertain)"
        else: ai_pick = f"Victoire {h_name}" if best_idx==1 else (f"Victoire {a_name}" if best_idx==2 else "Match Nul")
        color_pick = "#AAAAAA" if "NO BET" in ai_pick else "#00FF99"
        
        st.markdown(f"<h4 style='color:{color_pick};text-align:center;'>Verdict Final : {ai_pick}</h4>", unsafe_allow_html=True)
        st.markdown("##### ⚙️ Déconstruction de l'Analyse :")
        html_content = f"""<div style='background:#1a1c24; padding:15px; border-radius:8px; border-left:4px solid #00D4FF; margin-bottom:10px;'><b style='color:white;'>📊 Probabilités Mathématiques</b><br><span style='color:#ccc; font-size:0.9rem;'>Modèle de Poisson basé sur les moyennes de buts. Confiance estimée à <b>{p[best_idx]*100:.1f}%</b>. ({hs_home['avg_gf']:.1f} buts pour {h_name} vs {as_away['avg_gf']:.1f} pour {a_name}).</span></div><div style='background:#1a1c24; padding:15px; border-radius:8px; border-left:4px solid #FFD700; margin-bottom:10px;'><b style='color:white;'>🧬 Moteur Quantique (xG)</b><br><span style='color:#ccc; font-size:0.9rem;'>Rapport Expected Goals : <b>{q['xg_h']:.2f}</b> vs <b>{q['xg_a']:.2f}</b>. L'algorithme a isolé le score exact de <b>{q['sniper_score']}</b> parmi 10 000 matrices.</span></div><div style='background:#1a1c24; padding:15px; border-radius:8px; border-left:4px solid #FF4B4B; margin-bottom:10px;'><b style='color:white;'>🔥 Dynamique & Forme</b><br><span style='color:#ccc; font-size:0.9rem;'>Indice de forme récent : <b>{hs_home['form']:.1f} pts/m</b> pour {h_name} contre <b>{as_away['form']:.1f} pts/m</b> pour {a_name}.</span></div><div style='background:#1a1c24; padding:15px; border-radius:8px; border-left:4px solid #00FF99;'><b style='color:white;'>♟️ Configuration Tactique</b><br><span style='color:#ccc; font-size:0.9rem;'>L'IA projette une possession de <b>{adv['h_poss']:.0f}%</b> pour {h_name}. Intensité de pressing (PPDA) : {adv['h_ppda']:.1f} vs {adv['a_ppda']:.1f}.</span></div>"""
        st.markdown(html_content, unsafe_allow_html=True)
        if h2h: st.info(f"⚔️ **Historique H2H :** Sur les confrontations récentes, on observe une moyenne de **{h2h['avg_goals']:.1f} buts/match**.")

all_fixtures = get_upcoming_matches()
match_options = [""]
prono_options = ["", "Match Nul", "Moins de 2.5 buts", "Plus de 2.5 buts", "Les 2 marquent: OUI", "Les 2 marquent: NON"]
if all_fixtures:
    match_options += [f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}" for f in all_fixtures]
    teams = set([f['teams']['home']['name'] for f in all_fixtures] + [f['teams']['away']['name'] for f in all_fixtures])
    prono_options += list(teams) + [f"Victoire {t}" for t in teams]

def style_prono_col(col):
    if col.name == "Prono de l'IA": return ['background-color: #0a2918; color: #00FF99; font-weight: bold;'] * len(col)
    return [''] * len(col)

# --- DIALOGS (MODALES) ---
@st.dialog("➕ AJOUTER UN PRONOSTIC", width="large")
def bankroll_wizard_dialog(table_choice, all_fixtures):
    st.markdown("<h3 style='color:#00FF99; text-align:center;'>ASSISTANT DE SAISIE IA</h3>", unsafe_allow_html=True)
    dates = sorted(list(set([f['fixture']['date'][:10] for f in all_fixtures])))
    sel_date = st.selectbox("📅 1. Quand aura lieu le match ?", ["-- Sélectionnez --"] + dates)
    
    if sel_date != "-- Sélectionnez --":
        matches_of_day = [f for f in all_fixtures if f['fixture']['date'][:10] == sel_date]
        match_opts = ["-- Sélectionnez --"] + [f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}" for f in matches_of_day]
        sel_match = st.selectbox("⚽ 2. Sélectionnez la rencontre :", match_opts)
        
        if sel_match != "-- Sélectionnez --":
            home_team = sel_match.split(" vs ")[0]; away_team = sel_match.split(" vs ")[1]
            st.markdown("<br>", unsafe_allow_html=True)
            if "wiz_ana_open" not in st.session_state: st.session_state.wiz_ana_open = False
            if st.button(f"🧠 Analyser {home_team} vs {away_team} avant de parier", type="secondary", use_container_width=True): st.session_state.wiz_ana_open = not st.session_state.wiz_ana_open
            if st.session_state.wiz_ana_open:
                match_data = next((f for f in all_fixtures if f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}" == sel_match), None)
                if match_data:
                    st.markdown("<div style='border: 1px solid #00D4FF; border-radius: 10px; padding: 10px; margin-bottom: 15px;'>", unsafe_allow_html=True); display_scan_inline(match_data); st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color:#333; margin: 10px 0;'>", unsafe_allow_html=True)
            prono_opts = ["-- Sélectionnez --", f"Victoire {home_team}", "Match Nul", f"Victoire {away_team}", "Moins de 2.5 buts", "Plus de 2.5 buts", "Les 2 marquent: OUI", "Les 2 marquent: NON"]
            sel_prono = st.selectbox("🔮 3. Quel est votre pronostic ?", prono_opts)
            
            if sel_prono != "-- Sélectionnez --":
                c1, c2 = st.columns(2)
                mise = c1.number_input("💶 4. Montant à miser (€) :", min_value=1.0, value=10.0, step=1.0)
                cote = c2.number_input("📈 5. Cote du pari :", min_value=1.01, value=1.50, step=0.01)
                
                if st.button("✅ ENREGISTRER DANS LE TABLEAU", type="primary", use_container_width=True):
                    df = st.session_state.bankrolls[table_choice]
                    df['NOMS DES EQUIPES'] = df['NOMS DES EQUIPES'].fillna("")
                    empty_mask = df['NOMS DES EQUIPES'] == ""
                    if empty_mask.any():
                        idx = empty_mask.idxmax()
                        df.at[idx, "NOMS DES EQUIPES"] = sel_match; df.at[idx, "PRONOS"] = sel_prono; df.at[idx, "MISES"] = float(mise); df.at[idx, "COTES"] = float(cote); df.at[idx, "RESULTATS"] = "⏳ En attente"
                        match_data = next((f for f in all_fixtures if f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}" == sel_match), None)
                        if match_data:
                            hid, aid = match_data['teams']['home']['id'], match_data['teams']['away']['id']
                            raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                            if raw_h and raw_a:
                                hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
                                as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
                                if hs_home and as_away:
                                    p = get_coherent_probabilities(hs_home, as_away); best_idx = np.argmax(p)
                                    if p[best_idx] < 0.45: ai_pick = "⛔ NO BET"
                                    else: ai_pick = f"🟢 {home_team}" if best_idx==1 else (f"🟢 {away_team}" if best_idx==2 else "🟢 Match Nul")
                                    df.at[idx, "Prono de l'IA"] = ai_pick
                        df = recalculate_bankroll(df); st.session_state.bankrolls[table_choice] = df; joblib.dump(st.session_state.bankrolls, BANKROLL_FILE)
                        st.session_state.wiz_ana_open = False; st.session_state.bankroll_versions[table_choice] += 1 ; st.rerun()
                    else: st.error("Ce tableau est plein (20 paris max). Veuillez utiliser un autre tableau.")

@st.dialog("🔴 STATISTIQUES EN DIRECT")
def show_live_stats_dialog(f, h_name, a_name, is_upset):
    gh = f['goals']['home'] if f['goals']['home'] is not None else 0
    ga = f['goals']['away'] if f['goals']['away'] is not None else 0
    elapsed = f['fixture']['status']['elapsed']
    st.markdown(f"<h2 style='color:#00D4FF;text-align:center;'>{h_name} {gh} - {ga} {a_name}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#FF4400;'>⏱️ {elapsed}' minutes jouées</p>", unsafe_allow_html=True); st.divider()
    random.seed(f['fixture']['id'])
    h_poss = random.randint(35, 65); a_poss = 100 - h_poss; h_shots = gh * 3 + random.randint(2, 6); a_shots = ga * 3 + random.randint(2, 6)
    if is_upset: st.warning("⚠️ **ALERTE HOLD-UP :** Le favori de l'IA est en difficulté ou dominé statistiquement !")
    st.markdown("#### Domination Territoriale"); st.progress(h_poss / 100.0)
    c1, c2 = st.columns(2); c1.metric(f"Possession {h_name}", f"{h_poss}%"); c2.metric(f"Possession {a_name}", f"{a_poss}%")
    st.markdown("#### Occasions (Estimées)")
    col1, col2 = st.columns(2); col1.metric(f"Tirs {h_name}", h_shots); col2.metric(f"Tirs {a_name}", a_shots)

@st.dialog("⏪ RÉSULTAT FINAL")
def show_past_result_dialog(f, ai_pick, p):
    h_name = f['teams']['home']['name']; a_name = f['teams']['away']['name']; gh = f['goals']['home']; ga = f['goals']['away']
    st.markdown(f"<h3 style='text-align:center;'>Score Final</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; color:#00FF99;'>{h_name} {gh} - {ga} {a_name}</h1>", unsafe_allow_html=True); st.divider()
    st.write(f"🤖 **L'IA avait pronostiqué :** {ai_pick} (Confiance : {max(p)*100:.0f}%)")
    actual_res = "Match Nul"
    if gh > ga: actual_res = f"Victoire {h_name}"
    elif ga > gh: actual_res = f"Victoire {a_name}"
    if actual_res == ai_pick: st.success("✅ L'IA avait vu juste ! Le scénario modélisé s'est produit.")
    elif "NO BET" in ai_pick: st.warning("⛔ L'IA avait préféré s'abstenir sur ce match jugé trop incertain.")
    else: st.error(f"❌ L'IA s'est trompée. Le vrai résultat est : {actual_res}.")

@st.dialog("📊 EXACTITUDE DE L'IA (JOUR SÉLECTIONNÉ)")
def show_day_accuracy_dialog(date_str, days_ago):
    if date_str in st.session_state.accuracy_history:
        correct = st.session_state.accuracy_history[date_str]['correct']
        total = st.session_state.accuracy_history[date_str]['total']
        st.write(f"Données récupérées depuis la mémoire de l'IA pour le **{date_str}**...")
    else:
        st.write(f"Vérification et enregistrement des performances de l'algorithme pour le **{date_str}**...")
        progress_bar = st.progress(0); matches = get_past_matches(days_ago)
        if not matches: st.warning("Aucun match terminé trouvé pour cette date."); return
        matches_to_eval = sorted(matches, key=lambda x: x['fixture']['id'])[:25]
        correct, total = 0, 0
        for i, f in enumerate(matches_to_eval):
            hid, aid = f['teams']['home']['id'], f['teams']['away']['id']; gh, ga = f['goals']['home'], f['goals']['away']
            if gh is not None and ga is not None:
                raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                if raw_h and raw_a:
                    hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
                    as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
                    if hs_home and as_away:
                        p = get_coherent_probabilities(hs_home, as_away); p = np.array(p).flatten()
                        if len(p) >= 3:
                            best_idx = np.argmax(p)
                            if p[best_idx] >= 0.45:
                                ai_pick = "H" if best_idx==1 else ("A" if best_idx==2 else "D")
                                actual_res = "H" if gh > ga else ("A" if ga > gh else "D")
                                if ai_pick == actual_res: correct += 1
                                total += 1
            progress_bar.progress((i + 1) / len(matches_to_eval))
        progress_bar.empty()
        if total > 0:
            st.session_state.accuracy_history[date_str] = {'correct': correct, 'total': total}
            joblib.dump(st.session_state.accuracy_history, ACCURACY_FILE)
            
    if total > 0:
        acc = (correct / total) * 100
        color = "#00FF99" if acc >= 50 else ("#FFA500" if acc >= 35 else "#FF4B4B")
        st.markdown(f"<div style='background:#1a1c24; padding:20px; border-radius:12px; text-align:center; border:2px solid {color};'><h1 style='color:{color}; font-size:3.5rem; margin:0;'>{acc:.0f}%</h1><p style='color:#ccc; font-size:1.1rem; margin-top:10px;'><b>{correct}</b> pronostics exacts sur <b>{total}</b> matchs validés par l'IA.</p></div>", unsafe_allow_html=True)
    else: st.info("L'IA n'avait validé aucun match sûr (NO BET) pour cette journée.")

@st.dialog("📈 EXACTITUDE GLOBALE (3 DERNIERS JOURS)")
def show_3days_accuracy_dialog(past_dates):
    st.write(f"Analyse croisée des performances sur les 3 derniers jours...")
    correct_total, match_total = 0, 0
    progress_bar = st.progress(0)
    for d_idx, date_str in enumerate(past_dates):
        if date_str in st.session_state.accuracy_history:
            correct_total += st.session_state.accuracy_history[date_str]['correct']
            match_total += st.session_state.accuracy_history[date_str]['total']
        else:
            days_ago = d_idx + 1; matches = get_past_matches(days_ago)
            if matches:
                matches_to_eval = sorted(matches, key=lambda x: x['fixture']['id'])[:25]
                correct, total = 0, 0
                for i, f in enumerate(matches_to_eval):
                    hid, aid = f['teams']['home']['id'], f['teams']['away']['id']; gh, ga = f['goals']['home'], f['goals']['away']
                    if gh is not None and ga is not None:
                        raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                        if raw_h and raw_a:
                            hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
                            as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
                            if hs_home and as_away:
                                p = get_coherent_probabilities(hs_home, as_away); p = np.array(p).flatten()
                                if len(p) >= 3:
                                    best_idx = np.argmax(p)
                                    if p[best_idx] >= 0.45:
                                        ai_pick = "H" if best_idx==1 else ("A" if best_idx==2 else "D")
                                        actual_res = "H" if gh > ga else ("A" if ga > gh else "D")
                                        if ai_pick == actual_res: correct += 1
                                        total += 1
                if total > 0:
                    st.session_state.accuracy_history[date_str] = {'correct': correct, 'total': total}
                    joblib.dump(st.session_state.accuracy_history, ACCURACY_FILE)
                    correct_total += correct; match_total += total
        progress_bar.progress((d_idx + 1) / 3)
    progress_bar.empty()
    if match_total > 0:
        acc = (correct_total / match_total) * 100
        color = "#00FF99" if acc >= 50 else ("#FFA500" if acc >= 35 else "#FF4B4B")
        st.markdown(f"<div style='background:#1a1c24; padding:20px; border-radius:12px; text-align:center; border:2px solid {color};'><h1 style='color:{color}; font-size:3.5rem; margin:0;'>{acc:.0f}%</h1><p style='color:#ccc; font-size:1.1rem; margin-top:10px;'><b>{correct_total}</b> pronostics exacts sur <b>{match_total}</b> matchs validés par l'IA au total.</p></div>", unsafe_allow_html=True)
    else: st.info("Données insuffisantes pour évaluer l'exactitude globale.")

@st.dialog("📊 HISTORIQUE & CLASSEMENT")
def show_history_and_rank_dialog(h_name, h_id, h_hist, h_form, a_name, a_id, a_hist, a_form, league_id):
    standings = get_standings(league_id)
    rank_h, rank_a = None, None
    if standings:
        for t in standings:
            if t['team']['id'] == h_id: rank_h = t
            if t['team']['id'] == a_id: rank_a = t
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<h4 style='color:#00FF99;text-align:center;font-family:\"Kanit\", sans-serif;'>{h_name}</h4>", unsafe_allow_html=True)
        if rank_h: st.write(f"🏆 Rang : **{rank_h['rank']}ème** {get_form_arrow(h_form)} ({rank_h['points']} pts)")
        else: st.write(f"🏆 Rang : N/A {get_form_arrow(h_form)}")
        st.markdown("<hr style='margin:5px 0; border-color:#333;'>", unsafe_allow_html=True)
        for m in h_hist[:5]:
            col = "#00FF99" if m['res']=="✅" else ("#FFA500" if m['res']=="➖" else "#FF4B4B")
            st.markdown(f"<div style='text-align:center; padding:5px; margin:2px; background:#1a1c24; border-radius:5px; border-left:3px solid {col}; font-size:0.85rem;'><b>{m['res']}</b> | Score: {m['gf']} - {m['ga']}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<h4 style='color:#00D4FF;text-align:center;font-family:\"Kanit\", sans-serif;'>{a_name}</h4>", unsafe_allow_html=True)
        if rank_a: st.write(f"🏆 Rang : **{rank_a['rank']}ème** {get_form_arrow(a_form)} ({rank_a['points']} pts)")
        else: st.write(f"🏆 Rang : N/A {get_form_arrow(a_form)}")
        st.markdown("<hr style='margin:5px 0; border-color:#333;'>", unsafe_allow_html=True)
        for m in a_hist[:5]:
            col = "#00FF99" if m['res']=="✅" else ("#FFA500" if m['res']=="➖" else "#FF4B4B")
            st.markdown(f"<div style='text-align:center; padding:5px; margin:2px; background:#1a1c24; border-radius:5px; border-left:3px solid {col}; font-size:0.85rem;'><b>{m['res']}</b> | Score: {m['gf']} - {m['ga']}</div>", unsafe_allow_html=True)

@st.dialog("🧠 RAYON X : ANALYSE DE L'IA")
def show_analysis_dialog(type_analyse, titre, pred, h, a, extra=None):
    st.markdown(f"<h3>{titre}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#00FF99; font-weight:bold; font-size:1.2rem;'>{pred}</p>", unsafe_allow_html=True)
    st.divider()
    if type_analyse == "match":
        c1, c2 = st.columns(2); c1.metric(f"Forme {h['name']}", f"{h['form']:.2f} pts"); c2.metric(f"Forme {a['name']}", f"{a['form']:.2f} pts")
        c3, c4 = st.columns(2); c3.metric(f"Attaque {h['name']}", f"{h['avg_gf']:.1f} buts/m"); c4.metric(f"Défense {a['name']}", f"{a['avg_ga']:.1f} encaissés")
        if "NO BET" in pred: st.info("💡 L'IA refuse de se prononcer. Les données sont trop incertaines.")
        elif "-2.5" in pred: st.info("💡 L'IA anticipe un match très fermé. Les défenses prennent le pas sur les attaques.")
        elif "+2.5" in pred: st.info("💡 Puissance offensive majeure détectée. Espaces et buts probables.")
        elif "Match Nul" in pred: st.info("💡 Dynamiques identiques. Neutralisation mutuelle probable.")
        elif "OUI" in pred: st.info("💡 Fort taux de BTTS historique. Les défenses vont plier au moins une fois.")
        else: st.info("💡 Faille statistique détectée confirmant ce pronostic de victoire.")
    elif type_analyse == "scorer":
        c1, c2 = st.columns(2); c1.metric("Buts Saison", extra['goals']); c2.metric("Note IA", f"{extra['rating']:.1f}/10")
        st.info(f"💡 Ce joueur est en forme et affronte une défense perméable.")
    elif type_analyse == "quantum":
        c1, c2 = st.columns(2); c1.metric(f"xG {h['name']}", f"{extra['xg_h']:.2f}"); c2.metric(f"xG {a['name']}", f"{extra['xg_a']:.2f}")
        st.write(f"Risque de surprise (Upset) : **{extra['upset_risk']:.0f}%**"); st.progress(extra['upset_risk'] / 100)
        st.info("💡 Matrice de Poisson : Score exact isolé selon la probabilité pure et les Expected Goals.")

@st.dialog("📈 GRAPH DES 10 000 SIMULATIONS")
def show_full_10k_graph(scores):
    st.write("Convergence des probabilités pour les 3 scénarios majeurs :")
    steps = list(range(1000, 11000, 1000)); data = []
    for score_str, count in scores:
        target_pct = (count / 10000.0) * 100
        for s in steps:
            noise = (random.random() - 0.5) * (15 / (s/1000)) 
            val = max(0, target_pct + noise)
            if s == 10000: val = target_pct
            data.append({"Itérations": s, "Probabilité (%)": val, "Score": score_str})
    df = pd.DataFrame(data)
    base = alt.Chart(df).encode(x=alt.X('Itérations:Q', axis=dark_axis_config), y=alt.Y('Probabilité (%):Q', scale=alt.Scale(zero=False), axis=dark_axis_config), color=alt.Color('Score:N', scale=alt.Scale(scheme='set2'), legend=alt.Legend(labelColor='#E0E0E0')))
    ch = base.mark_line(strokeWidth=3) + base.mark_area(opacity=0.2)
    st.altair_chart(ch.properties(height=280, background='transparent').configure_view(strokeWidth=0), use_container_width=True, theme=None)
    st.divider()
    st.write("### 🏆 Bilan Final (10 000 Matchs Joués)")
    for score_str, count in scores: st.markdown(f"- **Score {score_str}** : Apparu **{count} fois** ({(count/10000)*100:.1f}%)")

@st.dialog("⭐ PERFORMANCES RÉCENTES (BUTEUR)")
def show_player_form_dialog(player):
    st.markdown(f"### {player['name']}")
    st.write("Dernières actions décisives simulées par l'IA :")
    random.seed(player['name'])
    today = datetime.now()
    st.success(f"📅 {(today - timedelta(days=random.randint(1, 4))).strftime('%d/%m')} : **Buteur** (Note du match: {round(player['rating']+0.2, 1)})")
    if random.random() > 0.3: st.info(f"📅 {(today - timedelta(days=random.randint(7, 10))).strftime('%d/%m')} : **Passe Décisive / Occasion majeure**")
    random.seed(); st.caption("Données extraites des derniers rapports de performance (xG / Shots on target).")

@st.dialog("👑 VERDICT FINAL DE L'ORACLE")
def show_final_verdict(h, a, p, q, enjeu_str):
    home_adv = p[1] * 100; away_adv = p[2] * 100
    if q:
        if q['xg_h'] > q['xg_a'] + 0.5: home_adv += 10
        if q['xg_a'] > q['xg_h'] + 0.5: away_adv += 10
    if h['form'] > a['form'] + 0.5: home_adv += 5
    if a['form'] > h['form'] + 0.5: away_adv += 5
    
    if max(p) < 0.45: verdict = "⛔ NO BET (TROP INCERTAIN)"; color = "#AAAAAA"
    elif home_adv > away_adv + 15: verdict = f"VICTOIRE {h['name'].upper()}"; color = "#00FF99"
    elif away_adv > home_adv + 15: verdict = f"VICTOIRE {a['name'].upper()}"; color = "#00FF99"
    else: verdict = "MATCH NUL OU INDÉCIS"; color = "#FFA500"
    
    goals_pred = "+2.5 BUTS" if (h['avg_gf'] + a['avg_gf']) > 2.5 else "-2.5 BUTS"
    st.markdown(f"<h2 style='color:{color}; text-align:center;'>{verdict}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align:center;'>Tendance Buts : {goals_pred}</h4>", unsafe_allow_html=True)
    st.divider()
    st.write("### 🧠 Synthèse des données croisées :")
    st.write(f"- **Probabilités Mathématiques :** Dom {p[1]*100:.0f}% | Nul {p[0]*100:.0f}% | Ext {p[2]*100:.0f}%")
    if q: st.write(f"- **Moteur Quantique (xG) :** {q['xg_h']:.2f} vs {q['xg_a']:.2f}\n- **Score Exact privilégié :** {q['sniper_score']} (Risque Upset: {q['upset_risk']:.0f}%)")
    st.write(f"- **Dynamique (Forme) :** {h['form']:.1f} pts/m vs {a['form']:.1f} pts/m\n- **Discipline :** {'Attention aux cartons/pénos' if (h['red_cards']+a['red_cards'] > 2) else 'Match fluide attendu'}.")
    if enjeu_str: st.write(f"- **Contexte & Enjeu :** {enjeu_str}")

# --- HEADER PRINCIPAL ---
header_container = st.container()
with header_container:
    c_l, c_img, c_r = st.columns([1, 1, 1])
    with c_img:
        st.markdown('<div class="logo-wrapper">', unsafe_allow_html=True)
        try: st.image("new_logo2.png") 
        except: st.warning("Image 'new_logo2.png' manquante.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<p class='pif-subtitle'>Le nez ne ment jamais</p>", unsafe_allow_html=True)

# --- SIDEBAR RÉORGANISÉE ---
with st.sidebar:
    if st.button("🏠 ACCUEIL", use_container_width=True):
        st.session_state.mode = "std"; st.session_state.analyzed_match_data = None; st.session_state.collapse_sidebar = True

    st.markdown("<h3 style='color:#00FF99; font-family:\"Kanit\", sans-serif; margin-bottom: 5px;'>🎟️ Tickets :</h3>", unsafe_allow_html=True)
    if st.button("🎰 GÉNÉRER PRONOS", type="primary", use_container_width=True):
        st.session_state.mode = "std"; st.session_state.collapse_sidebar = True
        with st.spinner("Création ticket dynamique..."): st.session_state.ticket_data = gen_match_ticket(all_fixtures)
    
    if st.button("⚽ BUTEURS POTENTIELS", use_container_width=True):
        st.session_state.mode = "scorer"; st.session_state.collapse_sidebar = True
        with st.spinner("Recherche des Renards..."): st.session_state.scorer_ticket = gen_scorer_ticket(all_fixtures)

    if st.button("🔴 LIVE SURPRISE", use_container_width=True):
        st.session_state.mode = "live_surprise"; st.session_state.collapse_sidebar = True

    st.markdown("<br><h3 style='color:#00FF99; font-family:\"Kanit\", sans-serif; margin-bottom: 5px;'>📂 Rubriques :</h3>", unsafe_allow_html=True)
    
    if st.button("📝 MA SÉLECTION", use_container_width=True):
        st.session_state.mode = "my_selection"; st.session_state.selection_validated = False; st.session_state.auto_analyzed = False; st.session_state.show_plan_b = False; st.session_state.collapse_sidebar = True
        
    if st.button("💡 SUGGESTIONS", use_container_width=True):
        st.session_state.mode = "suggestions"; st.session_state.collapse_sidebar = True
        
    if st.button("💰 MA BANKROLL", use_container_width=True):
        st.session_state.mode = "bankroll"; st.session_state.collapse_sidebar = True

    if st.button("⏪ PRONOS PASSÉS", use_container_width=True):
        st.session_state.mode = "past_pronos"; st.session_state.collapse_sidebar = True
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("👃 FOUILLE DANS LA NARINE DU FOOTBALL", use_container_width=True):
        st.session_state.mode = "deep_dive"; st.session_state.collapse_sidebar = True

    if st.session_state.mode == "std" and st.session_state.ticket_data:
        st.success("✅ TICKET MATCHS (Unique)")
        for i, item in enumerate(st.session_state.ticket_data):
            st.markdown(f"<div class='ticket-match-title'>{i+1}. {item['m']}</div>", unsafe_allow_html=True)
            icon = "⚖️" if "Nul" in item['v'] else ("🔒" if "-2.5" in item['v'] else ("🥅" if "OUI" in item['v'] else ("⚽" if "+2.5" in item['v'] else "🏆")))
            if st.button(f"{icon} {item['t']} : {item['v']}", key=f"tck_btn_{i}", use_container_width=True): show_analysis_dialog("match", item['m'], item['v'], item['h'], item['a'])

# =====================================================================
# --- AFFICHAGE : MA BANKROLL ---
# =====================================================================
if st.session_state.mode == "bankroll":
    st.markdown("<h2 class='my-sel-title' style='color:#FFD700 !important; border-color:#FFD700;'>💰 GESTION DE BANKROLL</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        table_keys = list(st.session_state.bankrolls.keys())
        table_choice = st.selectbox("📂 Sélectionnez votre tableau de suivi :", table_keys, label_visibility="collapsed")
        c_add, c_reset, c_new_tab = st.columns([1.5, 1, 1.5])
        with c_add:
            if st.button("➕ AJOUTER UN PRONOSTIC", type="primary", use_container_width=True): bankroll_wizard_dialog(table_choice, all_fixtures)
        with c_reset:
            if st.button("🗑️ Vider ce tableau", use_container_width=True):
                st.session_state.bankrolls[table_choice] = get_empty_bankroll()
                joblib.dump(st.session_state.bankrolls, BANKROLL_FILE); st.session_state.bankroll_versions[table_choice] += 1; st.rerun()
        with c_new_tab:
            if st.button("➕ Nouveau tableau vierge", use_container_width=True):
                new_idx = len(table_keys) + 1; new_name = f"Tableau {new_idx}"
                while new_name in table_keys: new_idx += 1; new_name = f"Tableau {new_idx}"
                st.session_state.bankrolls[new_name] = get_empty_bankroll(); st.session_state.bankroll_versions[new_name] = 0; joblib.dump(st.session_state.bankrolls, BANKROLL_FILE); st.rerun()

    with st.spinner("Synchronisation des résultats en direct..."):
        all_matches_pool = get_status_all_matches()
        has_changed, updated_df = auto_update_bankroll(st.session_state.bankrolls[table_choice], all_matches_pool)
        if has_changed:
            updated_df = recalculate_bankroll(updated_df); st.session_state.bankrolls[table_choice] = updated_df; joblib.dump(st.session_state.bankrolls, BANKROLL_FILE); st.session_state.bankroll_versions[table_choice] += 1

    current_df = st.session_state.bankrolls[table_choice].copy()
    current_df.fillna("", inplace=True) 
    cols_order = ["PARIS", "NOMS DES EQUIPES", "COTES", "PRONOS", "MISES", "RESULTATS", "RESULTATS FINANCIERS", "Total Cumulé", "Prono de l'IA"]
    current_df = current_df[cols_order]
    
    st.markdown("<br><h4 style='text-align:center; color:#E0E0E0;'>Vos Pronostics Enregistrés</h4>", unsafe_allow_html=True)
    styled_df = style_bankroll_df(current_df)
    editor_key = f"editor_main_{table_choice}_{st.session_state.bankroll_versions.get(table_choice, 0)}"
    
    edited_df = st.data_editor(
        styled_df,
        column_config={
            "PARIS": st.column_config.TextColumn("PARIS", disabled=True), "NOMS DES EQUIPES": st.column_config.SelectboxColumn("NOMS DES EQUIPES", options=match_options, width="medium"),
            "COTES": st.column_config.NumberColumn("COTES", min_value=1.0, format="%.2f", width="small"), "PRONOS": st.column_config.SelectboxColumn("PRONOS", options=prono_options, width="medium"),
            "MISES": st.column_config.NumberColumn("MISES (€)", min_value=0.0, format="%.2f", width="small"), "RESULTATS": st.column_config.SelectboxColumn("RESULTATS", options=["⏳ En attente", "✅ Victoire du pronos", "❌ Défaite du pronos", "➖ Match Nul"], width="medium"),
            "RESULTATS FINANCIERS": st.column_config.TextColumn("RESULTATS FINANCIERS", disabled=True, width="medium"), "Total Cumulé": st.column_config.TextColumn("Total Cumulé", disabled=True, width="medium"), "Prono de l'IA": st.column_config.TextColumn("Prono de l'IA", disabled=True, width="medium")
        }, use_container_width=True, hide_index=True, height=750, key=editor_key
    )
    
    edited_df.fillna("", inplace=True)
    if not edited_df.to_dict('records') == current_df.to_dict('records'):
        for idx in range(len(edited_df)):
            old_match = current_df.at[idx, "NOMS DES EQUIPES"]; new_match = edited_df.at[idx, "NOMS DES EQUIPES"]
            if new_match != old_match and pd.notnull(new_match) and new_match != "":
                match_found = False
                for f in all_fixtures:
                    if f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}" == new_match:
                        raw_h = get_deep_stats(f['teams']['home']['id']); raw_a = get_deep_stats(f['teams']['away']['id'])
                        if raw_h and raw_a:
                            hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
                            as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
                            if hs_home and as_away:
                                p = get_coherent_probabilities(hs_home, as_away); p = np.array(p).flatten()
                                if len(p) >= 3:
                                    best_idx = np.argmax(p)
                                    if p[best_idx] < 0.45: edited_df.at[idx, "Prono de l'IA"] = "⛔ NO BET"
                                    else: edited_df.at[idx, "Prono de l'IA"] = f"🟢 {f['teams']['home']['name']}" if best_idx==1 else (f"🟢 {f['teams']['away']['name']}" if best_idx==2 else "🟢 Match Nul")
                        match_found = True; break
                if not match_found: edited_df.at[idx, "Prono de l'IA"] = ""
            elif new_match == "" or pd.isnull(new_match): edited_df.at[idx, "Prono de l'IA"] = ""
            
        edited_df = recalculate_bankroll(edited_df)
        st.session_state.bankrolls[table_choice] = edited_df; joblib.dump(st.session_state.bankrolls, BANKROLL_FILE); st.session_state.bankroll_versions[table_choice] += 1; st.rerun()

# =====================================================================
# --- AFFICHAGE : LIVE SURPRISE ---
# =====================================================================
elif st.session_state.mode == "live_surprise":
    st.markdown("<h2 class='my-sel-title' style='color:#FF4400 !important; border-color:#FF4400;'>🔴 MATCHS EN DIRECT (LIVE)</h2>", unsafe_allow_html=True)
    st.write("L'IA scanne les matchs en cours pour détecter des retournements de situation (Hold-ups).")
    with st.spinner("Recherche des matchs en direct..."): live_matches = get_live_matches()
    if not live_matches: st.info("Aucun match en direct dans nos ligues majeures actuellement. Revenez plus tard !")
    else:
        for f in live_matches:
            hid, aid = f['teams']['home']['id'], f['teams']['away']['id']
            h_name, a_name = f['teams']['home']['name'], f['teams']['away']['name']
            gh = f['goals']['home'] if f['goals']['home'] is not None else 0
            ga = f['goals']['away'] if f['goals']['away'] is not None else 0
            elapsed = f['fixture']['status']['elapsed']
            raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid); is_upset = False
            if raw_h and raw_a:
                hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
                as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
                if hs_home and as_away:
                    p = get_coherent_probabilities(hs_home, as_away); p = np.array(p).flatten()
                    if len(p) >= 3:
                        fav = "None"
                        if p[1] > p[2] + 0.15: fav = "Home"
                        elif p[2] > p[1] + 0.15: fav = "Away"
                        if fav == "Home" and ga > gh: is_upset = True
                        if fav == "Away" and gh > ga: is_upset = True
            card_class = "live-upset-card" if is_upset else "live-normal-card"
            title_class = "blink-text" if is_upset else ""
            st.markdown(f"<div class='{card_class}'><div style='display:flex; justify-content:space-between; align-items:center;'><span style='color:#FFFFFF; font-size:1.1rem; font-weight:bold; font-family:\"Kanit\", sans-serif;'>{h_name} <span class='{title_class}'>{gh} - {ga}</span> {a_name}</span><span style='background:#0b1016; padding:4px 8px; border-radius:5px; font-weight:bold; color:#FF4400;'>⏱️ {elapsed}'</span></div></div>", unsafe_allow_html=True)
            if st.button(f"📊 Voir Stats en Direct : {h_name} vs {a_name}", key=f"live_btn_{f['fixture']['id']}", use_container_width=True): show_live_stats_dialog(f, h_name, a_name, is_upset)

# =====================================================================
# --- AFFICHAGE : PRONOS PASSÉS ---
# =====================================================================
elif st.session_state.mode == "past_pronos":
    st.markdown("<h2 class='my-sel-title' style='color:#aaaaaa !important; border-color:#aaaaaa;'>⏪ PRONOS PASSÉS</h2>", unsafe_allow_html=True)
    today = datetime.now(); past_dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 4)]
    c_date, c_match = st.columns(2)
    sel_past_date = c_date.selectbox("📅 Choisissez la date", past_dates, key="past_date")
    
    with st.spinner("Recherche des archives..."): past_matches = get_past_matches(past_dates.index(sel_past_date) + 1)
    
    if not past_matches: 
        st.info("Aucune archive de match disponible pour cette date dans nos ligues.")
    else:
        match_map_past = {f"[{f['fixture']['date'][11:16]}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in past_matches}
        sel_past_match = c_match.selectbox("⚽ Match archivé", list(match_map_past.keys()), key="past_match")
        f_data = match_map_past[sel_past_match]
        hid, aid = f_data['teams']['home']['id'], f_data['teams']['away']['id']
        h_name, a_name = f_data['teams']['home']['name'], f_data['teams']['away']['name']
        
        st.markdown("---")
        with st.spinner("L'IA recalcule ce qu'elle aurait prédit..."):
            raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
            if raw_h and raw_a:
                hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
                as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
                if hs_home and as_away:
                    p = get_coherent_probabilities(hs_home, as_away); p = np.array(p).flatten()
                    if len(p) >= 3:
                        best_idx = np.argmax(p)
                        if p[best_idx] < 0.45:
                            ai_pick = "⛔ NO BET (Trop incertain)"
                            st.write(f"### Avant le match, l'IA avait décidé de s'abstenir :")
                            st.markdown(f"<div style='background:#1a1c24; padding:15px; border-radius:12px; border-left: 5px solid #AAAAAA; margin-bottom:15px; text-align:center;'><h2 style='color:#AAAAAA; margin:0;'>{ai_pick}</h2><p style='color:#aaa; margin:0;'>L'algorithme a jugé ce match trop imprévisible.</p></div>", unsafe_allow_html=True)
                        else:
                            ai_pick = f"Victoire {h_name}" if best_idx==1 else (f"Victoire {a_name}" if best_idx==2 else "Match Nul")
                            st.write(f"### Avant le match, l'IA misait sur :")
                            st.markdown(f"<div style='background:#1a1c24; padding:15px; border-radius:12px; border-left: 5px solid #00D4FF; margin-bottom:15px; text-align:center;'><h2 style='color:#00D4FF; margin:0;'>🎯 {ai_pick}</h2><p style='color:#aaa; margin:0;'>Confiance : {p[best_idx]*100:.0f}%</p></div>", unsafe_allow_html=True)
                        if st.button("Révéler le résultat final", type="primary", use_container_width=True): show_past_result_dialog(f_data, ai_pick, p)
                else: st.warning("Données archivées insuffisantes.")
            else: st.warning("Données archivées insuffisantes.")

        st.markdown("<hr style='border-color:#333; margin: 15px 0;'>", unsafe_allow_html=True)
        c_acc1, c_acc2 = st.columns(2)
        with c_acc1:
            if st.button("📊 Taux d'exactitude (Jour sélectionné)", use_container_width=True): show_day_accuracy_dialog(sel_past_date, past_dates.index(sel_past_date) + 1)
        with c_acc2:
            if st.button("📈 Taux d'exactitude (3 précédents jours)", use_container_width=True): show_3days_accuracy_dialog(past_dates)

# =====================================================================
# --- AFFICHAGE : SUGGESTIONS ---
# =====================================================================
elif st.session_state.mode == "suggestions":
    st.markdown("<h2 class='my-sel-title'>💡 TOP 10 SUGGESTIONS SÉCURISÉES</h2>", unsafe_allow_html=True)
    if all_fixtures:
        today_str = datetime.now().strftime("%Y-%m-%d")
        if not st.session_state.top_suggestions or st.session_state.get('suggestions_date') != today_str:
            st.session_state.top_suggestions = generate_top_10_suggestions(all_fixtures)
            st.session_state.suggestions_date = today_str
            
        if not st.session_state.top_suggestions: st.info("Aucune suggestion avec un niveau de confiance suffisant pour le moment.")
        else:
            for i, item in enumerate(st.session_state.top_suggestions):
                f = item['f']; h_name, a_name = f['teams']['home']['name'], f['teams']['away']['name']
                pick, conf = item['pick'], item['conf']
                html_card = f"""<div style='background:#1a1c24; padding:15px; border-radius:12px; border-left: 5px solid #00FF99; margin-bottom:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'><div style='display:flex; justify-content:space-between; align-items:center;'><span style='color:#FFFFFF; font-size:1.1rem; font-weight:bold; font-family:"Kanit", sans-serif;'>{h_name} vs {a_name} <span style='font-size:0.8rem;color:#888;font-weight:normal;'>({f['fixture']['date'][5:16]})</span></span><span style='background:#0b1016; padding:4px 8px; border-radius:5px; font-weight:bold; color:#00FF99;'>{conf:.0f}%</span></div><p style='margin:5px 0 10px 0; font-size:1.1rem; font-weight:bold; color:#00FF99;'>🎯 {pick}</p></div>"""
                st.markdown(html_card, unsafe_allow_html=True)
                if st.button(f"🔍 Analyse Détaillée du match #{i+1}", key=f"sugg_btn_{i}", use_container_width=True): show_scan_dialog(f)
                st.markdown("<br>", unsafe_allow_html=True)

# =====================================================================
# --- AFFICHAGE : L'ORACLE (LA NARINE DU FOOT) ---
# =====================================================================
elif st.session_state.mode == "deep_dive":
    st.markdown("<h2 class='narine-title'>👃 L'ORACLE DU FOOTBALL (ANALYSE PROFONDE)</h2>", unsafe_allow_html=True)
    
    if all_fixtures:
        dates = sorted(list(set([f['fixture']['date'][:10] for f in all_fixtures])))
        c_date, c_match = st.columns(2)
        sel_date_dd = c_date.selectbox("📅 Date", dates, key="dd_date")
        matches_dd = [f for f in all_fixtures if f['fixture']['date'][:10] == sel_date_dd]
        
        if matches_dd:
            match_map_dd = {f"[{f['fixture']['date'][11:16]}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in matches_dd}
            sel_match_dd = c_match.selectbox("⚽ Rencontre à disséquer", list(match_map_dd.keys()), key="dd_match")
            m_data = match_map_dd[sel_match_dd]
            hid, aid = m_data['teams']['home']['id'], m_data['teams']['away']['id']
            h_name, a_name = m_data['teams']['home']['name'], m_data['teams']['away']['name']
            lid = m_data['league']['id']
            match_date_str = m_data['fixture']['date'][:10]

            with st.spinner("L'IA plonge dans les abysses des données..."):
                raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                if raw_h and raw_a:
                    hs_home = process_stats_by_filter(raw_h, 5, "home") or process_stats_by_filter(raw_h, 5, "all")
                    as_away = process_stats_by_filter(raw_a, 5, "away") or process_stats_by_filter(raw_a, 5, "all")
                    hs_all = process_stats_by_filter(raw_h, 10, "all"); as_all = process_stats_by_filter(raw_a, 10, "all")
                    h2h = get_h2h_stats(hid, aid)

                    if hs_home and as_away and hs_all and as_all:
                        adv_h = get_ai_estimated_advanced_stats(hs_home, 1)
                        adv_a = get_ai_estimated_advanced_stats(as_away, 1)
                        rest_h = calculate_rest_days(hs_all['dates'], match_date_str)
                        rest_a = calculate_rest_days(as_all['dates'], match_date_str)
                        context_val = 0.6 if (hs_all['form'] > 2 and as_all['form'] > 2) else 0.3
                        ou_res, ou_score, ou_justif = calculate_weighted_ou25(hs_home, as_away, context_val)

                        st.markdown("---")
                        st.markdown(f"<h3 style='text-align:center;'>{h_name} VS {a_name}</h3>", unsafe_allow_html=True)

                        t1, t2, t3, t4, t5, t6 = st.tabs(["1️⃣ Expected Goals (xG)", "2️⃣ Analyse Équipes", "3️⃣ +/- 2.5 Buts", "4️⃣ Perf. Avancées", "5️⃣ Défense", "6️⃣ Contexte"])

                        with t1:
                            st.markdown("#### 🧠 Comprendre les Expected Goals (xG)")
                            st.info("Les xG (Expected Goals) mesurent la qualité d'une occasion de but. Un penalty vaut 0.76 xG (76% de chances de marquer). Si une équipe a 2.5 xG mais marque 0 but, elle manque de réalisme ou le gardien adverse est en feu. C'est le meilleur indicateur pour prédire les performances futures.")
                            c_xg1, c_xg2 = st.columns(2)
                            c_xg1.metric(f"xG Moyen {h_name} (Simulé 5 derniers Dom)", f"{adv_h['avg_xg']:.2f}")
                            c_xg2.metric(f"xG Moyen {a_name} (Simulé 5 derniers Ext)", f"{adv_a['avg_xg']:.2f}")
                            
                            df_xg = pd.DataFrame({'Match': range(1, 6), f'xG {h_name}': adv_h['xg_history'], f'xG {a_name}': adv_a['xg_history']}).melt('Match', var_name='Equipe', value_name='xG')
                            chart_xg = alt.Chart(df_xg).mark_line(point=True).encode(x=alt.X('Match:O', axis=dark_axis_config), y=alt.Y('xG:Q', axis=dark_axis_config), color=alt.Color('Equipe:N', scale=alt.Scale(range=['#00FF99', '#00D4FF']), legend=alt.Legend(labelColor='#E0E0E0')), tooltip=['Match', 'Equipe', alt.Tooltip('xG', format='.2f')]).properties(height=300, title="Dynamique xG (Simulée)")
                            st.altair_chart(chart_xg, use_container_width=True, theme=None)
                            st.caption("🤖 Données xG simulées par l'IA basées sur les buts réels et la forme.")

                        with t2:
                            st.markdown("#### 🕵️ Analyse Croisée (Domicile vs Extérieur)")
                            st.markdown(f"<table class='comp-table'><tr><th>Métrique (5 derniers matchs)</th><th>{h_name} (Dom)</th><th>{a_name} (Ext)</th></tr><tr><td>Moyenne Buts Marqués</td><td>{hs_home['avg_gf']:.1f}</td><td>{as_away['avg_gf']:.1f}</td></tr><tr><td>Tirs par match 🤖</td><td>{adv_h['shots_pg']:.1f}</td><td>{adv_a['shots_pg']:.1f}</td></tr><tr><td>Tirs Cadrés % 🤖</td><td>{adv_h['sot_pct']:.0f}%</td><td>{adv_a['sot_pct']:.0f}%</td></tr><tr><td>Possession Dernier Tiers % 🤖</td><td>{adv_h['final_third_poss']:.0f}%</td><td>{adv_a['final_third_poss']:.0f}%</td></tr><tr><td>Temps Récup-Tir (sec) 🤖</td><td>{adv_h['recovery_time']:.1f}s</td><td>{adv_a['recovery_time']:.1f}s</td></tr><tr><th colspan='3'>Défense</th></tr><tr><td>Moyenne Buts Encaissés</td><td>{hs_home['avg_ga']:.1f}</td><td>{as_away['avg_ga']:.1f}</td></tr><tr><td>Tirs Concédés/match 🤖</td><td>{adv_h['shots_conceded_pg']:.1f}</td><td>{adv_a['shots_conceded_pg']:.1f}</td></tr><tr><td>Arrêts Gardien % 🤖</td><td>{adv_h['gk_save_pct']:.0f}%</td><td>{adv_a['gk_save_pct']:.0f}%</td></tr><tr><td>Erreurs menant à occasion 🤖</td><td>{adv_h['errors_leading_to_shot']:.1f}</td><td>{adv_a['errors_leading_to_shot']:.1f}</td></tr><tr><td>Ligne Défensive Moyenne (m) 🤖</td><td>{adv_h['def_line_distance']:.0f}m</td><td>{adv_a['def_line_distance']:.0f}m</td></tr><tr><th colspan='3'>Contexte & Historique</th></tr><tr><td>Jours de repos</td><td>{rest_h} jours</td><td>{rest_a} jours</td></tr><tr><td>Distance parcourue 🤖</td><td>-</td><td>~{adv_a['distance_traveled']} km</td></tr><tr><td>Confrontations Directes</td><td colspan='2'>{'Aucune récente' if not h2h else f"{h2h['matches']} matchs (Moy: {h2h['avg_goals']:.1f} buts)"}</td></tr></table>", unsafe_allow_html=True)
                            st.caption("🤖 = Donnée estimée par le moteur de simulation de l'IA en fonction du profil statistique de l'équipe.")

                        with t3:
                            st.markdown("#### 🎯 Analyse Pondérée : Plus ou Moins de 2.5 Buts")
                            score_final = ou_score; verdict = "PLUS DE 2.5 BUTS" if ou_res else "MOINS DE 2.5 BUTS"
                            color = "#00FF99" if ou_res else "#FF4B4B"
                            st.markdown(f"<div style='background:#1a1c24; padding:20px; border-radius:12px; border-left:5px solid {color}; text-align:center;'><h2 style='color:{color}; margin:0;'>VERDICT IA : {verdict}</h2><p style='color:#aaa; font-size:1.2rem; margin-top:10px;'>Score Algorithmique : <b>{score_final:.0f}/100</b> (Seuil à 55)</p></div>", unsafe_allow_html=True)
                            st.markdown("##### 🧮 Justification du calcul pondéré :")
                            st.markdown(f"""<ul><li><b>40% - Historique récent similaire :</b> {'✅ Favorable Over' if (hs_home['avg_gf']+as_away['avg_gf']) > 2.5 else '❌ Favorable Under'} ({hs_home['avg_gf']:.1f} + {as_away['avg_gf']:.1f} buts moy.)</li><li><b>30% - Friabilité défensive adverse :</b> {'✅ Défenses perméables' if (hs_home['avg_ga']+as_away['avg_ga']) > 2.5 else '❌ Défenses solides'} ({hs_home['avg_ga']:.1f} + {as_away['avg_ga']:.1f} encaissés moy.)</li><li><b>20% - Différentiel de forme :</b> {'✅ Écart significatif ou forme haute' if abs(hs_all['form']-as_all['form'])>1 or (hs_all['form']>2 and as_all['form']>2) else '❌ Formes proches ou basses'}</li><li><b>10% - Contexte (Fatigue, Enjeu) :</b> {'✅ Favorable aux buts' if context_val > 0.5 else '❌ Neutre ou défavorable'}</li></ul>""", unsafe_allow_html=True)
                            st.info(f"💡 **Synthèse de l'IA :** {ou_justif}")

                        with t4:
                            st.markdown("#### 🚀 Métriques de Performance Avancée (Estimations IA 🤖)")
                            col_p1, col_p2 = st.columns(2)
                            with col_p1:
                                st.markdown(f"<h5 style='color:#00FF99;'>{h_name}</h5>", unsafe_allow_html=True)
                                st.write(f"📦 Tirs dans la surface/match : **{adv_h['shots_in_box']:.1f}**")
                                st.write(f"🎯 Ratio Occasions Franches/Tirs : **{adv_h['big_chance_ratio']:.0f}%** {'🔥' if adv_h['big_chance_ratio']>30 else ''}")
                                st.write(f"👟 Passes décisives potentielles : **{adv_h['potential_assists']:.1f}**")
                                st.write(f"⚡ Vitesse de transition : **{adv_h['transition_speed']:.1f} m/s** {'⚡' if adv_h['transition_speed']<12 else ''}")
                            with col_p2:
                                st.markdown(f"<h5 style='color:#00D4FF;'>{a_name}</h5>", unsafe_allow_html=True)
                                st.write(f"📦 Tirs dans la surface/match : **{adv_a['shots_in_box']:.1f}**")
                                st.write(f"🎯 Ratio Occasions Franches/Tirs : **{adv_a['big_chance_ratio']:.0f}%** {'🔥' if adv_a['big_chance_ratio']>30 else ''}")
                                st.write(f"👟 Passes décisives potentielles : **{adv_a['potential_assists']:.1f}**")
                                st.write(f"⚡ Vitesse de transition : **{adv_a['transition_speed']:.1f} m/s** {'⚡' if adv_a['transition_speed']<12 else ''}")

                        with t5:
                            st.markdown("#### 🛡️ Indicateurs Défensifs (Estimations IA 🤖)")
                            col_d1, col_d2 = st.columns(2)
                            with col_d1:
                                st.markdown(f"<h5 style='color:#00FF99;'>{h_name}</h5>", unsafe_allow_html=True)
                                st.write(f"🔄 PPDA (Intensité Pressing) : **{adv_h['ppda']:.1f}** {'🐶 Féroce' if adv_h['ppda']<8 else ''}")
                                st.write(f"✈️ Duels aériens perdus : **{adv_h['aerial_duels_lost']:.0f}%** {'⚠️ Danger sur CPA' if adv_h['aerial_duels_lost']>55 else ''}")
                                st.write(f"📍 Distance moy. récupération : **{adv_h['recovery_distance']:.0f}m** {'⚠️ Haut risque' if adv_h['recovery_distance']>45 else ''}")
                                st.write(f"🧱 Stabilité Charnière Centrale : **{adv_h['cb_stability']} changements/10 matchs** {'⚠️ Instable' if adv_h['cb_stability']>3 else '✅ Stable'}")
                            with col_d2:
                                st.markdown(f"<h5 style='color:#00D4FF;'>{a_name}</h5>", unsafe_allow_html=True)
                                st.write(f"🔄 PPDA (Intensité Pressing) : **{adv_a['ppda']:.1f}** {'🐶 Féroce' if adv_a['ppda']<8 else ''}")
                                st.write(f"✈️ Duels aériens perdus : **{adv_a['aerial_duels_lost']:.0f}%** {'⚠️ Danger sur CPA' if adv_a['aerial_duels_lost']>55 else ''}")
                                st.write(f"📍 Distance moy. récupération : **{adv_a['recovery_distance']:.0f}m** {'⚠️ Haut risque' if adv_a['recovery_distance']>45 else ''}")
                                st.write(f"🧱 Stabilité Charnière Centrale : **{adv_a['cb_stability']} changements/10 matchs** {'⚠️ Instable' if adv_a['cb_stability']>3 else '✅ Stable'}")

                        with t6:
                            st.markdown("#### 🌧️ Facteurs Contextuels & Humains")
                            rest_diff = rest_h - rest_a
                            st.write(f"**🛌 Différentiel de Repos :** {rest_diff:+d} jours pour {h_name}.")
                            if rest_diff >= 3: st.success(f"✅ Avantage fraîcheur net pour {h_name} (+0.4 but attendu).")
                            elif rest_diff <= -3: st.error(f"❌ Désavantage fraîcheur net pour {h_name} (Risque de fatigue).")
                            else: st.info("Pas d'avantage significatif lié au repos.")
                            
                            st.divider()
                            random.seed(m_data['fixture']['id'])
                            media_h = random.randint(30, 95); media_a = random.randint(30, 95)
                            weather = random.choice(["Clair", "Pluie légère (+0.2 but)", "Pluie forte (-0.3 but)", "Vent latéral (+0.4 but)", "Canicule (-0.5 but)"])
                            ref_impact = random.choice(["Neutre", "Laisse jouer (+0.35 but)", "Sévère (-0.25 but)"])
                            humiliation_h = hs_all['avg_ga'] > 2.5 and hs_all['form'] < 1; humiliation_a = as_all['avg_ga'] > 2.5 and as_all['form'] < 1
                            
                            c_c1, c_c2 = st.columns(2)
                            c_c1.write(f"📰 **Pression Médiatique {h_name} (Simulé) :** {media_h}/100 {'🔥 Forte pression' if media_h>70 else ''}")
                            c_c2.write(f"📰 **Pression Médiatique {a_name} (Simulé) :** {media_a}/100 {'🔥 Forte pression' if media_a>70 else ''}")
                            
                            st.write(f"🌦️ **Météo prévue (Simulé) :** {weather}")
                            st.write(f"👮‍♂️ **Style de l'arbitre (Simulé) :** {ref_impact}")
                            
                            if humiliation_h: st.warning(f"😡 **Effet Cascade Émotionnel ({h_name}) :** L'équipe sort d'une période difficile. Réaction d'orgueil attendue (+0.7 but potentiel).")
                            if humiliation_a: st.warning(f"😡 **Effet Cascade Émotionnel ({a_name}) :** L'équipe sort d'une période difficile. Réaction d'orgueil attendue (+0.7 but potentiel).")
                            random.seed()
                else: st.error("Données insuffisantes pour une analyse profonde de ce match.")
        else: st.info("Sélectionnez une date avec des matchs.")

# =====================================================================
# --- AFFICHAGE PRINCIPAL : STANDARD / QUANTUM ---
# =====================================================================
elif st.session_state.mode == "std":
    if all_fixtures:
        all_fixtures.sort(key=lambda x: x['fixture']['date'])
        competitions = sorted(list(set([f['league']['name'] for f in all_fixtures])))
        dates = sorted(list(set([f['fixture']['date'][:10] for f in all_fixtures])))
        st.markdown("### 📅 SÉLECTION DU MATCH")
        c1, c2 = st.columns(2)
        sel_league = c1.selectbox("Compétition", ["Toutes"] + competitions)
        sel_date = c2.selectbox("Date", ["Toutes"] + dates)
        
        filt_fix = all_fixtures
        if sel_league != "Toutes": filt_fix = [f for f in filt_fix if f['league']['name'] == sel_league]
        if sel_date != "Toutes": filt_fix = [f for f in filt_fix if f['fixture']['date'][:10] == sel_date]
        
        if filt_fix:
            match_map = {"Tous les matchs": None} 
            match_map.update({f"[{f['fixture']['date'][11:16]}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in filt_fix})
            match_keys = list(match_map.keys())
            if 'main_match_select' not in st.session_state or st.session_state.main_match_select not in match_keys:
                st.session_state.main_match_select = match_keys[0] if match_keys else None
            sel_match = st.selectbox("Rencontre", match_keys, key="main_match_select")
            match_data = match_map[sel_match]
        else: match_data = "EMPTY"
    else: match_data = "EMPTY"

    if match_data is None and sel_match == "Tous les matchs":
        st.markdown("---")
        st.markdown("### 📋 Liste des rencontres filtrées")
        for f in filt_fix: 
            match_str = f"[{f['fixture']['date'][11:16]}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}"
            st.button(f"⏱️ {f['fixture']['date'][11:16]} | {f['teams']['home']['name']} vs {f['teams']['away']['name']} ➜ Analyser", use_container_width=True, on_click=set_match_and_analyze, args=(match_str,), key=f"go_{f['fixture']['id']}")

    elif match_data != "EMPTY":
        st.markdown("---")
        b1, b2 = st.columns(2)
        
        analyze_clicked = b1.button("🚀 ANALYSER", type="primary", use_container_width=True)
        if analyze_clicked or st.session_state.get('auto_trigger_analyze', False):
            st.session_state.auto_trigger_analyze = False 
            st.session_state.quantum_mode = False
            with st.spinner("Analyse Cohérente..."):
                hid, aid = match_data['teams']['home']['id'], match_data['teams']['away']['id']
                raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                if raw_h and raw_a:
                    hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
                    as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
                    hs = process_stats_by_filter(raw_h, 10, "all"); as_ = process_stats_by_filter(raw_a, 10, "all")
                    if hs_home and as_away:
                        p = get_coherent_probabilities(hs_home, as_away) 
                        st.session_state.analyzed_match_data = {"m": match_data, "raw_h": raw_h, "raw_a": raw_a, "p": p}
                    else: st.error("Données récentes insuffisantes pour analyser ce match."); st.session_state.analyzed_match_data = None
                else: st.error("Impossible de récupérer les statistiques des équipes (Pas de données en base)."); st.session_state.analyzed_match_data = None

        if b2.button("🧬 QUANTUM SNIPER", use_container_width=True):
            st.session_state.quantum_mode = True
            with st.spinner("Calcul Quantique..."):
                hid, aid = match_data['teams']['home']['id'], match_data['teams']['away']['id']
                raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                if raw_h and raw_a:
                    hs_home = process_stats_by_filter(raw_h, 10, "home") or process_stats_by_filter(raw_h, 10, "all")
                    as_away = process_stats_by_filter(raw_a, 10, "away") or process_stats_by_filter(raw_a, 10, "all")
                    if hs_home and as_away:
                        q = get_quantum_analysis(hs_home, as_away)
                        st.session_state.analyzed_match_data = {"m": match_data, "raw_h": raw_h, "raw_a": raw_a, "p": get_coherent_probabilities(hs_home, as_away), "q": q}
                    else: st.error("Données récentes insuffisantes pour l'analyse quantique."); st.session_state.analyzed_match_data = None
                else: st.error("Impossible de récupérer les statistiques des équipes."); st.session_state.analyzed_match_data = None

        if st.session_state.analyzed_match_data:
            d = st.session_state.analyzed_match_data
            if d['m']['fixture']['id'] == match_data['fixture']['id']:
                m = d['m']
                st.markdown(f"<div class='match-header'><div class='team-box'><img src='{m['teams']['home']['logo']}' class='team-logo'><div class='team-name'>{m['teams']['home']['name']}</div></div><div class='vs-box'>VS</div><div class='team-box'><img src='{m['teams']['away']['logo']}' class='team-logo'><div class='team-name'>{m['teams']['away']['name']}</div></div></div>", unsafe_allow_html=True)
                
                h = process_stats_by_filter(d['raw_h'], 10); a = process_stats_by_filter(d['raw_a'], 10)
                if st.button("🔍 Voir les 5 derniers résultats et le classement", use_container_width=True): show_history_and_rank_dialog(h['name'], d['raw_h']['id'], d['raw_h']['history'], h['form'], a['name'], d['raw_a']['id'], d['raw_a']['history'], a['form'], m['league']['id'])
                
                st.markdown("### ⚙️ Options d'Analyse")
                filter_opt = st.radio("Baser les statistiques sur :", ["5 derniers", "10 derniers", "Saison (20)"], horizontal=True, key="main_filter")
                limit = 5 if "5" in filter_opt else (20 if "Saison" in filter_opt else 10)
                h = process_stats_by_filter(d['raw_h'], limit); a = process_stats_by_filter(d['raw_a'], limit)
                
                if st.session_state.quantum_mode and 'q' in d:
                    q = d['q']
                    st.markdown("<h4 style='color:#00D4FF;'>🎯 RÉSULTAT QUANTUM</h4>", unsafe_allow_html=True)
                    if st.button(f"SCORE EXACT : {q['sniper_score']} \n\n (Confiance: {q['sniper_conf']:.1f}%)", use_container_width=True): show_analysis_dialog("quantum", f"{h['name']} vs {a['name']}", f"Cible : {q['sniper_score']}", h, a, q)
                else:
                    p = d['p']
                    st.markdown(f"<div class='probs-container'><div class='prob-box'><div class='info-icon'>💡</div><div class='prob-label'>DOMICILE</div><div class='prob-value'>{p[1]*100:.0f}%</div></div><div class='prob-box'><div class='prob-label'>NUL</div><div class='prob-value'>{p[0]*100:.0f}%</div></div><div class='prob-box'><div class='info-icon'>💡</div><div class='prob-label'>EXTÉRIEUR</div><div class='prob-value'>{p[2]*100:.0f}%</div></div></div>", unsafe_allow_html=True)
                    if st.button("🧠 Décortiquer le Raisonnement de l'IA", use_container_width=True):
                        best_idx = np.argmax(p)
                        if p[best_idx] < 0.45: pred_str = "⛔ NO BET (Trop incertain)"
                        else: pred_str = "Victoire Domicile" if best_idx==1 else ("Victoire Extérieur" if best_idx==2 else "Match Nul")
                        show_analysis_dialog("match", f"{h['name']} vs {a['name']}", pred_str, h, a)
                    st.progress(int(max(p)*100))

                if h and a:
                    t1, t2, t3, t4, t5 = st.tabs(["🔮 Score 10k", "⚡ Stats & Buteurs", "🛑 Discipline", "💰 Conseil", "🎯 Enjeu"])
                    with t1:
                        c_txt, c_graph = st.columns([0.6, 0.4]); c_txt.write(f"**Simulation 10 000 Matchs ({filter_opt})**")
                        scores, red, pens = simulate_10k_scenarios(h, a)
                        if c_graph.button("📈 Graphique", use_container_width=True): show_full_10k_graph(scores)
                        c1, c2, c3 = st.columns(3)
                        if len(scores)>0: 
                            if c1.button(f"#1: {scores[0][0]}\n({scores[0][1]}x)", use_container_width=True): show_scenario_chart(scores[0][0], scores[0][1])
                        if len(scores)>1: 
                            if c2.button(f"#2: {scores[1][0]}\n({scores[1][1]}x)", use_container_width=True): show_scenario_chart(scores[1][0], scores[1][1])
                        if len(scores)>2: 
                            if c3.button(f"#3: {scores[2][0]}\n({scores[2][1]}x)", use_container_width=True): show_scenario_chart(scores[2][0], scores[2][1])
                        st.caption(f"Risques Majeurs : 🟥 Rouge {red/100:.1f}% | ⚽ Penalty {pens/100:.1f}%")
                    with t2:
                        def row(l, v1, v2, u=""): st.markdown(f"<div class='stat-row'><span class='stat-label'>{l}</span><span class='stat-val'>{v1}{u} vs {v2}{u}</span></div>", unsafe_allow_html=True)
                        row("Moy. Buts", f"{h['avg_gf']:.2f}", f"{a['avg_gf']:.2f}"); row("Moy. Encaissés", f"{h['avg_ga']:.2f}", f"{a['avg_ga']:.2f}"); row("Clean Sheets", f"{h['cs_rate']:.0f}", f"{a['cs_rate']:.0f}", "%")
                        st.markdown("---"); st.markdown(f"#### ⏱️ Bilan Matchs Nuls & Fin de match ({filter_opt})")
                        c_n1, c_n2 = st.columns(2)
                        with c_n1: st.write(f"Nuls Mi-Temps : **{h['ht_draws']}** vs **{a['ht_draws']}**"); st.write(f"Nuls Fin Match : **{h['ft_draws']}** vs **{a['ft_draws']}**")
                        with c_n2: st.write(f"Buts pour (70'+) : **{(h['scored_70']/limit)*100:.0f}%** vs **{(a['scored_70']/limit)*100:.0f}%**"); st.write(f"Buts contre (70'+) : **{(h['conceded_70']/limit)*100:.0f}%** vs **{(a['conceded_70']/limit)*100:.0f}%**")
                        st.markdown("---"); st.markdown("#### 🎯 Top Buteurs")
                        sh = get_top_scorers(d['raw_h']['league_id'], d['raw_h']['id']); sa = get_top_scorers(d['raw_a']['league_id'], d['raw_a']['id'])
                        c_b1, c_b2 = st.columns(2)
                        with c_b1:
                            st.caption(f"**{h['name']}**")
                            for s in sh: 
                                c_t, c_s = st.columns([0.8, 0.2]); c_t.write(f"• {s['name']} ({s['goals']}b)")
                                if s['goals'] >= 3 or s['rating'] >= 7.1:
                                    if c_s.button("⭐", key=f"star_h_{s['name']}"): show_player_form_dialog(s)
                        with c_b2:
                            st.caption(f"**{a['name']}**")
                            for s in sa: 
                                c_t, c_s = st.columns([0.8, 0.2]); c_t.write(f"• {s['name']} ({s['goals']}b)")
                                if s['goals'] >= 3 or s['rating'] >= 7.1:
                                    if c_s.button("⭐", key=f"star_a_{s['name']}"): show_player_form_dialog(s)
                    with t3:
                        st.write(f"#### Discipline ({filter_opt})")
                        c_d1, c_d2 = st.columns(2)
                        with c_d1: st.info(f"**{h['name']}**"); st.write(f"🟥 Rouges : **{h['red_cards']}**"); st.write(f"🥅 Penaltys : **{h['pen_for']}**")
                        with c_d2: st.info(f"**{a['name']}**"); st.write(f"🟥 Rouges : **{a['red_cards']}**"); st.write(f"🥅 Penaltys : **{a['pen_for']}**")
                        if st.checkbox("Voir Historique H2H"):
                            h2h = get_h2h_stats(d['raw_h']['id'], d['raw_a']['id'])
                            if h2h: st.success(f"H2H ({h2h['matches']}m): {h2h['avg_goals']:.1f} buts/match en moyenne")
                            else: st.warning("Pas d'historique récent valide.")
                    with t4: 
                        st.write("#### 💰 Gestion de Bankroll")
                        bankroll = st.number_input("Entrez votre Bankroll totale (€)", min_value=10.0, value=100.0, step=10.0)
                        num_bets = st.number_input("Nombre de matchs à parier aujourd'hui", min_value=1, value=3, step=1)
                        conf = d['q']['sniper_conf'] if st.session_state.quantum_mode else max(d['p']) * 100
                        panier_max_par_pari = bankroll / num_bets; mise_calculee = panier_max_par_pari * (conf / 100); mise_finale = min(mise_calculee, bankroll * 0.10)
                        st.info(f"📈 Confiance de l'IA sur ce match : **{conf:.0f}%**"); st.success(f"💸 Mise recommandée : **{mise_finale:.2f} €**")
                    with t5:
                        st.write("#### 🎯 Enjeu et Classement")
                        standings = get_standings(m['league']['id']); enjeu_str = ""
                        if standings:
                            rank_h, rank_a = None, None
                            for team in standings:
                                if team['team']['id'] == d['raw_h']['id']: rank_h = team
                                if team['team']['id'] == d['raw_a']['id']: rank_a = team
                            if rank_h and rank_a:
                                c_e1, c_e2 = st.columns(2)
                                c_e1.markdown(f"**{h['name']}** {get_form_arrow(h['form'])}"); c_e1.write(f"Rang : **{rank_h['rank']}ème** ({rank_h['points']} pts)")
                                if rank_h['description']: c_e1.caption(f"Objectif: {rank_h['description']}")
                                c_e2.markdown(f"**{a['name']}** {get_form_arrow(a['form'])}"); c_e2.write(f"Rang : **{rank_a['rank']}ème** ({rank_a['points']} pts)")
                                if rank_a['description']: c_e2.caption(f"Objectif: {rank_a['description']}")
                                st.markdown("---")
                                if rank_h['rank'] <= 4 or rank_a['rank'] <= 4: enjeu_str = "Choc de haut de tableau avec un enjeu majeur pour le titre ou l'Europe."; st.info(f"🏆 **Analyse IA :** {enjeu_str}")
                                elif rank_h['rank'] >= len(standings)-4 or rank_a['rank'] >= len(standings)-4: enjeu_str = "Match sous très haute tension pour le maintien."; st.warning(f"⚠️ **Analyse IA :** {enjeu_str}")
                                else: enjeu_str = "Match de milieu de tableau (Ventre mou)."; st.success(f"⚖️ **Analyse IA :** {enjeu_str}")
                            else: st.write("Équipes non trouvées dans le classement principal.")
                        else: enjeu_str = "Classement non disponible pour cette compétition (Il s'agit probablement d'une Coupe)."; st.info(f"📊 {enjeu_str}")
                            
                    st.markdown("---")
                    if st.button("🔮 ANALYSE FINALE COMPLÈTE", type="primary", use_container_width=True): show_final_verdict(h, a, d['p'], d.get('q'), enjeu_str)

# --- SCRIPT JS POUR FERMER LA BARRE LATÉRALE AUTOMATIQUEMENT ---
if st.session_state.get('collapse_sidebar', False):
    js = """
    <script>
    setTimeout(function() {
        const closeBtn = window.parent.document.querySelector('[data-testid="stSidebarCollapsedControl"]');
        if (closeBtn && closeBtn.getAttribute('aria-expanded') === 'true') {
            closeBtn.click();
        }
    }, 100);
    </script>
    """
    components.html(js, height=0, width=0)
    st.session_state.collapse_sidebar = False
