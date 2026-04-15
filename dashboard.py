import streamlit as st
from datetime import datetime, date
import plotly.graph_objects as go
import pandas as pd
import calendar

def show_dashboard(lang, stats, biases, df=None):

    if lang == "FR":
        st.title("📊 Dashboard — Suivi de challenge")
        param_title = "⚙️ Paramètres de ton challenge"
        capital_label = "Capital du compte (£/$/€)"
        target_label = "Objectif de profit (%)"
        drawdown_label = "Drawdown maximum autorisé (%)"
        deadline_toggle = "Je veux me fixer une deadline"
        start_label = "Date de début du challenge"
        end_label = "Ma deadline personnelle"
        progress_title = "📈 Progression vers l'objectif"
        score_title = "🎯 Score de discipline"
        keypoints_title = "✅ Key points pour tes prochains trades"
        notes_title = "📝 Mes notes personnelles"
        notes_placeholder = "Écris tes observations, tes résolutions, tes points d'attention..."
        days_left = "jours restants"
        days_elapsed = "jours écoulés"
        calendar_title = "📅 Calendrier de trading"
    else:
        st.title("📊 Dashboard — Challenge Tracker")
        param_title = "⚙️ Your challenge parameters"
        capital_label = "Account capital (£/$/€)"
        target_label = "Profit target (%)"
        drawdown_label = "Maximum allowed drawdown (%)"
        deadline_toggle = "I want to set a personal deadline"
        start_label = "Challenge start date"
        end_label = "My personal deadline"
        progress_title = "📈 Progress toward target"
        score_title = "🎯 Discipline score"
        keypoints_title = "✅ Key points for your next trades"
        notes_title = "📝 My personal notes"
        notes_placeholder = "Write your observations, resolutions, focus points..."
        days_left = "days remaining"
        days_elapsed = "days elapsed"
        calendar_title = "📅 Trading calendar"

    # PARAMÈTRES
    st.markdown(f"### {param_title}")
    col1, col2 = st.columns(2)
    with col1:
        capital = st.number_input(capital_label, min_value=1000, max_value=200000, value=10000, step=1000)
        target_pct = st.number_input(target_label, min_value=1.0, max_value=20.0, value=10.0, step=0.5)
        drawdown_pct = st.number_input(drawdown_label, min_value=1.0, max_value=20.0, value=10.0, step=0.5)
    with col2:
        start_date = st.date_input(start_label, value=date.today())
        use_deadline = st.checkbox(deadline_toggle, value=False)
        if use_deadline:
            end_date = st.date_input(end_label, value=date(date.today().year, date.today().month + 1 if date.today().month < 12 else 1, date.today().day))
        else:
            end_date = None

    # CALCULS
    target_amount = capital * target_pct / 100
    drawdown_amount = capital * drawdown_pct / 100
    current_profit = stats['net_profit'] if stats else 0
    progress_pct = min(max(current_profit / target_amount * 100, 0), 100) if target_amount > 0 else 0

    today = date.today()
    elapsed_days = max((today - start_date).days, 0)

    # DEADLINE
    if use_deadline and end_date:
        remaining_days = (end_date - today).days
        total_days = (end_date - start_date).days
        time_progress = min(max(elapsed_days / total_days * 100, 0), 100) if total_days > 0 else 0

        st.markdown("---")
        col1, col2 = st.columns(2)
        col1.metric(days_elapsed, f"{elapsed_days}")
        col2.metric(days_left, f"{max(remaining_days, 0)}")

        st.markdown(f"**⏳ Time elapsed**" if lang == "EN" else "**⏳ Temps écoulé**")
        st.progress(int(time_progress))

    # PROGRESSION PROFIT
    st.markdown("---")
    st.markdown(f"### {progress_title}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current P&L" if lang == "EN" else "P&L actuel", f"${current_profit}")
    col2.metric("Target" if lang == "EN" else "Objectif", f"${round(target_amount, 2)}")
    col3.metric("Max drawdown", f"${round(drawdown_amount, 2)}")

    st.markdown(f"**{'Profit target' if lang == 'EN' else 'Objectif de profit'} — {round(progress_pct, 1)}%**")
    progress_color = "normal" if progress_pct >= 50 else "inverse"
    st.progress(int(progress_pct))

    if progress_pct >= 100:
        st.success("🎉 Target reached! You can request your payout." if lang == "EN" else "🎉 Objectif atteint ! Tu peux demander ton payout.")
    elif progress_pct >= 70:
        st.info("🔥 Almost there! Stay disciplined." if lang == "EN" else "🔥 Presque ! Reste discipliné.")
    elif progress_pct >= 30:
        st.warning("💪 Keep going, stay consistent." if lang == "EN" else "💪 Continue, reste consistant.")
    else:
        st.error("📉 Early stage — focus on discipline, not profit." if lang == "EN" else "📉 Début du challenge — focus sur la discipline, pas le profit.")

    # CALENDRIER
    if df is not None:
        st.markdown("---")
        st.markdown(f"### {calendar_title}")

        df['Date'] = df['Open'].dt.date
        daily_pnl = df.groupby('Date')['Profit'].sum().round(2)

        today = date.today()
        year = today.year
        month = today.month

        cal = calendar.monthcalendar(year, month)
        month_name = date(year, month, 1).strftime("%B %Y")

        st.markdown(f"**{month_name}**")

        days_header = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        cols = st.columns(7)
        for i, d in enumerate(days_header):
            cols[i].markdown(f"<div style='text-align:center; font-size:12px; font-weight:600; color:gray;'>{d}</div>", unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown("")
                else:
                    current = date(year, month, day)
                    pnl = daily_pnl.get(current, None)

                    if pnl is not None:
                        color = "#e8f5e9" if pnl >= 0 else "#ffebee"
                        text_color = "#2e7d32" if pnl >= 0 else "#c62828"
                        sign = "+" if pnl >= 0 else ""
                        cols[i].markdown(f"""
                        <div style='text-align:center; background:{color}; border-radius:8px; padding:4px; margin:2px;'>
                            <div style='font-size:11px; color:gray;'>{day}</div>
                            <div style='font-size:11px; font-weight:600; color:{text_color};'>{sign}{pnl}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    elif current == today:
                        cols[i].markdown(f"""
                        <div style='text-align:center; background:#e3f2fd; border-radius:8px; padding:4px; margin:2px; border:1px solid #1565c0;'>
                            <div style='font-size:11px; font-weight:700; color:#1565c0;'>{day}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    elif current <= today:
                        cols[i].markdown(f"""
                        <div style='text-align:center; background:#f5f5f5; border-radius:8px; padding:4px; margin:2px;'>
                            <div style='font-size:11px; color:#bbb;'>{day}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        cols[i].markdown(f"""
                        <div style='text-align:center; padding:4px; margin:2px;'>
                            <div style='font-size:11px; color:#ddd;'>{day}</div>
                        </div>
                        """, unsafe_allow_html=True)

    # SCORE DE DISCIPLINE
    st.markdown("---")
    st.markdown(f"### {score_title}")

    if stats and biases:
        score = 100
        for b in biases:
            if b['severity'] == 'CRITICAL':
                score -= 30
            elif b['severity'] == 'HIGH':
                score -= 20
            elif b['severity'] == 'MEDIUM':
                score -= 10
        score = max(score, 0)

        color = "#4caf7d" if score >= 70 else "#c9a84c" if score >= 40 else "#e8604c"
        label = ("Excellent" if score >= 80 else "Good" if score >= 60 else "Needs work" if score >= 40 else "Critical") if lang == "EN" else ("Excellent" if score >= 80 else "Bon" if score >= 60 else "À améliorer" if score >= 40 else "Critique")

        st.markdown(f"**Score : {score}/100 — {label}**")
        st.progress(score)

        col1, col2, col3 = st.columns(3)
        col1.metric("Score", f"{score}/100")
        col2.metric("Status", label)
        col3.metric("Biases", len([b for b in biases if b['severity'] != 'POSITIVE']))

    # KEY POINTS
    st.markdown("---")
    st.markdown(f"### {keypoints_title}")

    if biases:
        for b in biases:
            if b['severity'] == 'CRITICAL':
                st.error(f"🔴 **{b['name']}** — {b['advice']}")
            elif b['severity'] == 'HIGH':
                st.warning(f"🟠 **{b['name']}** — {b['advice']}")
            elif b['severity'] == 'MEDIUM':
                st.info(f"🔵 **{b['name']}** — {b['advice']}")

    # NOTES
    st.markdown("---")
    st.markdown(f"### {notes_title}")
    st.text_area("", placeholder=notes_placeholder, height=200, key="personal_notes")