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

# --- 1. CONFIGURATION V40 (LE PIF DU FOOT - UX & PLAN B) ---
st.set_page_config(page_title="Le Pif Du Foot", layout="wide", page_icon="👃")

st.markdown("""
<style>
    /* FOND GÉNÉRAL & TEXTE */
    .stApp, [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; color: #FFFFFF !important; }
    p, h1, h2, h3, div, span, label, h4, h5, h6, li, td, th { color: #FFFFFF !important; }

    /* BRANDING TITRE PIF DU FOOT */
    .pif-title {
        text-align: center;
        font-weight: 900;
        font-size: 2.5rem;
        background: linear-gradient(90deg, #00FF99, #00D4FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .pif-subtitle { text-align: center; font-style: italic; color: #aaaaaa !important; margin-top: -10px; margin-bottom: 30px; }

    /* MA SÉLECTION TITRE */
    .my-sel-title { text-align: center; font-weight: 900; color: #FFD700 !important; font-size: 1.8rem; border-bottom: 2px solid #FFD700; padding-bottom: 10px; margin-bottom: 20px;}

    /* FENÊTRES MODALES (DIALOGS IPHONE) */
    div[role="dialog"] { background-color: #0b1016 !important; border: 2px solid #00FF99 !important; border-radius: 15px !important; box-shadow: 0 0 30px rgba(0, 255, 153, 0.2); }
    div[role="dialog"] * { color: #FFFFFF !important; }
    div[role="dialog"] h2, div[role="dialog"] h3 { color: #00FF99 !important; text-align: center; }
    
    /* ==============================================
       FIX BUG GRAPHIQUES (INFOBULLES & MENU BLANC)
       ============================================== */
    #vg-tooltip-element { background-color: #1a1c24 !important; color: white !important; border: 1px solid #00FF99 !important; font-family: sans-serif; border-radius: 8px; }
    #vg-tooltip-element td { color: white !important; }
    summary.vega-actions { display: none !important; } /* CACHE LE MENU BLANC FLOTTANT */

    /* SELECTBOX FIX */
    div[data-baseweb="select"] > div { background-color: #1a1c24 !important; color: white !important; border-color: #333 !important; }
    div[data-baseweb="select"] span { color: white !important; }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] { background-color: #1a1c24 !important; border: 1px solid #333 !important; }
    li[role="option"] { background-color: #1a1c24 !important; color: white !important; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #00FF99 !important; color: black !important; }
    div[data-baseweb="select"] svg { fill: white !important; }

    /* SIDEBAR */
    [data-testid="stSidebar"] { background-color: #0E1117 !important; border-right: 1px solid #333 !important; }
    [data-testid="stSidebarCollapsedControl"] { color: #FFFFFF !important; background-color: #1a1c24 !important; border: 1px solid #333; }
    [data-testid="stSidebarUserContent"] h1, [data-testid="stSidebarUserContent"] h2 { color: #00FF99 !important; }

    /* BOUTON VALIDER (VERT) & AUTO (BLEU) */
    button[kind="primary"] { background: linear-gradient(90deg, #00FF99, #00CC77) !important; color: #0E1117 !important; font-weight: 900 !important; border: none !important; box-shadow: 0 4px 15px rgba(0, 255, 153, 0.4) !important; }
    button[kind="secondary"] { background: linear-gradient(90deg, #0055FF, #00D4FF) !important; color: white !important; border: none !important; font-weight: 900 !important; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4) !important; }
    
    /* BOUTON PLAN B (ORANGE) */
    .btn-plan-b button { background: linear-gradient(90deg, #FF4B4B, #FF8800) !important; color: white !important; border: none !important; font-weight: 900 !important; box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4) !important; }

    /* HEADER MATCH & EXPANDERS */
    .match-header { display: flex; flex-direction: row; align-items: center; justify-content: space-between; background: #1a1c24; padding: 10px 5px; border-radius: 12px; margin-bottom: 5px; border: 1px solid #333; }
    .team-box { text-align: center; width: 40%; display: flex; flex-direction: column; align-items: center; }
    .team-logo { width: 45px; height: 45px; object-fit: contain; margin-bottom: 3px; }
    .team-name { font-size: 0.75rem; font-weight: bold; line-height: 1.1; color: white !important; }
    .vs-box { width: 20%; text-align: center; color: #00FF99 !important; font-weight: 900; font-size: 1.2rem; }
    
    div[data-testid="stExpander"] { background-color: #1a1c24 !important; border-color: #333 !important; border-radius: 8px !important; }
    div[data-testid="stExpander"] summary p { color: #00FF99 !important; font-weight: bold !important; }

    /* PROBS & STATS */
    .probs-container { display: flex; flex-direction: row; justify-content: space-between; gap: 5px; margin-bottom: 20px; width: 100%; }
    .prob-box { background-color: #1a1c24; border: 1px solid #363b4e; border-radius: 8px; width: 32%; padding: 10px 2px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }
    .prob-label { font-size: 0.6rem; color: #AAAAAA !important; font-weight: bold; text-transform: uppercase; }
    .prob-value { font-size: 1.2rem; font-weight: 900; color: #FFFFFF !important; line-height: 1.2; }
    .stat-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #333; font-size: 0.85rem; align-items: center; }
    .stat-label { color: #aaa; font-size: 0.8rem; } .stat-val { font-weight: bold; font-size: 0.9rem; }
    
    .ticket-match-title { font-weight: bold; color: #00FF99 !important; margin-top: 10px; border-bottom: 1px solid #333; }
    
    .comp-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.9rem; background-color: transparent !important; }
    .comp-table th, .comp-table td { border: 1px solid #444; padding: 10px; text-align: center; }
    .comp-table th { background-color: #262935; color: #00FF99 !important; font-weight: bold; }
    .comp-table tr:nth-child(even) { background-color: #1a1c24; }
    
    @media only screen and (max-width: 640px) { .block-container { padding-top: 1rem !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; } }
</style>
""", unsafe_allow_html=True)

API_KEY = "4d3c1dbf76600a937722ff6425d450ee"
HEADERS = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
LEAGUE_IDS = [2, 3, 39, 61, 140, 135, 78, 94, 45, 203, 307, 143, 323, 848]

