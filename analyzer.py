import pandas as pd

def load_trades(filepath):
    df = pd.read_csv(filepath)
    df.columns = [
        'Ticket', 'Open', 'Type', 'Volume', 'Symbol',
        'Entry_Price', 'SL', 'TP', 'Close', 'Exit_Price',
        'Swap', 'Commission', 'Profit', 'Pips', 'Duration_sec'
    ]
    df['Open'] = pd.to_datetime(df['Open'])
    df['Close'] = pd.to_datetime(df['Close'])
    df['Open_Hour'] = df['Open'].dt.hour
    df['Duration_min'] = df['Duration_sec'] / 60
    df['Won'] = df['Profit'] > 0
    df['Net_Profit'] = df['Profit'] + df['Swap'] + df['Commission']
    return df

def get_stats(df):
    wins = df[df['Won']]
    losses = df[~df['Won']]
    stats = {
        'total_trades': len(df),
        'win_rate': round(df['Won'].mean() * 100, 1),
        'total_profit': round(df['Profit'].sum(), 2),
        'net_profit': round(df['Net_Profit'].sum(), 2),
        'avg_win': round(wins['Profit'].mean(), 2),
        'avg_loss': round(losses['Profit'].mean(), 2),
        'rr_ratio': round(abs(wins['Profit'].mean() / losses['Profit'].mean()), 2),
        'trades_no_sl': len(df[df['SL'] == 0]),
        'pnl_no_sl': round(df[df['SL'] == 0]['Profit'].sum(), 2),
    }
    return stats

def get_stats_by_hour(df):
    return df.groupby('Open_Hour').agg(
        trades=('Profit', 'count'),
        profit=('Profit', 'sum'),
        win_rate=('Won', 'mean')
    ).round(2)

def get_stats_by_direction(df):
    return df.groupby('Type').agg(
        trades=('Profit', 'count'),
        profit=('Profit', 'sum'),
        win_rate=('Won', 'mean'),
        avg_profit=('Profit', 'mean')
    ).round(2)