import streamlit as st
import json

st.header("Profile")

# Cek login
if not st.session_state.get("logged_in", False):
    st.warning("Silakan login terlebih dahulu")
    st.stop()

def read_user():
    with open("users.json", "r") as file:
        return json.load(file)

def save_user(user_data):
    with open("users.json", "w") as file:
        json.dump(user_data, file, indent=2)

def remove_from_favorites(recipe_id):
    users = read_user()
    username = st.session_state.username
    favorites = users[username].get("favorites", [])
    
    # Filter out recipe dengan id yang cocok
    users[username]["favorites"] = [f for f in favorites if f["id"] != recipe_id]
    save_user(users)

def search_favorites(query):
    users = read_user()
    username = st.session_state.username
    favorites = users[username].get("favorites", [])
    
    # Linear search di array favorites
    query_lower = query.lower()
    results = []
    
    for recipe in favorites:
        if query_lower in recipe["name"].lower():
            results.append(recipe)
    
    return results

# Tampilkan info user
username = st.session_state.username
st.subheader(f"Hello, {username}!")

st.markdown("---")

# Tampilkan favorit
st.subheader("Resep Favorit Saya")

# Fitur search
search_query = st.text_input("Cari resep favorit", placeholder="Ketik nama resep...")

users = read_user()
favorites = users[username].get("favorites", [])

# Filter berdasarkan search
if search_query:
    favorites = search_favorites(search_query)
    st.write(f"Ditemukan {len(favorites)} resep")

if len(favorites) == 0:
    if search_query:
        st.info("Tidak ada resep yang cocok dengan pencarian")
    else:
        st.info("Belum ada resep favorit. Tambahkan resep dari halaman Home!")
else:
    st.write(f"Total resep favorit: {len(favorites)}")
    
    # Sorting option
    sort_option = st.selectbox("Urutkan berdasarkan", ["Nama A-Z", "Nama Z-A", "Kategori", "Area"])
    
    # Bubble sort implementation
    def bubble_sort(arr, key, reverse=False):
        n = len(arr)
        sorted_arr = arr.copy()
        
        for i in range(n):
            for j in range(0, n-i-1):
                if reverse:
                    if sorted_arr[j][key].lower() < sorted_arr[j+1][key].lower():
                        sorted_arr[j], sorted_arr[j+1] = sorted_arr[j+1], sorted_arr[j]
                else:
                    if sorted_arr[j][key].lower() > sorted_arr[j+1][key].lower():
                        sorted_arr[j], sorted_arr[j+1] = sorted_arr[j+1], sorted_arr[j]
        
        return sorted_arr
    
    # Apply sorting
    if sort_option == "Nama A-Z":
        favorites = bubble_sort(favorites, "name", reverse=False)
    elif sort_option == "Nama Z-A":
        favorites = bubble_sort(favorites, "name", reverse=True)
    elif sort_option == "Kategori":
        favorites = bubble_sort(favorites, "category", reverse=False)
    elif sort_option == "Area":
        favorites = bubble_sort(favorites, "area", reverse=False)
    
    st.markdown("---")
    
    # Tampilkan dalam grid 3 kolom
    for idx in range(0, len(favorites), 3):
        cols = st.columns(3)
        
        for col_idx, col in enumerate(cols):
            if idx + col_idx < len(favorites):
                recipe = favorites[idx + col_idx]
                
                with col:
                    st.image(recipe["image"], use_container_width=True)
                    st.write(f"**{recipe['name']}**")
                    
                    if recipe.get("category"):
                        st.caption(f"Category: {recipe['category']}")
                    if recipe.get("area"):
                        st.caption(f"Area: {recipe['area']}")
                    
                    with st.expander("Lihat Instruksi"):
                        st.write(recipe["instructions"])
                    
                    if st.button("🗑️ Hapus", key=f"del_{recipe['id']}"):
                        remove_from_favorites(recipe["id"])
                        st.success("Resep dihapus dari favorit!")
                        st.rerun()
                    
                    st.markdown("---")

st.markdown("---")

# Tombol logout
if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.switch_page("login.py")