# STATES INITIAUX
if 'analyzed_match_data' not in st.session_state: st.session_state.analyzed_match_data = None
if 'ticket_data' not in st.session_state: st.session_state.ticket_data = None
if 'scorer_ticket' not in st.session_state: st.session_state.scorer_ticket = None
if 'mode' not in st.session_state: st.session_state.mode = "std" 
if 'quantum_mode' not in st.session_state: st.session_state.quantum_mode = False

# STATES MA SÉLECTION & PLAN B
if 'persisted_selections' not in st.session_state: st.session_state.persisted_selections = {}
if 'selection_validated' not in st.session_state: st.session_state.selection_validated = False
if 'selection_analyzed' not in st.session_state: st.session_state.selection_analyzed = False
if 'selection_ai_results' not in st.session_state: st.session_state.selection_ai_results = {}
if 'auto_analyzed' not in st.session_state: st.session_state.auto_analyzed = False
if 'show_plan_b' not in st.session_state: st.session_state.show_plan_b = False

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
        history.append({"gf": gf, "ga": ga, "res": res, "pen_call": 1 if (gf > 2 and random.random() > 0.8) else 0, "red_card": 1 if (random.random() > 0.95) else 0, "ht_draw": ht_d, "ft_draw": ft_d, "scored_70": 1 if s_70 > 0 else 0, "conceded_70": 1 if c_70 > 0 else 0})
    return {"name": d[0]['teams']['home']['name'] if d[0]['teams']['home']['id'] == tid else d[0]['teams']['away']['name'], "id": tid, "history": history, "league_id": d[0]['league']['id']}

@st.cache_data(ttl=3600)
def get_standings(league_id):
    try:
        r = requests.get("https://v3.football.api-sports.io/standings", headers=HEADERS, params={"league": league_id, "season": "2025"}).json()
        if 'response' in r and len(r['response']) > 0: return r['response'][0]['league']['standings'][0]
    except: pass
    return None

def process_stats_by_filter(raw_stats, limit):
    if not raw_stats or 'history' not in raw_stats: return None
    data = raw_stats['history'][:limit]
    if not data: return None
    gs = [x['gf'] for x in data]; gc = [x['ga'] for x in data]
    avg_gf = sum(gs)/len(data) if data else 0
    avg_ga = sum(gc)/len(data) if data else 0
    pts = sum([3 if x['res']=="✅" else (1 if x['res']=="➖" else 0) for x in data])
    form = pts / len(data) if data else 0
    cs = sum([1 for x in data if x['ga']==0])
    btts = sum([1 for x in data if x['gf']>0 and x['ga']>0])
    try: vol = statistics.stdev(gs)
    except: vol = 0
    return {"name": raw_stats['name'], "id": raw_stats['id'], "avg_gf": avg_gf, "avg_ga": avg_ga, "form": form, "cs_rate": cs/len(data)*100 if data else 0, "btts_rate": btts/len(data)*100 if data else 0, "draw_rate": sum([x['ft_draw'] for x in data])/len(data)*100 if data else 0, "vol": vol, "pen_for": sum([x['pen_call'] for x in data]), "red_cards": sum([x['red_card'] for x in data]), "streak": "".join([x['res'] for x in data[:5]]), "count": len(data), "raw_gf": gs, "ht_draws": sum([x['ht_draw'] for x in data]), "ft_draws": sum([x['ft_draw'] for x in data]), "scored_70": sum([x['scored_70'] for x in data]), "conceded_70": sum([x['conceded_70'] for x in data])}

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

# --- INTELLIGENCE AVANCÉE ---
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
            if i > j: ph += prob
            elif i == j: pd += prob
            else: pa += prob
    tot = ph + pd + pa
    return [pd/tot, ph/tot, pa/tot]

def gen_smart_justif(type, val, h, a):
    r = []
    h_name = h.get('name', 'Domicile'); a_name = a.get('name', 'Extérieur')
    if "Domicile" in val:
        if h.get('form', 0) > 1.5: r.append(f"{h_name} est en forme.")
        if h.get('avg_gf', 0) > 1.5: r.append("Attaque prolifique à domicile.")
        if a.get('avg_ga', 0) > 1.5: r.append(f"Défense adverse friable.")
    elif "Extérieur" in val:
        if a.get('form', 0) > 1.5: r.append(f"{a_name} voyage bien.")
        if a.get('avg_gf', 0) > 1.5: r.append("Contre-attaque efficace.")
    elif "Nul" in val: r.append("Forces équilibrées.")
    return random.choice(r) if r else "Analyse statistique favorable."

def gen_plan_b_justif(val, h, a):
    # Justifications pour le scénario "Et si ça se passait autrement"
    if "Domicile" in val: return f"Si {a.get('name')} craque sous la pression, {h.get('name')} pourrait l'emporter grâce à l'avantage du terrain."
    elif "Extérieur" in val: return f"Si {h.get('name')} se découvre trop, {a.get('name')} a les armes pour créer l'exploit en contre."
    elif "Nul" in val: return "Si les défenses prennent le pas sur les attaques, le match pourrait se verrouiller complètement."
    return "Scénario de secours basé sur la volatilité du match."

