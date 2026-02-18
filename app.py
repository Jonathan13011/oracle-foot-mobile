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

# --- 1. CONFIGURATION & DESIGN V9 (Identique V8) ---
st.set_page_config(page_title="Oracle Football Ultimate V9", layout="wide", page_icon="🔮")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div[data-testid="stMetric"] { background-color: #1a1c24 !important; border: 1px solid #363b4e; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    div[data-testid="stMetric"]:hover { border-color: #00FF99; transform: translateY(-2px); }
    div[data-testid="stMetricLabel"] { color: #DDDDDD !important; font-size: 0.9rem; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 800; font-size: 1.8rem; }
    .stButton > button { background-color: #262935; color: white !important; border: 1px solid #444; border-radius: 8px; }
    .stButton > button:hover { background-color: #00FF99 !important; color: black !important; border-color: #00FF99; }
    div[data-testid="stSidebarUserContent"] .stButton > button { background: linear-gradient(45deg, #FF4B4B, #FF0000); color: white !important; border: none; font-weight: bold; }
    div[data-testid="stPopoverBody"] { background-color: #1a1c24; color: white; border: 1px solid #00FF99; }
    .graph-info { background-color: #1a1c24; color: #00FF99; padding: 10px; border-radius: 5px; border-left: 5px solid #00FF99; margin-bottom: 10px; }
    .ticket-match-title { font-weight: bold; color: #00FF99; margin-top: 10px; margin-bottom: 5px; font-size: 1.1em; }
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

# --- 3. MOTEUR DE DONNÉES ---
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
    
    return {
        "name": data[0]['teams']['home']['name'] if data[0]['teams']['home']['id'] == team_id else data[0]['teams']['away']['name'],
        "form_score": points / len(data),
        "avg_goals": sum(goals_scored) / len(data),
        "avg_conceded": sum(goals_conceded) / len(data),
        "clean_sheet_rate": (clean_sheets / len(data)) * 100,
        "btts_rate": (btts_count / len(data)) * 100,
        "ht_win_rate": (ht_wins / len(data)) * 100,
        "draw_rate": (draws_count / len(data)) * 100,
        "volatility": volatility,
        "streak": "".join(results_codes[:5]),
        "total_matches": len(data)
    }

# --- 4. INTELLIGENCE V9 ---

def generate_smart_justification(bet_type, bet_val, h_stats, a_stats):
    reasons = []
    if bet_type == "🏆 Résultat":
        if "Nul" in bet_val:
            reasons.append(f"Tendance Nul élevée ({max(h_stats['draw_rate'], a_stats['draw_rate'])}%).")
            reasons.append("Forces équilibrées, neutralisation attendue.")
        elif "Domicile" in bet_val: reasons.append(f"{h_stats['name']} est très solide à domicile ({h_stats['streak']}).")
        else: reasons.append(f"{a_stats['name']} performe mieux à l'extérieur.")
    elif bet_type == "⚽ Buts":
        total_xG = h_stats['avg_goals'] + a_stats['avg_goals']
        if "+2.5" in bet_val: reasons.append(f"Attaques en feu (Moyenne cumulée {total_xG:.1f}).")
        else: reasons.append(f"Match fermé : Moyenne de buts faible ({total_xG:.1f}).")
    elif "BTTS" in bet_val:
        if "OUI" in bet_val: reasons.append(f"Les deux marquent souvent ({(h_stats['btts_rate']+a_stats['btts_rate'])/2:.0f}%).")
        else: reasons.append("Défense hermétique d'un côté.")
    
    if not reasons: reasons.append("Analyse statistique favorable.")
    return random.choice(reasons)

def simulate_sixth_sense_scores(h_stats, a_stats):
    exp_h = (h_stats['avg_goals'] + a_stats['avg_conceded']) / 2
    exp_a = (a_stats['avg_goals'] + h_stats['avg_conceded']) / 2
    simulations = []
    for _ in range(5000):
        s_h = np.random.poisson(exp_h); s_a = np.random.poisson(exp_a)
        simulations.append(f"{s_h}-{s_a}")
    return Counter(simulations).most_common(3)

def analyze_match_probabilities(h_stats, a_stats, model_probs):
    predictions = []
    
    # 1. ANALYSE RÉSULTAT (Victoire / Nul)
    winner_prob = max(model_probs)
    # Detection Nul (Si proba nul > 28% et écart faible)
    if model_probs[0] > 0.28 and abs(model_probs[1] - model_probs[2]) < 0.15:
        # On booste artificiellement la confiance du Nul pour qu'il apparaisse dans le ticket
        predictions.append({"type": "🏆 Résultat", "val": "Match Nul", "conf": model_probs[0] + 0.35, "category": "DRAW"})
    
    elif winner_prob > 0.55:
        label = f"Victoire {h_stats['name']}" if model_probs[1] == winner_prob else f"Victoire {a_stats['name']}"
        predictions.append({"type": "🏆 Résultat", "val": label, "conf": winner_prob, "category": "WIN"})
        
    # 2. ANALYSE BUTS (+/- 2.5)
    avg_total = (h_stats['avg_goals'] + a_stats['avg_goals'] + h_stats['avg_conceded'] + a_stats['avg_conceded']) / 2
    
    # UNDER 2.5 (Match Fermé)
    if avg_total < 2.2:
        # Confiance inversement proportionnelle aux buts
        conf = min(0.85, 2.0 / (avg_total + 0.1)) 
        predictions.append({"type": "⚽ Buts", "val": "-2.5 Buts", "conf": conf, "category": "UNDER"})
    
    # OVER 2.5 (Match Ouvert)
    elif avg_total > 2.8:
        conf = min(0.90, avg_total / 3.5)
        predictions.append({"type": "⚽ Buts", "val": "+2.5 Buts", "conf": conf, "category": "OVER"})
        
    # 3. BTTS (Les deux marquent)
    btts_avg = (h_stats['btts_rate'] + a_stats['btts_rate']) / 2
    if btts_avg > 60:
        predictions.append({"type": "🥅 BTTS", "val": "Les 2 marquent : OUI", "conf": btts_avg/100, "category": "BTTS"})
    elif btts_avg < 40:
        predictions.append({"type": "🥅 BTTS", "val": "Les 2 marquent : NON", "conf": 1 - (btts_avg/100), "category": "BTTS_NO"})

    # Ajout Justifications
    for p in predictions:
        p['justif'] = generate_smart_justification(p['type'], p['val'], h_stats, a_stats)
        
    return predictions

def generate_grouped_winning_ticket(fixtures_list):
    """ GÉNÉRATEUR V9 : DIVERSIFICATION FORCÉE """
    
    # Paniers pour stocker les paris par type
    pools = {
        "WIN": [], "DRAW": [], "OVER": [], "UNDER": [], "BTTS": [], "BTTS_NO": []
    }
    
    prog_bar = st.sidebar.progress(0, text="Scan Diversifié V9...")
    scan_limit = min(len(fixtures_list), 30) # Scan large
    
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
                # On ajoute au bon panier si confiance décente (>50%)
                if p['conf'] > 0.50:
                    item = {
                        "match_name": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                        "match_id": f['fixture']['id'],
                        "bet": p, "h_stats": h_stats, "a_stats": a_stats
                    }
                    if p['category'] in pools:
                        pools[p['category']].append(item)
        count += 1
        prog_bar.progress(count / scan_limit)
    prog_bar.empty()
    
    # CONSTRUCTION DU TICKET ÉQUILIBRÉ (10 Paris max)
    final_picks = []
    
    # On force la pioche dans chaque catégorie (si dispo)
    # Ordre de priorité pour assurer la variété
    categories_order = ["DRAW", "UNDER", "BTTS", "WIN", "OVER", "BTTS_NO"]
    
    # Tour 1 : On prend le meilleur de chaque catégorie
    for cat in categories_order:
        if pools[cat]:
            # Tri par confiance
            pools[cat].sort(key=lambda x: x['bet']['conf'], reverse=True)
            # On prend le top 1
            final_picks.append(pools[cat].pop(0))
            
    # Tour 2 : On complète jusqu'à 10 avec les meilleurs restants (toutes catégories)
    remaining_pool = []
    for cat in categories_order:
        remaining_pool.extend(pools[cat])
    
    random.shuffle(remaining_pool) # Mélange pour la fraîcheur
    remaining_pool.sort(key=lambda x: x['bet']['conf'], reverse=True) # Puis qualité
    
    needed = 10 - len(final_picks)
    if needed > 0:
        final_picks.extend(remaining_pool[:needed])
        
    # Regroupement par Match pour affichage
    grouped_ticket = {}
    for pick in final_picks:
        m_name = pick['match_name']
        if m_name not in grouped_ticket: grouped_ticket[m_name] = []
        if len(grouped_ticket[m_name]) < 3: # Max 3 paris par match
            grouped_ticket[m_name].append(pick)
            
    return grouped_ticket

# --- 5. INTERFACE ---
st.title("🔮 ORACLE FOOTBALL ULTIME V9")

with st.sidebar:
    st.header("🎟️ TICKET GAGNANT IA")
    fixtures = get_upcoming_matches()
    
    if st.button("🎰 GÉNÉRER TICKET ULTIME"):
        if not fixtures: st.error("Pas de matchs.")
        else:
            with st.spinner("Recherche Nuls, Under 2.5, BTTS..."): 
                st.session_state.ticket_data = generate_grouped_winning_ticket(fixtures)
    
    if st.session_state.ticket_data:
        st.success("✅ TICKET DIVERSIFIÉ !")
        st.markdown("---")
        ticket_dict = st.session_state.ticket_data
        match_idx = 1
        for match_name, bets in ticket_dict.items():
            st.markdown(f"<div class='ticket-match-title'>{match_idx}. {match_name}</div>", unsafe_allow_html=True)
            for bet_obj in bets:
                bet_info = bet_obj['bet']
                cols = st.columns([0.85, 0.15])
                
                # Icone selon type
                icon = "🔸"
                if "Nul" in bet_info['val']: icon = "⚖️"
                elif "-2.5" in bet_info['val']: icon = "🔒"
                elif "BTTS" in bet_info['val']: icon = "🥅"
                
                cols[0].markdown(f"{icon} {bet_info['type']} : **{bet_info['val']}**")
                with cols[1].popover("💡", use_container_width=True):
                    st.markdown(f"### Analyse : {match_name}")
                    st.info(f"🗣️ **Oracle :** {bet_info['justif']}")
                    st.write(f"Confiance : **{bet_info['conf']*100:.1f}%**")
                st.caption(f"Confiance: {bet_info['conf']*100:.1f}%")
            st.markdown("---")
            match_idx += 1

    st.header("🔍 Analyse Match")
    if fixtures:
        fixtures.sort(key=lambda x: x['fixture']['date'])
        match_map = {f"[{f['league']['name']}] {f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fixtures}
        selected_label = st.selectbox("Choisir une rencontre", list(match_map.keys()))
        match_data = match_map[selected_label]

# --- 6. MAIN ANALYSIS (Reste V8) ---
if st.button("🚀 LANCER L'ANALYSE DÉTAILLÉE", type="primary"):
    with st.spinner("Activation du Sixième Sens..."):
        h_id, a_id, l_id = match_data['teams']['home']['id'], match_data['teams']['away']['id'], match_data['league']['id']
        h_stats, a_stats = get_deep_stats(h_id), get_deep_stats(a_id)
        if h_stats and a_stats and model:
            vec = np.array([[l_id, h_stats['form_score'], h_stats['avg_goals'], h_stats['avg_conceded'], a_stats['form_score'], a_stats['avg_goals'], a_stats['avg_conceded']]])
            probs = model.predict_proba(vec)[0]
            future_scores = simulate_sixth_sense_scores(h_stats, a_stats)
            st.session_state.analyzed_match_data = {"m_info": match_data, "h_stats": h_stats, "a_stats": a_stats, "probs": probs, "future_scores": future_scores}

if st.session_state.analyzed_match_data:
    data = st.session_state.analyzed_match_data
    h_stats, a_stats, probs, m_info, future_scores = data['h_stats'], data['a_stats'], data['probs'], data['m_info'], data['future_scores']

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: st.image(m_info['teams']['home']['logo'], width=110)
    with c2: 
        st.markdown(f"<h1 style='text-align: center; margin-bottom: 0;'>{m_info['teams']['home']['name']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #00FF99; margin: 0;'>VS</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; margin-top: 0;'>{m_info['teams']['away']['name']}</h1>", unsafe_allow_html=True)
    with c3: st.image(m_info['teams']['away']['logo'], width=110)

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    def metric_bulb(col, label, val, stats, prob):
        c_main, c_bulb = col.columns([0.8, 0.2])
        c_main.metric(label, val)
        with c_bulb.popover("💡", use_container_width=True):
            st.markdown(f"### Détail {label}")
            st.info(generate_smart_justification("🏆 Résultat", label, stats, a_stats if label=="DOMICILE" else h_stats))
            st.write(f"Probabilité brute IA : {prob*100:.2f}%")
    metric_bulb(m1, "DOMICILE", f"{probs[1]*100:.1f}%", h_stats, probs[1])
    m2.metric("NUL", f"{probs[0]*100:.1f}%")
    metric_bulb(m3, "EXTÉRIEUR", f"{probs[2]*100:.1f}%", a_stats, probs[2])
    st.progress(int(max(probs)*100))

    st.markdown("### 📊 Comparateur Visuel Épuré")
    graph_explanations = {
        "Puissance Offensive": "Moyenne de buts marqués sur les 10 derniers matchs.",
        "Solidité Défensive": "Moyenne de buts encaissés.",
        "Volatilité (Chaos)": "Indique si l'équipe est régulière (bas) ou imprévisible (haut).",
        "Forme": "Points moyens pris récemment."
    }
    graph_option = st.selectbox("Choisir le critère d'analyse :", list(graph_explanations.keys()), key="graph_select")
    st.markdown(f"<div class='graph-info'>ℹ️ <b>Comprendre :</b> {graph_explanations[graph_option]}</div>", unsafe_allow_html=True)
    val_h, val_a, title_y = 0, 0, ""
    color_range = ['#00FF99', '#00CCFF']
    if graph_option == "Puissance Offensive": val_h, val_a, title_y = h_stats['avg_goals'], a_stats['avg_goals'], "Buts Moyens"
    elif graph_option == "Solidité Défensive": val_h, val_a, title_y, color_range = h_stats['avg_conceded'], a_stats['avg_conceded'], "Buts Encaissés", ['#FF4B4B', '#FF8888']
    elif graph_option == "Volatilité (Chaos)": val_h, val_a, title_y, color_range = h_stats['volatility'], a_stats['volatility'], "Indice Chaos", ['#FFA500', '#FFD700']
    elif graph_option == "Forme": val_h, val_a, title_y = h_stats['form_score'], a_stats['form_score'], "Points Moyens"
    source = pd.DataFrame({'Équipe': [m_info['teams']['home']['name'], m_info['teams']['away']['name']], 'Valeur': [val_h, val_a]})
    base = alt.Chart(source).encode(
        x=alt.X('Valeur', axis=alt.Axis(grid=False, labelColor='#888', title=title_y)),
        y=alt.Y('Équipe', axis=alt.Axis(labelColor='white', title=None, labelFontWeight='bold')),
        color=alt.Color('Équipe', legend=None, scale=alt.Scale(range=color_range)),
        tooltip=['Équipe', 'Valeur']
    )
    st.altair_chart(alt.layer(base.mark_rule(size=3), base.mark_circle(size=250)).properties(height=250, background='transparent').configure_view(stroke=None), use_container_width=True)

    t1, t2, t3, t4 = st.tabs(["🔮 6ème Sens & Score Exact", "⚡ Stats & BTTS", "🛑 Discipline", "💰 Bankroll"])
    with t1:
        st.subheader("Vision du Futur : Simulation du Score")
        st.write("L'IA a simulé ce match **5000 fois**. Résultats probables :")
        c_score1, c_score2, c_score3 = st.columns(3)
        if len(future_scores) > 0: c_score1.metric("Scénario #1", future_scores[0][0])
        if len(future_scores) > 1: c_score2.metric("Scénario #2", future_scores[1][0])
        if len(future_scores) > 2: c_score3.metric("Scénario #3", future_scores[2][0])
    with t2:
        c_a, c_b = st.columns(2)
        c_a.info(f"**Domicile** : Clean Sheet {h_stats['clean_sheet_rate']:.0f}% | BTTS {h_stats['btts_rate']:.0f}%")
        c_b.info(f"**Extérieur** : Clean Sheet {a_stats['clean_sheet_rate']:.0f}% | BTTS {a_stats['btts_rate']:.0f}%")
    with t3:
        c_a, c_b = st.columns(2)
        c_a.write(f"Risque Penalty Domicile : **{'ÉLEVÉ' if h_stats['volatility'] > 1.4 else 'Faible'}**")
        c_b.write(f"Risque Penalty Extérieur : **{'ÉLEVÉ' if a_stats['volatility'] > 1.4 else 'Faible'}**")
    with t4:
        best_prob = max(probs)
        if best_prob > 0.65: st.success(f"Confiance IA MAX ({best_prob*100:.1f}%). Value Bet.")
        else: st.info(f"Confiance Moyenne ({best_prob*100:.1f}%).")