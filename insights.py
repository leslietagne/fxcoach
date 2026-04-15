def detect_biases(df):
    biases = []
    df_sorted = df.sort_values('Open').reset_index(drop=True)
    df_sorted['Prev_Won'] = df_sorted['Won'].shift(1)

    # Biais 1 — Revenge sizing
    after_loss = df_sorted[df_sorted['Prev_Won'] == False]
    after_win = df_sorted[df_sorted['Prev_Won'] == True]
    vol_after_loss = round(after_loss['Volume'].mean(), 3)
    vol_after_win = round(after_win['Volume'].mean(), 3)

    if vol_after_loss > vol_after_win * 1.2:
        pct = round((vol_after_loss - vol_after_win) / vol_after_win * 100)
        biases.append({
            'name': 'Revenge sizing',
            'severity': 'HIGH',
            'detail': f"You increase position size by {pct}% after a loss ({vol_after_loss} vs {vol_after_win} after a win).",
            'advice': "After every losing trade, your next position must be equal or smaller. No exceptions."
        })

    # Biais 2 — Trades sans SL
    no_sl = df_sorted[df_sorted['SL'] == 0]
    if len(no_sl) > 0:
        pnl_no_sl = round(no_sl['Profit'].sum(), 2)
        biases.append({
            'name': 'Missing stop loss',
            'severity': 'CRITICAL',
            'detail': f"{len(no_sl)} trades had no stop loss. Total P&L on those trades: ${pnl_no_sl}.",
            'advice': "No stop loss = no trade. Set your SL before entering, every single time."
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
            'name': 'Off-peak trading',
            'severity': 'MEDIUM',
            'detail': f"Your best hour is {best_hour}:00 UTC. You have 0% win rate at hours: {worst_hours}.",
            'advice': f"Stick to your {best_hour}:00 UTC window. Close your platform outside of it."
        })

    # Biais 4 — Early exit (couper les gagnants trop tôt)
    wins = df_sorted[df_sorted['Won']]
    losses = df_sorted[~df_sorted['Won']]
    avg_win_duration = wins['Duration_min'].mean()
    avg_loss_duration = losses['Duration_min'].mean()

    if avg_win_duration < avg_loss_duration * 0.6:
        biases.append({
            'name': 'Early exit on winners',
            'severity': 'HIGH',
            'detail': f"You close winning trades in {round(avg_win_duration)} min on average, but let losing trades run for {round(avg_loss_duration)} min. You cut winners too early and hold losers too long.",
            'advice': "Let your winners breathe. Set a minimum hold time for winning trades before considering an exit."
        })

    # Biais 5 — Overtrading (trop de trades en une session)
    df_sorted['Date'] = df_sorted['Open'].dt.date
    trades_per_day = df_sorted.groupby('Date').size()
    avg_trades_per_day = trades_per_day.mean()
    max_trades_day = trades_per_day.max()

    if max_trades_day >= 6:
        high_days = trades_per_day[trades_per_day >= 6]
        biases.append({
            'name': 'Overtrading',
            'severity': 'MEDIUM',
            'detail': f"You averaged {round(avg_trades_per_day, 1)} trades/day with a peak of {max_trades_day} trades in one session. High-volume days often signal emotional trading.",
            'advice': "Set a daily max of 3-4 trades. If you reach your limit, close the platform. More trades ≠ more profit."
        })

    # Biais 6 — Overconfidence après série gagnante
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
                'name': 'Overconfidence after winning streak',
                'severity': 'MEDIUM',
                'detail': f"After winning streaks of 3+, your win rate drops significantly. You tend to overtrade or take lower quality setups when on a roll.",
                'advice': "After 3 consecutive wins, take a break or reduce position size. Winning streaks create false confidence."
            })

    # Biais 7 — Biais directionnel (trop long ou trop short)
    long_trades = df_sorted[df_sorted['Type'] == 'buy']
    short_trades = df_sorted[df_sorted['Type'] == 'sell']

    if len(long_trades) > 0 and len(short_trades) > 0:
        long_wr = long_trades['Won'].mean()
        short_wr = short_trades['Won'].mean()

        if long_wr > 0.6 and short_wr < 0.3:
            biases.append({
                'name': 'Directional bias — avoid shorts',
                'severity': 'MEDIUM',
                'detail': f"Your win rate on longs is {round(long_wr*100)}% vs {round(short_wr*100)}% on shorts. You perform significantly better when buying.",
                'advice': "Consider focusing exclusively on long setups until your short strategy is properly backtested."
            })
        elif short_wr > 0.6 and long_wr < 0.3:
            biases.append({
                'name': 'Directional bias — avoid longs',
                'severity': 'MEDIUM',
                'detail': f"Your win rate on shorts is {round(short_wr*100)}% vs {round(long_wr*100)}% on longs. You perform significantly better when selling.",
                'advice': "Consider focusing exclusively on short setups until your long strategy is properly backtested."
            })

    # Biais 8 — Positions trop grandes
    avg_volume = df_sorted['Volume'].mean()
    max_volume = df_sorted['Volume'].max()

    if max_volume > avg_volume * 3:
        big_trades = df_sorted[df_sorted['Volume'] > avg_volume * 2]
        big_wr = big_trades['Won'].mean()
        biases.append({
            'name': 'Inconsistent position sizing',
            'severity': 'HIGH',
            'detail': f"Your largest position ({max_volume} lots) is {round(max_volume/avg_volume, 1)}x your average ({round(avg_volume, 3)} lots). Win rate on oversized positions: {round(big_wr*100)}%.",
            'advice': "Stick to consistent lot sizes. Large positions during emotional moments is one of the fastest ways to blow a challenge."
        })

    # Si aucun biais détecté
    if not biases:
        biases.append({
            'name': 'Strong discipline detected',
            'severity': 'POSITIVE',
            'detail': "No major behavioral biases detected in your trading data. Your discipline is above average.",
            'advice': "Keep following your rules consistently. Focus on refining your entry timing and position sizing."
        })

    return biases