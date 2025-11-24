import streamlit as st
import requests
import pandas as pd
import json
import string
import google.generativeai as genai
import os
import re
import time
from dotenv import load_dotenv

# ============================
# . Functions
# ============================

def read_user():
    with open("users.json", "r") as file:
        return json.load(file)


def save_user(user_data):
    with open("users.json", "w") as file:
        json.dump(user_data, file, indent=2)


def add_to_favorites(meal_data):
    users = read_user()
    username = st.session_state.username

    recipe = {
        "id": meal_data["idMeal"],
        "name": meal_data["strMeal"],
        "image": meal_data["strMealThumb"],
        "instructions": meal_data["strInstructions"],
        "category": meal_data.get("strCategory", ""),
        "area": meal_data.get("strArea", "")
    }

    favorites = users[username].get("favorites", [])
    favorite_ids = [f["id"] for f in favorites]

    if recipe["id"] not in favorite_ids:
        favorites.append(recipe)
        users[username]["favorites"] = favorites
        save_user(users)
        return True
    return False


def remove_from_favorites(recipe_id):
    users = read_user()
    username = st.session_state.username
    favorites = users[username].get("favorites", [])
    
    users[username]["favorites"] = [f for f in favorites if f["id"] != recipe_id]
    save_user(users)
    

def is_favorite(meal_id):
    users = read_user()
    username = st.session_state.username
    favorites = users[username].get("favorites", [])
    return meal_id in [f["id"] for f in favorites]


def favorite_button(data):
    if is_favorite(data["idMeal"]):
            st.write("❤️ Favorited")
    else:
            if st.button("🤍 Add", key=f"add_{data["idMeal"]}"):
                if add_to_favorites(data):
                    st.success("Ditambahkan ke favorit")
                    st.rerun()


def show_ingredients(data):
    count1=0
    count2=0
    ingredients=[]
    for bahan in data:
        if "strIngredient" in bahan:
            if data[bahan]==""or data[bahan]==" ":
                break
            count1+=1 
            ingredients.append(data[bahan])
            # st.text(f"{count}. {data[bahan]}")
    for measure in data:
        if "strMeasure" in measure:
            if data[measure]==""or data[measure]==" ":
                break
            count2+=1 
            st.text(f"{count2}.  {data[measure]}  {ingredients[count2-1]}")


def show_details(data):
    st.header(data["strMeal"])
    col1,col2,col3= st.columns(3)
    with col1:
        st.image(data["strMealThumb"],width=500)
        st.markdown("<br><br>", unsafe_allow_html=True)
    with col2:
        st.subheader("Cara Memasak!")
        st.write(data["strInstructions"])
        st.markdown("<br><br>", unsafe_allow_html=True)
    with col3:
        st.subheader("Bahan yang dibutuhkan!")
        show_ingredients(data)
        st.markdown("<br><br>", unsafe_allow_html=True)

def data_for_gemini():
    if "allMeals" not in st.session_state:
        all_api = [f"https://www.themealdb.com/api/json/v1/1/search.php?f={i}" for i in string.ascii_lowercase]
        names = []
        for link in all_api:
            data = requests.get(link).json()
            meals = data.get("meals") or []
            for meal in meals:
                names.append(meal["strMeal"])
        st.session_state.allMeals=names
    names=st.session_state.allMeals    
    return names
    
    
# ============================
# . Fungsi: Cari Resep
# ============================

def cari_resep():
    st.header("Cari Resep 🔎")

    nama = st.text_input("Masukkan nama makanan")

    if st.button("Cari"):
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={nama}"
        response = requests.get(url).json()

        if not response["meals"]:
            st.warning("Resep tidak ditemukan.")
            return

        meal = response["meals"][0]

        show_details(meal)
        
        


# ============================
# . Fungsi: FIlter resep dengan Ai
# ============================

