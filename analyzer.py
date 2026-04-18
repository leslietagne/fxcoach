import pandas as pd

COLUMN_ALIASES = {
    'Ticket': ['Ticket', 'ticket', 'Order', 'order', 'ID', 'id', 'Trade #', 'Position'],
    'Open': ['Open', 'open', 'Open Time', 'OpenTime', 'Date/Time', 'Open time', 'Time', 'Entry Time', 'open_time'],
    'Type': ['Type', 'type', 'Action', 'Direction', 'Side', 'B/S'],
    'Volume': ['Volume', 'volume', 'Lots', 'lots', 'Size', 'size', 'Quantity', 'Lot Size'],
    'Symbol': ['Symbol', 'symbol', 'Instrument', 'instrument', 'Asset', 'Pair'],
    'Entry_Price': ['Entry_Price', 'Open Price', 'OpenPrice', 'Price', 'Entry', 'entry_price', 'Open price'],
    'SL': ['SL', 'Stop Loss', 'StopLoss', 'stop_loss', 'S/L', 'Stop loss'],
    'TP': ['TP', 'Take Profit', 'TakeProfit', 'take_profit', 'T/P', 'Take profit'],
    'Close': ['Close', 'close', 'Close Time', 'CloseTime', 'Exit Time', 'close_time', 'Close time'],
    'Exit_Price': ['Exit_Price', 'Close Price', 'ClosePrice', 'Exit', 'exit_price', 'Close price'],
    'Swap': ['Swap', 'swap', 'Rollover', 'rollover'],
    'Commission': ['Commission', 'commission', 'Fee', 'fee', 'Fees'],
    'Profit': ['Profit', 'profit', 'P&L', 'PnL', 'pnl', 'Net P&L', 'Gain', 'Result'],
    'Pips': ['Pips', 'pips', 'Points', 'points'],
    'Duration_sec': ['Duration_sec', 'Duration', 'duration'],
}

def find_column(df_columns, aliases):
    for alias in aliases:
        if alias in df_columns:
            return alias
    return None

def load_trades(filepath):
    # Essaie différents séparateurs
    for sep in [',', ';', '\t']:
        try:
            df = pd.read_csv(filepath, sep=sep)
            if len(df.columns) > 3:
                break
        except:
            continue

    # Nettoie les noms de colonnes
    df.columns = [str(c).strip() for c in df.columns]
    original_cols = list(df.columns)

    # Mappe les colonnes trouvées
    col_map = {}
    for standard_name, aliases in COLUMN_ALIASES.items():
        found = find_column(original_cols, aliases)
        if found:
            col_map[found] = standard_name

    df = df.rename(columns=col_map)

    # Colonnes obligatoires
    required = ['Open', 'Close', 'Profit']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes : {missing}. Colonnes trouvées : {original_cols}")

    # Colonnes optionnelles — valeur par défaut si absentes
    if 'Volume' not in df.columns:
        df['Volume'] = 0.01
    if 'SL' not in df.columns:
        df['SL'] = 0
    if 'TP' not in df.columns:
        df['TP'] = 0
    if 'Swap' not in df.columns:
        df['Swap'] = 0
    if 'Commission' not in df.columns:
        df['Commission'] = 0
    if 'Entry_Price' not in df.columns:
        df['Entry_Price'] = 0
    if 'Exit_Price' not in df.columns:
        df['Exit_Price'] = 0
    if 'Symbol' not in df.columns:
        df['Symbol'] = 'UNKNOWN'
    if 'Type' not in df.columns:
        df['Type'] = 'buy'
    if 'Pips' not in df.columns:
        df['Pips'] = 0

    # Conversions
    df['Open'] = pd.to_datetime(df['Open'], infer_datetime_format=True)
    df['Close'] = pd.to_datetime(df['Close'], infer_datetime_format=True)
    df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce').fillna(0)
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0.01)
    df['SL'] = pd.to_numeric(df['SL'], errors='coerce').fillna(0)
    df['Commission'] = pd.to_numeric(df['Commission'], errors='coerce').fillna(0)
    df['Swap'] = pd.to_numeric(df['Swap'], errors='coerce').fillna(0)

    # Calculs
    df['Open_Hour'] = df['Open'].dt.hour
    df['Duration_sec'] = (df['Close'] - df['Open']).dt.total_seconds()
    df['Duration_min'] = df['Duration_sec'] / 60
    df['Won'] = df['Profit'] > 0
    df['Net_Profit'] = df['Profit'] + df['Swap'] + df['Commission']

    # Filtre les lignes sans profit valide
    df = df.dropna(subset=['Profit'])
    df = df[df['Profit'] != 0]

    return df

def get_stats(df):
    wins = df[df['Won']]
    losses = df[~df['Won']]

    avg_win = round(wins['Profit'].mean(), 2) if len(wins) > 0 else 0
    avg_loss = round(losses['Profit'].mean(), 2) if len(losses) > 0 else 0
    rr = round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0

    stats = {
        'total_trades': len(df),
        'win_rate': round(df['Won'].mean() * 100, 1),
        'total_profit': round(df['Profit'].sum(), 2),
        'net_profit': round(df['Net_Profit'].sum(), 2),
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rr_ratio': rr,
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