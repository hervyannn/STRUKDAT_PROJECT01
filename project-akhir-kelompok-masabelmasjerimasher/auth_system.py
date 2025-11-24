import json
import hashlib
from pathlib import Path
import streamlit as st
from datetime import datetime

class UserManager:
    """Class untuk mengelola data pengguna sesuai struktur login.py yang ada"""
    
    def __init__(self, file_path="users.json"):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Memastikan file users.json exists"""
        if not Path(self.file_path).exists():
            with open(self.file_path, "w") as file:
                json.dump({}, file)
    
    def read_users(self):
        """Membaca data pengguna dari file - sesuai format login.py"""
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_user(self, username, password, email=None):
        """Menyimpan data pengguna baru - dengan extended profile"""
        users = self.read_users()
        users[username] = {
            "password": password,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "profile": {
                "full_name": "",
                "bio": "",
                "avatar": ""
            }
        }
        with open(self.file_path, "w") as file:
            json.dump(users, file, indent=4)
    
    def update_user_profile(self, username, profile_data):
        """Update profile user"""
        users = self.read_users()
        if username in users:
            if "profile" not in users[username]:
                users[username]["profile"] = {}
            users[username]["profile"].update(profile_data)
            with open(self.file_path, "w") as file:
                json.dump(users, file, indent=4)
            return True
        return False
    
    def get_user_profile(self, username):
        """Mendapatkan profile user"""
        users = self.read_users()
        if username in users:
            return users[username].get("profile", {})
        return {}
    
    def user_exists(self, username):
        """Memeriksa apakah username sudah terdaftar"""
        users = self.read_users()
        return username in users
    
    def validate_login(self, username, password):
        """Validasi login pengguna - sesuai logic login.py"""
        users = self.read_users()
        if username in users and password == users[username].get("password"):
            # Update last login
            users[username]["last_login"] = datetime.now().isoformat()
            with open(self.file_path, "w") as file:
                json.dump(users, file, indent=4)
            return True
        return False

class AuthSystem:
    """Sistem autentikasi utama berdasarkan login.py"""
    
    def __init__(self):
        self.user_manager = UserManager()
    
    def register(self, username, password, confirm_password, email=None):
        """Registrasi user baru - sesuai logic login.py"""
        # Validasi input
        if not username or not password or not confirm_password:
            return False, "Please fill in all fields!"
        
        # Cek username sudah ada
        if self.user_manager.user_exists(username):
            return False, "This username already exists!"
        
        # Cek password match
        if password != confirm_password:
            return False, "Password error"
        
        # Validasi password strength (tambahan dari original)
        if len(password) < 6:
            return False, "Password must be at least 6 characters long!"
        
        # Simpan user
        self.user_manager.save_user(username, password, email)
        return True, "Account created successfully!"
    
    def login(self, username, password):
        """Login user - sesuai logic login.py"""
        # Validasi input
        if not username or not password:
            return False, "Please fill in all fields!"
        
        # Validasi credentials
        if self.user_manager.validate_login(username, password):
            return True, "Login successful!"
        else:
            return False, "Username or password incorrect."
    
    def logout(self, username):
        """Logout user"""
        # Di sini kita bisa menambahkan logika logout seperti:
        # - Menyimpan waktu logout
        # - Log aktivitas
        return True, "Logout successful!"
    
    def get_user_data(self, username):
        """Mendapatkan data user lengkap"""
        users = self.user_manager.read_users()
        return users.get(username)
    
    def update_profile(self, username, profile_data):
        """Update profile user"""
        success = self.user_manager.update_user_profile(username, profile_data)
        if success:
            return True, "Profile updated successfully!"
        return False, "Failed to update profile"
    
    def get_profile(self, username):
        """Mendapatkan profile user"""
        return self.user_manager.get_user_profile(username)

class SessionManager:
    """Manager untuk session Streamlit"""
    
    def __init__(self):
        self.initialize_session()
    
    def initialize_session(self):
        """Initialize session state sesuai login.py"""
        if "page_mode" not in st.session_state:
            st.session_state.page_mode = "login"
        if "current_user" not in st.session_state:
            st.session_state.current_user = None
        if "auth_system" not in st.session_state:
            st.session_state.auth_system = AuthSystem()
        if "is_logged_in" not in st.session_state:
            st.session_state.is_logged_in = False
    
    def set_login_mode(self):
        """Set mode ke login"""
        st.session_state.page_mode = "login"
    
    def set_signup_mode(self):
        """Set mode ke signup"""
        st.session_state.page_mode = "signup"
    
    def set_current_user(self, username):
        """Set user yang sedang login"""
        st.session_state.current_user = username
        st.session_state.is_logged_in = True
    
    def get_current_user(self):
        """Get user yang sedang login"""
        return st.session_state.current_user
    
    def logout(self):
        """Logout user - clear semua session state terkait login"""
        if st.session_state.current_user:
            # Panggil logout dari auth system
            st.session_state.auth_system.logout(st.session_state.current_user)
        
        # Reset semua session state
        st.session_state.current_user = None
        st.session_state.is_logged_in = False
        st.session_state.page_mode = "login"
    
    def is_logged_in(self):
        """Cek apakah user sudah login"""
        return st.session_state.is_logged_in and st.session_state.current_user is not None
    
    def get_login_status(self):
        """Get status login lengkap"""
        return {
            "is_logged_in": self.is_logged_in(),
            "current_user": self.get_current_user(),
            "page_mode": st.session_state.page_mode
        }