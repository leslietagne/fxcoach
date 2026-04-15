import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_coach_report(stats, biases, hour_stats, lang="EN"):
    biases_text = "\n".join([
        f"- {b['name']} ({b['severity']}): {b['detail']}"
        for b in biases
    ])
    hour_text = hour_stats.to_string()

    if lang == "FR":
        prompt = f"""Tu es FXCoach, un coach trading expert en psychologie des marchés et en prop trading (FTMO, The5ers, funded accounts).

Voici les données de trading d'un utilisateur :

STATS GÉNÉRALES :
- Total trades : {stats['total_trades']}
- Win rate : {stats['win_rate']}%
- Profit net : {stats['net_profit']} USD
- Gain moyen : {stats['avg_win']} USD
- Perte moyenne : {stats['avg_loss']} USD
- Ratio R/R : {stats['rr_ratio']}
- Trades sans SL : {stats['trades_no_sl']} (P&L : {stats['pnl_no_sl']} USD)

BIAIS DÉTECTÉS :
{biases_text}

PERFORMANCE PAR HEURE :
{hour_text}

Génère un rapport coach complet, personnalisé et bienveillant en français.
Structure ton rapport ainsi :
1. Une introduction qui résume le profil du trader en 2-3 phrases
2. Une analyse détaillée de chaque biais avec des exemples concrets tirés des données
3. 3 règles concrètes et personnalisées à appliquer pour les prochains trades
4. Un message de motivation final

Ton ton doit être celui d'un coach professionnel — direct, bienveillant, et basé uniquement sur les données. Pas de généralités."""

    else:
        prompt = f"""You are FXCoach, an expert trading coach specializing in trading psychology and prop trading (FTMO, The5ers, funded accounts).

Here is a trader's data:

GENERAL STATS:
- Total trades: {stats['total_trades']}
- Win rate: {stats['win_rate']}%
- Net profit: {stats['net_profit']} USD
- Avg win: {stats['avg_win']} USD
- Avg loss: {stats['avg_loss']} USD
- R/R ratio: {stats['rr_ratio']}
- Trades with no SL: {stats['trades_no_sl']} (P&L: {stats['pnl_no_sl']} USD)

DETECTED BIASES:
{biases_text}

PERFORMANCE BY HOUR:
{hour_text}

Generate a complete, personalized and supportive coach report in English.
Structure your report as follows:
1. An introduction summarizing the trader's profile in 2-3 sentences
2. A detailed analysis of each bias with concrete examples from the data
3. 3 concrete and personalized rules to apply for the next trades
4. A final motivational message

Your tone should be that of a professional coach — direct, supportive, and based solely on the data. No generic advice."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def generate_chat_response(question, stats, biases, lang="EN"):
    biases_text = "\n".join([
        f"- {b['name']}: {b['detail']}"
        for b in biases
    ])

    if lang == "FR":
        system = f"""Tu es FXCoach, un coach trading expert.
Tu as accès aux données de trading de l'utilisateur :
- Win rate : {stats['win_rate']}%
- Profit net : {stats['net_profit']} USD
- Ratio R/R : {stats['rr_ratio']}
- Biais détectés : {biases_text}

Réponds en français de façon concise, directe et personnalisée basée sur ces données."""

    else:
        system = f"""You are FXCoach, an expert trading coach.
You have access to the user's trading data:
- Win rate: {stats['win_rate']}%
- Net profit: {stats['net_profit']} USD
- R/R ratio: {stats['rr_ratio']}
- Detected biases: {biases_text}

Reply in English in a concise, direct and personalized way based on this data."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        system=system,
        messages=[{"role": "user", "content": question}]
    )

    return response.content[0].text