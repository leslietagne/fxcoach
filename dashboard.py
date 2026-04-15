import streamlit as st
from datetime import datetime, date
import plotly.graph_objects as go

def show_dashboard(lang, stats, biases):

    if lang == "FR":
        st.title("📊 Dashboard — Suivi de challenge")
        param_title = "⚙️ Paramètres de ton challenge"
        capital_label = "Capital du compte"
        target_label = "Objectif de profit (%)"
        drawdown_label = "Drawdown maximum autorisé (%)"
        start_label = "Date de début du challenge"
        end_label = "Date de fin du challenge"
        progress_title = "📈 Progression"
        countdown_title = "⏳ Temps restant"
        score_title = "🎯 Score de discipline"
        keypoints_title = "✅ Key points pour tes prochains trades"
        notes_title = "📝 Mes notes personnelles"
        notes_placeholder = "Écris tes observations, tes résolutions, tes points d'attention..."
        days_left = "jours restants"
        days_elapsed = "jours écoulés"
        challenge_over = "Challenge terminé !"
    else:
        st.title("📊 Dashboard — Challenge Tracker")
        param_title = "⚙️ Your challenge parameters"
        capital_label = "Account capital"
        target_label = "Profit target (%)"
        drawdown_label = "Maximum allowed drawdown (%)"
        start_label = "Challenge start date"
        end_label = "Challenge end date"
        progress_title = "📈 Progress"
        countdown_title = "⏳ Time remaining"
        score_title = "🎯 Discipline score"
        keypoints_title = "✅ Key points for your next trades"
        notes_title = "📝 My personal notes"
        notes_placeholder = "Write your observations, resolutions, focus points..."
        days_left = "days remaining"
        days_elapsed = "days elapsed"
        challenge_over = "Challenge completed!"

    # PARAMÈTRES
    st.markdown(f"### {param_title}")
    col1, col2 = st.columns(2)
    with col1:
        capital = st.number_input(capital_label, min_value=1000, max_value=200000, value=10000, step=1000)
        target_pct = st.number_input(target_label, min_value=1.0, max_value=20.0, value=10.0, step=0.5)
        drawdown_pct = st.number_input(drawdown_label, min_value=1.0, max_value=20.0, value=10.0, step=0.5)
    with col2:
        start_date = st.date_input(start_label, value=date.today())
        end_date = st.date_input(end_label, value=date(date.today().year, date.today().month + 1, date.today().day) if date.today().month < 12 else date(date.today().year + 1, 1, date.today().day))

    # CALCULS
    target_amount = capital * target_pct / 100
    drawdown_amount = capital * drawdown_pct / 100
    current_profit = stats['net_profit'] if stats else 0
    progress_pct = min(max(current_profit / target_amount * 100, 0), 100) if target_amount > 0 else 0

    today = date.today()
    total_days = (end_date - start_date).days
    elapsed_days = (today - start_date).days
    remaining_days = (end_date - today).days

    # COUNTDOWN
    st.markdown("---")
    st.markdown(f"### {countdown_title}")
    col1, col2, col3 = st.columns(3)

    if remaining_days > 0:
        col1.metric(days_left, f"{remaining_days}")
        col2.metric(days_elapsed, f"{max(elapsed_days, 0)}")
        col3.metric("Total", f"{total_days}")
    else:
        st.success(challenge_over)

    # BARRE DE TEMPS
    time_progress = min(max(elapsed_days / total_days * 100, 0), 100) if total_days > 0 else 0
    fig_time = go.Figure(go.Indicator(
        mode="gauge+number",
        value=time_progress,
        title={'text': "Time elapsed %" if lang == "EN" else "Temps écoulé %"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#c9a84c"},
            'steps': [
                {'range': [0, 50], 'color': "#e8f5e9"},
                {'range': [50, 80], 'color': "#fff3e0"},
                {'range': [80, 100], 'color': "#ffebee"},
            ]
        }
    ))
    fig_time.update_layout(height=250, margin=dict(t=40, b=0, l=20, r=20))
    st.plotly_chart(fig_time, use_container_width=True)

    # PROGRESSION PROFIT
    st.markdown("---")
    st.markdown(f"### {progress_title}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Current P&L" if lang == "EN" else "P&L actuel", f"${current_profit}")
    col2.metric("Target" if lang == "EN" else "Objectif", f"${round(target_amount, 2)}")
    col3.metric("Max drawdown", f"${round(drawdown_amount, 2)}")

    fig_profit = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=progress_pct,
        delta={'reference': 50},
        title={'text': "Profit target %" if lang == "EN" else "Objectif atteint %"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4caf7d"},
            'steps': [
                {'range': [0, 30], 'color': "#ffebee"},
                {'range': [30, 70], 'color': "#fff3e0"},
                {'range': [70, 100], 'color': "#e8f5e9"},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    fig_profit.update_layout(height=250, margin=dict(t=40, b=0, l=20, r=20))
    st.plotly_chart(fig_profit, use_container_width=True)

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
        if stats.get('trades_no_sl', 0) > 0:
            score -= 10
        score = max(score, 0)

        color = "#4caf7d" if score >= 70 else "#c9a84c" if score >= 40 else "#e8604c"
        label = ("Excellent" if score >= 80 else "Good" if score >= 60 else "Needs work" if score >= 40 else "Critical") if lang == "EN" else ("Excellent" if score >= 80 else "Bon" if score >= 60 else "À améliorer" if score >= 40 else "Critique")

        fig_score = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': f"Discipline Score — {label}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 40], 'color': "#ffebee"},
                    {'range': [40, 70], 'color': "#fff3e0"},
                    {'range': [70, 100], 'color': "#e8f5e9"},
                ]
            }
        ))
        fig_score.update_layout(height=250, margin=dict(t=40, b=0, l=20, r=20))
        st.plotly_chart(fig_score, use_container_width=True)
    else:
        st.info("Upload your trades to see your discipline score." if lang == "EN" else "Upload tes trades pour voir ton score de discipline.")

    # KEY POINTS
    st.markdown("---")
    st.markdown(f"### {keypoints_title}")

    if biases:
        for b in biases:
            if b['severity'] in ['CRITICAL', 'HIGH']:
                st.markdown(f"🔴 **{b['name']}** — {b['advice']}")
            else:
                st.markdown(f"🟡 **{b['name']}** — {b['advice']}")
    else:
        st.success("No critical issues detected. Keep following your rules!" if lang == "EN" else "Aucun problème critique détecté. Continue à suivre tes règles !")

    # NOTES PERSONNELLES
    st.markdown("---")
    st.markdown(f"### {notes_title}")
    st.text_area("", placeholder=notes_placeholder, height=200, key="personal_notes")