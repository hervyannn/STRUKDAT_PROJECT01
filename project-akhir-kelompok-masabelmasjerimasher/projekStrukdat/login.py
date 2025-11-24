import streamlit as st
import json
import base64


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# TAMBAHAN: Fungsi kompatibilitas untuk otentikasi (agar tidak mengubah logic asli)
def check_user_credentials(username, password, user_data):
    if username in user_data and user_data[username].get('password') == password:
        return True
    return False

with open("logo.png", "rb") as file:
    img_base64 = base64.b64encode(file.read()).decode()


st.markdown(f"""
<style>
.navbar {{
    position: relative;
    top: 0;
    width: 100%;
    left: 0;
    right: 0;
    padding: 10px;
    background-color: #9973a0;
    border-radius: 8px;
    color: white;
    font-size: 28px;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 15px;
    transition: all 0.3s ease;
}}

.navbar img {{
    height: 200px;
    width: 300px;
    border-radius: 20px;
}}

.navbar:hover {{
    background-color: #d487a8;
    color: #9973a0;
    transform: scale(1.01);
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}}
</style>

<div class="navbar">
    <img src="data:image/png;base64,{img_base64}" alt="Logo">
</div>
""", unsafe_allow_html=True)


st.markdown("<br><br>", unsafe_allow_html=True)


st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #9973a0;
    color: white;
    border: none;
    padding: 10px 60px;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
    transition: all 0.3s ease;
}
div.stButton > button:first-child:hover {
    background-color: #d487a8;
    transform: scale(1.05);
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    color: #9973a0;
}
</style>
""", unsafe_allow_html=True)

file_user="users.json"

def read_user():
    with open(file_user,"r") as file:
        return json.load(file)
    return{}

def save_user(user):
    with open(file_user,"w") as file:
        json.dump(user,file,indent=2)

user=read_user()


if "page_mode" not in st.session_state:
    st.session_state.page_mode = "login"
    
    
    
    
# ---- Login 
if st.session_state.page_mode == "login":
    st.title("LOG IN")
    st.text("Login to your account!")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in user and password == user[username]["password"]:
            # Simpan status login ke session_state
            st.session_state.logged_in = True
            st.session_state.username = username
            
            # Inisialisasi favorites jika belum ada
            if "favorites" not in user[username]:
                user[username]["favorites"] = []
                save_user(user)
            
            st.success("Login berhasil!")
            st.switch_page("pages/home.py")
        else:
            st.error("Username atau password salah.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.text("Don't have an account?")
    st.button("SignUp", on_click=lambda: st.session_state.update(page_mode="signup"))

# ---- SignUp
elif st.session_state.page_mode == "signup":
    st.title("SIGN UP")
    st.text("Create your account!")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")

    if st.button("Sign Up"):
        if new_username in user:
            st.error("This username is already exists!")
        elif new_password != confirm_password:
            st.error("Password error")
        elif new_username == "" or new_password == "":
            st.error("Username dan password tidak boleh kosong!")
        else:
            # Buat akun baru dengan field favorites
            user[new_username] = {
                "password": new_password,
                "favorites": []
            }
            save_user(user)
            st.success("Akun berhasil dibuat!")
            st.session_state.update(page_mode = "login")

    st.markdown("<br>", unsafe_allow_html=True)
    st.text("Already have an account?")
    st.button("Log In", on_click=lambda: st.session_state.update(page_mode="login"))