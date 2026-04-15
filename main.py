from analyzer import load_trades, get_stats, get_stats_by_hour
from insights import detect_biases

df = load_trades('data/trading-journal.csv')

stats = get_stats(df)
print("\n===== FXCOACH — TON RAPPORT =====")
print(f"Total trades      : {stats['total_trades']}")
print(f"Win rate          : {stats['win_rate']}%")
print(f"Profit net        : ${stats['net_profit']}")
print(f"Gain moyen        : ${stats['avg_win']}")
print(f"Perte moyenne     : ${stats['avg_loss']}")
print(f"Ratio R/R         : {stats['rr_ratio']}")
print(f"Trades sans SL    : {stats['trades_no_sl']} (P&L: ${stats['pnl_no_sl']})")

print("\n===== PERFORMANCE PAR HEURE =====")
print(get_stats_by_hour(df).to_string())

print("\n===== BIAIS DÉTECTÉS =====")
biases = detect_biases(df)
for b in biases:
    print(f"\n[{b['severity']}] {b['name']}")
    print(f"  -> {b['detail']}")
    print(f"  💡 {b['advice']}")

print("\n==================================")