def filter_by_gemini():
    st.header("Filter Resep ❇️")

    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    names=data_for_gemini()

    filters = st.multiselect("Pilih Filter", ["Vegan", "Gluten Free", "Less Sugar"])

    if st.button("Tampilkan Resep"):
        prompt = f"""
        Berdasarkan daftar resep berikut: {names}
        dan filter berikut: {filters},
        berikan 3-5 rekomendasi resep yang memenuhi kriteria di atas!.
        Kembalikan strMeal HANYA dalam format json, contoh:
        (resep:["strMeal", "strMeal", "strMeal"])
        Tidak boleh ada teks penjelasan.
        """
        
        response = model.generate_content(prompt)
        data= response.text

        match = re.search(r"```json(.*?)```", data, re.S)
        json_str = match.group(1).strip()
        data = json.loads(json_str)
        data=data["resep"]

        for meal in data:
            api_Meal_by_name=(f"https://www.themealdb.com/api/json/v1/1/search.php?s={meal}")
            data = requests.get(api_Meal_by_name).json()
            meal = data["meals"]
            
            st.subheader(meal[0]["strMeal"])
            st.image(meal[0]["strMealThumb"],width=200)
            favorite_button(meal[0])

# ============================
# . Fungsi: Rekomendasi Randm
# ============================

def rekomendasi_random():
    st.header("Rekomendasi")

    if "rekomendasi" not in st.session_state:
        st.session_state.rekomendasi = []
    if "rec_page" not in st.session_state:
        st.session_state.rec_page = 0

    if st.button("Refresh 🔄️"):
        st.session_state.rekomendasi = []
        for _ in range(10):
            data = requests.get("https://www.themealdb.com/api/json/v1/1/random.php").json()
            st.session_state.rekomendasi.extend(data["meals"])
        st.session_state.rec_page = 0

    if not st.session_state.rekomendasi:
        return

    per_page = 5
    start = st.session_state.rec_page * per_page
    end = start + per_page
    page_data = st.session_state.rekomendasi[start:end]

    for meal in page_data:
        st.markdown("---")
        st.write(f"### {meal['strMeal']}")
        col1,col2,col3 = st.columns(3)
        with col1 :

            st.image(meal["strMealThumb"], width=500)
            favorite_button(meal)
        with col2:
            # with st.expander("Cara Memasak"):
            st.subheader("Cara Memasak!")
            st.write(meal["strInstructions"])
        with col3:
            # with st.expander("Ingredients"):
            st.subheader("Bahan yang dibutuhkan!")
            show_ingredients(meal)
                
    
    # Paging
    col1, col2 = st.columns(2)
    if col1.button("◀️Prev") and st.session_state.rec_page > 0:
        st.session_state.rec_page -= 1
        st.rerun()
    if col2.button("Next▶️") and end < len(st.session_state.rekomendasi):
        st.session_state.rec_page += 1
        st.rerun()

# ============================
# . Fungsi: FIlter resep dengan Ai
# ============================

def rekomendasi_gemini():
    st.header("Rekomendasi By Gemini ❇️")

    jenis_makanan= st. text_input("Jenis makanan apa yang anda inginkan?")
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    names=data_for_gemini()

    if st.button("Cari makanan"):
        prompt = f"""
        Berdasarkan daftar resep berikut: {names}, dan jenis makanan {jenis_makanan}
        berikan 1 rekomendasi/tidak boleh lebih. resep berdasarkan daftar dan jenis makanan, 
        dan juga alasan mengapa merekomendasikan makanan tersebut!.
        apapun hasilnya tetap Kembalikan 1 strMeal, dan alasannya HANYA dalam format json seperti contoh ini:
        (resep:("strMeal":"nama_resep", "alasan":"alasan")) # tanda "("/")" adalah jurung kurawal.
        Tidak boleh ada teks penjelasan tambahan dan harus sama persis dengan format.
        """
        
        response = model.generate_content(prompt)
        data= response.text
        
        meal_match = re.search(r'"strMeal"\s*:\s*"([^"]+)"', data)
        meal = meal_match.group(1) if meal_match else None

        alasan_match = re.search(r'"alasan"\s*:\s*"([^"]+)"', data)
        alasan = alasan_match.group(1) if alasan_match else None
        
        
        api_Meal_by_name=(f"https://www.themealdb.com/api/json/v1/1/search.php?s={meal}")
        data = requests.get(api_Meal_by_name).json()
        meal = data["meals"]
        
        with st.spinner("..."):
            time.sleep(3)
        st.info(alasan)
        show_details(meal[0])
        favorite_button(meal[0])



# ============================
# . MAIN PAGE
# ============================

st.header("Home")

if not st.session_state.get("logged_in", False):
    st.warning("Silakan login terlebih dahulu")
    st.stop()

cari_resep()
st.markdown("---")
filter_by_gemini()
st.markdown("---")
rekomendasi_random()
st.markdown("---")
rekomendasi_gemini()