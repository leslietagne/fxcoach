def detect_biases(df, lang="EN"):
    biases = []
    df_sorted = df.sort_values('Open').reset_index(drop=True)
    df_sorted['Prev_Won'] = df_sorted['Won'].shift(1)

    def t(en, fr):
        return fr if lang == "FR" else en

    # Biais 1 — Revenge sizing
    after_loss = df_sorted[df_sorted['Prev_Won'] == False]
    after_win = df_sorted[df_sorted['Prev_Won'] == True]
    vol_after_loss = round(after_loss['Volume'].mean(), 3)
    vol_after_win = round(after_win['Volume'].mean(), 3)

    if vol_after_loss > vol_after_win * 1.2:
        pct = round((vol_after_loss - vol_after_win) / vol_after_win * 100)
        biases.append({
            'name': t('Revenge sizing', 'Revenge sizing'),
            'severity': 'HIGH',
            'detail': t(
                f"You increase position size by {pct}% after a loss ({vol_after_loss} vs {vol_after_win} after a win).",
                f"Tu augmentes ta taille de position de {pct}% après une perte ({vol_after_loss} vs {vol_after_win} après un gain)."
            ),
            'advice': t(
                "After every losing trade, your next position must be equal or smaller. No exceptions.",
                "Après chaque trade perdant, ta prochaine position doit être égale ou plus petite. Sans exception."
            )
        })

    # Biais 2 — Trades sans SL
    no_sl = df_sorted[df_sorted['SL'] == 0]
    if len(no_sl) > 0:
        pnl_no_sl = round(no_sl['Profit'].sum(), 2)
        biases.append({
            'name': t('Missing stop loss', 'Stop loss manquant'),
            'severity': 'CRITICAL',
            'detail': t(
                f"{len(no_sl)} trades had no stop loss. Total P&L on those trades: ${pnl_no_sl}.",
                f"{len(no_sl)} trades n'avaient pas de stop loss. P&L total sur ces trades : ${pnl_no_sl}."
            ),
            'advice': t(
                "No stop loss = no trade. Set your SL before entering, every single time.",
                "Pas de stop loss = pas de trade. Place ton SL avant d'entrer, à chaque fois sans exception."
            )
        })

    # Biais 3 — Heure suboptimale
    hour_stats = df_sorted.groupby('Open_Hour').agg(
        trades=('Profit', 'count'),
        win_rate=('Won', 'mean'),
        profit=('Profit', 'sum')
    ).round(2)

    best_hour = hour_stats['profit'].idxmax()
    worst_hours = hour_stats[hour_stats['win_rate'] == 0].index.tolist()

    if worst_hours:
        biases.append({
            'name': t('Off-peak trading', 'Trading hors pic'),
            'severity': 'MEDIUM',
            'detail': t(
                f"Your best hour is {best_hour}:00 UTC. You have 0% win rate at hours: {worst_hours}.",
                f"Ta meilleure heure est {best_hour}h UTC. Tu as 0% de win rate aux heures : {worst_hours}."
            ),
            'advice': t(
                f"Stick to your {best_hour}:00 UTC window. Close your platform outside of it.",
                f"Reste sur ta fenêtre de {best_hour}h UTC. Ferme ta plateforme en dehors."
            )
        })

    # Biais 4 — Early exit
    wins = df_sorted[df_sorted['Won']]
    losses = df_sorted[~df_sorted['Won']]
    avg_win_duration = wins['Duration_min'].mean()
    avg_loss_duration = losses['Duration_min'].mean()

    if avg_win_duration < avg_loss_duration * 0.6:
        biases.append({
            'name': t('Early exit on winners', 'Sortie prématurée sur les gagnants'),
            'severity': 'HIGH',
            'detail': t(
                f"You close winning trades in {round(avg_win_duration)} min on average, but let losing trades run for {round(avg_loss_duration)} min.",
                f"Tu fermes tes trades gagnants en {round(avg_win_duration)} min en moyenne, mais laisses courir les perdants {round(avg_loss_duration)} min."
            ),
            'advice': t(
                "Let your winners breathe. Set a minimum hold time for winning trades before considering an exit.",
                "Laisse tes gagnants respirer. Fixe un temps minimum de maintien avant d'envisager une sortie."
            )
        })

    # Biais 5 — Overtrading
    df_sorted['Date'] = df_sorted['Open'].dt.date
    trades_per_day = df_sorted.groupby('Date').size()
    avg_trades_per_day = trades_per_day.mean()
    max_trades_day = trades_per_day.max()

    if max_trades_day >= 6:
        biases.append({
            'name': t('Overtrading', 'Overtrading'),
            'severity': 'MEDIUM',
            'detail': t(
                f"You averaged {round(avg_trades_per_day, 1)} trades/day with a peak of {max_trades_day} trades in one session.",
                f"Tu fais en moyenne {round(avg_trades_per_day, 1)} trades/jour avec un pic de {max_trades_day} trades en une session."
            ),
            'advice': t(
                "Set a daily max of 3-4 trades. If you reach your limit, close the platform.",
                "Fixe un maximum de 3-4 trades par jour. Si tu atteins ta limite, ferme la plateforme."
            )
        })

    # Biais 6 — Overconfidence
    streaks = []
    current_streak = 0
    for won in df_sorted['Won']:
        if won:
            current_streak += 1
        else:
            if current_streak >= 3:
                streaks.append(current_streak)
            current_streak = 0

    if streaks:
        after_streak = []
        count = 0
        for i, row in df_sorted.iterrows():
            if count >= 3:
                after_streak.append(row['Won'])
                count = 0
            if row['Won']:
                count += 1
            else:
                count = 0

        if after_streak and sum(after_streak) / len(after_streak) < 0.3:
            biases.append({
                'name': t('Overconfidence after winning streak', 'Surconfiance après série gagnante'),
                'severity': 'MEDIUM',
                'detail': t(
                    "After winning streaks of 3+, your win rate drops significantly.",
                    "Après des séries gagnantes de 3+, ton win rate chute significativement."
                ),
                'advice': t(
                    "After 3 consecutive wins, take a break or reduce position size.",
                    "Après 3 gains consécutifs, fais une pause ou réduis ta taille de position."
                )
            })

    # Biais 7 — Biais directionnel
    long_trades = df_sorted[df_sorted['Type'] == 'buy']
    short_trades = df_sorted[df_sorted['Type'] == 'sell']

    if len(long_trades) > 0 and len(short_trades) > 0:
        long_wr = long_trades['Won'].mean()
        short_wr = short_trades['Won'].mean()

        if long_wr > 0.6 and short_wr < 0.3:
            biases.append({
                'name': t('Directional bias — avoid shorts', 'Biais directionnel — évite les shorts'),
                'severity': 'MEDIUM',
                'detail': t(
                    f"Your win rate on longs is {round(long_wr*100)}% vs {round(short_wr*100)}% on shorts.",
                    f"Ton win rate sur les longs est {round(long_wr*100)}% vs {round(short_wr*100)}% sur les shorts."
                ),
                'advice': t(
                    "Consider focusing exclusively on long setups until your short strategy is properly backtested.",
                    "Concentre-toi exclusivement sur les setups long jusqu'à ce que ta stratégie short soit backtestée."
                )
            })
        elif short_wr > 0.6 and long_wr < 0.3:
            biases.append({
                'name': t('Directional bias — avoid longs', 'Biais directionnel — évite les longs'),
                'severity': 'MEDIUM',
                'detail': t(
                    f"Your win rate on shorts is {round(short_wr*100)}% vs {round(long_wr*100)}% on longs.",
                    f"Ton win rate sur les shorts est {round(short_wr*100)}% vs {round(long_wr*100)}% sur les longs."
                ),
                'advice': t(
                    "Consider focusing exclusively on short setups until your long strategy is properly backtested.",
                    "Concentre-toi exclusivement sur les setups short jusqu'à ce que ta stratégie long soit backtestée."
                )
            })

    # Biais 8 — Position sizing
    avg_volume = df_sorted['Volume'].mean()
    max_volume = df_sorted['Volume'].max()

    if max_volume > avg_volume * 3:
        big_trades = df_sorted[df_sorted['Volume'] > avg_volume * 2]
        big_wr = big_trades['Won'].mean()
        biases.append({
            'name': t('Inconsistent position sizing', 'Position sizing incohérent'),
            'severity': 'HIGH',
            'detail': t(
                f"Your largest position ({max_volume} lots) is {round(max_volume/avg_volume, 1)}x your average ({round(avg_volume, 3)} lots). Win rate on oversized positions: {round(big_wr*100)}%.",
                f"Ta plus grande position ({max_volume} lots) est {round(max_volume/avg_volume, 1)}x ta moyenne ({round(avg_volume, 3)} lots). Win rate sur positions oversized : {round(big_wr*100)}%."
            ),
            'advice': t(
                "Stick to consistent lot sizes. Large positions during emotional moments is one of the fastest ways to blow a challenge.",
                "Reste sur des tailles de lots cohérentes. Les grosses positions dans les moments émotionnels sont parmi les causes les plus fréquentes d'échec au challenge."
            )
        })

    if not biases:
        biases.append({
            'name': t('Strong discipline detected', 'Excellente discipline détectée'),
            'severity': 'POSITIVE',
            'detail': t(
                "No major behavioral biases detected in your trading data. Your discipline is above average.",
                "Aucun biais comportemental majeur détecté dans tes données. Ta discipline est au-dessus de la moyenne."
            ),
            'advice': t(
                "Keep following your rules consistently. Focus on refining your entry timing and position sizing.",
                "Continue à suivre tes règles. Concentre-toi sur l'affinage de ton timing d'entrée et de ton position sizing."
            )
        })

    return biases