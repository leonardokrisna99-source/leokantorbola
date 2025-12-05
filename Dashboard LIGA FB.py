import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Liga FB Dashboard", layout="wide")

# ==========================
# Background & CSS
# ==========================
page_bg_img = """
<style>
body {
background-image: url('https://images.unsplash.com/photo-1571456408655-c06f21b9a1d2?auto=format&fit=crop&w=1470&q=80');
background-size: cover;
background-attachment: fixed;
background-repeat: no-repeat;
background-position: center;
}
.stApp {
    background-color: rgba(255,255,255,0.95);
    padding: 1rem;
    border-radius: 10px;
}
h1, h2, h3 { text-align: center; color: #222; }
table { border-collapse: collapse; width: 100%; }
th, td { padding: 0.5rem 0.8rem; text-align: center; border: 1px solid #ddd; }
tr:nth-child(even) {background-color: rgba(0,0,0,0.03);}
th { background-color: rgba(0,0,0,0.1); font-weight: bold; }
.top1 {background-color: #ffd700; font-weight:bold;}
.top2 {background-color: #c0c0c0; font-weight:bold;}
.top3 {background-color: #cd7f32; font-weight:bold;}
.bottom3 {background-color: rgba(255,0,0,0.1); font-weight:bold;}
.bar { height: 15px; background-color: #4CAF50; border-radius: 5px; }
.top_scorer {background-color: rgba(255,255,0,0.3);}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# ==========================
# Daftar Tim
# ==========================
teams = [
    "Leo", "Irzal", "KING FIRHAN", "Ulhaq", "Putu", "Handika", "Mas Pras",
    "Danang", "Bang WAnn", "Rahman", "ical", "Husen", "Atalarix", "Mathew",
    "Dey", "Kom", "Prasalda"
]

# ==========================
# File CSV untuk penyimpanan
# ==========================
DATA_FILE = "matches_data.csv"

# ==========================
# Generate Round Robin
# ==========================
def generate_round_robin_fixed(team_list):
    teams_copy = team_list[:]
    if len(teams_copy) % 2 != 0:
        teams_copy.append("BYE")

    n = len(teams_copy)
    schedule = []

    for round_no in range(n - 1):
        pairs = []
        for i in range(n // 2):
            home, away = teams_copy[i], teams_copy[-(i + 1)]
            if home != "BYE" and away != "BYE":
                pairs.append({
                    'round': round_no + 1,
                    'home': home,
                    'away': away,
                    'home_score': None,
                    'away_score': None
                })

        teams_copy = [teams_copy[0]] + [teams_copy[-1]] + teams_copy[1:-1]
        schedule.append(pairs)

    # Putaran kedua (home-away dibalik)
    schedule2 = []
    for round_matches in schedule:
        pairs = []
        for m in round_matches:
            pairs.append({
                'round': m['round'] + n - 1,
                'home': m['away'],
                'away': m['home'],
                'home_score': None,
                'away_score': None
            })
        schedule2.append(pairs)

    all_matches = (
        [m for round_matches in schedule for m in round_matches] +
        [m for round_matches in schedule2 for m in round_matches]
    )

    df = pd.DataFrame(all_matches)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'match_id'}, inplace=True)
    return df

# ==========================
# Load Data (Persistent)
# ==========================
if "matches" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.matches = pd.read_csv(DATA_FILE)
    else:
        st.session_state.matches = generate_round_robin_fixed(teams)
        st.session_state.matches.to_csv(DATA_FILE, index=False)

# ==========================
# Judul
# ==========================
st.title("⚽ Liga FB (FTTH Berlaga)")
st.write("Input skor → klasemen update otomatis")

# ==========================
# Input skor per minggu
# ==========================
st.header("Input Skor Pertandingan per Minggu")
rounds = st.selectbox("Pilih Minggu (Round)", sorted(st.session_state.matches['round'].unique()))
matches_week = st.session_state.matches[st.session_state.matches['round'] == rounds]

for _, row in matches_week.iterrows():
    c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
    with c1:
        st.markdown(f"**{row['home']} ⚔ {row['away']}**")
    with c2:
        hs = st.text_input(
            f"hs_{row['match_id']}",
            value=("" if pd.isna(row['home_score']) else str(int(row['home_score']))),
            key=f"hs_{row['match_id']}"
        )
    with c3:
        aw = st.text_input(
            f"aw_{row['match_id']}",
            value=("" if pd.isna(row['away_score']) else str(int(row['away_score']))),
            key=f"aw_{row['match_id']}"
        )
    with c4:
        if st.button("Simpan", key=f"save_{row['match_id']}"):
            try:
                hs_val = int(hs) if hs != "" else None
                aw_val = int(aw) if aw != "" else None
            except ValueError:
                st.error("Skor harus angka!")
                st.stop()

            st.session_state.matches.at[row['match_id'], 'home_score'] = hs_val
            st.session_state.matches.at[row['match_id'], 'away_score'] = aw_val

            st.session_state.matches.to_csv(DATA_FILE, index=False)
            st.success(f"Skor {row['home']} vs {row['away']} tersimpan ✅")

# ==========================
# Reset Skor
# ==========================
st.subheader("Reset Semua Skor")
if st.button("Reset skor (kosongkan semua)"):
    st.session_state.matches[['home_score', 'away_score']] = None
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.success("Semua skor sudah dikosongkan!")

# ==========================
# Hitung Standings (No Cache)
# ==========================
def compute_standings(df, team_list):
    table = pd.DataFrame({
        'Team': team_list,
        'Main': 0, 'Menang': 0, 'Seri': 0, 'Kalah': 0,
        'GF': 0, 'GA': 0, 'GD': 0, 'Poin': 0
    })

    for _, m in df.iterrows():
        if pd.isna(m['home_score']) or pd.isna(m['away_score']):
            continue

        h, a = m['home'], m['away']
        hs, aw = int(m['home_score']), int(m['away_score'])

        table.loc[table.Team == h, 'Main'] += 1
        table.loc[table.Team == a, 'Main'] += 1

        table.loc[table.Team == h, 'GF'] += hs
        table.loc[table.Team == h, 'GA'] += aw
        table.loc[table.Team == a, 'GF'] += aw
        table.loc[table.Team == a, 'GA'] += hs

        if hs > aw:
            table.loc[table.Team == h, 'Menang'] += 1
            table.loc[table.Team == h, 'Poin'] += 3
            table.loc[table.Team == a, 'Kalah'] += 1
        elif aw > hs:
            table.loc[table.Team == a, 'Menang'] += 1
            table.loc[table.Team == a, 'Poin'] += 3
            table.loc[table.Team == h, 'Kalah'] += 1
        else:
            table.loc[table.Team == h, 'Seri'] += 1
            table.loc[table.Team == a, 'Seri'] += 1
            table.loc[table.Team == h, 'Poin'] += 1
            table.loc[table.Team == a, 'Poin'] += 1

    table['GD'] = table['GF'] - table['GA']
    return table.sort_values(['Poin', 'GD', 'GF'], ascending=False).reset_index(drop=True)

standings = compute_standings(st.session_state.matches, teams)

# ==========================
# Top Scorer Minggu
# ==========================
week_matches = st.session_state.matches[st.session_state.matches['round'] == rounds]
goal_count = {}
for _, m in week_matches.iterrows():
    if pd.isna(m['home_score']) or pd.isna(m['away_score']):
        continue
    goal_count[m['home']] = goal_count.get(m['home'], 0) + int(m['home_score'])
    goal_count[m['away']] = goal_count.get(m['away'], 0) + int(m['away_score'])

top_goals = max(goal_count.values()) if goal_count else 0
top_scorers = [team for team, g in goal_count.items() if g == top_goals] if top_goals > 0 else []

if top_scorers:
    st.subheader(f"🥅 Top Scorer Minggu {rounds}: {', '.join(top_scorers)} ({top_goals} gol)")
else:
    st.subheader(f"🥅 Top Scorer Minggu {rounds}: Belum ada gol")

# ==========================
# Render Standings
# ==========================
st.header("🏆 Klasemen Sementara Liga FB")

max_poin = standings['Poin'].max()
html = "<table><tr><th>Rank</th><th>Team</th><th>Main</th><th>Menang</th><th>Seri</th><th>Kalah</th><th>GF</th><th>GA</th><th>GD</th><th>Poin</th></tr>"

n = len(standings)
for idx, row in standings.iterrows():
    cls = ""
    medal = ""

    if idx == 0:
        cls = "top1"; medal = "🥇"
    elif idx == 1:
        cls = "top2"; medal = "🥈"
    elif idx == 2:
        cls = "top3"; medal = "🥉"

    if idx >= n - 3:
        cls += " bottom3"

    bar_width = int((row['Poin'] / max_poin) * 100) if max_poin > 0 else 0
    top_class = "top_scorer" if row['Team'] in top_scorers else ""

    bottom_emojis = ["😵‍💫", "🤯", "🪦"]
    bottom_emoji = bottom_emojis[idx - (n - 3)] if idx >= n - 3 else ""

    html += f"<tr class='{cls} {top_class}'>"
    html += f"<td>{idx+1}</td><td>{medal}{bottom_emoji} {row['Team']}</td>"
    html += f"<td>{row['Main']}</td><td>{row['Menang']}</td><td>{row['Seri']}</td>"
    html += f"<td>{row['Kalah']}</td><td>{row['GF']}</td><td>{row['GA']}</td><td>{row['GD']}</td>"
    html += f"<td>{row['Poin']}<div class='bar' style='width:{bar_width}%;'></div></td>"
    html += "</tr>"

html += "</table>"
st.markdown(html, unsafe_allow_html=True)