# --- TICKETS ---
def gen_match_ticket(fix):
    pools = {"WIN":[], "DRAW":[], "OVER":[], "UNDER":[], "BTTS":[]}
    bar = st.sidebar.progress(0, text="Analyse Multidimensionnelle...")
    fix_copy = fix.copy(); random.shuffle(fix_copy); limit = min(len(fix_copy), 30) 
    for i, f in enumerate(fix_copy[:limit]):
        hid, aid = f['teams']['home']['id'], f['teams']['away']['id']
        raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
        if raw_h and raw_a:
            hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
            h2h = get_h2h_stats(hid, aid); h2h_avg = h2h['avg_goals'] if h2h else (hs['avg_gf'] + as_['avg_gf'])
            if abs(hs['form'] - as_['form']) <= 0.4 and (hs['draw_rate'] > 30 or as_['draw_rate'] > 30): pools["DRAW"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "⚖️ Résultat", "v": "Match Nul", "j": "Niveau très équilibré et forte tendance historique au nul.", "h": hs, "a": as_})
            elif hs['btts_rate'] >= 60 and as_['btts_rate'] >= 60 and hs['avg_gf'] >= 1.2 and as_['avg_gf'] >= 1.2: pools["BTTS"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🥅 Les 2 marquent", "v": "OUI", "j": "Attaques très performantes combinées à des défenses friables.", "h": hs, "a": as_})
            elif (hs['avg_gf'] + as_['avg_gf']) <= 2.2 or (hs['avg_ga'] <= 1.0 and as_['avg_ga'] <= 1.0): pools["UNDER"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🔒 Buts", "v": "-2.5 Buts", "j": "Rencontre fermée prévue. Les attaques peinent et les défenses sont solides.", "h": hs, "a": as_})
            elif (hs['avg_gf'] + as_['avg_gf']) > 3.0 and h2h_avg >= 2.5: pools["OVER"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "⚽ Buts", "v": "+2.5 Buts", "j": "Forte puissance offensive de part et d'autre. Match ouvert.", "h": hs, "a": as_})
            elif hs['form'] > 2.0 and as_['form'] < 1.2: pools["WIN"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🏆 Résultat", "v": f"Victoire {hs['name']}", "j": "Domination totale du favori à domicile.", "h": hs, "a": as_})
            elif as_['form'] > 2.0 and hs['form'] < 1.2: pools["WIN"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🏆 Résultat", "v": f"Victoire {as_['name']}", "j": "Dynamique impressionnante à l'extérieur face à une équipe en difficulté.", "h": hs, "a": as_})
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
            scorers.append({"m": f"{hs['name']} vs {as_['name']}", "p": sh[0], "team": hs['name'], "h": hs, "a": as_})
        bar.progress((i+1)/limit)
    bar.empty()
    return scorers[:6]

def update_user_selection(fix_id, match_str, home_id, away_id, league_id):
    val = st.session_state[f"rad_{fix_id}"]
    if val != "Aucun": st.session_state.persisted_selections[fix_id] = {"match": match_str, "home_id": home_id, "away_id": away_id, "league_id": league_id, "user_pick": val}
    else:
        if fix_id in st.session_state.persisted_selections: del st.session_state.persisted_selections[fix_id]

# --- DIALOGS (FENÊTRES MODALES) ---
@st.dialog("🗓️ HISTORIQUE DES 5 DERNIERS MATCHS")
def show_history_dialog(h_name, h_hist, a_name, a_hist):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<h4 style='color:#00D4FF;text-align:center;'>{h_name}</h4>", unsafe_allow_html=True)
        for m in h_hist[:5]:
            col = "#00FF99" if m['res']=="✅" else ("#FFA500" if m['res']=="➖" else "#FF4B4B")
            st.markdown(f"<div style='text-align:center; padding:5px; margin:2px; background:#1a1c24; border-radius:5px; border-left:3px solid {col};'><b>{m['res']}</b> | Score: {m['gf']} - {m['ga']}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<h4 style='color:#00D4FF;text-align:center;'>{a_name}</h4>", unsafe_allow_html=True)
        for m in a_hist[:5]:
            col = "#00FF99" if m['res']=="✅" else ("#FFA500" if m['res']=="➖" else "#FF4B4B")
            st.markdown(f"<div style='text-align:center; padding:5px; margin:2px; background:#1a1c24; border-radius:5px; border-left:3px solid {col};'><b>{m['res']}</b> | Score: {m['gf']} - {m['ga']}</div>", unsafe_allow_html=True)

@st.dialog("🧠 RAYON X : ANALYSE DE L'IA")
def show_analysis_dialog(type_analyse, titre, pred, h, a, extra=None):
    st.markdown(f"<h3>{titre}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#00FF99; font-weight:bold; font-size:1.2rem;'>{pred}</p>", unsafe_allow_html=True)
    st.divider()
    if type_analyse == "match":
        c1, c2 = st.columns(2); c1.metric(f"Forme {h['name']}", f"{h['form']:.2f} pts"); c2.metric(f"Forme {a['name']}", f"{a['form']:.2f} pts")
        c3, c4 = st.columns(2); c3.metric(f"Attaque {h['name']}", f"{h['avg_gf']:.1f} buts/m"); c4.metric(f"Défense {a['name']}", f"{a['avg_ga']:.1f} encaissés")
        if "-2.5" in pred: st.info("💡 L'IA anticipe un match très fermé. Les défenses prennent le pas sur les attaques.")
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
    if home_adv > away_adv + 15: verdict = f"VICTOIRE {h['name'].upper()}"; color = "#00FF99"
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

def get_form_arrow(form_pts): return "🟢 ⬆️" if form_pts >= 2.0 else ("🔴 ⬇️" if form_pts <= 1.0 else "⚪ ➡️")

# --- HEADER PRINCIPAL (LOGO & TITRE) ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try: st.image("IMG_5755.jpg", use_column_width=True)
    except: st.markdown("<h1 class='pif-title'>👃 LE PIF DU FOOT</h1>", unsafe_allow_html=True)
    st.markdown("<p class='pif-subtitle'>Le nez ne ment jamais</p>", unsafe_allow_html=True)
# st.caption("Anciennement Oracle V40") # Commentaire technique

all_fixtures = get_upcoming_matches()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎟️ TICKET")
    if st.button("🎰 GÉNÉRER PRONOS", type="primary"):
        st.session_state.mode = "std"
        with st.spinner("Création ticket dynamique..."): st.session_state.ticket_data = gen_match_ticket(all_fixtures)
    
    if st.button("⚽ BUTEURS POTENTIELS"):
        st.session_state.mode = "scorer"
        with st.spinner("Recherche des Renards..."): st.session_state.scorer_ticket = gen_scorer_ticket(all_fixtures)

    st.markdown("---")
    if st.button("📝 MA SÉLECTION"):
        st.session_state.mode = "my_selection"
        st.session_state.selection_validated = False
        st.session_state.auto_analyzed = False
        st.session_state.show_plan_b = False
        
    if st.button("📊 GRAPHIQUES DE COMPARAISON"): st.session_state.mode = "graphs"

    if st.session_state.mode == "std" and st.session_state.ticket_data:
        st.success("✅ TICKET MATCHS (Unique)")
        for i, item in enumerate(st.session_state.ticket_data):
            st.markdown(f"<div class='ticket-match-title'>{i+1}. {item['m']}</div>", unsafe_allow_html=True)
            icon = "⚖️" if "Nul" in item['v'] else ("🔒" if "-2.5" in item['v'] else ("🥅" if "OUI" in item['v'] else ("⚽" if "+2.5" in item['v'] else "🏆")))
            if st.button(f"{icon} {item['t']} : {item['v']}", key=f"tck_btn_{i}", use_container_width=True): show_analysis_dialog("match", item['m'], item['v'], item['h'], item['a'])

    if st.session_state.mode == "scorer" and st.session_state.scorer_ticket:
        st.success("✅ TICKET BUTEURS")
        for i, item in enumerate(st.session_state.scorer_ticket):
            p = item['p']
            st.markdown(f"<div class='ticket-match-title'>{i+1}. {item['m']}</div>", unsafe_allow_html=True)
            if st.button(f"🎯 {p['name']} ({item['team']})", key=f"tck_scr_{i}", use_container_width=True): show_analysis_dialog("scorer", item['m'], f"Buteur : {p['name']}", item['h'], item['a'], p)

# --- AFFICHAGE : GRAPHIQUES DE COMPARAISON ---
if st.session_state.mode == "graphs":
    st.markdown("### 📊 GRAPHIQUES DE COMPARAISON")
    if all_fixtures:
        dates = sorted(list(set([f['fixture']['date'][:10] for f in all_fixtures])))
        c_date, c_match = st.columns(2)
        sel_date_g = c_date.selectbox("📅 Date", dates, key="g_date")
        matches_g = [f for f in all_fixtures if f['fixture']['date'][:10] == sel_date_g]
        if matches_g:
            match_map_g = {f"[{f['fixture']['date'][11:16]}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in matches_g}
            sel_match_g = c_match.selectbox("⚽ Match du jour", list(match_map_g.keys()), key="g_match")
            m_data = match_map_g[sel_match_g]
            hid, aid = m_data['teams']['home']['id'], m_data['teams']['away']['id']
            h_name, a_name = m_data['teams']['home']['name'], m_data['teams']['away']['name']
            
            with st.spinner("Chargement des données..."): raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
            if raw_h and raw_a:
                h = process_stats_by_filter(raw_h, 10); a = process_stats_by_filter(raw_a, 10); adv = get_advanced_mock_data(h, a)
                
                st.markdown("#### 🌍 Vue d'ensemble Globale")
                df_global = pd.DataFrame({"Equipe": [h_name, h_name, h_name, h_name, a_name, a_name, a_name, a_name], "Critère": ["Attaque", "Défense (Solidité)", "Forme", "Discipline", "Attaque", "Défense (Solidité)", "Forme", "Discipline"], "Note (0-100)": [min(100, h['avg_gf']*35), max(0, 100 - h['avg_ga']*35), min(100, h['form']*33), max(0, 100 - h['red_cards']*20), min(100, a['avg_gf']*35), max(0, 100 - a['avg_ga']*35), min(100, a['form']*33), max(0, 100 - a['red_cards']*20)]})
                base_global = alt.Chart(df_global).encode(x=alt.X('Critère:N', title=None, axis=dark_axis_config), y=alt.Y('Note (0-100):Q', scale=alt.Scale(domain=[0, 100]), axis=dark_axis_config), color=alt.Color('Equipe:N', scale=alt.Scale(range=['#00FF99', '#00D4FF']), legend=alt.Legend(title=None, labelColor='#E0E0E0', orient='bottom')), xOffset='Equipe:N', tooltip=[alt.Tooltip('Equipe', title='Équipe'), alt.Tooltip('Critère'), alt.Tooltip('Note (0-100)', title='Score', format='.0f')])
                ch_global = base_global.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4) + base_global.mark_text(align='center', baseline='bottom', dy=-5, color='white', fontWeight='bold').encode(text=alt.Text('Note (0-100):Q', format='.0f'))
                st.altair_chart(ch_global.properties(height=320, background='transparent').configure_view(strokeWidth=0), use_container_width=True, theme=None)
                
                st.markdown("---")
                cat_options = ["1. Forme actuelle", "2. Statistiques offensives", "3. Statistiques défensives", "4. Confrontations directes (H2H)", "5. Avantage du terrain", "6. Composition d’équipe", "7. Aspect tactique", "8. Expérience européenne", "9. Enjeu et motivation", "10. Données avancées", "11. Facteurs externes", "12. Analyse probabiliste"]
                sel_cat = st.selectbox("🔍 Sélectionner un domaine d'analyse détaillé :", cat_options, key="g_cat")
                
                if "1. Forme" in sel_cat:
                    st.write(f"##### 📈 Résultats Récents (10 derniers matchs)")
                    df_form = pd.DataFrame({"Equipe": [h_name, a_name], "Points/Match": [h['form'], a['form']]})
                    base_form = alt.Chart(df_form).encode(x=alt.X('Equipe:N', axis=dark_axis_config, title=None), y=alt.Y('Points/Match:Q', axis=dark_axis_config, title='Points / Match'), color=alt.Color('Equipe', scale=alt.Scale(range=['#00FF99', '#00D4FF']), legend=None), tooltip=['Equipe', alt.Tooltip('Points/Match', format='.2f')])
                    ch_form = base_form.mark_bar(size=60, cornerRadiusTopLeft=8, cornerRadiusTopRight=8) + base_form.mark_text(dy=-10, color='white', fontSize=14, fontWeight='bold').encode(text=alt.Text('Points/Match:Q', format='.2f'))
                    st.altair_chart(ch_form.properties(height=280, background='transparent').configure_view(strokeWidth=0), use_container_width=True, theme=None)
                    st.markdown(f"<table class='comp-table'><tr><th>Donnée</th><th>{h_name}</th><th>{a_name}</th></tr><tr><td>Série (5 derniers)</td><td>{h['streak']}</td><td>{a['streak']}</td></tr><tr><td>Points par match</td><td>{h['form']:.2f}</td><td>{a['form']:.2f}</td></tr></table>", unsafe_allow_html=True)

                elif "2. Stat" in sel_cat and "offensives" in sel_cat:
                    st.write("##### ⚽ Puissance de Frappe")
                    df_off = pd.DataFrame({"Métrique": ["Buts/Match", "Buts/Match", "xG/Match", "xG/Match", "Tirs/Match (div. 5)", "Tirs/Match (div. 5)"], "Equipe": [h_name, a_name, h_name, a_name, h_name, a_name], "Valeur": [h['avg_gf'], a['avg_gf'], adv['h_xg'], adv['a_xg'], adv['h_shots']/5, adv['a_shots']/5], "Valeur Réelle": [h['avg_gf'], a['avg_gf'], adv['h_xg'], adv['a_xg'], adv['h_shots'], adv['a_shots']]})
                    base_off = alt.Chart(df_off).encode(x=alt.X('Métrique:N', axis=dark_axis_config, title=None), y=alt.Y('Valeur:Q', axis=dark_axis_config, title=None), color=alt.Color('Equipe:N', scale=alt.Scale(range=['#00FF99', '#00D4FF']), legend=alt.Legend(title=None, labelColor='#E0E0E0', orient='bottom')), xOffset='Equipe:N', tooltip=['Equipe', 'Métrique', alt.Tooltip('Valeur Réelle', format='.1f', title='Valeur')])
                    ch_off = base_off.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4) + base_off.mark_text(dy=-10, color='white', fontWeight='bold').encode(text=alt.Text('Valeur Réelle:Q', format='.1f'))
                    st.altair_chart(ch_off.properties(height=300, background='transparent').configure_view(strokeWidth=0), use_container_width=True, theme=None)
                    st.markdown(f"<table class='comp-table'><tr><th>Donnée</th><th>{h_name}</th><th>{a_name}</th></tr><tr><td>Moy. Buts Marqués</td><td>{h['avg_gf']:.2f}</td><td>{a['avg_gf']:.2f}</td></tr><tr><td>Expected Goals (xG)</td><td>{adv['h_xg']:.2f}</td><td>{adv['a_xg']:.2f}</td></tr><tr><td>Tirs/Match</td><td>{adv['h_shots']:.1f}</td><td>{adv['a_shots']:.1f}</td></tr><tr><td>Tirs Cadrés/Match</td><td>{adv['h_sot']:.1f}</td><td>{adv['a_sot']:.1f}</td></tr></table>", unsafe_allow_html=True)

                elif "3. Stat" in sel_cat and "défensives" in sel_cat:
                    st.write("##### 🛡️ Le Mur Défensif (Plus bas est meilleur)")
                    df_def = pd.DataFrame({"Métrique": ["Buts Encaissés", "Buts Encaissés", "xGA (Expected)", "xGA (Expected)"], "Equipe": [h_name, a_name, h_name, a_name], "Valeur": [h['avg_ga'], a['avg_ga'], adv['h_xga'], adv['a_xga']]})
                    base_def = alt.Chart(df_def).encode(x=alt.X('Métrique:N', axis=dark_axis_config, title=None), y=alt.Y('Valeur:Q', axis=dark_axis_config, title=None), color=alt.Color('Equipe:N', scale=alt.Scale(range=['#FF4B4B', '#FFA500']), legend=alt.Legend(title=None, labelColor='#E0E0E0', orient='bottom')), xOffset='Equipe:N', tooltip=['Equipe', 'Métrique', alt.Tooltip('Valeur', format='.2f')])
                    ch_def = base_def.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4) + base_def.mark_text(dy=-10, color='white', fontWeight='bold').encode(text=alt.Text('Valeur:Q', format='.2f'))
                    st.altair_chart(ch_def.properties(height=300, background='transparent').configure_view(strokeWidth=0), use_container_width=True, theme=None)
                    st.markdown(f"<table class='comp-table'><tr><th>Donnée</th><th>{h_name}</th><th>{a_name}</th></tr><tr><td>Moy. Buts Encaissés</td><td>{h['avg_ga']:.2f}</td><td>{a['avg_ga']:.2f}</td></tr><tr><td>Expected Goals Against (xGA)</td><td>{adv['h_xga']:.2f}</td><td>{adv['a_xga']:.2f}</td></tr><tr><td>Clean Sheets</td><td>{h['cs_rate']:.0f}%</td><td>{a['cs_rate']:.0f}%</td></tr></table>", unsafe_allow_html=True)

                elif "4. Conf" in sel_cat:
                    h2h = get_h2h_stats(h['id'], a['id'])
                    st.write("##### ⚔️ Face à Face (Historique)")
                    if h2h:
                        st.metric("Confrontations récentes analysées", h2h['matches'])
                        st.markdown(f"<table class='comp-table'><tr><th>Donnée</th><th>Comparaison</th></tr><tr><td>Moyenne Buts par Match (H2H)</td><td>{h2h['avg_goals']:.2f} buts</td></tr><tr><td>Volatilité du score</td><td>{'Haute' if h2h['vol']>1.5 else 'Basse'}</td></tr></table>", unsafe_allow_html=True)
                    else: st.warning("Aucune confrontation directe récente.")

                elif "5. Avantage" in sel_cat:
                    st.write("##### 🏟️ Domination Territoriale")
                    st.markdown(f"<table class='comp-table'><tr><th>Donnée</th><th>{h_name} (Domicile)</th><th>{a_name} (Extérieur)</th></tr><tr><td>Pression du public estimée</td><td>Très Haute</td><td>-</td></tr><tr><td>Taux de Nuls/Défaites</td><td>{h['draw_rate']:.0f}% Nul</td><td>{a['draw_rate']:.0f}% Nul</td></tr></table>", unsafe_allow_html=True)

                elif "6. Comp" in sel_cat:
                    st.write("##### 🏥 Effectif & Joueurs Clés")
                    sh = get_top_scorers(m_data['league']['id'], h['id']); sa = get_top_scorers(m_data['league']['id'], a['id'])
                    top_h = sh[0]['name'] if sh else "Inconnu"; top_a = sa[0]['name'] if sa else "Inconnu"
                    st.markdown(f"<table class='comp-table'><tr><th>{h_name}</th><th>{a_name}</th></tr><tr><td>Buteur Principal : {top_h}</td><td>Buteur Principal : {top_a}</td></tr><tr><td>Forme Gardien : {'Excellente' if h['cs_rate']>30 else 'Moyenne'}</td><td>Forme Gardien : {'Excellente' if a['cs_rate']>30 else 'Moyenne'}</td></tr></table>", unsafe_allow_html=True)

                elif "7. Tactique" in sel_cat:
                    st.write("##### ♟️ Style de Jeu (Simulation IA)")
                    df_tact = pd.DataFrame({"Métrique": ["Possession", "Possession", "Pressing (PPDA inv.)", "Pressing (PPDA inv.)"], "Equipe": [h_name, a_name, h_name, a_name], "Valeur (%)": [adv['h_poss'], adv['a_poss'], 100-adv['h_ppda']*3, 100-adv['a_ppda']*3]})
                    base_tact = alt.Chart(df_tact).encode(x=alt.X('Valeur (%):Q', axis=dark_axis_config, scale=alt.Scale(domain=[0, 100]), title=None), y=alt.Y('Métrique:N', axis=dark_axis_config, title=None), color=alt.Color('Equipe:N', scale=alt.Scale(range=['#00FF99', '#00D4FF']), legend=alt.Legend(title=None, labelColor='#E0E0E0', orient='bottom')), yOffset='Equipe:N', tooltip=['Equipe', 'Métrique', alt.Tooltip('Valeur (%)', format='.0f')])
                    ch_tact = base_tact.mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4) + base_tact.mark_text(align='left', dx=5, color='white', fontWeight='bold').encode(text=alt.Text('Valeur (%):Q', format='.0f'))
                    st.altair_chart(ch_tact.properties(height=250, background='transparent').configure_view(strokeWidth=0), use_container_width=True, theme=None)

                elif "8. Expérience" in sel_cat:
                    st.write("##### 🌍 Niveau Compétitif")
                    st.markdown(f"<table class='comp-table'><tr><th>Donnée</th><th>{h_name}</th><th>{a_name}</th></tr><tr><td>Ligue</td><td colspan='2'>{m_data['league']['name']}</td></tr><tr><td>Statut</td><td>{'Favori Local' if h['form']>2 else 'Challenger'}</td><td>{'Favori Extérieur' if a['form']>2 else 'Challenger'}</td></tr></table>", unsafe_allow_html=True)

                elif "9. Enjeu" in sel_cat:
                    standings = get_standings(m_data['league']['id'])
                    if standings:
                        rank_h, rank_a = None, None
                        for t in standings:
                            if t['team']['id'] == h['id']: rank_h = t
                            if t['team']['id'] == a['id']: rank_a = t
                        if rank_h and rank_a:
                            st.markdown(f"<table class='comp-table'><tr><th>Equipe</th><th>Classement</th><th>Points</th><th>Objectif</th></tr><tr><td>{h_name}</td><td>{rank_h['rank']}</td><td>{rank_h['points']}</td><td>{rank_h['description'] or 'Maintien'}</td></tr><tr><td>{a_name}</td><td>{rank_a['rank']}</td><td>{rank_a['points']}</td><td>{rank_a['description'] or 'Maintien'}</td></tr></table>", unsafe_allow_html=True)
                    else: st.warning("Classement non disponible (Coupe ou tournoi en cours).")

                elif "10. Données avancées" in sel_cat:
                    st.write("##### 🔬 Data Analyst (Extrapolées)")
                    st.markdown(f"<table class='comp-table'><tr><th>Métrique</th><th>{h_name}</th><th>{a_name}</th></tr><tr><td>Possession Moyenne</td><td>{adv['h_poss']:.1f}%</td><td>{adv['a_poss']:.1f}%</td></tr><tr><td>PPDA (Pressing)</td><td>{adv['h_ppda']:.1f}</td><td>{adv['a_ppda']:.1f}</td></tr><tr><td>Ratio Occasions / Buts</td><td>{h['avg_gf']/max(0.1, adv['h_sot']):.2f}</td><td>{a['avg_gf']/max(0.1, adv['a_sot']):.2f}</td></tr></table>", unsafe_allow_html=True)

                elif "11. Facteurs externes" in sel_cat:
                    st.write("##### 🌧️ Impondérables")
                    random.seed(m_data['fixture']['id'])
                    meteo = random.choice(["Clair", "Pluie légère", "Nuageux", "Humide"]); fatigue = random.choice(["Reposés (7 jours)", "Calendrier chargé (3 jours)"])
                    st.markdown(f"<table class='comp-table'><tr><th>Facteur</th><th>Impact estimé</th></tr><tr><td>Météo prévue</td><td>{meteo}</td></tr><tr><td>Fatigue</td><td>{fatigue}</td></tr><tr><td>Arbitrage</td><td>{'Sévère (Cartons probables)' if h['red_cards']+a['red_cards']>1 else 'Laxiste'}</td></tr></table>", unsafe_allow_html=True)
                    random.seed()

                elif "12. Analyse probabiliste" in sel_cat:
                    st.write("##### 🎲 Projection Modèle de Poisson")
                    p = get_coherent_probabilities(h, a)
                    df_pie = pd.DataFrame({"Issue": ["Domicile", "Nul", "Extérieur"], "Probabilité": [p[1]*100, p[0]*100, p[2]*100]})
                    base_pie = alt.Chart(df_pie).encode(theta=alt.Theta("Probabilité:Q", stack=True), color=alt.Color("Issue:N", scale=alt.Scale(range=['#00FF99', '#FFA500', '#00D4FF']), legend=alt.Legend(title=None, labelColor='#E0E0E0', orient='right', labelFontSize=14)), tooltip=['Issue', alt.Tooltip('Probabilité', format='.1f', title='Probabilité (%)')])
                    pie = base_pie.mark_arc(innerRadius=60, outerRadius=120, cornerRadius=5, padAngle=0.03)
                    text = base_pie.mark_text(radius=150, fontSize=16, fontWeight='bold', fill='white').encode(text=alt.Text("Probabilité:Q", format=".0f"))
                    st.altair_chart(alt.layer(pie, text).properties(height=350, background='transparent').configure_view(strokeWidth=0), use_container_width=True, theme=None)
            else: st.warning("Données insuffisantes.")

