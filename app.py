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

# --- 1. CONFIGURATION V20 (QUANTUM EDITION) ---
st.set_page_config(page_title="Oracle V20", layout="wide", page_icon="🧬")

st.markdown("""
<style>
    /* FOND GÉNÉRAL & TEXTE */
    .stApp { background-color: #0E1117; color: #FFFFFF !important; }
    p, h1, h2, h3, div, span, li, label, h4, h5, h6 { color: #FFFFFF !important; }

    /* SIDEBAR & BOUTONS */
    [data-testid="stSidebar"] { background-color: #0E1117 !important; border-right: 1px solid #333 !important; }
    [data-testid="stSidebarCollapsedControl"] { color: #FFFFFF !important; background-color: #1a1c24 !important; border: 1px solid #333; }
    [data-testid="stSidebarUserContent"] h1, [data-testid="stSidebarUserContent"] h2 { color: #00FF99 !important; }

    /* BOUTON QUANTUM (NOUVEAU) */
    .quantum-btn {
        border: 2px solid #00D4FF !important;
        background: linear-gradient(90deg, #00D4FF, #0055FF) !important;
        color: white !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4) !important;
    }
    
    /* MOBILE FIXES */
    @media only screen and (max-width: 640px) {
        .block-container { padding-top: 1rem !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; }
        div[data-testid="column"] { padding: 0 !important; }
    }

    /* HEADER MATCH */
    .match-header {
        display: flex; flex-direction: row; align-items: center; justify-content: space-between; 
        background: #1a1c24; padding: 10px 5px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #333;
    }
    .team-box { text-align: center; width: 40%; display: flex; flex-direction: column; align-items: center; }
    .team-logo { width: 45px; height: 45px; object-fit: contain; margin-bottom: 3px; }
    .team-name { font-size: 0.75rem; font-weight: bold; line-height: 1.1; color: white !important; }
    .vs-box { width: 20%; text-align: center; color: #00FF99 !important; font-weight: 900; font-size: 1.2rem; }

    /* PROBS CONTAINER */
    .probs-container { display: flex; flex-direction: row; justify-content: space-between; gap: 5px; margin-bottom: 20px; width: 100%; }
    .prob-box { background-color: #1a1c24; border: 1px solid #363b4e; border-radius: 8px; width: 32%; padding: 10px 2px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }
    .prob-label { font-size: 0.6rem; color: #AAAAAA !important; font-weight: bold; text-transform: uppercase; }
    .prob-value { font-size: 1.2rem; font-weight: 900; color: #FFFFFF !important; line-height: 1.2; }
    .info-icon { position: absolute; top: 1px; right: 2px; font-size: 0.8rem; cursor: pointer; color: #00FF99 !important; }

    /* QUANTUM STATS STYLES */
    .q-stat-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #222; font-size: 0.9rem; }
    .q-label { color: #00D4FF !important; font-weight: bold; }
    .q-val { color: white; font-weight: bold; }
    .fair-odd { color: #FFA500 !important; font-weight: 900; font-size: 1.1rem; }

    /* GENERAL */
    div[data-baseweb="select"] > div, div[data-baseweb="popover"] { background-color: #1a1c24 !important; color: white !important; border-color: #333 !important; }
    .stButton > button { background-color: #262935; color: white !important; border: 1px solid #444; border-radius: 8px; width: 100%; }
    div[data-testid="stSidebarUserContent"] .stButton > button { border: none; font-weight: bold; }
    .ticket-match-title { font-weight: bold; color: #00FF99 !important; margin-top: 10px; border-bottom: 1px solid #333; }
    .ticket-row { display: flex; justify-content: space-between; align-items: center; }
</style>
""", unsafe_allow_html=True)

API_KEY = "4d3c1dbf76600a937722ff6425d450ee"
HEADERS = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
LEAGUE_IDS = [2, 39, 61, 140, 135, 78, 94, 45, 203, 307, 143, 323]

# Session States
if 'analyzed_match_data' not in st.session_state: st.session_state.analyzed_match_data = None
if 'ticket_data' not in st.session_state: st.session_state.ticket_data = None
if 'quantum_mode' not in st.session_state: st.session_state.quantum_mode = False

