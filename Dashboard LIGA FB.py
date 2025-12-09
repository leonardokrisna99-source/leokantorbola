import streamlit as st
import pandas as pd
import os
import base64

st.set_page_config(page_title="Liga FB Dashboard", layout="wide")

# ==========================
# Mapping Nama
# ==========================
name_map = {
    "Leo": "Masjawa2",
    "Irzal": "Wenger",
    "KING FIRHAN": "~ Firhan Service Delivery",
    "Ulhaq": "Masjawa",
    "Putu": "Putu",
    "Handika": "r_dhiie",
    "Mas Pras": "Sarpy",
    "Danang": "BOOM-DNNG",
    "Bang WAnn": "Sumbar",
    "Rahman": "Gewinnen",
    "ical": "Sunda Empire",
    "Husen": "Madun",
    "Atalarix": "Masjawa3",
    "Mathew": "ccc",
    "Dey": "Kill.yahuud",
    "Kom": "Mummy's",
    "Prasalda": "Easywin",
    "Mas Aris": "Aries"
}

teams = list(name_map.keys())
LOGO_FOLDER = "logos"
MAX_LOGO_HEIGHT = 50
DATA_FILE = "matches_data.csv"

# ==========================
# Global CSS
# ==========================
page_style = """
<style>
body, .block-container {
    background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
    background-attachment: fixed;
}
h1,h2,h3,h4,h5 {
    text-align:center;
    font-family: 'Segoe UI','Comic Sans MS',Arial,sans-serif;
    color:#2a9d8f;
    text-shadow:2px 2px 5px rgba(0,0,0,0.2);
}
div[style*='border-radius:12px'] {
    transition: transform 0.4s, box-shadow 0.4s;
}
div[style*='border-radius:12px']:hover {
    transform: translateY(-7px) scale(1.02);
    box-shadow: 0px 12px 30px rgba(0,0,0,0.35);
}
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #c2e9fb 0%, #a1c4fd 100%);
}
.tooltip {
  position: relative;
  display: inline-block;
  cursor: pointer;
}
.tooltip .tooltiptext {
  visibility: hidden;
  width: 220px;
  background-color: rgba(0,0,0,0.8);
  color: #fff;
  text-align: left;
  padding: 6px;
  border-radius: 6px;
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.3s;
  font-size:12px;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
}
.progress-bar {
  height: 14px;
  border-radius: 7px;
  background: linear-gradient(90deg, #2a9d8f, #00bfff);
  transition: width 1s ease-in-out;
}
::-webkit-scrollbar { width:10px; }
::-webkit-scrollbar-thumb { background-color: rgba(42,157,143,0.7); border-radius:5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.1); }
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

st.title("⚽ LIGA FTTH ")
st.markdown("<h2>Update Jadwal & Klasemen Mingguan</h2>", unsafe_allow_html=True)

# ==========================
# Fungsi logo & card
# ==========================
def get_logo_base64(path):
    if os.path.exists(path):
        with open(path,"rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def team_card_schedule(home, away, home_score, away_score):
    home_logo = get_logo_base64(os.path.join(LOGO_FOLDER,f"{home}.png"))
    away_logo = get_logo_base64(os.path.join(LOGO_FOLDER,f"{away}.png"))
    home_html = f"<img src='data:image/png;base64,{home_logo}' style='height:{MAX_LOGO_HEIGHT}px; margin-right:8px; background:transparent;'/> {home}" if home_logo else home
    away_html = f"{away} <img src='data:image/png;base64,{away_logo}' style='height:{MAX_LOGO_HEIGHT}px; margin-left:8px; background:transparent;'/>" if away_logo else away
    home_score = 0 if home_score is None or pd.isna(home_score) else int(home_score)
    away_score = 0 if away_score is None or pd.isna(away_score) else int(away_score)
    score_html = f"<b>{home_score} - {away_score}</b>"
    card_html = f"""
    <div style='border:2px solid #ccc; border-radius:12px; padding:12px; margin-bottom:10px;
                background: linear-gradient(135deg, #fefefe, #e0f7fa);'>
        <div style='display:flex; justify-content:space-between; align-items:center; font-size:18px;'>
            <div style='flex:1; display:flex; justify-content:flex-start; align-items:center;'>{home_html}</div>
            <div style='flex:0.3; text-align:center; font-weight:bold; color:#2a9d8f; font-size:20px;'>{score_html}</div>
            <div style='flex:1; display:flex; justify-content:flex-end; align-items:center;'>{away_html}</div>
        </div>
    </div>
    """
    return card_html

def team_with_logo_class(team, bg_color=None):
    logo_path = os.path.join(LOGO_FOLDER,f"{team}.png")
    display_name = name_map.get(team, team)
    style_bg = f"background-color:{bg_color}; padding:2px 6px; border-radius:4px;" if bg_color else ""
    if os.path.exists(logo_path):
        encoded = base64.b64encode(open(logo_path,'rb').read()).decode()
        return f"<div style='display:flex; align-items:center; {style_bg}'><img src='data:image/png;base64,{encoded}' style='height:{MAX_LOGO_HEIGHT}px; margin-right:8px; background:transparent;'>{display_name}</div>"
    else:
        return f"<div style='{style_bg}'>{display_name}</div>"

# ==========================
# Round-robin generate
# ==========================
def generate_round_robin_fixed(team_list):
    teams_copy = team_list[:]
    if len(teams_copy) % 2 != 0: teams_copy.append("BYE")
    n = len(teams_copy)
    schedule = []
    for round_no in range(n-1):
        pairs=[]
        for i in range(n//2):
            home, away = teams_copy[i], teams_copy[-(i+1)]
            if home != "BYE" and away != "BYE":
                pairs.append({'round': round_no+1,'home':home,'away':away,'home_score':None,'away_score':None})
        teams_copy = [teams_copy[0]] + [teams_copy[-1]] + teams_copy[1:-1]
        schedule.append(pairs)
    schedule2 = []
    for round_matches in schedule:
        pairs=[]
        for m in round_matches:
            pairs.append({'round':m['round']+n-1,'home':m['away'],'away':m['home'],'home_score':None,'away_score':None})
        schedule2.append(pairs)
    all_matches = [m for round_matches in schedule for m in round_matches]+[m for round_matches in schedule2 for m in round_matches]
    df=pd.DataFrame(all_matches)
    df.reset_index(inplace=True)
    df.rename(columns={'index':'match_id'}, inplace=True)
    return df

# ==========================
# Load / buat data
# ==========================
if "matches" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.matches = pd.read_csv(DATA_FILE)
    else:
        st.session_state.matches = generate_round_robin_fixed(teams)
        st.session_state.matches.to_csv(DATA_FILE, index=False)

# ==========================
# Admin login
# ==========================
st.sidebar.title("🔑 Admin Panel")
ADMIN_PASSWORD = "admin123"
if "is_admin" not in st.session_state: st.session_state.is_admin = False
pw = st.sidebar.text_input("Password Admin:", type="password")
if st.sidebar.button("Login"):
    if pw == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        st.sidebar.success("Admin Mode Aktif! 🔥")
    else:
        st.sidebar.error("Password salah!")
is_admin = st.session_state.is_admin
st.sidebar.info("Mode: ADMIN" if is_admin else "Mode: VIEWER")

# ==========================
# Jadwal
# ==========================
st.header("📅 Jadwal Pertandingan")
round_select = st.selectbox("Pilih Minggu (Round)", sorted(st.session_state.matches['round'].unique()))
week_matches = st.session_state.matches[st.session_state.matches['round']==round_select]
for _, row in week_matches.iterrows():
    st.markdown(team_card_schedule(row['home'], row['away'], row['home_score'], row['away_score']), unsafe_allow_html=True)

# ==========================
# Input skor admin
# ==========================
if is_admin:
    st.header("✏️ Input / Edit Skor")
    rounds = st.selectbox("Pilih Minggu (Round)", sorted(st.session_state.matches['round'].unique()), key="input_round")
    matches_week = st.session_state.matches[st.session_state.matches['round']==rounds]
    for _, row in matches_week.iterrows():
        cols = st.columns([3,1,1,2])
        with cols[0]: st.markdown(f"**{row['home']} vs {row['away']}**")
        with cols[1]: hs = st.text_input(f"hs_{row['match_id']}", value=("" if pd.isna(row['home_score']) else str(int(row['home_score']))), key=f"hs_{row['match_id']}")
        with cols[2]: aw = st.text_input(f"aw_{row['match_id']}", value=("" if pd.isna(row['away_score']) else str(int(row['away_score']))), key=f"aw_{row['match_id']}")
        with cols[3]:
            if st.button("Simpan", key=f"save_{row['match_id']}"):
                try:
                    hs_val = int(float(hs)) if hs!="" else None
                    aw_val = int(float(aw)) if aw!="" else None
                except:
                    st.error("Skor harus angka!")
                    st.stop()
                st.session_state.matches.at[row['match_id'],'home_score']=hs_val
                st.session_state.matches.at[row['match_id'],'away_score']=aw_val
                st.session_state.matches.to_csv(DATA_FILE,index=False)
                st.success(f"Skor {row['home']} vs {row['away']} tersimpan!")

# ==========================
# Hitung klasemen
# ==========================
def compute_standings(df, team_list):
    table=pd.DataFrame({'Team':team_list,'Main':0,'Menang':0,'Seri':0,'Kalah':0,'GF':0,'GA':0,'GD':0,'Poin':0})
    for _, m in df.iterrows():
        if pd.isna(m['home_score']) or pd.isna(m['away_score']): continue
        h,a = m['home'], m['away']; hs,aw=int(m['home_score']),int(m['away_score'])
        table.loc[table.Team==h,'Main']+=1; table.loc[table.Team==a,'Main']+=1
        table.loc[table.Team==h,'GF']+=hs; table.loc[table.Team==h,'GA']+=aw
        table.loc[table.Team==a,'GF']+=aw; table.loc[table.Team==a,'GA']+=hs
        if hs>aw: table.loc[table.Team==h,'Menang']+=1; table.loc[table.Team==h,'Poin']+=3; table.loc[table.Team==a,'Kalah']+=1
        elif aw>hs: table.loc[table.Team==a,'Menang']+=1; table.loc[table.Team==a,'Poin']+=3; table.loc[table.Team==h,'Kalah']+=1
        else: table.loc[table.Team==h,'Seri']+=1; table.loc[table.Team==a,'Seri']+=1; table.loc[table.Team==h,'Poin']+=1; table.loc[table.Team==a,'Poin']+=1
    table['GD'] = table['GF'] - table['GA']
    return table.sort_values(['Poin','GD','GF'], ascending=False).reset_index(drop=True)

standings = compute_standings(st.session_state.matches, teams)
max_poin = standings['Poin'].max()
bottom_emojis=["😵‍💫","🤯","🪦"]
top_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
bottom_color = "#ff4d4d"
middle_color = "#e0f7fa"

# ==========================
# Highlight top scorer
# ==========================
st.header("🔥 Highlight Mingguan")
rounds_current = st.session_state.matches['round'].max()
week_matches = st.session_state.matches[st.session_state.matches['round']==rounds_current]
goal_count = {}
for _,m in week_matches.iterrows():
    if pd.isna(m['home_score']) or pd.isna(m['away_score']): continue
    goal_count[m['home']] = goal_count.get(m['home'],0)+int(m['home_score'])
    goal_count[m['away']] = goal_count.get(m['away'],0)+int(m['away_score'])
top_goals = max(goal_count.values()) if goal_count else 0
top_scorers = [team for team,g in goal_count.items() if g==top_goals] if top_goals>0 else []
st.subheader(f"🥅 Top Scorer Minggu Ini: {', '.join(top_scorers)} ({top_goals} gol)" if top_scorers else "🥅 Belum ada gol")

# ==========================
# Klasemen premium lengkap
# ==========================
st.header("🏆 Klasemen Lengkap Liga FB")
for idx, row in standings.iterrows():
    # Warna
    if idx < 3: bg_color = top_colors[idx]
    elif idx >= len(standings)-3: bg_color = bottom_color
    else: bg_color = middle_color
    # Medal / emoji
    medal = ["🥇","🥈","🥉"][idx] if idx < 3 else ""
    emoji = bottom_emojis[idx-(len(standings)-3)] if idx >= len(standings)-3 else ""
    # Progress bar
    bar_width = int((row['Poin']/max_poin)*100) if max_poin > 0 else 0
    display_name = team_with_logo_class(row['Team'])
    tooltip_info = f"""Menang: {row['Menang']}
Seri: {row['Seri']}
Kalah: {row['Kalah']}
GF: {row['GF']}
GA: {row['GA']}
GD: {row['GD']}
Poin: {row['Poin']}
Main: {row['Main']}"""
    st.markdown(f"""
    <div style='display:flex; flex-direction:column; padding:12px; margin-bottom:12px;
                border-radius:12px; background:{bg_color};
                box-shadow: 0px 4px 12px rgba(0,0,0,0.15);'>
        <div style='display:flex; justify-content:space-between; align-items:center; font-size:16px;'>
            <div style='flex:0.05; font-weight:bold;'>{idx+1}</div>
            <div class="tooltip" style='flex:0.3; display:flex; align-items:center; font-weight:bold; font-size:16px;'>{medal} {display_name}
                <span class="tooltiptext">{tooltip_info}</span>
            </div>
            <div style='flex:0.65; display:flex; justify-content:space-between; font-size:14px;'>
                <span>Main: {row['Main']}</span>
                <span>Menang: {row['Menang']}</span>
                <span>Seri: {row['Seri']}</span>
                <span>Kalah: {row['Kalah']}</span>
                <span>GF: {row['GF']}</span>
                <span>GA: {row['GA']}</span>
                <span>GD: {row['GD']}</span>
                <span>Poin: {row['Poin']} {emoji}</span>
            </div>
        </div>
        <div class="progress-bar" style='width:{bar_width}%; margin-top:4px;'></div>
    </div>
    """, unsafe_allow_html=True)
