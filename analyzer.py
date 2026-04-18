import pandas as pd

def load_trades(filepath):
    # Essaie différents séparateurs
    for sep in [',', ';', '\t']:
        try:
            df = pd.read_csv(filepath, sep=sep, header=0)
            if len(df.columns) > 3:
                break
        except:
            continue

    # Nettoie les noms de colonnes
    df.columns = [str(c).strip() for c in df.columns]

    # Gère les colonnes dupliquées "Price" (FTMO)
    cols = list(df.columns)
    price_indices = [i for i, c in enumerate(cols) if c == 'Price']
    if len(price_indices) >= 2:
        cols[price_indices[0]] = 'Entry_Price'
        cols[price_indices[1]] = 'Exit_Price'
        df.columns = cols

    # Mapping des colonnes selon différents formats
    rename_map = {}
    col_lower = {c.lower(): c for c in df.columns}

    mappings = {
        'Commission': ['commissions', 'commission', 'fee', 'fees'],
        'SL': ['sl', 'stop loss', 'stoploss', 's/l'],
        'TP': ['tp', 'take profit', 'takeprofit', 't/p'],
        'Volume': ['volume', 'lots', 'size', 'quantity', 'lot size'],
        'Symbol': ['symbol', 'instrument', 'asset', 'pair'],
        'Type': ['type', 'action', 'direction', 'side', 'b/s'],
        'Swap': ['swap', 'rollover'],
        'Profit': ['profit', 'p&l', 'pnl', 'net p&l', 'gain', 'result'],
        'Pips': ['pips', 'points'],
        'Duration_sec': ['trade duration in seconds', 'duration_sec', 'duration'],
        'Entry_Price': ['entry_price', 'open price', 'openPrice', 'entry'],
        'Exit_Price': ['exit_price', 'close price', 'closePrice', 'exit'],
    }

    for standard, aliases in mappings.items():
        if standard not in df.columns:
            for alias in aliases:
                if alias in col_lower:
                    rename_map[col_lower[alias]] = standard
                    break

    df = df.rename(columns=rename_map)

    # Colonnes obligatoires
    required = ['Open', 'Close', 'Profit']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes : {missing}. Colonnes trouvées : {list(df.columns)}")

    # Colonnes optionnelles — valeur par défaut si absentes
    defaults = {
        'Volume': 0.01,
        'SL': 0,
        'TP': 0,
        'Swap': 0,
        'Commission': 0,
        'Entry_Price': 0,
        'Exit_Price': 0,
        'Symbol': 'UNKNOWN',
        'Type': 'buy',
        'Pips': 0,
        'Duration_sec': 0,
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    # Conversions dates — compatible tous formats
    try:
        df['Open'] = pd.to_datetime(df['Open'], format='mixed', dayfirst=False)
        df['Close'] = pd.to_datetime(df['Close'], format='mixed', dayfirst=False)
    except Exception:
        df['Open'] = pd.to_datetime(df['Open'], infer_datetime_format=True, errors='coerce')
        df['Close'] = pd.to_datetime(df['Close'], infer_datetime_format=True, errors='coerce')

    # Conversions numériques
    for col in ['Profit', 'Volume', 'SL', 'TP', 'Commission', 'Swap', 'Entry_Price', 'Exit_Price', 'Pips', 'Duration_sec']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Calculs
    df['Open_Hour'] = df['Open'].dt.hour
    df['Duration_min'] = df['Duration_sec'] / 60
    df['Won'] = df['Profit'] > 0
    df['Net_Profit'] = df['Profit'] + df['Swap'] + df['Commission']

    # Filtre les lignes invalides
    df = df.dropna(subset=['Profit', 'Open', 'Close'])
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