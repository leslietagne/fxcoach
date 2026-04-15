import streamlit as st
import plotly.express as px
from landing import show_landing
from analyzer import load_trades, get_stats, get_stats_by_hour
from insights import detect_biases
from coach import generate_coach_report, generate_chat_response
import tempfile
import os

# Init session state
if 'page' not in st.session_state:
    st.session_state.page = "landing"
if 'lang' not in st.session_state:
    st.session_state.lang = "EN"
if 'df' not in st.session_state:
    st.session_state.df = None
if 'stats' not in st.session_state:
    st.session_state.stats = None
if 'biases' not in st.session_state:
    st.session_state.biases = None
if 'premium' not in st.session_state:
    st.session_state.premium = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'report' not in st.session_state:
    st.session_state.report = None

st.set_page_config(page_title="FXCoach", page_icon="📈", layout="centered")
st.markdown("""
<style>
   @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
lang = st.sidebar.selectbox("🌍 Language", ["EN", "FR"])
st.session_state.lang = lang

# Mode premium simulé pour test
st.session_state.premium = st.sidebar.checkbox(
    "✨ Premium mode (test)" if lang == "EN" else "✨ Mode Premium (test)"
)

# NAVIGATION
if st.session_state.page == "landing":
    show_landing(lang)

elif st.session_state.page == "analyse":
    if lang == "FR":
        st.title("📊 Analyse de tes trades")
        upload_label = "Upload ton journal CSV"
        back = "← Retour"
    else:
        st.title("📊 Your trade analysis")
        upload_label = "Upload your CSV trade journal"
        back = "← Back"

    if st.button(back):
        st.session_state.page = "landing"
        st.rerun()

    uploaded_file = st.file_uploader(upload_label, type=["csv"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            df = load_trades(tmp_path)
            st.session_state.df = df
            stats = get_stats(df)
            st.session_state.stats = stats
            biases = detect_biases(df)
            st.session_state.biases = biases
            hour_stats = get_stats_by_hour(df)

            # VUE GÉNÉRALE
            st.markdown("---")
            st.markdown("### 📊 Overview" if lang == "EN" else "### 📊 Vue générale")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total trades", stats['total_trades'])
            col2.metric("Win rate", f"{stats['win_rate']}%")
            col3.metric("Net profit", f"${stats['net_profit']}")
            col4, col5, col6 = st.columns(3)
            col4.metric("Avg win", f"${stats['avg_win']}")
            col5.metric("Avg loss", f"${stats['avg_loss']}")
            col6.metric("R/R ratio", stats['rr_ratio'])

            if stats['trades_no_sl'] > 0:
                st.warning(f"⚠️ {stats['trades_no_sl']} trades with no SL — P&L: ${stats['pnl_no_sl']}")

            # GRAPHIQUES — PREMIUM
            if st.session_state.premium:
                st.markdown("---")
                st.markdown("### 📈 Charts" if lang == "EN" else "### 📈 Graphiques")

                hour_df = hour_stats.reset_index()
                hour_df.columns = ['Hour', 'Trades', 'Profit', 'Win Rate']
                hour_df['Win Rate'] = (hour_df['Win Rate'] * 100).round(1)

                fig1 = px.bar(
                    hour_df, x='Hour', y='Profit',
                    color='Profit',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    title='P&L by Hour' if lang == "EN" else 'P&L par heure'
                )
                st.plotly_chart(fig1, use_container_width=True)

                fig2 = px.bar(
                    hour_df, x='Hour', y='Win Rate',
                    color='Win Rate',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    title='Win Rate by Hour (%)' if lang == "EN" else 'Win Rate par heure (%)'
                )
                st.plotly_chart(fig2, use_container_width=True)

            # BIAIS
            st.markdown("---")
            st.markdown("### 🧠 Biases detected" if lang == "EN" else "### 🧠 Biais détectés")

            if st.session_state.premium:
                for b in biases:
                    if b['severity'] == 'CRITICAL':
                        st.error(f"🔴 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
                    elif b['severity'] == 'HIGH':
                        st.warning(f"🟠 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
                    else:
                        st.info(f"🔵 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
            else:
                if biases:
                    b = biases[0]
                    if b['severity'] == 'CRITICAL':
                        st.error(f"🔴 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
                    elif b['severity'] == 'HIGH':
                        st.warning(f"🟠 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
                    else:
                        st.info(f"🔵 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")

            # RAPPORT COACH — PREMIUM
            if st.session_state.premium:
                st.markdown("---")
                st.markdown("### 🎯 Coach report" if lang == "EN" else "### 🎯 Rapport coach")

                if st.session_state.report is None:
                    with st.spinner("Generating your personalized report..." if lang == "EN" else "Génération de ton rapport personnalisé..."):
                        report = generate_coach_report(stats, biases, hour_stats, lang)
                        st.session_state.report = report

                st.markdown(st.session_state.report)

                # CHAT
                st.markdown("---")
                st.markdown("### 💬 Chat with your coach" if lang == "EN" else "### 💬 Chat avec ton coach")

                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

                question = st.chat_input(
                    "Ask your coach anything..." if lang == "EN" else "Pose une question à ton coach..."
                )

                if question:
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    with st.chat_message("user"):
                        st.markdown(question)
                    with st.chat_message("assistant"):
                        with st.spinner("..."):
                            answer = generate_chat_response(question, stats, biases, lang)
                            st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

            else:
                st.markdown("---")
                if lang == "FR":
                    st.info("🔒 **Rapport coach complet, tous les biais, graphiques et chat disponibles en Premium.**")
                    st.button("✨ Passer en Premium — €19/mois", type="primary")
                else:
                    st.info("🔒 **Full coach report, all biases, charts and chat available in Premium.**")
                    st.button("✨ Upgrade to Premium — €19/month", type="primary")

        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            os.unlink(tmp_path)