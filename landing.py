import streamlit as st

def show_landing(lang):
    if lang == "FR":
        hero_title = "Ton coach trading IA personnel"
        hero_sub = "Upload ton journal de trades et découvre exactement quels comportements te coûtent de l'argent — sans écrire une seule note."
        cta = "Commencer l'analyse →"
        why_title = "Pourquoi FXCoach ?"
        features = [
            ("🧠", "Zéro journal requis", "Notre IA détecte tes biais directement dans tes données brutes. Pas besoin d'écrire tes ressentis après chaque trade."),
            ("🎯", "Personnalisé pour toi", "Chaque rapport est unique. Pas de conseils génériques — une analyse basée sur TES trades, TES patterns, TON profil."),
            ("🌍", "Multilingue", "FXCoach parle ta langue. Analyse disponible en français et en anglais."),
            ("⚡", "Résultats en secondes", "Upload ton CSV et reçois ton rapport complet en moins de 30 secondes."),
            ("🏆", "Conçu pour les prop traders", "FTMO, The5ers, MyFundedFX — FXCoach comprend les règles des funded accounts et adapte son analyse."),
            ("📈", "Suis ta progression", "Visualise ton évolution challenge après challenge et corrige tes erreurs avant qu'elles te coûtent ton compte."),
        ]
        free_label = "Gratuit"
        premium_label = "Premium"
        free_features = [
            "✅ Stats de base (win rate, R/R, profit net)",
            "✅ 1 biais détecté — le plus critique",
            "✅ Aperçu du message coach",
            "❌ Rapport coach complet",
            "❌ Tous les biais détectés",
            "❌ Graphiques interactifs",
            "❌ Chat avec le coach IA",
            "❌ Suivi de progression",
        ]
        premium_features = [
            "✅ Stats complètes + graphiques interactifs",
            "✅ Tous les biais détectés (IA personnalisée)",
            "✅ Rapport coach complet",
            "✅ Chat avec le coach IA",
            "✅ Suivi progression + countdown FTMO",
            "✅ Key points pour tes prochains trades",
            "✅ Notes personnelles",
            "✅ Multilingue",
        ]
        premium_price = "€19/mois"
        pricing_title = "Gratuit ou Premium ?"

    else:
        hero_title = "Your personal AI trading coach"
        hero_sub = "Upload your trade history and discover exactly which behavioral patterns are costing you money — no journaling required."
        cta = "Start my analysis →"
        why_title = "Why FXCoach?"
        features = [
            ("🧠", "Zero journaling required", "Our AI detects your biases directly from raw trade data. No need to write down your feelings after every trade."),
            ("🎯", "Personalized for you", "Every report is unique. No generic advice — analysis based on YOUR trades, YOUR patterns, YOUR profile."),
            ("🌍", "Multilingual", "FXCoach speaks your language. Analysis available in English and French."),
            ("⚡", "Results in seconds", "Upload your CSV and get your full report in under 30 seconds."),
            ("🏆", "Built for prop traders", "FTMO, The5ers, MyFundedFX — FXCoach understands funded account rules and adapts its analysis accordingly."),
            ("📈", "Track your progress", "Visualize your improvement challenge after challenge and fix your mistakes before they cost you your account."),
        ]
        free_label = "Free"
        premium_label = "Premium"
        free_features = [
            "✅ Basic stats (win rate, R/R, net profit)",
            "✅ 1 bias detected — the most critical",
            "✅ Coach message preview",
            "❌ Full coach report",
            "❌ All biases detected",
            "❌ Interactive charts",
            "❌ Chat with AI coach",
            "❌ Progress tracking",
        ]
        premium_features = [
            "✅ Full stats + interactive charts",
            "✅ All biases detected (personalized AI)",
            "✅ Full coach report",
            "✅ Chat with AI coach",
            "✅ Progress tracking + FTMO countdown",
            "✅ Key points for your next trades",
            "✅ Personal notes",
            "✅ Multilingual",
        ]
        premium_price = "€19/month"
        pricing_title = "Free or Premium?"

    # HERO
    st.markdown(f"""
        <div style='text-align:center; padding: 3rem 1rem 2rem;'>
            <h1 style='font-size:2.5rem; font-weight:700;'>📈 FXCoach</h1>
            <h2 style='font-size:1.4rem; font-weight:400; color:gray;'>{hero_title}</h2>
            <p style='font-size:1rem; color:gray; max-width:600px; margin:1rem auto;'>{hero_sub}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button(cta, type="primary", use_container_width=False):
        st.session_state.page = "analyse"
        st.rerun()

    # WHY FXCOACH
    st.markdown("---")
    st.markdown(f"### {why_title}")
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"**{icon} {title}**")
            st.caption(desc)
            st.markdown("")

    # PRICING
    st.markdown("---")
    st.markdown(f"### {pricing_title}")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {free_label}")
        st.markdown("**€0**")
        for f in free_features:
            st.markdown(f)

    with col2:
        st.markdown(f"#### 🌟 {premium_label}")
        st.markdown(f"**{premium_price}**")
        for f in premium_features:
            st.markdown(f)