try: model = joblib.load('oracle_brain.pkl'); MODEL_LOADED = True
except: model = None; MODEL_LOADED = False

# --- MOTEUR DONNÉES ---
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
    return {"name": d[0]['teams']['home']['name'] if d[0]['teams']['home']['id'] == tid else d[0]['teams']['away']['name'], 
            "form": pts/len(d), "avg_gf": sum(gs)/len(d), "avg_ga": sum(gc)/len(d), 
            "cs_rate": cs/len(d)*100, "btts_rate": btts/len(d)*100, "draw_rate": dr/len(d)*100, 
            "vol": vol, "streak": "".join(res[:5]), "total_matches": len(d), "raw_gf": gs}

@st.cache_data(ttl=3600)
def get_h2h_stats(h_id, a_id):
    d = requests.get("https://v3.football.api-sports.io/fixtures/headtohead", headers=HEADERS, params={"h2h": f"{h_id}-{a_id}"}).json().get('response', [])
    if not d: return None
    goals = []
    for m in d:
        if m['fixture']['status']['short'] in ['FT', 'AET', 'PEN']:
            gh, ga = m['goals']['home'], m['goals']['away']
            if gh is not None and ga is not None: goals.append(gh+ga)
    if not goals: return None
    return {"vol": statistics.stdev(goals) if len(goals)>1 else 0, "matches": len(goals), "avg_goals": sum(goals)/len(goals)}

# --- INTELLIGENCE V20 (QUANTUM ENGINE) ---
def calculate_poisson_probs(avg_h, avg_a):
    # Calcul des probabilités exactes avec Poisson (0-0, 1-0, etc.)
    probs = {}
    for i in range(6):
        for j in range(6):
            p = (math.exp(-avg_h) * (avg_h**i) / math.factorial(i)) * \
                (math.exp(-avg_a) * (avg_a**j) / math.factorial(j))
            probs[f"{i}-{j}"] = p
    
    win_h = sum([p for s, p in probs.items() if int(s[0]) > int(s[2])])
    draw = sum([p for s, p in probs.items() if int(s[0]) == int(s[2])])
    win_a = sum([p for s, p in probs.items() if int(s[0]) < int(s[2])])
    return win_h, draw, win_a, probs

def get_quantum_analysis(h, a):
    # 1. Force Attaque/Défense (Modèle simplifié Dixon-Coles)
    # On suppose une moyenne ligue approx de 1.35 buts/match
    lg_avg = 1.35
    
    att_h = h['avg_gf'] / lg_avg
    def_h = h['avg_ga'] / lg_avg
    att_a = a['avg_gf'] / lg_avg
    def_a = a['avg_ga'] / lg_avg
    
    # 2. Expected Goals (xG) prédictifs
    xg_h = att_h * def_a * lg_avg * 1.15 # 1.15 = Avantage domicile
    xg_a = att_a * def_h * lg_avg
    
    # 3. Probabilités Poisson
    ph, pd, pa, score_matrix = calculate_poisson_probs(xg_h, xg_a)
    
    # 4. Fair Odds (Cotes Équitables)
    odd_h = 1/ph if ph > 0 else 99
    odd_d = 1/pd if pd > 0 else 99
    odd_a = 1/pa if pa > 0 else 99
    
    return {
        "xg_h": xg_h, "xg_a": xg_a,
        "prob_h": ph, "prob_d": pd, "prob_a": pa,
        "odd_h": odd_h, "odd_d": odd_d, "odd_a": odd_a,
        "att_power_h": att_h, "def_wall_h": 1/def_h if def_h > 0 else 2,
        "att_power_a": att_a, "def_wall_a": 1/def_a if def_a > 0 else 2
    }

