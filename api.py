from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from analyzer import load_trades, get_stats, get_stats_by_hour
from insights import detect_biases
from coach import generate_coach_report, generate_chat_response
from fastapi import FastAPI, UploadFile, File, Request
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), lang: str = "EN"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        df = load_trades(tmp_path)
        stats = get_stats(df)
        biases = detect_biases(df)
        hour_stats = get_stats_by_hour(df)

        return {
            "stats": stats,
            "biases": biases,
            "hour_stats": hour_stats.reset_index().to_dict(orient="records"),
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

import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.post("/create-checkout-session")
async def create_checkout_session(data: dict):
    user_id = data.get("user_id")
    price_id = data.get("price_id")
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url="http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:3000/pricing",
        metadata={"user_id": user_id}
    )
    return {"url": session.url}

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        return {"error": str(e)}
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        
        from supabase import create_client
        sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        sb.table("profiles").update({"is_premium": True}).eq("id", user_id).execute()
    
    return {"status": "ok"}