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

# --- 1. CONFIGURATION V24 (BOUTONS JUMEAUX) ---
st.set_page_config(page_title="Oracle V24", layout="wide", page_icon="📱")

st.markdown("""
<style>
    /* FOND GÉNÉRAL & TEXTE */
    .stApp { background-color: #0E1117; color: #FFFFFF !important; }
    p, h1, h2, h3, div, span, label, h4, h5, h6 { color: #FFFFFF !important; }

    /* ==============================================
       FIX CRITIQUE : LISTES DÉROULANTES (SELECTBOX)
       ============================================== */
    div[data-baseweb="select"] > div {
        background-color: #1a1c24 !important;
        color: white !important;
        border-color: #333 !important;
    }
    div[data-baseweb="select"] span { color: white !important; }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #1a1c24 !important;
        border: 1px solid #333 !important;
    }
    li[role="option"] {
        background-color: #1a1c24 !important;
        color: white !important;
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #00FF99 !important;
        color: black !important;
    }
    div[data-baseweb="select"] svg { fill: white !important; }
    /* ============================================== */

    /* SIDEBAR */
    [data-testid="stSidebar"] { background-color: #0E1117 !important; border-right: 1px solid #333 !important; }
    [data-testid="stSidebarCollapsedControl"] { color: #FFFFFF !important; background-color: #1a1c24 !important; border: 1px solid #333; }
    [data-testid="stSidebarUserContent"] h1, [data-testid="stSidebarUserContent"] h2 { color: #00FF99 !important; }

    /* BADGE QUANTUM (Une fois activé) */
    .quantum-btn {
        border: 2px solid #00D4FF; background: linear-gradient(90deg, #001133, #004488);
        color: #00D4FF; font-weight: 900; padding: 15px; text-align: center; border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3); margin-bottom: 20px;
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

    /* PROBS */
    .probs-container { display: flex; flex-direction: row; justify-content: space-between; gap: 5px; margin-bottom: 20px; width: 100%; }
    .prob-box { background-color: #1a1c24; border: 1px solid #363b4e; border-radius: 8px; width: 32%; padding: 10px 2px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }
    .prob-label { font-size: 0.6rem; color: #AAAAAA !important; font-weight: bold; text-transform: uppercase; }
    .prob-value { font-size: 1.2rem; font-weight: 900; color: #FFFFFF !important; line-height: 1.2; }
    .info-icon { position: absolute; top: 1px; right: 2px; font-size: 0.8rem; cursor: pointer; color: #00FF99 !important; }

    /* QUANTUM STATS */
    .q-box { background: #0b1016; border: 1px solid #00D4FF; border-radius: 8px; padding: 10px; margin-bottom: 10px; }
    .q-title { color: #00D4FF !important; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }

    /* GENERAL */
    .stButton > button { background-color: #262935; color: white !important; border: 1px solid #444; border-radius: 8px; width: 100%; }
    div[data-testid="stSidebarUserContent"] .stButton > button { border: none; font-weight: bold; }
    .ticket-match-title { font-weight: bold; color: #00FF99 !important; margin-top: 10px; border-bottom: 1px solid #333; }
    .stat-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #333; font-size: 0.85rem; }
    .stat-label { color: #aaa; } .stat-val { font-weight: bold; }
    
    /* MOBILE PADDING */
    @media only screen and (max-width: 640px) {
        .block-container { padding-top: 1rem !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

API_KEY = "4d3c1dbf76600a937722ff6425d450ee"
HEADERS = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
LEAGUE_IDS = [2, 39, 61, 140, 135, 78, 94, 45, 203, 307, 143, 323]

# STATES
if 'analyzed_match_data' not in st.session_state: st.session_state.analyzed_match_data = None
if 'ticket_data' not in st.session_state: st.session_state.ticket_data = None
if 'quantum_mode' not in st.session_state: st.session_state.quantum_mode = False

try: model = joblib.load('oracle_brain.pkl'); MODEL_LOADED = True
except: model = None; MODEL_LOADED = False

# --- MOTEUR DONNÉES ---
@st.cache_data(ttl=3600)
def get_upcoming_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d") 
    fixtures = []
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
    gs, gc, ht, btts, pts, cs, dr, res, ht_w = [], [], 0, 0, 0, 0, 0, [], 0
    for m in d:
        h = m['teams']['home']['id'] == tid
        gf, ga = (m['goals']['home'] if h else m['goals']['away']) or 0, (m['goals']['away'] if h else m['goals']['home']) or 0
        gs.append(gf); gc.append(ga)
        try:
            hf, ha = (m['score']['halftime']['home'] if h else m['score']['halftime']['away']) or 0, (m['score']['halftime']['away'] if h else m['score']['halftime']['home']) or 0
            if hf > ha: ht_w += 1
        except: pass
        if gf>0 and ga>0: btts+=1
        if ga==0: cs+=1
        if gf>ga: pts+=3; res.append("✅")
        elif gf==ga: pts+=1; res.append("➖"); dr+=1
        else: res.append("❌")
    try: vol = statistics.stdev(gs)
    except: vol = 0
    return {"name": d[0]['teams']['home']['name'] if d[0]['teams']['home']['id'] == tid else d[0]['teams']['away']['name'], 
            "form": pts/len(d), "avg_gf": sum(gs)/len(d), "avg_ga": sum(gc)/len(d), 
            "cs_rate": cs/len(d)*100, "btts_rate": btts/len(d)*100, "draw_rate": dr/len(d)*100, "ht_win_rate": ht_w/len(d)*100,
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

# --- ANALYSES ---
def sim_score(h, a):
    sims = []
    for _ in range(5000):
        lam_h = max(0.1, (h['avg_gf']+a['avg_ga'])/2)
        lam_a = max(0.1, (a['avg_gf']+h['avg_ga'])/2)
        sims.append(f"{np.random.poisson(lam_h)}-{np.random.poisson(lam_a)}")
    return Counter(sims).most_common(3)

def get_quantum_analysis(h, a):
    lg_avg = 1.35
    xg_h = (h['avg_gf'] / lg_avg) * (a['avg_ga'] / lg_avg) * lg_avg * 1.15
    xg_a = (a['avg_gf'] / lg_avg) * (h['avg_ga'] / lg_avg) * lg_avg
    best_score, best_prob, upset_prob, fav_prob = "0-0", 0, 0, 0
    for i in range(6):
        for j in range(6):
            p = (math.exp(-xg_h) * (xg_h**i) / math.factorial(i)) * (math.exp(-xg_a) * (xg_a**j) / math.factorial(j))
            if p > best_prob: best_prob = p; best_score = f"{i}-{j}"
            if xg_h > xg_a and j > i: upset_prob += p
            elif xg_a > xg_h and i > j: upset_prob += p
            if xg_h > xg_a and i > j: fav_prob += p
            elif xg_a > xg_h and j > i: fav_prob += p
    
    def calc_mom(streak):
        s=0; w=[5,4,3,2,1]
        for i, c in enumerate(streak): s += (3 if c=="✅" else (1 if c=="➖" else 0)) * w[i]
        return s/45*100
    
    mom_h = calc_mom(h['streak']); mom_a = calc_mom(a['streak'])
    ht_pred = "1/N (MT)" if h['ht_win_rate'] > 45 else ("N/2 (MT)" if a['ht_win_rate'] > 45 else "Nul MT")
    alpha = min(99, (fav_prob * 100) + (abs(mom_h - mom_a) * 0.2))
    return {"sniper_score": best_score, "sniper_conf": best_prob*100, "momentum_h": mom_h, "momentum_a": mom_a, "upset_risk": upset_prob*100, "ht_pred": ht_pred, "alpha_index": alpha, "xg_h": xg_h, "xg_a": xg_a}

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

# --- INTERFACE & LAYOUT PRINCIPAL ---
st.title("📱 ORACLE V24")

# Récupération de TOUS les matchs (48h)
all_fixtures = get_upcoming_matches()

# --- SÉLECTION SUR LA PAGE PRINCIPALE (FILTRES + SELECTBOX) ---
if all_fixtures:
    all_fixtures.sort(key=lambda x: x['fixture']['date'])
    competitions = sorted(list(set([f['league']['name'] for f in all_fixtures])))
    dates = sorted(list(set([f['fixture']['date'][:10] for f in all_fixtures]))) # YYYY-MM-DD
    
    st.markdown("### 📅 SÉLECTION DU MATCH")
    c_filt1, c_filt2 = st.columns(2)
    selected_league = c_filt1.selectbox("Filtrer par Compétition", ["Toutes"] + competitions)
    selected_date = c_filt2.selectbox("Filtrer par Date", ["Toutes"] + dates)
    
    filtered_fixtures = all_fixtures
    if selected_league != "Toutes":
        filtered_fixtures = [f for f in filtered_fixtures if f['league']['name'] == selected_league]
    if selected_date != "Toutes":
        filtered_fixtures = [f for f in filtered_fixtures if f['fixture']['date'][:10] == selected_date]
        
    if not filtered_fixtures:
        st.warning("Aucun match ne correspond aux filtres.")
        match_data = None
    else:
        match_map = {f"[{f['fixture']['date'][11:16]}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in filtered_fixtures}
        selected_label = st.selectbox("Choisir une rencontre", list(match_map.keys()))
        match_data = match_map[selected_label]
else:
    st.error("Aucun match disponible pour les 48h prochaines heures.")
    match_data = None

# --- SIDEBAR (TICKET SEULEMENT) ---
with st.sidebar:
    st.header("🎟️ TICKET")
    if st.button("🎰 GÉNÉRER", type="primary"):
        if not all_fixtures: st.error("Pas de matchs.")
        else:
            with st.spinner("Analyse..."): 
                st.session_state.ticket_data = gen_ticket(all_fixtures)
                st.session_state.quantum_mode = False

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

# --- AFFICHAGE PRINCIPAL ---

if match_data:
    st.markdown("---")
    
    # --- LES DEUX BOUTONS CÔTE À CÔTE ---
    c_btn1, c_btn2 = st.columns(2)
    
    with c_btn1:
        if st.button("🚀 ANALYSER", type="primary", use_container_width=True):
            st.session_state.quantum_mode = False 
            with st.spinner("Chargement..."):
                hid, aid, lid = match_data['teams']['home']['id'], match_data['teams']['away']['id'], match_data['league']['id']
                hs, as_ = get_deep_stats(hid), get_deep_stats(aid)
                if hs and as_ and model:
                    vec = np.array([[lid, hs['form'], hs['avg_gf'], hs['avg_ga'], as_['form'], as_['avg_gf'], as_['avg_ga']]])
                    p = model.predict_proba(vec)[0]
                    s = sim_score(hs, as_) 
                    st.session_state.analyzed_match_data = {"m": match_data, "h": hs, "a": as_, "p": p, "s": s, "hid": hid, "aid": aid, "mode": "std"}

    with c_btn2:
        if st.button("🧬 QUANTUM SNIPER", use_container_width=True):
            st.session_state.quantum_mode = True
            st.session_state.ticket_data = None
            with st.spinner("Calcul Quantique..."):
                hid, aid, lid = match_data['teams']['home']['id'], match_data['teams']['away']['id'], match_data['league']['id']
                hs, as_ = get_deep_stats(hid), get_deep_stats(aid)
                q_data = get_quantum_analysis(hs, as_)
                st.session_state.analyzed_match_data = {"m": match_data, "h": hs, "a": as_, "q": q_data}

    # RÉSULTATS
    if st.session_state.analyzed_match_data:
        d = st.session_state.analyzed_match_data
        if d['m']['fixture']['id'] == match_data['fixture']['id']:
            h, a, m = d['h'], d['a'], d['m']
            
            st.markdown(f"""
            <div class="match-header">
                <div class="team-box"><img src="{m['teams']['home']['logo']}" class="team-logo"><div class="team-name">{m['teams']['home']['name']}</div></div>
                <div class="vs-box">VS</div>
                <div class="team-box"><img src="{m['teams']['away']['logo']}" class="team-logo"><div class="team-name">{m['teams']['away']['name']}</div></div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.quantum_mode and 'q' in d:
                q = d['q']
                st.markdown("<div class='quantum-btn'>🧬 ANALYSE QUANTIQUE</div>", unsafe_allow_html=True)
                st.markdown(f"""<div class="q-box"><div class="q-title">🎯 VISEUR SNIPER</div><div style="text-align:center; font-size: 2.5rem; font-weight:900; color:#00FF99;">{q['sniper_score']}</div><div style="text-align:center; font-size: 0.8rem; color:#888;">Confiance: {q['sniper_conf']:.1f}%</div></div>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1: st.markdown(f"""<div class="q-box" style="height:100px;"><div class="q-title">🌊 MOMENTUM</div><progress value="{q['momentum_h']}" max="100" style="width:100%; height:5px;"></progress><div style="font-size:0.7rem; display:flex; justify-content:space-between;"><span>Dom</span><span>Ext</span></div></div>""", unsafe_allow_html=True)
                with c2: 
                    col = "#FF4B4B" if q['upset_risk'] > 30 else "#00FF99"
                    st.markdown(f"""<div class="q-box" style="height:100px;"><div class="q-title">⚠️ UPSET</div><div style="text-align:center; font-size:1.5rem; font-weight:bold; color:{col};">{q['upset_risk']:.0f}%</div></div>""", unsafe_allow_html=True)
                st.info(f"Prévision xG : {h['name']} ({q['xg_h']:.2f}) - {a['name']} ({q['xg_a']:.2f})")

            elif 'p' in d:
                p, s, hid, aid = d['p'], d['s'], d['hid'], d['aid']
                st.markdown(f"""<div class="probs-container"><div class="prob-box"><div class="info-icon">💡</div><div class="prob-label">DOMICILE</div><div class="prob-value">{p[1]*100:.0f}%</div></div><div class="prob-box"><div class="prob-label">NUL</div><div class="prob-value">{p[0]*100:.0f}%</div></div><div class="prob-box"><div class="info-icon">💡</div><div class="prob-label">EXTÉRIEUR</div><div class="prob-value">{p[2]*100:.0f}%</div></div></div>""", unsafe_allow_html=True)
                with st.expander("🔎 Voir l'analyse"): st.info(f"**Dom :** {gen_justif('🏆 Résultat', 'Domicile', h, a)}"); st.info(f"**Ext :** {gen_justif('🏆 Résultat', 'Extérieur', h, a)}")
                st.progress(int(max(p)*100))
                
                st.markdown("### 📊 Comparateur")
                opts = {"Puissance Offensive": ["Buts", h['avg_gf'], a['avg_gf'], ['#00FF99', '#00CCFF']], "Solidité Défensive": ["Encaissés", h['avg_ga'], a['avg_ga'], ['#FF4B4B', '#FF8888']], "Volatilité": ["Chaos", h['vol'], a['vol'], ['#FFA500', '#FFD700']]}
                sel_opt = st.selectbox("Critère", list(opts.keys()), key="graph_sel")
                dat = opts[sel_opt]
                df = pd.DataFrame({'Eq': [m['teams']['home']['name'], m['teams']['away']['name']], 'Val': [dat[1], dat[2]]})
                ch = alt.Chart(df).encode(x=alt.X('Val', axis=alt.Axis(grid=False, title=None)), y=alt.Y('Eq', axis=alt.Axis(title=None, labelColor='white', labelLimit=100)), color=alt.Color('Eq', legend=None, scale=alt.Scale(range=dat[3])))
                st.altair_chart(alt.layer(ch.mark_rule(size=3), ch.mark_circle(size=120)).properties(height=150, background='transparent').configure_view(stroke=None), use_container_width=True)
                
                t1, t2, t3, t4 = st.tabs(["🔮 Score", "⚡ Stats", "🛑 Discipline", "💰 Conseil"])
                with t1:
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