# --- FONCTIONS STANDARDS ---
def gen_justif(type, val, h, a):
    r = []
    if type=="🏆 Résultat":
        if "Nul" in val: r.append(f"Tendance Nul ({max(h['draw_rate'], a['draw_rate'])}%).")
        elif "Domicile" in val: r.append(f"{h['name']} solide à domicile.")
        else: r.append(f"{a['name']} performant ext.")
    elif type=="⚽ Buts":
        xg = h['avg_gf']+a['avg_gf']
        if "+2.5" in val: r.append(f"Match ouvert (Moy {xg:.1f}).")
        else: r.append(f"Match fermé (Moy {xg:.1f}).")
    return random.choice(r) if r else "Stats favorables."

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
    
    for pr in preds: pr['j'] = gen_justif(pr['t'], pr['v'], h, a)
    return preds

def gen_ticket(fix):
    pools = {"WIN":[], "DRAW":[], "OVER":[], "UNDER":[], "BTTS":[], "BTTS_NO":[]}
    bar = st.sidebar.progress(0, text="Scan...")
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
    cats = ["DRAW", "UNDER", "BTTS", "WIN", "OVER"]
    for c in cats:
        if pools[c]: pools[c].sort(key=lambda x: x['b']['c'], reverse=True); final.append(pools[c].pop(0))
    rem = [item for c in cats for item in pools[c]]; random.shuffle(rem); rem.sort(key=lambda x: x['b']['c'], reverse=True)
    if len(final)<10: final.extend(rem[:10-len(final)])
    grouped = {}
    for item in final:
        if item['m'] not in grouped: grouped[item['m']] = []
        if len(grouped[item['m']])<3: grouped[item['m']].append(item)
    return grouped

# --- INTERFACE ---
st.title("📱 ORACLE V20")

