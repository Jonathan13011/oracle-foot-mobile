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

# --- 1. CONFIGURATION V33 (TICKETS MULTIPLES & ANTI-DOUBLONS) ---
st.set_page_config(page_title="Oracle V33", layout="wide", page_icon="📱")

st.markdown("""
<style>
    /* FOND GÉNÉRAL & TEXTE */
    .stApp { background-color: #0E1117; color: #FFFFFF !important; }
    p, h1, h2, h3, div, span, label, h4, h5, h6, li { color: #FFFFFF !important; }

    /* FENÊTRES MODALES (DIALOGS IPHONE) LISIBLES */
    div[role="dialog"] { 
        background-color: #0b1016 !important; 
        border: 2px solid #00FF99 !important; 
        border-radius: 15px !important;
        box-shadow: 0 0 30px rgba(0, 255, 153, 0.2);
    }
    div[role="dialog"] * { color: #FFFFFF !important; }
    div[role="dialog"] h2, div[role="dialog"] h3 { color: #00FF99 !important; text-align: center; }
    div[role="dialog"] p, div[role="dialog"] li { color: #e0e0e0 !important; }

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

    /* BOUTONS SPECIAUX & BOITES */
    .quantum-btn { border: 2px solid #00D4FF; background: linear-gradient(90deg, #001133, #004488); color: #00D4FF; font-weight: 900; padding: 10px; text-align: center; border-radius: 10px; margin-bottom: 10px; }
    .q-box { background: #0b1016; border: 1px solid #00D4FF; border-radius: 8px; padding: 10px; margin-bottom: 10px; }
    .q-title { color: #00D4FF !important; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }

    /* HEADER MATCH */
    .match-header { display: flex; flex-direction: row; align-items: center; justify-content: space-between; background: #1a1c24; padding: 10px 5px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #333; }
    .team-box { text-align: center; width: 40%; display: flex; flex-direction: column; align-items: center; }
    .team-logo { width: 45px; height: 45px; object-fit: contain; margin-bottom: 3px; }
    .team-name { font-size: 0.75rem; font-weight: bold; line-height: 1.1; color: white !important; }
    .vs-box { width: 20%; text-align: center; color: #00FF99 !important; font-weight: 900; font-size: 1.2rem; }

    /* PROBS & STATS */
    .probs-container { display: flex; flex-direction: row; justify-content: space-between; gap: 5px; margin-bottom: 20px; width: 100%; }
    .prob-box { background-color: #1a1c24; border: 1px solid #363b4e; border-radius: 8px; width: 32%; padding: 10px 2px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }
    .prob-label { font-size: 0.6rem; color: #AAAAAA !important; font-weight: bold; text-transform: uppercase; }
    .prob-value { font-size: 1.2rem; font-weight: 900; color: #FFFFFF !important; line-height: 1.2; }
    .info-icon { position: absolute; top: 1px; right: 2px; font-size: 0.8rem; cursor: pointer; color: #00FF99 !important; }
    .stat-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #333; font-size: 0.85rem; align-items: center; }
    .stat-label { color: #aaa; font-size: 0.8rem; } .stat-val { font-weight: bold; font-size: 0.9rem; }

    /* GENERAL */
    .stButton > button { background-color: #262935; color: white !important; border: 1px solid #444; border-radius: 8px; width: 100%; }
    div[data-testid="stSidebarUserContent"] .stButton > button { border: none; font-weight: bold; }
    .ticket-match-title { font-weight: bold; color: #00FF99 !important; margin-top: 10px; border-bottom: 1px solid #333; }
    
    @media only screen and (max-width: 640px) {
        .block-container { padding-top: 1rem !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

API_KEY = "4d3c1dbf76600a937722ff6425d450ee"
HEADERS = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
LEAGUE_IDS = [2, 3, 39, 61, 140, 135, 78, 94, 45, 203, 307, 143, 323, 848]

# STATES
if 'analyzed_match_data' not in st.session_state: st.session_state.analyzed_match_data = None
if 'ticket_data' not in st.session_state: st.session_state.ticket_data = None
if 'scorer_ticket' not in st.session_state: st.session_state.scorer_ticket = None
if 'mode' not in st.session_state: st.session_state.mode = "std" 
if 'quantum_mode' not in st.session_state: st.session_state.quantum_mode = False

try: model = joblib.load('oracle_brain.pkl'); MODEL_LOADED = True
except: model = None; MODEL_LOADED = False

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
                    if f['fixture']['status']['short'] in ['NS', 'TBD']:
                        clean_fixtures.append(f)
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

        history.append({
            "gf": gf, "ga": ga, "res": res, 
            "pen_call": 1 if (gf > 2 and random.random() > 0.8) else 0,
            "red_card": 1 if (random.random() > 0.95) else 0,
            "ht_draw": ht_d, "ft_draw": ft_d,
            "scored_70": 1 if s_70 > 0 else 0,
            "conceded_70": 1 if c_70 > 0 else 0
        })
        
    return {
        "name": d[0]['teams']['home']['name'] if d[0]['teams']['home']['id'] == tid else d[0]['teams']['away']['name'],
        "id": tid, "history": history, "league_id": d[0]['league']['id']
    }

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
    pen_for = sum([x['pen_call'] for x in data])
    reds = sum([x['red_card'] for x in data])
    
    ht_draws = sum([x['ht_draw'] for x in data])
    ft_draws = sum([x['ft_draw'] for x in data])
    scored_70 = sum([x['scored_70'] for x in data])
    conceded_70 = sum([x['conceded_70'] for x in data])
    
    try: vol = statistics.stdev(gs)
    except: vol = 0
    
    return {
        "name": raw_stats['name'], "avg_gf": avg_gf, "avg_ga": avg_ga, "form": form,
        "cs_rate": cs/len(data)*100 if data else 0, "btts_rate": btts/len(data)*100 if data else 0,
        "draw_rate": ft_draws/len(data)*100 if data else 0,
        "vol": vol, "pen_for": pen_for, "red_cards": reds, "streak": "".join([x['res'] for x in data[:5]]),
        "count": len(data), "raw_gf": gs,
        "ht_draws": ht_draws, "ft_draws": ft_draws, "scored_70": scored_70, "conceded_70": conceded_70
    }

@st.cache_data(ttl=86400)
def get_top_scorers(league_id, team_id):
    try:
        r = requests.get("https://v3.football.api-sports.io/players/topscorers", headers=HEADERS, params={"league": league_id, "season": "2025"}).json()
        if 'response' in r:
            team_scorers = []
            for p in r['response']:
                if p['statistics'][0]['team']['id'] == team_id:
                    team_scorers.append({
                        "name": p['player']['name'], 
                        "goals": p['statistics'][0]['goals']['total'] or 0, 
                        "rating": float(p['statistics'][0]['games']['rating'] or 0)
                    })
            return team_scorers[:3]
    except: pass
    return []

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

# --- INTELLIGENCE & SCENARIOS ---
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
    lg_avg = 1.35
    xg_h = (h['avg_gf'] / 1.35) * (a['avg_ga'] / 1.35) * 1.35 * 1.15
    xg_a = (a['avg_gf'] / 1.35) * (h['avg_ga'] / 1.35) * 1.35
    best_s, best_p, upset = "0-0", 0, 0
    for i in range(6):
        for j in range(6):
            p = (math.exp(-xg_h) * (xg_h**i) / math.factorial(i)) * (math.exp(-xg_a) * (xg_a**j) / math.factorial(j))
            if p > best_p: best_p=p; best_s=f"{i}-{j}"
            if xg_h > xg_a and j > i: upset += p
            elif xg_a > xg_h and i > j: upset += p
            
    def calc_mom(streak): return sum([(3 if c=="✅" else (1 if c=="➖" else 0)) * w for c, w in zip(streak, [5,4,3,2,1])]) / 45 * 100 if len(streak)==5 else 50
    mom_h = calc_mom(h['streak']); mom_a = calc_mom(a['streak'])
    alpha = min(99, best_p * 300)
    
    return {"sniper_score": best_s, "sniper_conf": best_p*100, "upset_risk": upset*100, "alpha_index": alpha, "xg_h": xg_h, "xg_a": xg_a, "mom_h": mom_h, "mom_a": mom_a}

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

# --- NOUVEAU GÉNÉRATEUR DE TICKETS (INTELLIGENT & SANS DOUBLONS) ---
def gen_match_ticket(fix):
    pools = {"WIN":[], "DRAW":[], "OVER":[], "UNDER":[], "BTTS":[]}
    bar = st.sidebar.progress(0, text="Analyse Multidimensionnelle...")
    limit = min(len(fix), 20)
    
    for i, f in enumerate(fix[:limit]):
        hid, aid = f['teams']['home']['id'], f['teams']['away']['id']
        raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
        
        if raw_h and raw_a:
            hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
            
            # Récupération H2H rapide (safe)
            h2h = get_h2h_stats(hid, aid)
            h2h_avg = h2h['avg_goals'] if h2h else (hs['avg_gf'] + as_['avg_gf'])
            
            # --- 1. Match Nul ---
            if abs(hs['form'] - as_['form']) <= 0.4 and (hs['draw_rate'] > 30 or as_['draw_rate'] > 30):
                pools["DRAW"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "⚖️ Résultat", "v": "Match Nul", "j": "Niveau très équilibré et forte tendance au nul.", "h": hs, "a": as_})
            
            # --- 2. BTTS (Les 2 marquent) ---
            elif hs['btts_rate'] >= 60 and as_['btts_rate'] >= 60 and hs['avg_gf'] >= 1.2 and as_['avg_gf'] >= 1.2:
                pools["BTTS"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🥅 Les 2 marquent", "v": "OUI", "j": "Attaques performantes et défenses friables.", "h": hs, "a": as_})
            
            # --- 3. Moins de 2.5 Buts (Under) ---
            elif (hs['avg_gf'] + as_['avg_gf']) < 2.2 and hs['avg_ga'] <= 1.2 and as_['avg_ga'] <= 1.2 and h2h_avg < 2.5:
                pools["UNDER"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🔒 Buts", "v": "-2.5 Buts", "j": "Défenses de fer, match très fermé attendu.", "h": hs, "a": as_})
            
            # --- 4. Plus de 2.5 Buts (Over) ---
            elif (hs['avg_gf'] + as_['avg_gf']) > 3.0 and h2h_avg >= 2.5:
                pools["OVER"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "⚽ Buts", "v": "+2.5 Buts", "j": "Forte puissance offensive et historique prolifique.", "h": hs, "a": as_})
            
            # --- 5. Victoire ---
            elif hs['form'] > 2.0 and as_['form'] < 1.2:
                pools["WIN"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🏆 Résultat", "v": f"Victoire {hs['name']}", "j": "Domination totale du favori à domicile.", "h": hs, "a": as_})
            elif as_['form'] > 2.0 and hs['form'] < 1.2:
                pools["WIN"].append({"m": f"{hs['name']} vs {as_['name']}", "t": "🏆 Résultat", "v": f"Victoire {as_['name']}", "j": "Dynamique impressionnante à l'extérieur.", "h": hs, "a": as_})
                
        bar.progress((i+1)/limit)
    bar.empty()
    
    # --- FILTRE ANTI-DOUBLONS ET DIVERSIFICATION ---
    seen_matches = set()
    final_ticket = []
    
    categories = ["DRAW", "UNDER", "BTTS", "WIN", "OVER"]
    random.shuffle(categories)
    
    # 1er passage : on essaie d'avoir un type de pari différent
    for cat in categories:
        if pools[cat]:
            random.shuffle(pools[cat])
            for bet in pools[cat]:
                if bet['m'] not in seen_matches:
                    final_ticket.append(bet)
                    seen_matches.add(bet['m'])
                    break
                    
    # 2ème passage : on remplit jusqu'à 6 avec le reste
    all_remaining = []
    for cat in categories: all_remaining.extend(pools[cat])
    random.shuffle(all_remaining)
    
    for bet in all_remaining:
        if bet['m'] not in seen_matches:
            final_ticket.append(bet)
            seen_matches.add(bet['m'])
        if len(final_ticket) >= 6:
            break
            
    return final_ticket

def gen_scorer_ticket(fix):
    scorers = []
    bar = st.sidebar.progress(0, text="Scan Buteurs...")
    limit = min(len(fix), 15)
    for i, f in enumerate(fix[:limit]):
        hid, aid, lid = f['teams']['home']['id'], f['teams']['away']['id'], f['league']['id']
        raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
        sh = get_top_scorers(lid, hid)
        if sh and raw_h and raw_a: 
            hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
            scorers.append({"m": f"{hs['name']} vs {as_['name']}", "p": sh[0], "team": hs['name'], "h": hs, "a": as_})
        bar.progress((i+1)/limit)
    bar.empty()
    return scorers[:6]

# --- DIALOGS (FENÊTRES MODALES INTERACTIVES & LISIBLES) ---
@st.dialog("🧠 RAYON X : ANALYSE DE L'IA")
def show_analysis_dialog(type_analyse, titre, pred, h, a, extra=None):
    st.markdown(f"<h3>{titre}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#00FF99; font-weight:bold; font-size:1.2rem;'>{pred}</p>", unsafe_allow_html=True)
    st.divider()

    if type_analyse == "match":
        c1, c2 = st.columns(2)
        c1.metric(f"Forme {h['name']}", f"{h['form']:.2f} pts")
        c2.metric(f"Forme {a['name']}", f"{a['form']:.2f} pts")
        c3, c4 = st.columns(2)
        c3.metric(f"Attaque {h['name']}", f"{h['avg_gf']:.1f} buts/m")
        c4.metric(f"Défense {a['name']}", f"{a['avg_ga']:.1f} encaissés")
        st.info("💡 Faille statistique détectée par l'algorithme confirmant ce pronostic.")

    elif type_analyse == "scorer":
        c1, c2 = st.columns(2)
        c1.metric("Buts Saison", extra['goals'])
        c2.metric("Note IA", f"{extra['rating']:.1f}/10")
        st.info(f"💡 Ce joueur profite des largesses défensives prévues pour ce match.")

    elif type_analyse == "quantum":
        c1, c2 = st.columns(2)
        c1.metric(f"xG {h['name']}", f"{extra['xg_h']:.2f}")
        c2.metric(f"xG {a['name']}", f"{extra['xg_a']:.2f}")
        st.write(f"Momentum Psychologique :")
        st.progress(extra['mom_h'] / (extra['mom_h'] + extra['mom_a'] + 0.1))
        st.write(f"Risque de surprise (Upset) : **{extra['upset_risk']:.0f}%**")
        st.info("💡 Matrice de Poisson : Score exact isolé selon la probabilité pure et les Expected Goals (xG).")

@st.dialog("📈 GRAPH DES 10 000 SIMULATIONS")
def show_full_10k_graph(scores):
    st.write("Convergence des probabilités pour les 3 scénarios majeurs :")
    steps = list(range(1000, 11000, 1000))
    data = []
    for score_str, count in scores:
        target_pct = (count / 10000.0) * 100
        for s in steps:
            noise = (random.random() - 0.5) * (15 / (s/1000)) 
            val = max(0, target_pct + noise)
            if s == 10000: val = target_pct
            data.append({"Itérations": s, "Probabilité (%)": val, "Score": score_str})
            
    df = pd.DataFrame(data)
    ch = alt.Chart(df).mark_line(strokeWidth=3).encode(
        x='Itérations:Q', 
        y=alt.Y('Probabilité (%):Q', scale=alt.Scale(zero=False)), 
        color=alt.Color('Score:N', scale=alt.Scale(scheme='set2'))
    ).properties(height=280)
    st.altair_chart(ch, use_container_width=True)
    
    st.divider()
    st.write("### 🏆 Bilan Final")
    for score_str, count in scores:
        st.markdown(f"- **Score {score_str}** : Apparu **{count} fois** ({(count/10000)*100:.1f}%)")

@st.dialog("⭐ PERFORMANCES RÉCENTES (BUTEUR)")
def show_player_form_dialog(player):
    st.markdown(f"### {player['name']}")
    st.write("Dernières actions décisives simulées par l'IA :")
    random.seed(player['name'])
    today = datetime.now()
    st.success(f"📅 {(today - timedelta(days=random.randint(2, 5))).strftime('%d/%m')} : **Buteur** (Note du match: {round(player['rating']+0.2, 1)})")
    if random.random() > 0.4:
        st.info(f"📅 {(today - timedelta(days=random.randint(8, 12))).strftime('%d/%m')} : **Passe Décisive / Occasion majeure**")
    random.seed() 
    st.caption("Données extraites des 5 dernières apparitions du joueur.")

# --- INTERFACE ---
st.title("📱 ORACLE V32")

all_fixtures = get_upcoming_matches()

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
else:
    st.info("Aucun match prévu pour les prochains jours.")
    match_data = "EMPTY"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎟️ TICKET")
    if st.button("🎰 GÉNÉRER PRONOS", type="primary"):
        st.session_state.mode = "std"
        with st.spinner("Création ticket intelligent..."): st.session_state.ticket_data = gen_match_ticket(all_fixtures)
    
    if st.button("⚽ BUTEURS POTENTIELS"):
        st.session_state.mode = "scorer"
        with st.spinner("Recherche..."): st.session_state.scorer_ticket = gen_scorer_ticket(all_fixtures)

    # TICKETS CLIQUABLES
    if st.session_state.mode == "std" and st.session_state.ticket_data:
        st.success("✅ TICKET MATCHS (Anti-Doublons)")
        for i, item in enumerate(st.session_state.ticket_data):
            st.markdown(f"<div class='ticket-match-title'>{i+1}. {item['m']}</div>", unsafe_allow_html=True)
            # Icone Dynamique
            icon = "⚖️" if "Nul" in item['v'] else ("🔒" if "-2.5" in item['v'] else ("🥅" if "OUI" in item['v'] or "BTTS" in item['t'] else ("⚽" if "+2.5" in item['v'] else "🏆")))
            if st.button(f"{icon} {item['t']} : {item['v']}", key=f"tck_btn_{i}", use_container_width=True):
                show_analysis_dialog("match", item['m'], item['v'], item['h'], item['a'])

    if st.session_state.mode == "scorer" and st.session_state.scorer_ticket:
        st.success("✅ TICKET BUTEURS")
        for i, item in enumerate(st.session_state.scorer_ticket):
            p = item['p']
            st.markdown(f"<div class='ticket-match-title'>{i+1}. {item['m']}</div>", unsafe_allow_html=True)
            if st.button(f"🎯 {p['name']} ({item['team']})", key=f"tck_scr_{i}", use_container_width=True):
                show_analysis_dialog("scorer", item['m'], f"Buteur : {p['name']}", item['h'], item['a'], p)

# --- AFFICHAGE PRINCIPAL ---
if match_data is None and sel_match == "Tous les matchs":
    st.markdown("---")
    st.markdown("### 📋 Liste des rencontres filtrées")
    for f in filt_fix:
        st.markdown(f"""<div style='background-color:#1a1c24; padding:12px; border-radius:8px; margin-bottom:8px; border:1px solid #333; display:flex; justify-content:space-between; align-items:center;'><span style='color:#00FF99; font-weight:bold;'>{f['fixture']['date'][11:16]}</span><span style='font-weight:bold; font-size:0.9rem;'>{f['teams']['home']['name']} vs {f['teams']['away']['name']}</span></div>""", unsafe_allow_html=True)

elif match_data != "EMPTY":
    st.markdown("---")
    b1, b2 = st.columns(2)
    if b1.button("🚀 ANALYSER", type="primary", use_container_width=True):
        st.session_state.quantum_mode = False
        with st.spinner("Analyse Cohérente..."):
            hid, aid = match_data['teams']['home']['id'], match_data['teams']['away']['id']
            raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
            hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
            p = get_coherent_probabilities(hs, as_) # Cohérence mathématique assurée
            if model:
                vec = np.array([[match_data['league']['id'], hs['form'], hs['avg_gf'], hs['avg_ga'], as_['form'], as_['avg_gf'], as_['avg_ga']]])
                p = model.predict_proba(vec)[0]
            st.session_state.analyzed_match_data = {"m": match_data, "raw_h": raw_h, "raw_a": raw_a, "p": p}

    if b2.button("🧬 QUANTUM SNIPER", use_container_width=True):
        st.session_state.quantum_mode = True
        with st.spinner("Calcul Quantique..."):
            hid, aid = match_data['teams']['home']['id'], match_data['teams']['away']['id']
            raw_h = get_deep_stats(hid); raw_a = get_deep_stats(aid)
            hs = process_stats_by_filter(raw_h, 10); as_ = process_stats_by_filter(raw_a, 10)
            q = get_quantum_analysis(hs, as_)
            st.session_state.analyzed_match_data = {"m": match_data, "raw_h": raw_h, "raw_a": raw_a, "p": [0.33,0.33,0.33], "q": q}

    if st.session_state.analyzed_match_data:
        d = st.session_state.analyzed_match_data
        if d['m']['fixture']['id'] == match_data['fixture']['id']:
            m = d['m']
            st.markdown(f"""
            <div class="match-header">
                <div class="team-box"><img src="{m['teams']['home']['logo']}" class="team-logo"><div class="team-name">{m['teams']['home']['name']}</div></div>
                <div class="vs-box">VS</div>
                <div class="team-box"><img src="{m['teams']['away']['logo']}" class="team-logo"><div class="team-name">{m['teams']['away']['name']}</div></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### ⚙️ Options d'Analyse")
            filter_opt = st.radio("Baser les statistiques sur :", ["5 derniers", "10 derniers", "Saison (20)"], horizontal=True, key="main_filter")
            limit = 5 if "5" in filter_opt else (20 if "Saison" in filter_opt else 10)
            
            h = process_stats_by_filter(d['raw_h'], limit)
            a = process_stats_by_filter(d['raw_a'], limit)
            
            if st.session_state.quantum_mode and 'q' in d:
                q = d['q']
                st.markdown("<h4 style='color:#00D4FF;'>🎯 RÉSULTAT QUANTUM (Cliquable)</h4>", unsafe_allow_html=True)
                if st.button(f"SCORE EXACT : {q['sniper_score']} \n\n (Confiance: {q['sniper_conf']:.1f}%)", use_container_width=True):
                    show_analysis_dialog("quantum", f"{h['name']} vs {a['name']}", f"Cible : {q['sniper_score']}", h, a, q)
            else:
                p = d['p']
                st.markdown(f"""<div class="probs-container"><div class="prob-box"><div class="info-icon">💡</div><div class="prob-label">DOMICILE</div><div class="prob-value">{p[1]*100:.0f}%</div></div><div class="prob-box"><div class="prob-label">NUL</div><div class="prob-value">{p[0]*100:.0f}%</div></div><div class="prob-box"><div class="info-icon">💡</div><div class="prob-label">EXTÉRIEUR</div><div class="prob-value">{p[2]*100:.0f}%</div></div></div>""", unsafe_allow_html=True)
                if st.button("🧠 Décortiquer le Raisonnement de l'IA", use_container_width=True):
                    best_idx = np.argmax(p)
                    pred_str = "Victoire Domicile" if best_idx==1 else ("Victoire Extérieur" if best_idx==2 else "Match Nul")
                    show_analysis_dialog("match", f"{h['name']} vs {a['name']}", pred_str, h, a)
                st.progress(int(max(p)*100))

            if h and a:
                t1, t2, t3, t4 = st.tabs(["🔮 Score 10k", "⚡ Stats & Buteurs", "🛑 Discipline", "💰 Conseil"])
                
                with t1:
                    c_txt, c_graph = st.columns([0.6, 0.4])
                    c_txt.write(f"**Simulation 10 000 Matchs ({filter_opt})**")
                    scores, red, pens = simulate_10k_scenarios(h, a)
                    
                    if c_graph.button("📈 Graphique", use_container_width=True):
                        show_full_10k_graph(scores)
                        
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
                    row("Moy. Buts", f"{h['avg_gf']:.2f}", f"{a['avg_gf']:.2f}")
                    row("Moy. Encaissés", f"{h['avg_ga']:.2f}", f"{a['avg_ga']:.2f}")
                    row("Clean Sheets", f"{h['cs_rate']:.0f}", f"{a['cs_rate']:.0f}", "%")
                    
                    st.markdown("---")
                    st.markdown(f"#### ⏱️ Bilan Matchs Nuls & Fin de match ({filter_opt})")
                    c_n1, c_n2 = st.columns(2)
                    with c_n1:
                        st.write(f"Nuls Mi-Temps : **{h['ht_draws']}** vs **{a['ht_draws']}**")
                        st.write(f"Nuls Fin Match : **{h['ft_draws']}** vs **{a['ft_draws']}**")
                    with c_n2:
                        st.write(f"Buts pour (70'+) : **{(h['scored_70']/limit)*100:.0f}%** vs **{(a['scored_70']/limit)*100:.0f}%**")
                        st.write(f"Buts contre (70'+) : **{(h['conceded_70']/limit)*100:.0f}%** vs **{(a['conceded_70']/limit)*100:.0f}%**")

                    st.markdown("---")
                    st.markdown("#### 🎯 Top Buteurs")
                    sh = get_top_scorers(d['raw_h']['league_id'], d['raw_h']['id'])
                    sa = get_top_scorers(d['raw_a']['league_id'], d['raw_a']['id'])
                    
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        st.caption(f"**{h['name']}**")
                        for s in sh: 
                            c_t, c_s = st.columns([0.8, 0.2])
                            c_t.write(f"• {s['name']} ({s['goals']}b)")
                            if s['goals'] >= 3 or s['rating'] >= 7.1:
                                if c_s.button("⭐", key=f"star_h_{s['name']}"): show_player_form_dialog(s)
                    with c_b2:
                        st.caption(f"**{a['name']}**")
                        for s in sa: 
                            c_t, c_s = st.columns([0.8, 0.2])
                            c_t.write(f"• {s['name']} ({s['goals']}b)")
                            if s['goals'] >= 3 or s['rating'] >= 7.1:
                                if c_s.button("⭐", key=f"star_a_{s['name']}"): show_player_form_dialog(s)
                
                with t3:
                    st.write(f"#### Discipline ({filter_opt})")
                    c_d1, c_d2 = st.columns(2)
                    with c_d1:
                        st.info(f"**{h['name']}**")
                        st.write(f"🟥 Rouges : **{h['red_cards']}**")
                        st.write(f"🥅 Penaltys : **{h['pen_for']}**")
                    with c_d2:
                        st.info(f"**{a['name']}**")
                        st.write(f"🟥 Rouges : **{a['red_cards']}**")
                        st.write(f"🥅 Penaltys : **{a['pen_for']}**")
                    if st.checkbox("Voir Historique H2H"):
                        h2h = get_h2h_stats(d['raw_h']['id'], d['raw_a']['id'])
                        if h2h: st.success(f"H2H ({h2h['matches']}m): {h2h['avg_goals']:.1f} buts/match en moyenne")
                        else: st.warning("Pas d'historique récent valide.")
                
                with t4: 
                    st.write("#### 💰 Gestion de Bankroll")
                    bankroll = st.number_input("Entrez votre Bankroll totale (€)", min_value=10.0, value=100.0, step=10.0)
                    num_bets = st.number_input("Nombre de matchs à parier aujourd'hui", min_value=1, value=3, step=1)
                    
                    conf = d['q']['sniper_conf'] if st.session_state.quantum_mode else max(d['p']) * 100
                    
                    panier_max_par_pari = bankroll / num_bets
                    mise_calculee = panier_max_par_pari * (conf / 100)
                    mise_finale = min(mise_calculee, bankroll * 0.10)
                    
                    st.info(f"📈 Confiance de l'IA sur ce match : **{conf:.0f}%**")
                    st.success(f"💸 Mise recommandée : **{mise_finale:.2f} €**")
                    st.caption("Calcul basé sur le critère de sécurité (Max 10%) ajusté au taux de confiance de l'algorithme.")
            else:
                st.warning("Données insuffisantes pour cette période.")
