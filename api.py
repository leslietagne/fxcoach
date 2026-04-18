from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from analyzer import load_trades, get_stats, get_stats_by_hour
from insights import detect_biases
from coach import generate_coach_report, generate_chat_response
import tempfile
import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), lang: str = Form("EN")):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        df = load_trades(tmp_path)
        stats = get_stats(df)
        biases = detect_biases(df, lang)
        hour_stats = get_stats_by_hour(df)

        df['_date'] = df['Open'].dt.strftime('%Y-%m-%d')
        daily = df.groupby('_date')['Profit'].sum().round(2)
        daily_pnl = [{"date": d, "pnl": float(p)} for d, p in daily.items()]

        return {
            "stats": stats,
            "biases": biases,
            "hour_stats": hour_stats.reset_index().to_dict(orient="records"),
            "daily_pnl": daily_pnl,
        }
    finally:
        os.unlink(tmp_path)

@app.post("/coach-report")
async def coach_report(data: dict):
    stats = data.get("stats")
    biases = data.get("biases")
    lang = data.get("lang", "EN")

    import pandas as pd
    hour_stats = pd.DataFrame(data.get("hour_stats", []))
    if not hour_stats.empty:
        hour_stats = hour_stats.set_index("Open_Hour")

    report = generate_coach_report(stats, biases, hour_stats, lang)
    return {"report": report}

@app.post("/chat")
async def chat(data: dict):
    question = data.get("question")
    stats = data.get("stats")
    biases = data.get("biases")
    lang = data.get("lang", "EN")

    answer = generate_chat_response(question, stats, biases, lang)
    return {"answer": answer}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/create-checkout-session")
async def create_checkout_session(data: dict):
    user_id = data.get("user_id")
    price_id = data.get("price_id")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url="https://fxcoach.app/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://fxcoach.app/pricing",
        metadata={"user_id": user_id}
    )
    return {"url": session.url}

@app.post("/create-payment-session")
async def create_payment_session(data: dict):
    user_id = data.get("user_id")
    price_id = data.get("price_id")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
        success_url="https://fxcoach.app/analyse?paid=true&session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://fxcoach.app/analyse",
        metadata={"user_id": user_id, "type": "one_shot"}
    )
    return {"url": session.url}

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            data = await request.json()
            event = data
    except Exception as e:
        return {"error": str(e)}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"].get("user_id")
        payment_type = session["metadata"].get("type")

        if user_id:
            from supabase import create_client
            sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

            if payment_type == "one_shot":
                sb.rpc("increment_analyses_paid", {"user_id_input": user_id}).execute()
            else:
                sb.table("profiles").update({"is_premium": True}).eq("id", user_id).execute()

    return {"status": "ok"}