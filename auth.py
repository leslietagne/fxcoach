import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(f"Missing Supabase credentials. URL: {SUPABASE_URL}, KEY: {SUPABASE_KEY}")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def show_auth(lang):
    if lang == "FR":
        title = "Connexion / Inscription"
        email_label = "Email"
        password_label = "Mot de passe"
        login_btn = "Se connecter"
        signup_btn = "Créer un compte"
        logout_btn = "Se déconnecter"
        error_msg = "Email ou mot de passe incorrect"
        success_msg = "Compte créé ! Tu peux te connecter."
        tab1_label = "Se connecter"
        tab2_label = "S'inscrire"
    else:
        title = "Login / Sign up"
        email_label = "Email"
        password_label = "Password"
        login_btn = "Login"
        signup_btn = "Create account"
        logout_btn = "Logout"
        error_msg = "Invalid email or password"
        success_msg = "Account created! You can now login."
        tab1_label = "Login"
        tab2_label = "Sign up"

    st.markdown(f"### {title}")
    tab1, tab2 = st.tabs([tab1_label, tab2_label])

    with tab1:
        email = st.text_input(email_label, key="login_email")
        password = st.text_input(password_label, type="password", key="login_password")

        if st.button(login_btn, type="primary"):
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = response.user
                st.session_state.access_token = response.session.access_token
                st.rerun()
            except Exception as e:
                st.error(error_msg)

    with tab2:
        email_signup = st.text_input(email_label, key="signup_email")
        password_signup = st.text_input(password_label, type="password", key="signup_password")

        if st.button(signup_btn, type="primary"):
            try:
                response = supabase.auth.sign_up({
                    "email": email_signup,
                    "password": password_signup
                })
                # Créer le profil
                supabase.table("profiles").insert({
                    "id": str(response.user.id),
                    "email": email_signup,
                    "is_premium": False
                }).execute()
                st.success(success_msg)
                if lang == "FR":
                    st.info("📧 Un email de confirmation t'a été envoyé. Confirme ton adresse avant de te connecter.")
                else:
                    st.info("📧 A confirmation email has been sent. Please confirm your email before logging in.")
            except Exception as e:
                st.error(f"Error: {e}")

def logout(lang):
    try:
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.page = "landing"
        st.rerun()
    except:
        pass

def get_user_notes(user_id):
    try:
        response = supabase.table("notes").select("*").eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]['content']
        return ""
    except:
        return ""

def save_user_notes(user_id, content):
    try:
        existing = supabase.table("notes").select("*").eq("user_id", user_id).execute()
        if existing.data:
            supabase.table("notes").update({
                "content": content,
                "updated_at": "NOW()"
            }).eq("user_id", user_id).execute()
        else:
            supabase.table("notes").insert({
                "user_id": user_id,
                "content": content
            }).execute()
    except Exception as e:
        pass

def save_chat_message(user_id, role, content):
    try:
        supabase.table("chat_history").insert({
            "user_id": user_id,
            "role": role,
            "content": content
        }).execute()
    except:
        pass

def get_chat_history(user_id):
    try:
        response = supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at").execute()
        return [{"role": msg["role"], "content": msg["content"]} for msg in response.data]
    except:
        return []

def is_premium(user_id):
    try:
        response = supabase.table("profiles").select("is_premium").eq("id", user_id).execute()
        if response.data:
            return response.data[0]['is_premium']
        return False
    except:
        return False