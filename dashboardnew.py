import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Spotify Wrapped 2025 · Grammy Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #0d0d0d; color: #f0f0f0; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #1a1a1a;
    border-radius: 12px;
    padding: 6px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #aaa;
    font-weight: 500;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: #1db954 !important;
    color: #000 !important;
    font-weight: 700;
}

/* Metric cards */
.metric-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 14px;
    padding: 22px 24px;
    text-align: center;
    transition: border-color .2s;
}
.metric-card:hover { border-color: #1db954; }
.metric-value { font-size: 2.2rem; font-weight: 700; color: #1db954; margin: 0; }
.metric-label { font-size: 0.82rem; color: #888; margin-top: 4px; text-transform: uppercase; letter-spacing: .05em; }

/* Era badge */
.era-before { background:#1db954; color:#000; border-radius:6px; padding:2px 10px; font-weight:600; font-size:.8rem; }
.era-after  { background:#e53935; color:#fff; border-radius:6px; padding:2px 10px; font-weight:600; font-size:.8rem; }

/* Section header */
.section-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: #f0f0f0;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #1db954;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
FILE_NAME = "spotify_wrapped_2025_grammy_count.xlsx"

def find_file():
    base = Path(__file__).parent
    for candidate in [base / FILE_NAME, base / "data" / FILE_NAME, Path(FILE_NAME)]:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"❌ Arquivo '{FILE_NAME}' não encontrado.\n"
        f"Coloque-o na mesma pasta do dashboard.py ({base}) e rode novamente."
    )

@st.cache_data
def load_data():
    df = pd.read_excel(find_file())
    df["Era"] = df["Release Year"].apply(lambda y: "Até 2015" if y <= 2015 else "Após 2015")
    df["Grammy Winner"] = df["Grammy Wins"] > 0
    return df

df = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown("<div style='font-size:3rem;margin-top:6px'>🎵</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin:0;font-size:2rem;font-weight:800;color:#f0f0f0'>Spotify Wrapped 2025</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin:0;color:#888;font-size:.95rem'>Top 50 Global Songs · Grammy Analysis</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── KPIs ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (len(df), "Músicas no Top 50"),
    (f"{df['Streams (B)'].sum():.1f}B", "Streams Totais"),
    (df["Grammy Wins"].sum(), "Grammys Totais"),
    (df[df["Era"] == "Até 2015"].shape[0], "Músicas ≤ 2015"),
    (df[df["Era"] == "Após 2015"].shape[0], "Músicas > 2015"),
]
for col, (val, label) in zip([c1, c2, c3, c4, c5], kpis):
    col.markdown(
        f'<div class="metric-card"><p class="metric-value">{val}</p><p class="metric-label">{label}</p></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📖  Sobre",
    "🏆  Visão Geral",
    "🎙️  Artistas",
    "🎸  Gêneros",
    "🕐  Era: ≤2015 vs >2015",
    "🔗  Correlação",
    "🗂️  Tabela Completa",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 · VISÃO GERAL
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col_l, col_r = st.columns([1.2, 1])

    with col_l:
        st.markdown('<p class="section-title">Top 15 · Streams (bilhões)</p>', unsafe_allow_html=True)
        top15 = df.head(15).sort_values("Streams (B)")
        colors = ["#1db954" if g else "#2a2a2a" for g in top15["Grammy Winner"]]
        fig = go.Figure(go.Bar(
            x=top15["Streams (B)"], y=top15["Song Title"],
            orientation="h", marker_color=colors,
            text=[f"{v:.2f}B" for v in top15["Streams (B)"]],
            textposition="outside", textfont=dict(color="#ccc", size=11),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", height=460,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            margin=dict(l=0, r=60, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🟢 Verde = vencedor do Grammy")

    with col_r:
        st.markdown('<p class="section-title">Distribuição de Grammys</p>', unsafe_allow_html=True)
        winners = df[df["Grammy Wins"] > 0].sort_values("Grammy Wins", ascending=False)
        fig2 = px.bar(
            winners, x="Grammy Wins", y="Artist", orientation="h",
            color="Grammy Wins", color_continuous_scale=["#1a5c2e", "#1db954", "#c3ff5a"],
            text="Grammy Wins",
        )
        fig2.update_traces(textposition="outside", textfont=dict(color="#ccc"))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", height=260,
            showlegend=False, coloraxis_showscale=False,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False),
            margin=dict(l=0, r=50, t=10, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<p class="section-title">Músicas Explícitas</p>', unsafe_allow_html=True)
        exp_counts = df["Explicit"].value_counts()
        fig3 = go.Figure(go.Pie(
            labels=["Explícita", "Não Explícita"],
            values=[exp_counts.get(True, 0), exp_counts.get(False, 0)],
            hole=0.55,
            marker_colors=["#e53935", "#1db954"],
            textfont=dict(color="#fff"),
        ))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="#ccc",
            height=200, margin=dict(l=0, r=0, t=10, b=10),
            legend=dict(font=dict(color="#ccc")),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Audio features heatmap
    st.markdown('<p class="section-title">Audio Features · Top 20</p>', unsafe_allow_html=True)
    feats = ["Danceability", "Energy", "Valence", "Acousticness"]
    heat_df = df.head(20).set_index("Song Title")[feats].T
    fig4 = px.imshow(
        heat_df, color_continuous_scale=["#0d0d0d", "#1db954", "#c3ff5a"],
        aspect="auto", zmin=0, zmax=1,
    )
    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc", height=200,
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(tickfont=dict(size=9)),
    )
    st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 · ARTISTAS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    # Count occurrences — split collabs simply by taking first artist name for ranking
    artist_streams = df.groupby("Artist")["Streams (B)"].sum().sort_values(ascending=False).head(15)
    artist_grammys = df.groupby("Artist")["Grammy Wins"].sum().sort_values(ascending=False)
    artist_songs   = df.groupby("Artist").size().sort_values(ascending=False).head(12)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-title">Top Artistas · Streams Totais</p>', unsafe_allow_html=True)
        fig = px.bar(
            x=artist_streams.values, y=artist_streams.index,
            orientation="h", text=[f"{v:.2f}B" for v in artist_streams.values],
            color=artist_streams.values, color_continuous_scale=["#1a5c2e", "#1db954"],
        )
        fig.update_traces(textposition="outside", textfont=dict(color="#ccc"))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", height=420, showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            margin=dict(l=0, r=70, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-title">Mais Músicas no Top 50</p>', unsafe_allow_html=True)
        fig2 = px.bar(
            x=artist_songs.values, y=artist_songs.index,
            orientation="h", text=artist_songs.values,
            color=artist_songs.values, color_continuous_scale=["#2a2a2a", "#1db954"],
        )
        fig2.update_traces(textposition="outside", textfont=dict(color="#ccc"))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", height=420, showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            margin=dict(l=0, r=50, t=10, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-title">Grammys por Artista</p>', unsafe_allow_html=True)
    winner_artists = artist_grammys[artist_grammys > 0]
    fig3 = px.treemap(
        names=winner_artists.index, parents=["" for _ in winner_artists],
        values=winner_artists.values,
        color=winner_artists.values, color_continuous_scale=["#1a5c2e", "#c3ff5a"],
    )
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color="#000", height=280,
        margin=dict(l=0, r=0, t=10, b=10), coloraxis_showscale=False,
    )
    st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 · GÊNEROS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    genre_streams = df.groupby("Genre")["Streams (B)"].sum().sort_values(ascending=False)
    genre_count   = df["Genre"].value_counts()
    genre_grammy  = df.groupby("Genre")["Grammy Wins"].sum().sort_values(ascending=False)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-title">Streams por Gênero</p>', unsafe_allow_html=True)
        fig = px.pie(
            values=genre_streams.values, names=genre_streams.index,
            hole=0.5, color_discrete_sequence=px.colors.sequential.Greens[::-1],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="#ccc", height=350,
            margin=dict(l=0, r=0, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-title">Quantidade de Músicas por Gênero</p>', unsafe_allow_html=True)
        fig2 = px.bar(
            x=genre_count.values, y=genre_count.index,
            orientation="h", text=genre_count.values,
            color=genre_count.values, color_continuous_scale=["#1a5c2e", "#1db954"],
        )
        fig2.update_traces(textposition="outside", textfont=dict(color="#ccc"))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", height=350, showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            margin=dict(l=0, r=50, t=10, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-title">BPM médio por Gênero</p>', unsafe_allow_html=True)
    bpm_genre = df.groupby("Genre")["BPM"].mean().sort_values(ascending=False)
    fig3 = px.bar(
        x=bpm_genre.index, y=bpm_genre.values,
        text=[f"{v:.0f}" for v in bpm_genre.values],
        color=bpm_genre.values, color_continuous_scale=["#1a5c2e", "#c3ff5a"],
    )
    fig3.update_traces(textposition="outside", textfont=dict(color="#ccc"))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc", height=280, coloraxis_showscale=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=False, showticklabels=False),
        margin=dict(l=0, r=0, t=20, b=10),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 · ERA ≤2015 vs >2015
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    before = df[df["Era"] == "Até 2015"]
    after  = df[df["Era"] == "Após 2015"]

    PALETTE = {"Até 2015": "#1db954", "Após 2015": "#e53935"}

    col_a, col_b, col_c, col_d = st.columns(4)
    for col, label, data in [
        (col_a, "Músicas",    [len(before), len(after)]),
        (col_b, "Streams (B)",[round(before["Streams (B)"].sum(),2), round(after["Streams (B)"].sum(),2)]),
        (col_c, "Grammys",    [before["Grammy Wins"].sum(), after["Grammy Wins"].sum()]),
        (col_d, "BPM Médio",  [round(before["BPM"].mean(),1), round(after["BPM"].mean(),1)]),
    ]:
        col.markdown(
            f"""<div class="metric-card">
                <p class="metric-label">{label}</p>
                <p style="margin:8px 0 4px;font-size:1.1rem;color:#1db954;font-weight:700">≤2015: {data[0]}</p>
                <p style="margin:0;font-size:1.1rem;color:#e53935;font-weight:700">&gt;2015: {data[1]}</p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<p class="section-title">Streams por Era</p>', unsafe_allow_html=True)
        era_streams = df.groupby("Era")["Streams (B)"].sum().reset_index()
        fig = px.bar(
            era_streams, x="Era", y="Streams (B)",
            color="Era", color_discrete_map=PALETTE,
            text=[f"{v:.2f}B" for v in era_streams["Streams (B)"]],
        )
        fig.update_traces(textposition="outside", textfont=dict(color="#ccc"))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", height=300, showlegend=False,
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, showticklabels=False),
            margin=dict(l=0, r=0, t=20, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<p class="section-title">Audio Features por Era</p>', unsafe_allow_html=True)
        feats = ["Danceability", "Energy", "Valence", "Acousticness"]
        era_avg = df.groupby("Era")[feats].mean().reset_index()
        era_melt = era_avg.melt(id_vars="Era", var_name="Feature", value_name="Score")
        fig2 = px.bar(
            era_melt, x="Feature", y="Score", color="Era",
            barmode="group", color_discrete_map=PALETTE,
            text=[f"{v:.2f}" for v in era_melt["Score"]],
        )
        fig2.update_traces(textposition="outside", textfont=dict(color="#ccc", size=10))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", height=300,
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, showticklabels=False),
            margin=dict(l=0, r=0, t=20, b=10),
            legend=dict(font=dict(color="#ccc")),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        st.markdown('<p class="section-title">Músicas ≤ 2015 no Top 50</p>', unsafe_allow_html=True)
        for _, row in before.sort_values("Rank").iterrows():
            badge = f'<span class="era-before">≤2015</span>'
            grm = f"🏆 {row['Grammy Wins']}G" if row["Grammy Wins"] > 0 else ""
            st.markdown(
                f"<div style='background:#1a1a1a;border-radius:10px;padding:10px 14px;margin-bottom:8px;border-left:3px solid #1db954'>"
                f"<span style='font-weight:700;color:#f0f0f0'>#{row['Rank']} {row['Song Title']}</span><br>"
                f"<span style='color:#888;font-size:.85rem'>{row['Artist']} · {row['Release Year']} · {row['Genre']}</span>&nbsp;{badge}&nbsp;<span style='color:#f0c040'>{grm}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown('<p class="section-title" style="margin-top:20px">Grammys: ≤2015 vs &gt;2015</p>', unsafe_allow_html=True)
        era_grm = df.groupby("Era")["Grammy Wins"].sum().reset_index()
        fig3 = go.Figure(go.Pie(
            labels=era_grm["Era"], values=era_grm["Grammy Wins"],
            hole=0.55, marker_colors=["#1db954", "#e53935"],
            textfont=dict(color="#000"),
        ))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="#ccc", height=220,
            margin=dict(l=0, r=0, t=10, b=10),
            legend=dict(font=dict(color="#ccc")),
        )
        st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 · TABELA COMPLETA
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        genre_opts = ["Todos"] + sorted(df["Genre"].unique().tolist())
        sel_genre = st.selectbox("Gênero", genre_opts)
    with col_f2:
        era_opts = ["Todas", "Até 2015", "Após 2015"]
        sel_era = st.selectbox("Era", era_opts)
    with col_f3:
        only_grammy = st.checkbox("Só vencedores Grammy")

    filtered = df.copy()
    if sel_genre != "Todos":
        filtered = filtered[filtered["Genre"] == sel_genre]
    if sel_era != "Todas":
        filtered = filtered[filtered["Era"] == sel_era]
    if only_grammy:
        filtered = filtered[filtered["Grammy Wins"] > 0]

    display_cols = ["Rank", "Song Title", "Artist", "Genre", "Release Year", "Era",
                    "Streams (B)", "Grammy Wins", "BPM", "Danceability", "Energy", "Country"]

    st.markdown(f"<p style='color:#888;font-size:.85rem'>{len(filtered)} músicas encontradas</p>", unsafe_allow_html=True)

    st.dataframe(
        filtered[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=460,
        column_config={
            "Streams (B)": st.column_config.NumberColumn(format="%.2fB"),
            "Grammy Wins": st.column_config.NumberColumn("🏆 Grammy"),
            "Danceability": st.column_config.ProgressColumn(min_value=0, max_value=1, format="%.2f"),
            "Energy":       st.column_config.ProgressColumn(min_value=0, max_value=1, format="%.2f"),
            "Era": st.column_config.TextColumn("Era"),
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 0 · SOBRE
# ─────────────────────────────────────────────────────────────────────────────
with tab0:
    st.markdown("""
    <div style='max-width:820px;margin:0 auto'>
        <h2 style='color:#1db954;font-size:1.6rem;margin-bottom:4px'>🎵 Sobre este Dashboard</h2>
        <p style='color:#888;margin-bottom:28px;font-size:.95rem'>Spotify Wrapped 2025 · Top 50 Global Songs · Grammy Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Contexto
    st.markdown("""
    <div style='background:#1a1a1a;border-radius:14px;padding:24px 28px;border-left:4px solid #1db954;max-width:820px;margin:0 auto 20px auto'>
        <h3 style='color:#f0f0f0;margin:0 0 10px 0;font-size:1.1rem'>📌 Contexto</h3>
        <p style='color:#ccc;line-height:1.7;margin:0'>
        O <strong style='color:#1db954'>Spotify Wrapped 2025</strong> revelou as 50 músicas mais ouvidas no mundo inteiro.
        Mais do que um ranking de streams, esses dados nos permitem entender <strong style='color:#fff'>o que o público global
        realmente consome</strong>, quais características musicais dominam as playlists e como o prestígio do Grammy
        se relaciona — ou não — com o sucesso em plataformas de streaming.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Perguntas centrais
    st.markdown("<div style='max-width:820px;margin:0 auto'>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">❓ Perguntas Centrais</p>', unsafe_allow_html=True)

    perguntas = [
        ("1", "Músicas antigas (≤ 2015) ainda conseguem competir em streams com lançamentos recentes?"),
        ("2", "Existem características musicais — como danceability, energia ou BPM — que se correlacionam com maior número de streams?"),
        ("3", "Ganhar um Grammy garante mais streams? Ou o sucesso no streaming independe do reconhecimento da indústria?"),
        ("4", "Quais gêneros e artistas dominam o Top 50 global, e o que isso diz sobre o gosto musical contemporâneo?"),
    ]
    for num, pergunta in perguntas:
        st.markdown(f"""
        <div style='background:#111;border:1px solid #2a2a2a;border-radius:10px;padding:14px 18px;margin-bottom:10px;display:flex;align-items:flex-start;gap:14px'>
            <span style='background:#1db954;color:#000;font-weight:800;border-radius:6px;padding:2px 10px;font-size:.9rem;white-space:nowrap'>{num}</span>
            <span style='color:#ddd;font-size:.95rem;line-height:1.5'>{pergunta}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Conclusões
    st.markdown("<br><div style='max-width:820px;margin:0 auto'>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">💡 Principais Conclusões</p>', unsafe_allow_html=True)

    conclusoes = [
        ("🕐", "Clássicos resistem, mas são exceção",
         "Apenas 3 das 50 músicas mais ouvidas foram lançadas antes de 2015 — Yellow (Coldplay, 2000), Running Up That Hill (Kate Bush, 1985) e Shake It Off (Taylor Swift, 2014). O streaming favorece fortemente o conteúdo recente, mas músicas com forte conexão emocional ou cultural desafiam essa tendência."),
        ("🎵", "Danceability e energia importam",
         "A análise de correlação mostra que músicas com maior danceability tendem a acumular mais streams. O público global prefere faixas dançantes, energéticas e com valência positiva — características dominantes no Top 50."),
        ("🏆", "Grammy e streams: prestígios paralelos",
         "Vencedores do Grammy aparecem no Top 50, mas não há uma correlação direta entre número de Grammys e volume de streams. O reconhecimento da indústria e o consumo popular seguem lógicas distintas — o que o público ouve nem sempre é o que a academia premia."),
    ]
    for icon, titulo, texto in conclusoes:
        st.markdown(f"""
        <div style='background:#1a1a1a;border-radius:12px;padding:20px 22px;margin-bottom:14px;border-left:4px solid #1db954'>
            <p style='color:#1db954;font-weight:700;font-size:1rem;margin:0 0 6px 0'>{icon} {titulo}</p>
            <p style='color:#ccc;line-height:1.65;margin:0;font-size:.93rem'>{texto}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Metodologia
    st.markdown("<br><div style='max-width:820px;margin:0 auto'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#111;border:1px solid #2a2a2a;border-radius:12px;padding:18px 22px'>
        <p style='color:#888;font-size:.82rem;margin:0'>
        <strong style='color:#555'>📂 Fonte dos dados:</strong> Spotify Wrapped 2025 · Top 50 Global Songs &nbsp;|&nbsp;
        <strong style='color:#555'>🔧 Ferramentas:</strong> Python · Streamlit · Plotly · Pandas &nbsp;|&nbsp;
        <strong style='color:#555'>📊 Técnicas:</strong> Estatística descritiva · Correlação de Pearson · Visualização de dados
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 · CORRELAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<p class="section-title">🔗 Correlação entre Variáveis Musicais e Streams</p>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1.4, 1])

    with col_l:
        st.markdown('<p class="section-title">Danceability × Streams</p>', unsafe_allow_html=True)
        fig_sc = px.scatter(
            df, x="Danceability", y="Streams (B)",
            color="Era", size="Grammy Wins",
            size_max=22,
            hover_data=["Song Title", "Artist", "Genre"],
            color_discrete_map={"Até 2015": "#1db954", "Após 2015": "#e53935"},
            trendline="ols",
            trendline_scope="overall",
            trendline_color_override="#f0c040",
            labels={"Streams (B)": "Streams (bilhões)", "Danceability": "Danceability (0–1)"},
        )
        fig_sc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", height=380,
            xaxis=dict(showgrid=True, gridcolor="#1e1e1e"),
            yaxis=dict(showgrid=True, gridcolor="#1e1e1e"),
            legend=dict(font=dict(color="#ccc")),
            margin=dict(l=0, r=0, t=10, b=10),
        )
        st.plotly_chart(fig_sc, use_container_width=True)
        st.caption("💛 Linha amarela = tendência geral (regressão linear) · Tamanho do ponto = nº de Grammys")

    with col_r:
        # Pearson correlation table
        st.markdown('<p class="section-title">Correlação de Pearson com Streams</p>', unsafe_allow_html=True)
        num_cols = ["Danceability", "Energy", "Valence", "Acousticness", "BPM", "Grammy Wins"]
        correlations = df[num_cols + ["Streams (B)"]].corr()["Streams (B)"].drop("Streams (B)").sort_values(ascending=False)

        for var, corr_val in correlations.items():
            bar_color = "#1db954" if corr_val >= 0 else "#e53935"
            bar_width  = abs(corr_val) * 100
            direction  = "positiva" if corr_val >= 0 else "negativa"
            st.markdown(f"""
            <div style='background:#1a1a1a;border-radius:10px;padding:12px 16px;margin-bottom:8px'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'>
                    <span style='color:#ddd;font-weight:500;font-size:.92rem'>{var}</span>
                    <span style='color:{bar_color};font-weight:700;font-size:.95rem'>{corr_val:+.3f}</span>
                </div>
                <div style='background:#222;border-radius:4px;height:6px;width:100%'>
                    <div style='background:{bar_color};height:6px;border-radius:4px;width:{bar_width:.1f}%'></div>
                </div>
                <span style='color:#555;font-size:.75rem'>correlação {direction}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='background:#111;border:1px solid #2a2a2a;border-radius:10px;padding:14px 16px;margin-top:16px'>
            <p style='color:#888;font-size:.82rem;line-height:1.6;margin:0'>
            <strong style='color:#ccc'>Interpretação:</strong> Valores próximos de <strong style='color:#1db954'>+1</strong> indicam que, 
            quanto maior a variável, mais streams a música tende a ter. Valores próximos de 
            <strong style='color:#e53935'>-1</strong> indicam relação inversa. Próximos de 0 = sem relação clara.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Heatmap completo de correlações
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">Mapa de Calor — Correlação entre Todas as Variáveis</p>', unsafe_allow_html=True)
    all_num = ["Streams (B)", "Danceability", "Energy", "Valence", "Acousticness", "BPM", "Grammy Wins"]
    corr_matrix = df[all_num].corr().round(2)
    fig_heat = px.imshow(
        corr_matrix,
        color_continuous_scale=["#e53935", "#111111", "#1db954"],
        zmin=-1, zmax=1,
        text_auto=True,
        aspect="auto",
    )
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color="#ccc",
        height=340, margin=dict(l=0, r=0, t=10, b=10),
        coloraxis_colorbar=dict(tickfont=dict(color="#ccc")),
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;margin-top:40px;color:#444;font-size:.78rem;border-top:1px solid #222;padding-top:16px'>
  Spotify Wrapped 2025 · Grammy Dashboard · Criado com Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
