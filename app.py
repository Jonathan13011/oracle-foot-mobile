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

# --- 1. CONFIGURATION MOBILE V14 (STABLE & FLUIDE) ---
st.set_page_config(page_title="Oracle Mobile V14", layout="wide", page_icon="📱")

st.markdown("""
<style>
    /* FOND GÉNÉRAL */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* ==============================================
       CSS SPÉCIAL IPHONE (Mobile Responsive Fixes) 
       ============================================== */
    
    @media only screen and (max-width: 640px) {
        /* 1. CONTENEUR PRINCIPAL : SUPPRIMER LES MARGES INUTILES */
        .block-container { 
            padding-top: 1rem !important; 
            padding-left: 5px !important; 
            padding-right: 5px !important; 
            max-width: 100vw !important;
            overflow-x: hidden !important;
        }

        /* 2. FORCER LES 3 COLONNES SUR UNE LIGNE */
        div[data-testid="column"] {
            width: 32% !important; /* 3 x 32% = 96% -> Ça rentre ! */
            flex: 0 0 auto !important;
            min-width: 0 !important;
            padding: 0 1px !important; /* Espacement minimal */
        }
        
        /* 3. TAILLE DES CHIFFRES (POUR QUE ÇA RENTRE) */
        .big-number { font-size: 1.1rem !important; }
        .small-label { font-size: 0.6rem !important; }
    }

    /* DESIGN DES METRICS PERSONNALISÉES (HTML/CSS) */
    .metric-card {
        background-color: #1a1c24;
        border: 1px solid #363b4e;
        border-radius: 8px;
        padding: 5px;
        text-align: center;
        height: 85px; /* Hauteur fixe pour alignement */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .small-label { color: #AAAAAA; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; }
    .big-number { color: #FFFFFF; font-weight: 800; font-size: 1.5rem; line-height: 1.2; }

    /* BOUTON AMPOULE (VRAIE ICÔNE CLIQUABLE) */
    div[data-testid="stPopover"] {
        display: flex; justify-content: center; width: 100%; margin-top: -5px;
    }
    div[data-testid="stPopover"] > button {
        border: none !important;
        background: transparent !important;
        color: #00FF99 !important;
        padding: 0 !important;
        font-size: 1.2rem !important; /* Taille de l'icône */
        height: 30px !important;
        line-height: 1 !important;
        box-shadow: none !important;
    }
    div[data-testid="stPopover"] > button:hover { color: #FFFFFF !important; transform: scale(1.1); }

    /* HEADER DU MATCH (FLEXBOX PUR) */
    .match-header {
        display: flex; 
        flex-direction: row; /* Force la ligne */
        align-items: center; 
        justify-content: space-between; 
        background: #1a1c24; 
        padding: 10px 5px; 
        border-radius: 12px; 
        margin-bottom: 15px;
        border: 1px solid #333;
        width: 100%;
    }
    .team-box { text-align: center; width: 40%; display: flex; flex-direction: column; align-items: center; }
    .team-logo { width: 45px; height: 45px; object-fit: contain; margin-bottom: 5px; }
    .team-name { font-size: 0.8rem; font-weight: bold; line-height: 1.1; color: white; word-wrap: break-word; }
    .vs-box { width: 15%; text-align: center; color: #00FF99; font-weight: 900; font-size: 1.2rem; }

    /* RESTE DU DESIGN */
    div[data-testid="stPopoverBody"] { background-color: #1a1c24; color: white; border: 1px solid #00FF99; }
    .stButton > button { background-color: #262935; color: white !important; border: 1px solid #444; border-radius: 8px; }
    div[data-testid="stSidebarUserContent"] .stButton > button { background: linear-gradient(45deg, #FF4B4B, #FF0000); border: none; font-weight: bold; }
    .ticket-match-title { font-weight: bold; color: #00FF99; margin-top: 10px; border-bottom: 1px solid #333; }
    .graph-info { background-color: #1a1c24; color: #00FF99; padding: 5px; border-radius: 5px; border-left: 3px solid #00FF99; font-size: 0.75rem; margin-bottom: 5px; }
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
    return {"name": d[0]['teams']['home']['name'] if d[0]['teams']['home']['id'] == tid else d[0]['teams']['away']['name'], "form": pts/len(d), "avg_gf": sum(gs)/len(d), "avg_ga": sum(gc)/len(d), "cs_rate": cs/len(d)*100, "btts_rate": btts/len(d)*100, "ht_win_rate": (ht_wins / len(data)) * 100 if 'data' in locals() else 0, "draw_rate": dr/len(d)*100, "vol": vol, "streak": "".join(res[:5]), "total_matches": len(d)}

# --- INTELLIGENCE ---
def gen_justif(type, val, h, a):
    r = []
    if type=="🏆 Résultat":
        if "Nul" in val: r.append(f"Forte tendance au nul ({max(h['draw_rate'], a['draw_rate'])}%).")
        elif "Domicile" in val: r.append(f"{h['name']} est solide à domicile.")
        else: r.append(f"{a['name']} est performant à l'extérieur.")
    elif type=="⚽ Buts":
        xg = h['avg_gf']+a['avg_gf']
        if "+2.5" in val: r.append(f"Match ouvert (Moy. {xg:.1f}).")
        else: r.append(f"Match fermé (Moy. {xg:.1f}).")
    return random.choice(r) if r else "Analyse favorable."

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

# --- INTERFACE ---
st.title("📱 ORACLE V14")

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
                c1, c2 = st.columns([0.85, 0.15])
                c1.markdown(f"{icon} {b['t']} : **{b['v']}**")
                with c2.popover("💡"): st.info(b['j'])
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
    
    # --- HEADER DU MATCH ---
    st.markdown(f"""
    <div class="match-header">
        <div class="team-box">
            <img src="{m['teams']['home']['logo']}" class="team-logo">
            <div class="team-name">{m['teams']['home']['name']}</div>
        </div>
        <div class="vs-box">VS</div>
        <div class="team-box">
            <img src="{m['teams']['away']['logo']}" class="team-logo">
            <div class="team-name">{m['teams']['away']['name']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- METRICS COMPACTES SANS SCROLL ---
    # On force 3 colonnes très serrées
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="small-label">DOMICILE</div>
            <div class="big-number">{p[1]*100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
        with st.popover("💡", use_container_width=True): st.info(gen_justif("🏆 Résultat", "Domicile", h, a))

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="small-label">MATCH NUL</div>
            <div class="big-number">{p[0]*100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
        # Pas d'ampoule pour le nul ici pour gagner de la place visuelle

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="small-label">EXTÉRIEUR</div>
            <div class="big-number">{p[2]*100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
        with st.popover("💡", use_container_width=True): st.info(gen_justif("🏆 Résultat", "Extérieur", h, a))

    st.progress(int(max(p)*100))
    
    # --- RESTE DU CONTENU ---
    st.markdown("### 📊 Comparateur")
    opts = {"Puissance Offensive": ["Buts", h['avg_gf'], a['avg_gf'], ['#00FF99', '#00CCFF']], 
            "Solidité Défensive": ["Encaissés", h['avg_ga'], a['avg_ga'], ['#FF4B4B', '#FF8888']],
            "Volatilité": ["Chaos", h['vol'], a['vol'], ['#FFA500', '#FFD700']],
            "Forme": ["Points", h['form'], a['form'], ['#00FF99', '#00CCFF']]}
    sel_opt = st.selectbox("Critère", list(opts.keys()))
    st.markdown(f"<div class='graph-info'>ℹ️ {sel_opt}</div>", unsafe_allow_html=True)
    dat = opts[sel_opt]
    df = pd.DataFrame({'Eq': [m['teams']['home']['name'], m['teams']['away']['name']], 'Val': [dat[1], dat[2]]})
    ch = alt.Chart(df).encode(x=alt.X('Val', axis=alt.Axis(grid=False, title=None)), y=alt.Y('Eq', axis=alt.Axis(title=None, labelColor='white', labelLimit=100)), color=alt.Color('Eq', legend=None, scale=alt.Scale(range=dat[3])))
    st.altair_chart(alt.layer(ch.mark_rule(size=3), ch.mark_circle(size=120)).properties(height=150, background='transparent').configure_view(stroke=None), use_container_width=True)
    
    t1, t2, t3 = st.tabs(["🔮 Score", "⚡ Stats", "💰 Avis"])
    with t1:
        c1, c2, c3 = st.columns(3)
        if len(s)>0: c1.metric("#1", s[0][0])
        if len(s)>1: c2.metric("#2", s[1][0])
        if len(s)>2: c3.metric("#3", s[2][0])
    with t2: st.info(f"**DOM:** CS {h['cs_rate']:.0f}% | BTTS {h['btts_rate']:.0f}%"); st.info(f"**EXT:** CS {a['cs_rate']:.0f}% | BTTS {a['btts_rate']:.0f}%")
    with t3: st.success(f"Confiance: {max(p)*100:.0f}% {'(Top)' if max(p)>0.65 else '(Moyen)'}")
