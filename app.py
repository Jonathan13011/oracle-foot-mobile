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

# --- 1. CONFIGURATION MOBILE V11 (RESPONSIVE FIX) ---
st.set_page_config(page_title="Oracle Mobile", layout="wide", page_icon="📱")

st.markdown("""
<style>
    /* FOND GÉNÉRAL */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* === CSS SPÉCIAL IPHONE & MOBILE === */
    @media only screen and (max-width: 600px) {
        /* Réduction des marges globales */
        .block-container { 
            padding-top: 1rem !important; 
            padding-bottom: 5rem !important;
            padding-left: 0.5rem !important; 
            padding-right: 0.5rem !important; 
        }
        
        /* Titres compacts */
        h1 { font-size: 1.5rem !important; margin-bottom: 0.5rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        /* Forcer l'alignement horizontal des colonnes (Le Fix du bug photo) */
        div[data-testid="column"] {
            width: auto !important;
            flex: 1 1 auto !important;
            min-width: 1px !important;
        }
    }

    /* DESIGN DES METRICS (BOITES DE SCORE) */
    div[data-testid="stMetric"] {
        background-color: #1a1c24 !important; 
        border: 1px solid #363b4e;
        padding: 8px; /* Padding réduit pour mobile */
        border-radius: 12px; 
    }
    div[data-testid="stMetricLabel"] { color: #AAAAAA !important; font-size: 0.75rem; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 800; font-size: 1.4rem !important; }

    /* BOUTON AMPOULE (FIX VISUEL) */
    /* On cible spécifiquement le bouton du popover pour qu'il soit transparent et petit */
    div[data-testid="stPopover"] > button {
        border: none !important;
        background-color: transparent !important;
        color: white !important;
        font-size: 1.2rem;
        padding: 0px !important;
        height: auto !important;
        width: auto !important;
        box-shadow: none !important;
    }
    div[data-testid="stPopover"] > button:hover {
        color: #00FF99 !important;
        transform: scale(1.2);
    }

    /* BOUTONS ACTIONS (Générer / Analyser) */
    .stButton > button {
        background-color: #262935; color: white !important; 
        border: 1px solid #444; border-radius: 10px; 
        padding: 0.5rem; min-height: 45px; font-size: 1rem; width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    div[data-testid="stSidebarUserContent"] .stButton > button {
        background: linear-gradient(45deg, #FF4B4B, #FF0000); border: none; font-weight: bold;
    }

    /* CONTENU POPOVER */
    div[data-testid="stPopoverBody"] { background-color: #1a1c24; color: white; border: 1px solid #00FF99; }
    
    /* TITRE TICKET */
    .ticket-match-title { font-weight: bold; color: #00FF99; margin-top: 10px; margin-bottom: 5px; border-bottom: 1px solid #333; font-size: 0.95rem; }
    
    /* INFO GRAPHIQUE */
    .graph-info { background-color: #1a1c24; color: #00FF99; padding: 8px; border-radius: 5px; border-left: 3px solid #00FF99; margin-bottom: 10px; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

API_KEY = "4d3c1dbf76600a937722ff6425d450ee"
HEADERS = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
LEAGUE_IDS = [2, 39, 61, 140, 135, 78, 94, 45, 203, 307, 143, 323]

if 'analyzed_match_data' not in st.session_state: st.session_state.analyzed_match_data = None
if 'ticket_data' not in st.session_state: st.session_state.ticket_data = None

try:
    model = joblib.load('oracle_brain.pkl')
    MODEL_LOADED = True
except:
    model = None
    MODEL_LOADED = False

# --- MOTEUR DONNÉES ---
@st.cache_data(ttl=3600)
def get_upcoming_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
    all_fixtures = []
    for i, league_id in enumerate(LEAGUE_IDS):
        try:
            url = "https://v3.football.api-sports.io/fixtures"
            params = {"league": league_id, "season": "2025", "from": today, "to": end_date, "timezone": "Europe/Paris"}
            r = requests.get(url, headers=HEADERS, params=params).json()
            if 'response' in r and r['response']: all_fixtures.extend(r['response'])
        except: pass
    return all_fixtures

@st.cache_data(ttl=3600)
def get_deep_stats(team_id):
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"team": str(team_id), "last": "10", "status": "FT"} 
    data = requests.get(url, headers=HEADERS, params=params).json().get('response', [])
    if not data: return None
    
    goals_scored, goals_conceded = [], []
    ht_wins, btts_count, points, clean_sheets, draws_count = 0, 0, 0, 0, 0
    results_codes = []
    for m in data:
        is_home = m['teams']['home']['id'] == team_id
        g_for, g_ag = (m['goals']['home'] if is_home else m['goals']['away']) or 0, (m['goals']['away'] if is_home else m['goals']['home']) or 0
        try:
            ht_for = m['score']['halftime']['home'] if is_home else m['score']['halftime']['away']
            ht_ag = m['score']['halftime']['away'] if is_home else m['score']['halftime']['home']
            if ht_for is not None and ht_ag is not None and ht_for > ht_ag: ht_wins += 1
        except: pass
        goals_scored.append(g_for); goals_conceded.append(g_ag)
        if g_for > 0 and g_ag > 0: btts_count += 1
        if g_ag == 0: clean_sheets += 1
        if g_for > g_ag: points += 3; results_codes.append("✅")
        elif g_for == g_ag: points += 1; results_codes.append("➖"); draws_count += 1
        else: results_codes.append("❌")
    try: volatility = statistics.stdev(goals_scored)
    except: volatility = 0
    return {"name": data[0]['teams']['home']['name'] if data[0]['teams']['home']['id'] == team_id else data[0]['teams']['away']['name'], "form_score": points / len(data), "avg_goals": sum(goals_scored) / len(data), "avg_conceded": sum(goals_conceded) / len(data), "clean_sheet_rate": (clean_sheets / len(data)) * 100, "btts_rate": (btts_count / len(data)) * 100, "ht_win_rate": (ht_wins / len(data)) * 100, "draw_rate": (draws_count / len(data)) * 100, "volatility": volatility, "streak": "".join(results_codes[:5]), "total_matches": len(data)}

# --- INTELLIGENCE V11 ---
def generate_smart_justification(bet_type, bet_val, h_stats, a_stats):
    reasons = []
    if bet_type == "🏆 Résultat":
        if "Nul" in bet_val: reasons.append(f"Tendance Nul élevée ({max(h_stats['draw_rate'], a_stats['draw_rate'])}%). Forces égales.")
        elif "Domicile" in bet_val: reasons.append(f"{h_stats['name']} est intraitable à domicile.")
        else: reasons.append(f"{a_stats['name']} voyage très bien.")
    elif bet_type == "⚽ Buts":
        total_xG = h_stats['avg_goals'] + a_stats['avg_goals']
        if "+2.5" in bet_val: reasons.append(f"Potentiel explosif (Moy. {total_xG:.1f} buts).")
        else: reasons.append(f"Match fermé attendu (Moy. {total_xG:.1f}).")
    elif "BTTS" in bet_val:
        if "OUI" in bet_val: reasons.append(f"Stats BTTS hautes ({(h_stats['btts_rate']+a_stats['btts_rate'])/2:.0f}%).")
        else: reasons.append("Une équipe risque de ne pas marquer.")
    if not reasons: reasons.append("Logique statistique favorable.")
    return random.choice(reasons)

def simulate_sixth_sense_scores(h_stats, a_stats):
    exp_h = (h_stats['avg_goals'] + a_stats['avg_conceded']) / 2
    exp_a = (a_stats['avg_goals'] + h_stats['avg_conceded']) / 2
    simulations = []
    for _ in range(5000): simulations.append(f"{np.random.poisson(exp_h)}-{np.random.poisson(exp_a)}")
    return Counter(simulations).most_common(3)

def analyze_match_probabilities(h_stats, a_stats, model_probs):
    predictions = []
    winner_prob = max(model_probs)
    if model_probs[0] > 0.28 and abs(model_probs[1] - model_probs[2]) < 0.15:
        predictions.append({"type": "🏆 Résultat", "val": "Match Nul", "conf": model_probs[0] + 0.35, "category": "DRAW"})
    elif winner_prob > 0.55:
        label = f"Victoire {h_stats['name']}" if model_probs[1] == winner_prob else f"Victoire {a_stats['name']}"
        predictions.append({"type": "🏆 Résultat", "val": label, "conf": winner_prob, "category": "WIN"})
    
    avg_total = (h_stats['avg_goals'] + a_stats['avg_goals'] + h_stats['avg_conceded'] + a_stats['avg_conceded']) / 2
    if avg_total < 2.2: predictions.append({"type": "⚽ Buts", "val": "-2.5 Buts", "conf": min(0.85, 2.0 / (avg_total + 0.1)), "category": "UNDER"})
    elif avg_total > 2.8: predictions.append({"type": "⚽ Buts", "val": "+2.5 Buts", "conf": min(0.90, avg_total / 3.5), "category": "OVER"})
    
    btts_avg = (h_stats['btts_rate'] + a_stats['btts_rate']) / 2
    if btts_avg > 60: predictions.append({"type": "🥅 BTTS", "val": "Les 2 marquent : OUI", "conf": btts_avg/100, "category": "BTTS"})
    elif btts_avg < 40: predictions.append({"type": "🥅 BTTS", "val": "Les 2 marquent : NON", "conf": 1-(btts_avg/100), "category": "BTTS_NO"})

    for p in predictions: p['justif'] = generate_smart_justification(p['type'], p['val'], h_stats, a_stats)
    return predictions

def generate_grouped_winning_ticket(fixtures_list):
    pools = {"WIN": [], "DRAW": [], "OVER": [], "UNDER": [], "BTTS": [], "BTTS_NO": []}
    prog_bar = st.sidebar.progress(0, text="Scan...")
    scan_limit = min(len(fixtures_list), 30)
    count = 0
    for f in fixtures_list:
        if count >= scan_limit: break
        h_id, a_id, l_id = f['teams']['home']['id'], f['teams']['away']['id'], f['league']['id']
        h_stats, a_stats = get_deep_stats(h_id), get_deep_stats(a_id)
        if h_stats and a_stats and model:
            vec = np.array([[l_id, h_stats['form_score'], h_stats['avg_goals'], h_stats['avg_conceded'], a_stats['form_score'], a_stats['avg_goals'], a_stats['avg_conceded']]])
            probs = model.predict_proba(vec)[0]
            preds = analyze_match_probabilities(h_stats, a_stats, probs)
            for p in preds:
                if p['conf'] > 0.50:
                    item = {"match_name": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}", "match_id": f['fixture']['id'], "bet": p, "h_stats": h_stats, "a_stats": a_stats}
                    if p['category'] in pools: pools[p['category']].append(item)
        count += 1
        prog_bar.progress(count / scan_limit)
    prog_bar.empty()
    final_picks = []
    categories_order = ["DRAW", "UNDER", "BTTS", "WIN", "OVER", "BTTS_NO"]
    for cat in categories_order:
        if pools[cat]:
            pools[cat].sort(key=lambda x: x['bet']['conf'], reverse=True)
            final_picks.append(pools[cat].pop(0))
    remaining = []
    for cat in categories_order: remaining.extend(pools[cat])
    random.shuffle(remaining)
    remaining.sort(key=lambda x: x['bet']['conf'], reverse=True)
    if len(final_picks) < 10: final_picks.extend(remaining[:10-len(final_picks)])
    
    grouped = {}
    for pick in final_picks:
        nm = pick['match_name']
        if nm not in grouped: grouped[nm] = []
        if len(grouped[nm]) < 3: grouped[nm].append(pick)
    return grouped

# --- INTERFACE ---
st.title("📱 ORACLE MOBILE")

with st.sidebar:
    st.header("🎟️ TICKET")
    fixtures = get_upcoming_matches()
    if st.button("🎰 GÉNÉRER"):
        if not fixtures: st.error("Pas de matchs.")
        else:
            with st.spinner("Analyse..."): st.session_state.ticket_data = generate_grouped_winning_ticket(fixtures)
    if st.session_state.ticket_data:
        st.success("✅ PRÊT !")
        st.markdown("---")
        idx = 1
        for m_name, bets in st.session_state.ticket_data.items():
            st.markdown(f"<div class='ticket-match-title'>{idx}. {m_name}</div>", unsafe_allow_html=True)
            for b_obj in bets:
                b = b_obj['bet']
                c1, c2 = st.columns([0.8, 0.2]) # Ratio ajusté pour mobile
                icon = "⚖️" if "Nul" in b['val'] else ("🔒" if "-2.5" in b['val'] else ("🥅" if "BTTS" in b['val'] else "🔸"))
                c1.markdown(f"{icon} {b['type']} : *{b['val']}*")
                with c2.popover("💡"): st.info(b['justif'])
            idx+=1
        st.markdown("---")

    st.header("🔍 Match")
    if fixtures:
        fixtures.sort(key=lambda x: x['fixture']['date'])
        m_map = {f"[{f['league']['name']}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fixtures}
        sel = st.selectbox("Rencontre", list(m_map.keys()))
        m_data = m_map[sel]

if st.button("🚀 ANALYSER", type="primary"):
    with st.spinner("Chargement..."):
        h_id, a_id, l_id = m_data['teams']['home']['id'], m_data['teams']['away']['id'], m_data['league']['id']
        h_s, a_s = get_deep_stats(h_id), get_deep_stats(a_id)
        if h_s and a_s and model:
            vec = np.array([[l_id, h_s['form_score'], h_s['avg_goals'], h_s['avg_conceded'], a_s['form_score'], a_s['avg_goals'], a_s['avg_conceded']]])
            probs = model.predict_proba(vec)[0]
            scores = simulate_sixth_sense_scores(h_s, a_s)
            st.session_state.analyzed_match_data = {"m": m_data, "h": h_s, "a": a_s, "p": probs, "s": scores}

if st.session_state.analyzed_match_data:
    d = st.session_state.analyzed_match_data
    h, a, p, m, s = d['h'], d['a'], d['p'], d['m'], d['s']
    
    # Header compact
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: st.image(m['teams']['home']['logo'], width=60)
    with c2: st.markdown(f"<h3 style='text-align:center;margin:0'>{m['teams']['home']['name']}</h3><h4 style='text-align:center;color:#00FF99;margin:0'>VS</h4><h3 style='text-align:center;margin:0'>{m['teams']['away']['name']}</h3>", unsafe_allow_html=True)
    with c3: st.image(m['teams']['away']['logo'], width=60)
    
    st.markdown("---")
    
    # METRICS RESPONSIVE (Le cœur du fix)
    m1, m2, m3 = st.columns(3)
    def mb(col, l, v, st_ref):
        # Ratio 3:1 pour laisser la place au pourcentage sans écraser le bouton
        c_a, c_b = col.columns([0.75, 0.25]) 
        c_a.metric(l, v)
        # Bouton Popover invisible (juste l'icone)
        with c_b.popover("💡", use_container_width=True): 
            st.info(generate_smart_justification("🏆 Résultat", l, st_ref, a if l=="DOM" else h))
    
    mb(m1, "DOM", f"{p[1]*100:.0f}%", h)
    m2.metric("NUL", f"{p[0]*100:.0f}%")
    mb(m3, "EXT", f"{p[2]*100:.0f}%", a)
    st.progress(int(max(p)*100))
    
    st.markdown("### 📊 Comparateur")
    opts = {"Puissance Offensive": ["Buts", h['avg_goals'], a['avg_goals'], ['#00FF99', '#00CCFF']], 
            "Solidité Défensive": ["Encaissés", h['avg_conceded'], a['avg_conceded'], ['#FF4B4B', '#FF8888']],
            "Volatilité": ["Chaos", h['volatility'], a['volatility'], ['#FFA500', '#FFD700']],
            "Forme": ["Points", h['form_score'], a['form_score'], ['#00FF99', '#00CCFF']]}
    sel_opt = st.selectbox("Critère", list(opts.keys()))
    st.markdown(f"<div class='graph-info'>ℹ️ {sel_opt}</div>", unsafe_allow_html=True)
    dat = opts[sel_opt]
    df = pd.DataFrame({'Eq': [m['teams']['home']['name'], m['teams']['away']['name']], 'Val': [dat[1], dat[2]]})
    ch = alt.Chart(df).encode(x=alt.X('Val', axis=alt.Axis(grid=False, title=None)), y=alt.Y('Eq', axis=alt.Axis(title=None, labelColor='white', labelLimit=100)), color=alt.Color('Eq', legend=None, scale=alt.Scale(range=dat[3])))
    st.altair_chart(alt.layer(ch.mark_rule(size=3), ch.mark_circle(size=100)).properties(height=150, background='transparent').configure_view(stroke=None), use_container_width=True)
    
    t1, t2, t3, t4 = st.tabs(["🔮 Score", "⚡ Stats", "🛑 Risque", "💰 Conseil"])
    with t1:
        c1, c2, c3 = st.columns(3)
        if len(s)>0: c1.metric("#1", s[0][0])
        if len(s)>1: c2.metric("#2", s[1][0])
        if len(s)>2: c3.metric("#3", s[2][0])
    with t2: st.info(f"*DOM:* CS {h['clean_sheet_rate']:.0f}% | BTTS {h['btts_rate']:.0f}%"); st.info(f"*EXT:* CS {a['clean_sheet_rate']:.0f}% | BTTS {a['btts_rate']:.0f}%")
    with t3: st.write(f"Penalty DOM: *{'ÉLEVÉ' if h['volatility']>1.4 else 'Faible'}*"); st.write(f"Penalty EXT: *{'ÉLEVÉ' if a['volatility']>1.4 else 'Faible'}*")
    with t4: st.success(f"Confiance: {max(p)*100:.0f}% {'(Top)' if max(p)>0.65 else '(Moyen)'}")