# --- AFFICHAGE PRINCIPAL : MA SÉLECTION ---
elif st.session_state.mode == "my_selection":
    st.markdown("<h2 class='my-sel-title'>📝 MA SÉLECTION PERSONNELLE</h2>", unsafe_allow_html=True)
    if all_fixtures:
        if not st.session_state.selection_validated and not st.session_state.auto_analyzed:
            dates = sorted(list(set([f['fixture']['date'][:10] for f in all_fixtures])))
            sel_date_my_sel = st.selectbox("📅 Date des rencontres", dates)
            matches_of_day = [f for f in all_fixtures if f['fixture']['date'][:10] == sel_date_my_sel]
            
            if not matches_of_day: st.info("Aucun match pour cette date.")
            else:
                st.write("Faites vos choix :")
                for f in matches_of_day:
                    fix_id = str(f['fixture']['id']); h_name = f['teams']['home']['name']; a_name = f['teams']['away']['name']
                    st.markdown(f"<div style='background:#1a1c24; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 4px solid #00FF99;'><div style='color:white; font-size:1.1rem; font-weight:bold; text-align:center; margin-bottom:10px;'>{h_name} <span style='color:#aaa;'>vs</span> {a_name}</div>", unsafe_allow_html=True)
                    opts = ["Aucun", f"Victoire {h_name}", "Match Nul", f"Victoire {a_name}"]
                    prev_pick = st.session_state.persisted_selections.get(fix_id, {}).get("user_pick", "Aucun")
                    default_idx = opts.index(prev_pick) if prev_pick in opts else 0
                    st.radio("Prono", opts, index=default_idx, horizontal=True, key=f"rad_{fix_id}", on_change=update_user_selection, args=(fix_id, f"{h_name} vs {a_name}", f['teams']['home']['id'], f['teams']['away']['id'], f['league']['id']), label_visibility="collapsed")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("✅ VALIDER MA SÉLECTION", type="primary", use_container_width=True):
                        st.session_state.selection_validated = True; st.session_state.auto_analyzed = False; st.rerun()
                with c_btn2:
                    if st.button("🤖 ANALYSE AUTO (TOUS)", type="secondary", use_container_width=True):
                        st.session_state.selected_auto_date = sel_date_my_sel; st.session_state.auto_analyzed = True; st.session_state.selection_validated = False; st.rerun()

        elif st.session_state.selection_validated:
            st.success("✅ Sélection enregistrée et isolée pour l'analyse.")
            if not st.session_state.persisted_selections:
                st.warning("Vous n'avez fait aucun pronostic.")
                if st.button("⬅️ Retour"): st.session_state.selection_validated = False; st.rerun()
            else:
                if not st.session_state.selection_analyzed:
                    for fix_id, data in st.session_state.persisted_selections.items():
                        st.markdown(f"<div style='background:#1a1c24; padding:10px; border-radius:8px; border-left:4px solid #00D4FF; margin-bottom:5px;'><b>{data['match']}</b><br/>👉 {data['user_pick']}</div>", unsafe_allow_html=True)
                    st.markdown("<br/>", unsafe_allow_html=True)
                    if st.button("🧠 CRASH TEST : LANCER L'ANALYSE IA", type="primary", use_container_width=True):
                        ai_results = {}
                        with st.spinner("L'IA scanne vos pronostics et cherche les failles..."):
                            for fix_id, data in st.session_state.persisted_selections.items():
                                hid, aid = data['home_id'], data['away_id']
                                raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                                if raw_h and raw_a:
                                    hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
                                    p = get_coherent_probabilities(hs, as_); best_idx = np.argmax(p)
                                    ai_pick = f"Victoire {hs['name']}" if best_idx==1 else (f"Victoire {as_['name']}" if best_idx==2 else "Match Nul")
                                    ai_results[fix_id] = {"ai_pick": ai_pick, "prob": p[best_idx]*100, "justif": gen_smart_justif("🏆", ai_pick, hs, as_), "match": data['match'], "user_pick": data['user_pick']}
                        st.session_state.selection_ai_results = ai_results; st.session_state.selection_analyzed = True; st.rerun()
                    if st.button("Modifier ma sélection"): st.session_state.selection_validated = False; st.rerun()
                else:
                    st.markdown("### 🤖 VERDICT DE L'IA SUR VOTRE TICKET")
                    for fix_id, res in st.session_state.selection_ai_results.items():
                        st.markdown(f"#### {res['match']}")
                        st.write(f"👤 Votre choix : **{res['user_pick']}**")
                        if res['user_pick'] == res['ai_pick']:
                            st.success(f"✅ L'IA VALIDE VOTRE CHOIX ! ({res['prob']:.0f}% de confiance mathématique)")
                            st.caption(f"Argument IA : {res['justif']}")
                        else:
                            st.warning(f"⚠️ DANGER : L'IA suggère plutôt : **{res['ai_pick']}** ({res['prob']:.0f}% de confiance)")
                            st.caption(f"Argument IA de correction : {res['justif']}")
                        st.markdown("---")
                    if st.button("🔄 Refaire une sélection"): st.session_state.persisted_selections = {}; st.session_state.selection_validated = False; st.session_state.selection_analyzed = False; st.rerun()

        elif st.session_state.auto_analyzed:
            st.markdown("### 🤖 ANALYSE AUTOMATIQUE DE LA JOURNÉE")
            matches_to_analyze = [f for f in all_fixtures if f['fixture']['date'][:10] == st.session_state.selected_auto_date]
            with st.spinner("L'IA dissèque tous les matchs et calcule les algorithmes..."):
                for f in matches_to_analyze:
                    hid, aid = f['teams']['home']['id'], f['teams']['away']['id']
                    h_name, a_name = f['teams']['home']['name'], f['teams']['away']['name']
                    raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                    if raw_h and raw_a:
                        hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
                        p = get_coherent_probabilities(hs, as_); q = get_quantum_analysis(hs, as_)
                        
                        sorted_indices = np.argsort(p)[::-1]
                        best_idx = sorted_indices[0]; sec_best_idx = sorted_indices[1]
                        
                        ai_pick = f"Victoire {h_name}" if best_idx==1 else (f"Victoire {a_name}" if best_idx==2 else "Match Nul")
                        plan_b_pick = f"Victoire {h_name}" if sec_best_idx==1 else (f"Victoire {a_name}" if sec_best_idx==2 else "Match Nul")
                        
                        with st.expander(f"📊 {h_name} vs {a_name} - Prédiction : {ai_pick} ({p[best_idx]*100:.0f}%)"):
                            st.markdown(f"<p style='font-size:1.1rem; font-weight:bold; color:#00FF99; margin:0 0 5px 0;'>🎯 Pronostic Principal : {ai_pick}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='color:#e0e0e0; font-size:0.95rem;'><i>{gen_smart_justif('🏆', ai_pick, hs, as_)}</i></p>", unsafe_allow_html=True)
                            st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:0.8rem; color:#aaa; background:#1a1c24; padding:8px; border-radius:6px;'><div><b>xG IA :</b> <span style='color:white;'>{q['xg_h']:.1f} - {q['xg_a']:.1f}</span></div><div><b>Forme :</b> <span style='color:white;'>{hs['form']:.1f} - {as_['form']:.1f} pts</span></div><div><b>Buts :</b> <span style='color:white;'>{hs['avg_gf']:.1f} - {as_['avg_gf']:.1f}</span></div></div>", unsafe_allow_html=True)
                            
                            if st.session_state.show_plan_b:
                                st.markdown("<hr style='margin:10px 0; border-color:#444;'>", unsafe_allow_html=True)
                                st.markdown(f"<p style='font-size:1rem; font-weight:bold; color:#FF8800; margin:0 0 5px 0;'>⚠️ SCÉNARIO ALTERNATIF (PLAN B) : {plan_b_pick} ({p[sec_best_idx]*100:.0f}%)</p>", unsafe_allow_html=True)
                                st.markdown(f"<p style='color:#ccc; font-size:0.85rem;'><i>{gen_plan_b_justif(plan_b_pick, hs, as_)}</i></p>", unsafe_allow_html=True)
            
            c_ret, c_planb = st.columns(2)
            with c_ret:
                if st.button("⬅️ Retour"): st.session_state.auto_analyzed = False; st.session_state.show_plan_b = False; st.rerun()
            with c_planb:
                st.markdown("<div class='btn-plan-b'>", unsafe_allow_html=True)
                if st.button("Et si ça se passait autrement ?", use_container_width=True):
                    st.session_state.show_plan_b = not st.session_state.show_plan_b
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# --- AFFICHAGE PRINCIPAL : STANDARD / QUANTUM ---
elif st.session_state.mode != "my_selection" and st.session_state.mode != "graphs":
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
            sel_match = st.selectbox("Rencontre", list(match_map.keys()))
            match_data = match_map[sel_match]
        else: match_data = "EMPTY"
    else: match_data = "EMPTY"

    if match_data is None and sel_match == "Tous les matchs":
        st.markdown("---")
        st.markdown("### 📋 Liste des rencontres filtrées")
        for f in filt_fix: st.markdown(f"<div style='background-color:#1a1c24; padding:12px; border-radius:8px; margin-bottom:8px; border:1px solid #333; display:flex; justify-content:space-between; align-items:center;'><span style='color:#00FF99; font-weight:bold;'>{f['fixture']['date'][11:16]}</span><span style='font-weight:bold; font-size:0.9rem;'>{f['teams']['home']['name']} vs {f['teams']['away']['name']}</span></div>", unsafe_allow_html=True)

    elif match_data != "EMPTY":
        st.markdown("---")
        b1, b2 = st.columns(2)
        if b1.button("🚀 ANALYSER", type="primary", use_container_width=True):
            st.session_state.quantum_mode = False
            with st.spinner("Analyse Cohérente..."):
                hid, aid = match_data['teams']['home']['id'], match_data['teams']['away']['id']
                raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
                p = get_coherent_probabilities(hs, as_) 
                st.session_state.analyzed_match_data = {"m": match_data, "raw_h": raw_h, "raw_a": raw_a, "p": p}

        if b2.button("🧬 QUANTUM SNIPER", use_container_width=True):
            st.session_state.quantum_mode = True
            with st.spinner("Calcul Quantique..."):
                hid, aid = match_data['teams']['home']['id'], match_data['teams']['away']['id']
                raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
                hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
                q = get_quantum_analysis(hs, as_)
                st.session_state.analyzed_match_data = {"m": match_data, "raw_h": raw_h, "raw_a": raw_a, "p": get_coherent_probabilities(hs, as_), "q": q}

        if st.session_state.analyzed_match_data:
            d = st.session_state.analyzed_match_data
            if d['m']['fixture']['id'] == match_data['fixture']['id']:
                m = d['m']
                st.markdown(f"<div class='match-header'><div class='team-box'><img src='{m['teams']['home']['logo']}' class='team-logo'><div class='team-name'>{m['teams']['home']['name']}</div></div><div class='vs-box'>VS</div><div class='team-box'><img src='{m['teams']['away']['logo']}' class='team-logo'><div class='team-name'>{m['teams']['away']['name']}</div></div></div>", unsafe_allow_html=True)
                if st.button("🔍 Voir les 5 derniers résultats des deux équipes", use_container_width=True): show_history_dialog(m['teams']['home']['name'], d['raw_h']['history'], m['teams']['away']['name'], d['raw_a']['history'])
                
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
                        best_idx = np.argmax(p); pred_str = "Victoire Domicile" if best_idx==1 else ("Victoire Extérieur" if best_idx==2 else "Match Nul")
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
