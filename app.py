import streamlit as st
import plotly.express as px
from landing import show_landing
from analyzer import load_trades, get_stats, get_stats_by_hour
from insights import detect_biases
from coach import generate_coach_report, generate_chat_response
from dashboard import show_dashboard
from auth import show_auth, logout, get_user_notes, save_user_notes, save_chat_message, get_chat_history, is_premium
import tempfile
import os

# Init session state
defaults = {
    'page': 'landing',
    'lang': 'EN',
    'df': None,
    'stats': None,
    'biases': None,
    'report': None,
    'chat_history': [],
    'user': None,
    'access_token': None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.set_page_config(page_title="FXCoach", page_icon="📈", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
lang = st.sidebar.selectbox("🌍 Language", ["EN", "FR"])
st.session_state.lang = lang

# Auth dans sidebar
if st.session_state.user:
    st.sidebar.markdown(f"👤 {st.session_state.user.email}")
    user_premium = is_premium(str(st.session_state.user.id))
    if user_premium:
        st.sidebar.success("✨ Premium")
    else:
        st.sidebar.info("Free plan")
        if st.sidebar.button("✨ Upgrade to Premium" if lang == "EN" else "✨ Passer Premium"):
                st.session_state.page = "analyse"
                st.rerun()
    if st.sidebar.button("Logout" if lang == "EN" else "Déconnexion"):
        logout(lang)
else:
    st.sidebar.markdown("---")
    if st.sidebar.button("🔐 Login / Sign up" if lang == "EN" else "🔐 Connexion / Inscription"):
        st.session_state.page = "auth"
        st.rerun()

# Navigation sidebar
if st.session_state.user and st.session_state.stats:
    st.sidebar.markdown("---")
    if st.sidebar.button("📊 Analysis" if lang == "EN" else "📊 Analyse"):
        st.session_state.page = "analyse"
        st.rerun()
    if st.sidebar.button("🏆 Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# PAGES
if st.session_state.page == "landing" or st.session_state.page not in ["auth", "analyse", "dashboard"]:
    show_landing(lang)

elif st.session_state.page == "auth":
    if st.session_state.user:
        st.session_state.page = "landing"
        st.rerun()
    show_auth(lang)

elif st.session_state.page == "dashboard":
    user_premium = is_premium(str(st.session_state.user.id)) if st.session_state.user else False
    if user_premium:
        show_dashboard(lang, st.session_state.stats, st.session_state.biases, st.session_state.df)
        if st.button("← Back to analysis" if lang == "EN" else "← Retour à l'analyse"):
            st.session_state.page = "analyse"
            st.rerun()
    else:
        st.warning("Premium feature — upgrade to access the dashboard." if lang == "EN" else "Fonctionnalité Premium — upgrade pour accéder au dashboard.")
        if st.button("← Back" if lang == "EN" else "← Retour"):
            st.session_state.page = "landing"
            st.rerun()

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

    # Vérifier si connecté
    if not st.session_state.user:
        st.info("🔐 Login to save your analysis and access Premium features." if lang == "EN" else "🔐 Connecte-toi pour sauvegarder tes analyses et accéder aux fonctionnalités Premium.")

    user_premium = is_premium(str(st.session_state.user.id)) if st.session_state.user else False

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
            if user_premium:
                st.markdown("---")
                st.markdown("### 📈 Charts" if lang == "EN" else "### 📈 Graphiques")
                hour_df = hour_stats.reset_index()
                hour_df.columns = ['Hour', 'Trades', 'Profit', 'Win Rate']
                hour_df['Win Rate'] = (hour_df['Win Rate'] * 100).round(1)
                fig1 = px.bar(hour_df, x='Hour', y='Profit',
                    color='Profit', color_continuous_scale=['red', 'yellow', 'green'],
                    title='P&L by Hour' if lang == "EN" else 'P&L par heure')
                st.plotly_chart(fig1, use_container_width=True)
                fig2 = px.bar(hour_df, x='Hour', y='Win Rate',
                    color='Win Rate', color_continuous_scale=['red', 'yellow', 'green'],
                    title='Win Rate by Hour (%)' if lang == "EN" else 'Win Rate par heure (%)')
                st.plotly_chart(fig2, use_container_width=True)

            # BIAIS
            st.markdown("---")
            st.markdown("### 🧠 Biases detected" if lang == "EN" else "### 🧠 Biais détectés")

            if user_premium:
                for b in biases:
                    if b['severity'] == 'CRITICAL':
                        st.error(f"🔴 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
                    elif b['severity'] == 'HIGH':
                        st.warning(f"🟠 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
                    elif b['severity'] == 'MEDIUM':
                        st.info(f"🔵 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
                    else:
                        st.success(f"✅ **{b['name']}** — {b['detail']}")
            else:
                if biases:
                    b = biases[0]
                    if b['severity'] == 'CRITICAL':
                        st.error(f"🔴 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
                    elif b['severity'] == 'HIGH':
                        st.warning(f"🟠 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")
                    else:
                        st.info(f"🔵 **{b['name']}** — {b['detail']}\n\n💡 {b['advice']}")

            # RAPPORT COACH
            if user_premium:
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

                # Charger historique si connecté
                if st.session_state.user and not st.session_state.chat_history:
                    st.session_state.chat_history = get_chat_history(str(st.session_state.user.id))

                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

                question = st.chat_input(
                    "Ask your coach anything..." if lang == "EN" else "Pose une question à ton coach..."
                )
                if question:
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    if st.session_state.user:
                        save_chat_message(str(st.session_state.user.id), "user", question)
                    with st.chat_message("user"):
                        st.markdown(question)
                    with st.chat_message("assistant"):
                        with st.spinner("..."):
                            answer = generate_chat_response(question, stats, biases, lang)
                            st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    if st.session_state.user:
                        save_chat_message(str(st.session_state.user.id), "assistant", answer)

                # DASHBOARD BUTTON
                st.markdown("---")
                if st.button("📊 Go to Challenge Dashboard →" if lang == "EN" else "📊 Voir mon Dashboard Challenge →", type="primary"):
                    st.session_state.page = "dashboard"
                    st.rerun()

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