import streamlit as st

def show_landing(lang):

    if lang == "FR":
        hero_title = "Arrête de perdre tes challenges à cause de toi-même."
        hero_sub = "FXCoach analyse tes trades et détecte exactement quels comportements te coûtent de l'argent. Sans journal. Sans effort. En 30 secondes."
        cta = "Analyser mes trades gratuitement →"
        why_title = "Pourquoi FXCoach ?"
        features = [
            ("🧠", "Zéro journal requis", "Notre IA détecte tes biais directement dans tes données brutes. Pas besoin d'écrire tes ressentis après chaque trade."),
            ("🎯", "100% personnalisé", "Chaque rapport est unique. Basé sur TES trades, TES patterns, TON profil. Pas de conseils génériques."),
            ("⚡", "Résultats en 30 secondes", "Upload ton CSV FTMO et reçois ton rapport complet instantanément."),
            ("🏆", "Conçu pour les prop traders", "FTMO, The5ers, MyFundedFX — FXCoach comprend les règles des funded accounts."),
            ("🌍", "Multilingue", "Analyse disponible en français et en anglais."),
            ("📈", "Suis ta progression", "Visualise ton évolution challenge après challenge."),
        ]
        free_label = "Gratuit"
        premium_label = "🌟 Premium"
        free_features = [
            "✅ Stats de base (win rate, R/R, profit net)",
            "✅ 1 biais détecté — le plus critique",
            "✅ Aperçu du message coach",
            "🔒 Rapport coach complet",
            "🔒 Tous les biais détectés",
            "🔒 Graphiques interactifs",
            "🔒 Chat avec le coach IA",
            "🔒 Suivi de progression FTMO",
        ]
        premium_features = [
            "✅ Stats complètes + graphiques interactifs",
            "✅ Tous les biais détectés (IA personnalisée)",
            "✅ Rapport coach complet en langage naturel",
            "✅ Chat avec le coach IA",
            "✅ Suivi progression + countdown FTMO",
            "✅ Key points pour tes prochains trades",
            "✅ Notes personnelles",
            "✅ Multilingue",
        ]
        premium_price = "€19/mois"
        free_price = "€0"
        pricing_title = "Gratuit ou Premium ?"
        pricing_sub = "Commence gratuitement. Upgrade quand tu es prêt."
        testimonial_title = "Ce que disent les traders"
        testimonials = [
            ("J'ai failli passer mon FTMO à £71 près. FXCoach m'a montré exactement pourquoi.", "Leslie T.", "Trader XAUUSD"),
            ("J'augmentais ma mise de 52% après chaque perte sans m'en rendre compte. Game changer.", "Marc D.", "Trader Forex"),
            ("Enfin un outil qui parle le langage des prop traders. Pas du blabla générique.", "Sofia R.", "FTMO Funded"),
        ]

    else:
        hero_title = "Stop losing your challenges because of yourself."
        hero_sub = "FXCoach analyzes your trades and detects exactly which behaviors are costing you money. No journaling. No effort. In 30 seconds."
        cta = "Analyze my trades for free →"
        why_title = "Why FXCoach?"
        features = [
            ("🧠", "Zero journaling required", "Our AI detects your biases directly from raw trade data. No need to write down your feelings after every trade."),
            ("🎯", "100% personalized", "Every report is unique. Based on YOUR trades, YOUR patterns, YOUR profile. No generic advice."),
            ("⚡", "Results in 30 seconds", "Upload your FTMO CSV and get your full report instantly."),
            ("🏆", "Built for prop traders", "FTMO, The5ers, MyFundedFX — FXCoach understands funded account rules."),
            ("🌍", "Multilingual", "Analysis available in English and French."),
            ("📈", "Track your progress", "Visualize your improvement challenge after challenge."),
        ]
        free_label = "Free"
        premium_label = "🌟 Premium"
        free_features = [
            "✅ Basic stats (win rate, R/R, net profit)",
            "✅ 1 bias detected — the most critical",
            "✅ Coach message preview",
            "🔒 Full coach report",
            "🔒 All biases detected",
            "🔒 Interactive charts",
            "🔒 Chat with AI coach",
            "🔒 FTMO progress tracking",
        ]
        premium_features = [
            "✅ Full stats + interactive charts",
            "✅ All biases detected (personalized AI)",
            "✅ Full coach report in natural language",
            "✅ Chat with AI coach",
            "✅ Progress tracking + FTMO countdown",
            "✅ Key points for your next trades",
            "✅ Personal notes",
            "✅ Multilingual",
        ]
        premium_price = "€19/month"
        free_price = "€0"
        pricing_title = "Free or Premium?"
        pricing_sub = "Start for free. Upgrade when you're ready."
        testimonial_title = "What traders say"
        testimonials = [
            ("I almost passed my FTMO by £71. FXCoach showed me exactly why I failed.", "Leslie T.", "XAUUSD Trader"),
            ("I was increasing my position size by 52% after every loss without realizing it. Game changer.", "Marc D.", "Forex Trader"),
            ("Finally a tool that speaks the prop trader language. Not generic advice.", "Sofia R.", "FTMO Funded"),
        ]

    # HERO SECTION
    st.markdown(f"""
    <div style="text-align:center; padding: 4rem 1rem 3rem;">
        <div style="display:inline-block; background:#c9a84c18; border:1px solid #c9a84c40; border-radius:20px; padding:6px 16px; font-size:12px; color:#c9a84c; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:1.5rem;">
            AI-Powered Trading Coach
        </div>
        <h1 style="font-size:2.8rem; font-weight:700; color:#f0efe8; line-height:1.2; margin-bottom:1rem; max-width:700px; margin-left:auto; margin-right:auto;">
            {hero_title}
        </h1>
        <p style="font-size:1.1rem; color:#9998a0; max-width:560px; margin:0 auto 2rem; line-height:1.7;">
            {hero_sub}
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(cta, type="primary", use_container_width=True):
            st.session_state.page = "analyse"
            st.rerun()

    # STATS SOCIALES
    st.markdown("""
    <div style="display:flex; justify-content:center; gap:3rem; padding:2rem 0; border-top:1px solid #ffffff12; border-bottom:1px solid #ffffff12; margin:2rem 0;">
        <div style="text-align:center;">
            <div style="font-size:1.8rem; font-weight:700; color:#c9a84c;">500+</div>
            <div style="font-size:12px; color:#9998a0; text-transform:uppercase; letter-spacing:0.05em;">Traders</div>
        </div>
        <div style="text-align:center;">
            <div style="font-size:1.8rem; font-weight:700; color:#c9a84c;">8</div>
            <div style="font-size:12px; color:#9998a0; text-transform:uppercase; letter-spacing:0.05em;">Biais détectés</div>
        </div>
        <div style="text-align:center;">
            <div style="font-size:1.8rem; font-weight:700; color:#c9a84c;">30s</div>
            <div style="font-size:12px; color:#9998a0; text-transform:uppercase; letter-spacing:0.05em;">Analyse</div>
        </div>
        <div style="text-align:center;">
            <div style="font-size:1.8rem; font-weight:700; color:#c9a84c;">FR/EN</div>
            <div style="font-size:12px; color:#9998a0; text-transform:uppercase; letter-spacing:0.05em;">Langues</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # WHY FXCOACH
    st.markdown(f"""
    <h2 style="text-align:center; font-size:1.8rem; color:#f0efe8; margin:2rem 0 0.5rem;">{why_title}</h2>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#111118; border:1px solid #ffffff12; border-radius:12px; padding:1.25rem; margin-bottom:1rem; height:160px;">
                <div style="font-size:1.5rem; margin-bottom:0.5rem;">{icon}</div>
                <div style="font-size:14px; font-weight:600; color:#f0efe8; margin-bottom:0.4rem;">{title}</div>
                <div style="font-size:12px; color:#9998a0; line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # TESTIMONIALS
    st.markdown(f"""
    <h2 style="text-align:center; font-size:1.8rem; color:#f0efe8; margin:2rem 0 1rem;">{testimonial_title}</h2>
    """, unsafe_allow_html=True)

    cols2 = st.columns(3)
    for i, (quote, name, role) in enumerate(testimonials):
        with cols2[i]:
            st.markdown(f"""
            <div style="background:#111118; border:1px solid #ffffff12; border-radius:12px; padding:1.25rem; margin-bottom:1rem;">
                <div style="font-size:1.2rem; color:#c9a84c; margin-bottom:0.5rem;">❝</div>
                <div style="font-size:13px; color:#f0efe8; line-height:1.7; margin-bottom:1rem; font-style:italic;">{quote}</div>
                <div style="font-size:13px; font-weight:600; color:#f0efe8;">{name}</div>
                <div style="font-size:11px; color:#9998a0;">{role}</div>
            </div>
            """, unsafe_allow_html=True)

    # PRICING
    st.markdown(f"""
    <h2 style="text-align:center; font-size:1.8rem; color:#f0efe8; margin:2rem 0 0.25rem;">{pricing_title}</h2>
    <p style="text-align:center; color:#9998a0; font-size:14px; margin-bottom:1.5rem;">{pricing_sub}</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="background:#111118; border:1px solid #ffffff12; border-radius:16px; padding:1.5rem;">
            <div style="font-size:14px; font-weight:600; color:#9998a0; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">{free_label}</div>
            <div style="font-size:2rem; font-weight:700; color:#f0efe8; margin-bottom:1.5rem;">{free_price}</div>
            {"".join([f'<div style="font-size:13px; color:#9998a0; padding:4px 0;">{f}</div>' for f in free_features])}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background:#111118; border:2px solid #c9a84c; border-radius:16px; padding:1.5rem; position:relative;">
            <div style="position:absolute; top:-12px; left:50%; transform:translateX(-50%); background:#c9a84c; color:#0d0d0f; font-size:11px; font-weight:700; padding:3px 12px; border-radius:20px; white-space:nowrap;">MOST POPULAR</div>
            <div style="font-size:14px; font-weight:600; color:#c9a84c; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">{premium_label}</div>
            <div style="font-size:2rem; font-weight:700; color:#f0efe8; margin-bottom:1.5rem;">{premium_price}</div>
            {"".join([f'<div style="font-size:13px; color:#f0efe8; padding:4px 0;">{f}</div>' for f in premium_features])}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(cta + " ", type="primary", use_container_width=True):
            st.session_state.page = "analyse"
            st.rerun()

    # FOOTER
    st.markdown("""
    <div style="text-align:center; padding:3rem 0 1rem; color:#55545c; font-size:12px; border-top:1px solid #ffffff12; margin-top:3rem;">
        FXCoach © 2026 — Built for prop traders, by a prop trader.
    </div>
    """, unsafe_allow_html=True)