with st.sidebar:
    st.header("🎟️ TICKET")
    fix = get_upcoming_matches()
    if st.button("🎰 GÉNÉRER", type="primary"):
        if not fix: st.error("Pas de matchs.")
        else:
            with st.spinner("Analyse..."): 
                st.session_state.ticket_data = gen_ticket(fix)
                st.session_state.quantum_mode = False # Reset quantum view

    if st.session_state.ticket_data and not st.session_state.quantum_mode:
        st.success("✅ PRÊT !")
        idx = 1
        for m_name, items in st.session_state.ticket_data.items():
            st.markdown(f"<div class='ticket-match-title'>{idx}. {m_name}</div>", unsafe_allow_html=True)
            for i in items:
                b = i['b']
                icon = "⚖️" if "Nul" in b['v'] else ("🔒" if "-2.5" in b['v'] else ("🥅" if "BTTS" in b['v'] else "🔸"))
                with st.container():
                    c1, c2 = st.columns([0.85, 0.15])
                    c1.markdown(f"{icon} {b['t']} : **{b['v']}**")
                    with c2.popover("💡"): st.info(b['j'])
            idx+=1

    st.header("🔍 MATCH")
    if fix:
        fix.sort(key=lambda x: x['fixture']['date'])
        m_map = {f"[{f['league']['name']}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fix}
        sel = st.selectbox("Rencontre", list(m_map.keys()))
        m_data = m_map[sel]

    # --- LE BOUTON QUANTUM SNIPER ---
    st.markdown("---")
    if st.button("🧬 QUANTUM SNIPER", key="btn_quantum"):
        st.session_state.quantum_mode = True
        st.session_state.ticket_data = None # Hide ticket
        
        with st.spinner("Calcul Quantique & xG..."):
            hid, aid, lid = m_data['teams']['home']['id'], m_data['teams']['away']['id'], m_data['league']['id']
            hs, as_ = get_deep_stats(hid), get_deep_stats(aid)
            
            # Calculs inédits
            q_data = get_quantum_analysis(hs, as_)
            st.session_state.analyzed_match_data = {"m": m_data, "h": hs, "a": as_, "q": q_data}

# --- AFFICHAGE PRINCIPAL ---

# 1. MODE STANDARD (BOUTON ANALYSER CLASSIQUE)
if st.button("🚀 ANALYSER", type="primary") and not st.session_state.quantum_mode:
    with st.spinner("Chargement..."):
        hid, aid, lid = m_data['teams']['home']['id'], m_data['teams']['away']['id'], m_data['league']['id']
        hs, as_ = get_deep_stats(hid), get_deep_stats(aid)
        if hs and as_ and model:
            vec = np.array([[lid, hs['form'], hs['avg_gf'], hs['avg_ga'], as_['form'], as_['avg_gf'], as_['avg_ga']]])
            p = model.predict_proba(vec)[0]
            s = sim_score(hs, as_) # Sim simple
            st.session_state.analyzed_match_data = {"m": m_data, "h": hs, "a": as_, "p": p, "s": s, "hid": hid, "aid": aid, "mode": "std"}
            st.session_state.quantum_mode = False

# LOGIQUE D'AFFICHAGE SELON LE MODE (Standard vs Quantum)
if st.session_state.analyzed_match_data:
    d = st.session_state.analyzed_match_data
    h, a, m = d['h'], d['a'], d['m']
    
    # Header Commun
    st.markdown(f"""
    <div class="match-header">
        <div class="team-box"><img src="{m['teams']['home']['logo']}" class="team-logo"><div class="team-name">{m['teams']['home']['name']}</div></div>
        <div class="vs-box">VS</div>
        <div class="team-box"><img src="{m['teams']['away']['logo']}" class="team-logo"><div class="team-name">{m['teams']['away']['name']}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # --- AFFICHAGE MODE QUANTUM (NOUVEAU) ---
    if st.session_state.quantum_mode and 'q' in d:
        q = d['q']
        st.markdown("### 🧬 ANALYSE QUANTIQUE AVANCÉE")
        
        # 1. Probas recalculées par Poisson (Plus précis)
        st.markdown(f"""
        <div class="probs-container">
            <div class="prob-box"><div class="prob-label">PROBA DOM</div><div class="prob-value" style="color:#00D4FF !important;">{q['prob_h']*100:.1f}%</div></div>
            <div class="prob-box"><div class="prob-label">PROBA NUL</div><div class="prob-value">{q['prob_d']*100:.1f}%</div></div>
            <div class="prob-box"><div class="prob-label">PROBA EXT</div><div class="prob-value" style="color:#00D4FF !important;">{q['prob_a']*100:.1f}%</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Les "Fair Odds" (Cote Réelle)
        st.info("ℹ️ **Cotes Réelles (Fair Odds)** : Si le bookmaker offre plus, c'est une Value Bet.")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**1:** <span class='fair-odd'>{q['odd_h']:.2f}</span>", unsafe_allow_html=True)
        c2.markdown(f"**N:** <span class='fair-odd'>{q['odd_d']:.2f}</span>", unsafe_allow_html=True)
        c3.markdown(f"**2:** <span class='fair-odd'>{q['odd_a']:.2f}</span>", unsafe_allow_html=True)
        
        # 3. xG Prédictifs
        st.write("---")
        st.write("#### 🎯 Performance Attendue (xG)")
        xg_col1, xg_col2 = st.columns(2)
        xg_col1.metric(f"xG {h['name']}", f"{q['xg_h']:.2f}")
        xg_col2.metric(f"xG {a['name']}", f"{q['xg_a']:.2f}")
        
        # 4. Indicateurs de Puissance
        st.write("#### ⚔️ Forces en présence")
        st.progress(q['att_power_h'] / (q['att_power_h'] + q['att_power_a']))
        st.caption(f"Puissance Offensive : {h['name']} (Gauche) vs {a['name']} (Droite)")
        
        st.progress(q['def_wall_h'] / (q['def_wall_h'] + q['def_wall_a']))
        st.caption(f"Solidité Défensive : {h['name']} (Gauche) vs {a['name']} (Droite)")

    # --- AFFICHAGE MODE STANDARD (ANCIEN MAIS OPTIMISÉ) ---
    elif 'p' in d:
        p, s, hid, aid = d['p'], d['s'], d['hid'], d['aid']
        
        st.markdown(f"""
        <div class="probs-container">
            <div class="prob-box"><div class="info-icon">💡</div><div class="prob-label">DOMICILE</div><div class="prob-value">{p[1]*100:.0f}%</div></div>
            <div class="prob-box"><div class="prob-label">NUL</div><div class="prob-value">{p[0]*100:.0f}%</div></div>
            <div class="prob-box"><div class="info-icon">💡</div><div class="prob-label">EXTÉRIEUR</div><div class="prob-value">{p[2]*100:.0f}%</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔎 Voir l'analyse"):
            st.info(f"**Domicile :** {gen_justif('🏆 Résultat', 'Domicile', h, a)}")
            st.info(f"**Extérieur :** {gen_justif('🏆 Résultat', 'Extérieur', h, a)}")
        
        st.progress(int(max(p)*100))
        
        # Graphique
        st.markdown("### 📊 Comparateur")
        opts = {"Puissance Offensive": ["Buts", h['avg_gf'], a['avg_gf'], ['#00FF99', '#00CCFF']], 
                "Solidité Défensive": ["Encaissés", h['avg_ga'], a['avg_ga'], ['#FF4B4B', '#FF8888']],
                "Volatilité": ["Chaos", h['vol'], a['vol'], ['#FFA500', '#FFD700']],
                "Forme": ["Points", h['form'], a['form'], ['#00FF99', '#00CCFF']]}
        sel_opt = st.selectbox("Critère", list(opts.keys()), key="graph_sel")
        dat = opts[sel_opt]
        df = pd.DataFrame({'Eq': [m['teams']['home']['name'], m['teams']['away']['name']], 'Val': [dat[1], dat[2]]})
        ch = alt.Chart(df).encode(x=alt.X('Val', axis=alt.Axis(grid=False, title=None)), y=alt.Y('Eq', axis=alt.Axis(title=None, labelColor='white', labelLimit=100)), color=alt.Color('Eq', legend=None, scale=alt.Scale(range=dat[3])))
        st.altair_chart(alt.layer(ch.mark_rule(size=3), ch.mark_circle(size=120)).properties(height=150, background='transparent').configure_view(stroke=None), use_container_width=True)
        
        # Tabs
        t1, t2, t3, t4 = st.tabs(["🔮 Score", "⚡ Stats", "🛑 Discipline", "💰 Conseil"])
        with t1:
            st.write("Simulations (Standard) :")
            c1, c2, c3 = st.columns(3)
            if len(s)>0: c1.metric("#1", s[0][0], f"{s[0][1]}x")
            if len(s)>1: c2.metric("#2", s[1][0], f"{s[1][1]}x")
            if len(s)>2: c3.metric("#3", s[2][0], f"{s[2][1]}x")
        with t2:
            def row(l, v1, v2, u=""): st.markdown(f"<div class='stat-row'><span class='stat-label'>{l}</span><span class='stat-val'>{v1}{u} vs {v2}{u}</span></div>", unsafe_allow_html=True)
            row("Moy. Buts", f"{h['avg_gf']:.2f}", f"{a['avg_gf']:.2f}")
            row("Moy. Encaissés", f"{h['avg_ga']:.2f}", f"{a['avg_ga']:.2f}")
            row("Clean Sheets", f"{h['cs_rate']:.0f}", f"{a['cs_rate']:.0f}", "%")
        with t3:
            filtre = st.radio("Filtre :", ["10 derniers", "5 derniers", "H2H"], horizontal=True)
            vh, va, msg = h['vol'], a['vol'], "10 derniers."
            if "5" in filtre: 
                try: vh = statistics.stdev(h['raw_gf'][:5]); va = statistics.stdev(a['raw_gf'][:5])
                except: pass
            elif "H2H" in filtre:
                h2h = get_h2h_stats(hid, aid)
                if h2h: vh=h2h['vol']; va=h2h['vol']; msg=f"Sur {h2h['matches']} matchs."
                else: msg="Pas d'historique."
            c_a, c_b = st.columns(2)
            c_a.write(f"Dom: **{'ÉLEVÉ' if vh>1.4 else 'Faible'}**"); c_b.write(f"Ext: **{'ÉLEVÉ' if va>1.4 else 'Faible'}**")
            st.caption(msg)
        with t4: st.success(f"Confiance: {max(p)*100:.0f}%")
