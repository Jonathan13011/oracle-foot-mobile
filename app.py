import streamlit as st
import pandas as pd
import requests
import joblib
import numpy as np
import statistics
import altair as alt
import random
from collections import Counter
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ULTIME & DESIGN IPHONE PERFECT V12 ---
st.set_page_config(page_title="Oracle Mobile V12", layout="wide", page_icon="📱")

st.markdown("""
<style>
    /* FOND GÉNÉRAL */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* ==============================================
       CSS SPÉCIAL IPHONE (Mobile Responsive Fixes) 
       ============================================== */
    @media only screen and (max-width: 640px) {
        
        /* --- FIX 1 : FORCER L'ALIGNEMENT HORIZONTAL --- */
        /* C'est le hack crucial pour que DOM/NUL/EXT restent sur la même ligne */
        div[data-testid="column"] {
            flex: 1 1 0% !important; /* Force les colonnes à partager l'espace équitablement */
            min-width: 0 !important; /* Autorise le rétrécissement des éléments */
        }
        /* Empêcher le conteneur de passer à la ligne */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
        }

        /* --- FIX 2 : AJUSTER LES TAILLES DE POLICE SUR MOBILE --- */
        /* Réduire les gros chiffres des metrics pour qu'ils tiennent à 3 */
        div[data-testid="stMetricValue"] { font-size: 1.1rem !important; }
        div[data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
        
        /* Réduire un peu les titres */
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1rem !important; }
        
        /* Réduire les marges globales */
        .block-container { padding-top: 1rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    }
    /* ============================================== */


    /* --- FIX 3 : BOUTON AMPOULE (POPOVER) --- */
    /* Le transforme en simple icône cliquable sans cadre */
    div[data-testid="stPopover"] > button {
        border: none !important;
        background: transparent !important;
        padding: 0px 5px !important; /* Petit padding latéral pour le doigt */
        color: #00FF99 !important; /* Couleur néon */
        font-size: 1.3rem !important;
        line-height: 1 !important;
        height: auto !important; min-height: 0 !important;
        box-shadow: none !important;
    }
    /* Contenu de la fenêtre popover */
    div[data-testid="stPopoverBody"] { background-color: #1a1c24; color: white; border: 1px solid #00FF99; }


    /* DESIGN DES METRICS (GLOBAL) */
    div[data-testid="stMetric"] {
        background-color: #1a1c24 !important; border: 1px solid #363b4e;
        padding: 10px; border-radius: 10px; text-align: center;
    }
    div[data-testid="stMetricLabel"] { color: #AAAAAA !important; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 800; }

    /* BOUTONS GÉNÉRAUX */
    .stButton > button {
        background-color: #262935; color: white !important; 
        border: 1px solid #444; border-radius: 10px; padding: 0.5rem;
    }
    div[data-testid="stSidebarUserContent"] .stButton > button {
        background: linear-gradient(45deg, #FF4B4B, #FF0000); border: none; font-weight: bold;
    }
    
    /* STYLE DU TICKET */
    .ticket-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; }
    .ticket-bet { font-size: 0.95rem; }
    .ticket-match-title { font-weight: bold; color: #00FF99; margin-top: 15px; border-bottom: 1px solid #333; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

API_KEY = "4d3c1dbf76600a937722ff6425d450ee"
HEADERS = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
LEAGUE_IDS = [2, 39, 61, 140, 135, 78, 94, 45, 203, 307, 143, 323]

if 'analyzed_match_data' not in st.session_state: st.session_state.analyzed_match_data = None
if 'ticket_data' not in st.session_state: st.session_state.ticket_data = None

try: model = joblib.load('oracle_brain.pkl'); MODEL_LOADED = True
except: model = None; MODEL_LOADED = False

# --- MOTEUR ---
@st.cache_data(ttl=3600)
def get_upcoming_matches():
    today = datetime.now().strftime("%Y-%m-%d"); end = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"); fixtures = []
    for l in LEAGUE_IDS:
        try:
            r = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"league": l, "season": "2025", "from": today, "to": end, "timezone": "Europe/Paris"}).json()
            if 'response' in r: fixtures.extend(r['response'])
        except: pass
    return fixtures

@st.cache_data(ttl=3600)
def get_deep_stats(tid):
    d = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"team": str(tid), "last": "10", "status": "FT"}).json().get('response', [])
    if not d: return None
    gs, gc, ht, btts, pts, cs, dr, res = [], [], 0, 0, 0, 0, 0, []
    for m in d:
        h = m['teams']['home']['id'] == tid
        gf, ga = (m['goals']['home'] if h else m['goals']['away']) or 0, (m['goals']['away'] if h else m['goals']['home']) or 0
        gs.append(gf); gc.append(ga)
        if gf>0 and ga>0: btts+=1
        if ga==0: cs+=1
        if gf>ga: pts+=3; res.append("✅")
        elif gf==ga: pts+=1; res.append("➖"); dr+=1
        else: res.append("❌")
    try: vol = statistics.stdev(gs)
    except: vol = 0
    return {"name": d[0]['teams']['home']['name'] if d[0]['teams']['home']['id'] == tid else d[0]['teams']['away']['name'], "form": pts/len(d), "avg_gf": sum(gs)/len(d), "avg_ga": sum(gc)/len(d), "cs_rate": cs/len(d)*100, "btts_rate": btts/len(d)*100, "dr_rate": dr/len(d)*100, "vol": vol, "streak": "".join(res[:5])}

# --- INTELLIGENCE ---
def gen_justif(type, val, h, a):
    r = []
    if type=="🏆 Résultat":
        if "Nul" in val: r.append(f"Forte tendance au nul ({max(h['dr_rate'], a['dr_rate'])}%).")
        elif "Domicile" in val: r.append(f"{h['name']} est solide à domicile ({h['streak']}).")
        else: r.append(f"{a['name']} est performant à l'extérieur.")
    elif type=="⚽ Buts":
        xg = h['avg_gf']+a['avg_gf']
        if "+2.5" in val: r.append(f"Match ouvert attendu (Moy. cumulée {xg:.1f}).")
        else: r.append(f"Défenses solides (Moy. cumulée {xg:.1f}).")
    elif type=="🥅 BTTS":
        if "OUI" in val: r.append(f"Les deux marquent souvent ({(h['btts_rate']+a['btts_rate'])/2:.0f}%).")
        else: r.append("Probabilité de Clean Sheet élevée.")
    return random.choice(r) if r else "Analyse statistique favorable."

def sim_score(h, a):
    sims = [f"{np.random.poisson((h['avg_gf']+a['avg_ga'])/2)}-{np.random.poisson((a['avg_gf']+h['avg_ga'])/2)}" for _ in range(5000)]
    return Counter(sims).most_common(3)

def analyze_probs(h, a, p):
    preds = []
    win_p = max(p)
    if p[0]>0.28 and abs(p[1]-p[2])<0.15: preds.append({"t": "🏆 Résultat", "v": "Match Nul", "c": p[0]+0.35, "cat": "DRAW"})
    elif win_p>0.55: preds.append({"t": "🏆 Résultat", "v": f"Victoire {h['name']}" if p[1]==win_p else f"Victoire {a['name']}", "c": win_p, "cat": "WIN"})
    
    avg_t = (h['avg_gf']+a['avg_gf']+h['avg_ga']+a['avg_ga'])/2
    if avg_t<2.2: preds.append({"t": "⚽ Buts", "v": "-2.5 Buts", "c": min(0.85, 2/(avg_t+0.1)), "cat": "UNDER"})
    elif avg_t>2.8: preds.append({"t": "⚽ Buts", "v": "+2.5 Buts", "c": min(0.9, avg_t/3.5), "cat": "OVER"})
    
    btts = (h['btts_rate']+a['btts_rate'])/2
    if btts>60: preds.append({"t": "🥅 BTTS", "v": "Oui", "c": btts/100, "cat": "BTTS"})
    elif btts<40: preds.append({"t": "🥅 BTTS", "v": "Non", "c": 1-(btts/100), "cat": "BTTS_NO"})

    for pr in preds: pr['j'] = gen_justif(pr['t'], pr['v'], h, a)
    return preds

def gen_ticket(fix):
    pools = {"WIN":[], "DRAW":[], "OVER":[], "UNDER":[], "BTTS":[], "BTTS_NO":[]}
    bar = st.sidebar.progress(0, text="Scan V12...")
    limit = min(len(fix), 30); count=0
    for f in fix:
        if count>=limit: break
        hid, aid, lid = f['teams']['home']['id'], f['teams']['away']['id'], f['league']['id']
        hs, as_ = get_deep_stats(hid), get_deep_stats(aid)
        if hs and as_ and model:
            vec = np.array([[lid, hs['form'], hs['avg_gf'], hs['avg_ga'], as_['form'], as_['avg_gf'], as_['avg_ga']]])
            probs = model.predict_proba(vec)[0]
            preds = analyze_probs(hs, as_, probs)
            for p in preds:
                if p['c']>0.5: pools[p['cat']].append({"m": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}", "b": p, "h": hs, "a": as_})
        count+=1; bar.progress(count/limit)
    bar.empty()
    
    final = []
    cats = ["DRAW", "UNDER", "BTTS", "WIN", "OVER", "BTTS_NO"]
    for c in cats:
        if pools[c]: pools[c].sort(key=lambda x: x['b']['c'], reverse=True); final.append(pools[c].pop(0))
    rem = [item for c in cats for item in pools[c]]; random.shuffle(rem); rem.sort(key=lambda x: x['b']['c'], reverse=True)
    if len(final)<10: final.extend(rem[:10-len(final)])
    
    grouped = {}
    for item in final:
        if item['m'] not in grouped: grouped[item['m']] = []
        if len(grouped[item['m']])<3: grouped[item['m']].append(item)
    return grouped

# --- INTERFACE V12 ---
st.title("📱 ORACLE V12")

with st.sidebar:
    st.header("🎟️ TICKET")
    fix = get_upcoming_matches()
    if st.button("🎰 GÉNÉRER"):
        if not fix: st.error("Pas de matchs.")
        else:
            with st.spinner("Analyse..."): st.session_state.ticket_data = gen_ticket(fix)
    if st.session_state.ticket_data:
        st.success("✅ PRÊT !")
        idx = 1
        for m_name, items in st.session_state.ticket_data.items():
            st.markdown(f"<div class='ticket-match-title'>{idx}. {m_name}</div>", unsafe_allow_html=True)
            for i in items:
                b = i['b']
                icon = "⚖️" if "Nul" in b['v'] else ("🔒" if "-2.5" in b['v'] else ("🥅" if "BTTS" in b['v'] else "🔸"))
                # Utilisation de conteneurs flex pour l'alignement parfait icone/texte/ampoule
                st.markdown(f"""
                <div class="ticket-row">
                    <span class="ticket-bet">{icon} {b['t']} : <b>{b['v']}</b></span>
                </div>
                """, unsafe_allow_html=True)
                # L'ampoule doit être en dehors du markdown HTML pour fonctionner
                with st.popover("💡"): st.info(b['j'])
            idx+=1

    st.header("🔍 Match")
    if fix:
        fix.sort(key=lambda x: x['fixture']['date'])
        m_map = {f"[{f['league']['name']}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fix}
        sel = st.selectbox("Rencontre", list(m_map.keys()))
        m_data = m_map[sel]

if st.button("🚀 ANALYSER", type="primary"):
    with st.spinner("Chargement..."):
        hid, aid, lid = m_data['teams']['home']['id'], m_data['teams']['away']['id'], m_data['league']['id']
        hs, as_ = get_deep_stats(hid), get_deep_stats(aid)
        if hs and as_ and model:
            vec = np.array([[lid, hs['form'], hs['avg_gf'], hs['avg_ga'], as_['form'], as_['avg_gf'], as_['avg_ga']]])
            p = model.predict_proba(vec)[0]
            s = sim_score(hs, as_)
            st.session_state.analyzed_match_data = {"m": m_data, "h": hs, "a": as_, "p": p, "s": s}

if st.session_state.analyzed_match_data:
    d = st.session_state.analyzed_match_data
    h, a, p, m, s = d['h'], d['a'], d['p'], d['m'], d['s']
    
    # --- HEADER FLEXBOX HORIZONTAL (FIX PHOTO 1) ---
    # On remplace les st.columns par du HTML Flexbox pur pour garantir l'alignement sur mobile
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-around; margin-bottom: 20px; background: #1a1c24; padding: 15px; border-radius: 15px;">
        <div style="text-align: center; flex: 1;">
            <img src="{m['teams']['home']['logo']}" width="60" style="margin-bottom: 5px;">
Écrire à 'Jonathan Turcan
