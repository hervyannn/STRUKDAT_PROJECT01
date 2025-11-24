import streamlit as st
import json
import base64
from datetime import datetime

st.set_page_config(
    page_title="Recipe App - Login",
    page_icon="🍳",
    layout="centered"
)

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "login"

# CSS Styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #9973a0, #d487a8);
    padding: 40px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.login-card {
    background-color: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border-left: 5px solid #9973a0;
}



div.stButton > button {
    background-color: #9973a0;
    color: ;
    border: none;
    padding: 12px 40px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
    transition: all 0.3s ease;
    width: 100%;
}

div.stButton > button:hover {
    background-color: #d487a8;
    transform: scale(1.02);
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.preference-section {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin-top: 15px;
    border-left: 4px solid #9973a0;
}

.info-box {
    background-color: #e3f2fd;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #2196F3;
    margin: 10px 0;
}

.logo-container {
    text-align: center;
    margin-bottom: 20px;
}

.logo-container img {
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

file_user = "users.json"

def read_user():
    try:
        with open(file_user, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user(user):
    with open(file_user, "w") as file:
        json.dump(user, file, indent=2)

def create_new_user(username, password, email, preferences):
    return {
        "password": password,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat(),
        "preferences": preferences,
        "favorites": [],
        "history": [],
        "profile": {
            "full_name": "",
            "bio": ""
        }
    }

users = read_user()

# Logo Display
try:
    with open("logo.png", "rb") as file:
        img_base64 = base64.b64encode(file.read()).decode()
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{img_base64}" alt="Logo" style="max-width: 300px; height: auto;">
    </div>
    """, unsafe_allow_html=True)
except:
    st.markdown("""
    <div class="main-header">
        <h1>🍳 Recipe App</h1>
        <p>Your Personal Recipe Assistant</p>
    </div>
    """, unsafe_allow_html=True)

# Login Page
if st.session_state.page_mode == "login":
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Login</h1>
        <p>Welcome back! Please login to your account</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.subheader("Login to Your Account")
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("🔑 Login", use_container_width=True)
            with col2:
                forgot_button = st.form_submit_button("❓ Forgot Password", use_container_width=True)
            
            if login_button:
                if not username or not password:
                    st.error("❌ Please fill in all fields")
                elif username in users and password == users[username]["password"]:
                    # Update last login
                    users[username]["last_login"] = datetime.now().isoformat()
                    save_user(users)
                    
                    # Set session state
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    
                    # Initialize favorites if not exists
                    if "favorites" not in users[username]:
                        users[username]["favorites"] = []
                        save_user(users)
                    
                    st.success("✅ Login successful!")
                    st.balloons()
                    st.switch_page("pages/home.py")
                else:
                    st.error("❌ Invalid username or password")
            
            if forgot_button:
                st.info("🔄 Password reset functionality would be implemented here")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("---")
            st.markdown("<p style='text-align: center;'>Don't have an account?</p>", unsafe_allow_html=True)
            if st.button("📝 Create New Account", use_container_width=True):
                st.session_state.page_mode = "signup"
                st.rerun()

# Signup Page
elif st.session_state.page_mode == "signup":
    st.markdown("""
    <div class="main-header">
        <h1>📝 Sign Up</h1>
        <p>Create your account and start cooking!</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="signup-card">', unsafe_allow_html=True)
        
        with st.form("signup_form"):
            st.subheader("Create Your Account")
            
            # Basic Information
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("👤 Username", placeholder="Choose a username")
            with col2:
                new_email = st.text_input("📧 Email", placeholder="Enter your email")
            
            col3, col4 = st.columns(2)
            with col3:
                new_password = st.text_input("🔒 Password", type="password", 
                                            placeholder="Choose a password",
                                            help="Minimum 6 characters")
            with col4:
                confirm_password = st.text_input("🔒 Confirm Password", type="password",
                                                placeholder="Confirm your password")
            
            st.markdown("---")
            
            # Dietary Preferences Section
            st.markdown("""
            <div class="preference-section">
                <h4>🥗 Dietary Preferences (Optional)</h4>
                <p>Help us personalize your experience</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Dietary Type
            dietary_type = st.selectbox(
                "🍽️ Dietary Type",
                ["None", "Vegetarian", "Vegan", "Pescatarian", "Halal", "Kosher"],
                help="Select your primary dietary preference"
            )
            
            # Diet Restrictions
            st.write("⚖️ Diet Restrictions")
            col1, col2, col3 = st.columns(3)
            with col1:
                low_sugar = st.checkbox("Low Sugar")
                low_salt = st.checkbox("Low Salt")
            with col2:
                low_calorie = st.checkbox("Low Calorie")
                keto = st.checkbox("Keto")
            with col3:
                paleo = st.checkbox("Paleo")
                gluten_free = st.checkbox("Gluten Free")
            
            # Allergies
            st.write("🚫 Food Allergies")
            col1, col2, col3 = st.columns(3)
            with col1:
                allergy_peanuts = st.checkbox("Peanuts")
                allergy_tree_nuts = st.checkbox("Tree Nuts")
            with col2:
                allergy_milk = st.checkbox("Dairy/Milk")
                allergy_eggs = st.checkbox("Eggs")
            with col3:
                allergy_seafood = st.checkbox("Seafood")
                allergy_shellfish = st.checkbox("Shellfish")
            
            col4, col5 = st.columns(2)
            with col4:
                allergy_soy = st.checkbox("Soy")
            with col5:
                allergy_wheat = st.checkbox("Wheat/Gluten")
            
            # Additional allergies
            other_allergies = st.text_input("Other Allergies (comma-separated)", 
                                           placeholder="e.g., sesame, mustard")
            
            st.markdown("---")
            
            # Terms and Conditions
            agree_terms = st.checkbox("I agree to the Terms and Conditions")
            
            # Submit Button
            signup_button = st.form_submit_button("✨ Create Account", use_container_width=True)
            
            if signup_button:
                # Validation
                if not new_username or not new_password or not new_email:
                    st.error("❌ Please fill in all required fields (Username, Email, Password)")
                elif new_username in users:
                    st.error("❌ Username already exists! Please choose another one.")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match!")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters long!")
                elif not agree_terms:
                    st.error("❌ Please agree to the Terms and Conditions")
                else:
                    # Collect diet restrictions
                    diet_restrictions = []
                    if low_sugar: diet_restrictions.append("low-sugar")
                    if low_salt: diet_restrictions.append("low-salt")
                    if low_calorie: diet_restrictions.append("low-calorie")
                    if keto: diet_restrictions.append("keto")
                    if paleo: diet_restrictions.append("paleo")
                    if gluten_free: diet_restrictions.append("gluten-free")
                    
                    # Collect allergies
                    allergies = []
                    if allergy_peanuts: allergies.append("peanuts")
                    if allergy_tree_nuts: allergies.append("tree-nuts")
                    if allergy_milk: allergies.append("dairy")
                    if allergy_eggs: allergies.append("eggs")
                    if allergy_seafood: allergies.append("seafood")
                    if allergy_shellfish: allergies.append("shellfish")
                    if allergy_soy: allergies.append("soy")
                    if allergy_wheat: allergies.append("wheat")
                    
                    # Add other allergies
                    if other_allergies:
                        other_list = [a.strip() for a in other_allergies.split(",")]
                        allergies.extend(other_list)
                    
                    # Create preferences dictionary
                    preferences = {
                        "dietary_type": dietary_type if dietary_type != "None" else "",
                        "diet_restrictions": diet_restrictions,
                        "allergies": allergies
                    }
                    
                    # Create new user
                    users[new_username] = create_new_user(
                        new_username, 
                        new_password, 
                        new_email, 
                        preferences
                    )
                    save_user(users)
                    
                    st.success("✅ Account created successfully!")
                    st.balloons()
                    st.info("🔄 Redirecting to login page...")
                    st.session_state.page_mode = "login"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("---")
            st.markdown("<p style='text-align: center;'>Already have an account?</p>", unsafe_allow_html=True)
            if st.button("🔑 Login Here", use_container_width=True):
                st.session_state.page_mode = "login"
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>🍳 Recipe App © 2024 | Your Personal Cooking Assistant</p>
    <p style='font-size: 12px;'>Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)