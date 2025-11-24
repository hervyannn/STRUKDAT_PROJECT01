import requests
from typing import List, Dict, Optional
from models import Recipe

class RecipeAPIService:
    """Service untuk integrasi multiple API eksternal"""
    
    def __init__(self):
        # TheMealDB - Free, no key required
        self.themealdb_base = "https://www.themealdb.com/api/json/v1/1"
        
        # Edamam - Requires APP_ID and APP_KEY
        self.edamam_base = "https://api.edamam.com/api/recipes/v2"
        self.edamam_app_id = "YOUR_EDAMAM_APP_ID"  # Replace with your credentials
        self.edamam_app_key = "YOUR_EDAMAM_APP_KEY"
        
        # API-Ninjas - Requires API_KEY
        self.apininjas_base = "https://api.api-ninjas.com/v1/recipe"
        self.apininjas_key = "YOUR_APININJAS_KEY"  # Replace with your key
    
    # ==================== THEMEALDB API ====================
    
    def search_recipes_themealdb(self, query: str) -> List[Recipe]:
        """Cari resep dari TheMealDB berdasarkan nama"""
        try:
            url = f"{self.themealdb_base}/search.php?s={query}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("meals"):
                return []
            
            recipes = []
            for meal in data["meals"][:10]:
                ingredients = self._parse_themealdb_ingredients(meal)
                
                recipe = Recipe(
                    recipe_id=f"tmd_{meal['idMeal']}",
                    name=meal["strMeal"],
                    ingredients=ingredients,
                    instructions=meal["strInstructions"],
                    cook_time=0,
                    image_url=meal.get("strMealThumb", ""),
                    diet_tags=[meal.get("strCategory", ""), meal.get("strArea", "")],
                    calories=0
                )
                recipes.append(recipe)
            
            return recipes
        except Exception as e:
            print(f"Error fetching from TheMealDB: {e}")
            return []
    
    def get_recipe_by_id_themealdb(self, recipe_id: str) -> Optional[Recipe]:
        """Ambil detail resep dari TheMealDB berdasarkan ID"""
        try:
            meal_id = recipe_id.replace("tmd_", "")
            url = f"{self.themealdb_base}/lookup.php?i={meal_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("meals"):
                return None
            
            meal = data["meals"][0]
            ingredients = self._parse_themealdb_ingredients(meal)
            
            recipe = Recipe(
                recipe_id=f"tmd_{meal['idMeal']}",
                name=meal["strMeal"],
                ingredients=ingredients,
                instructions=meal["strInstructions"],
                cook_time=0,
                image_url=meal.get("strMealThumb", ""),
                diet_tags=[meal.get("strCategory", ""), meal.get("strArea", "")],
                calories=0
            )
            
            return recipe
        except Exception as e:
            print(f"Error fetching recipe by ID from TheMealDB: {e}")
            return None
    
    def get_random_recipes_themealdb(self, count: int = 5) -> List[Recipe]:
        """Ambil resep random dari TheMealDB"""
        recipes = []
        try:
            for _ in range(count):
                url = f"{self.themealdb_base}/random.php"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data.get("meals"):
                    meal = data["meals"][0]
                    ingredients = self._parse_themealdb_ingredients(meal)
                    
                    recipe = Recipe(
                        recipe_id=f"tmd_{meal['idMeal']}",
                        name=meal["strMeal"],
                        ingredients=ingredients,
                        instructions=meal["strInstructions"],
                        cook_time=0,
                        image_url=meal.get("strMealThumb", ""),
                        diet_tags=[meal.get("strCategory", ""), meal.get("strArea", "")],
                        calories=0
                    )
                    recipes.append(recipe)
        except Exception as e:
            print(f"Error fetching random recipes from TheMealDB: {e}")
        
        return recipes
    
    def _parse_themealdb_ingredients(self, meal: Dict) -> List[str]:
        """Parse ingredients dari TheMealDB response"""
        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}", "")
            measure = meal.get(f"strMeasure{i}", "")
            if ing and ing.strip():
                ingredients.append(f"{measure} {ing}".strip())
        return ingredients
    
    # ==================== EDAMAM API ====================
    
    def search_recipes_edamam(self, query: str, diet: str = None) -> List[Recipe]:
        """Cari resep dari Edamam API"""
        try:
            url = f"{self.edamam_base}"
            params = {
                "type": "public",
                "q": query,
                "app_id": self.edamam_app_id,
                "app_key": self.edamam_app_key,
                "to": 10
            }
            
            if diet:
                params["diet"] = diet
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("hits"):
                return []
            
            recipes = []
            for hit in data["hits"]:
                recipe_data = hit["recipe"]
                
                ingredients = [
                    ing["text"] for ing in recipe_data.get("ingredients", [])
                ]
                
                diet_tags = recipe_data.get("dietLabels", []) + recipe_data.get("healthLabels", [])
                
                recipe = Recipe(
                    recipe_id=f"eda_{hash(recipe_data['uri'])}",
                    name=recipe_data["label"],
                    ingredients=ingredients,
                    instructions=recipe_data.get("url", "See full recipe at source"),
                    cook_time=int(recipe_data.get("totalTime", 0)),
                    image_url=recipe_data.get("image", ""),
                    diet_tags=diet_tags[:5],
                    calories=int(recipe_data.get("calories", 0))
                )
                recipes.append(recipe)
            
            return recipes
        except Exception as e:
            print(f"Error fetching from Edamam: {e}")
            return []
    
    def get_recipe_by_id_edamam(self, recipe_id: str) -> Optional[Recipe]:
        """Ambil detail resep dari Edamam (menggunakan URI)"""
        try:
            uri = recipe_id.replace("eda_", "")
            url = f"{self.edamam_base}/{uri}"
            params = {
                "type": "public",
                "app_id": self.edamam_app_id,
                "app_key": self.edamam_app_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            recipe_data = data["recipe"]
            ingredients = [ing["text"] for ing in recipe_data.get("ingredients", [])]
            diet_tags = recipe_data.get("dietLabels", []) + recipe_data.get("healthLabels", [])
            
            recipe = Recipe(
                recipe_id=recipe_id,
                name=recipe_data["label"],
                ingredients=ingredients,
                instructions=recipe_data.get("url", "See full recipe at source"),
                cook_time=int(recipe_data.get("totalTime", 0)),
                image_url=recipe_data.get("image", ""),
                diet_tags=diet_tags[:5],
                calories=int(recipe_data.get("calories", 0))
            )
            
            return recipe
        except Exception as e:
            print(f"Error fetching recipe by ID from Edamam: {e}")
            return None
    
    # ==================== API-NINJAS ====================
    
    def search_recipes_apininjas(self, query: str) -> List[Recipe]:
        """Cari resep dari API-Ninjas"""
        try:
            url = f"{self.apininjas_base}"
            headers = {"X-Api-Key": self.apininjas_key}
            params = {"query": query}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return []
            
            recipes = []
            for item in data[:10]:
                recipe = Recipe(
                    recipe_id=f"nin_{hash(item['title'])}",
                    name=item["title"],
                    ingredients=item.get("ingredients", "").split("|"),
                    instructions=item.get("instructions", ""),
                    cook_time=0,
                    image_url="",
                    diet_tags=[],
                    calories=0
                )
                recipes.append(recipe)
            
            return recipes
        except Exception as e:
            print(f"Error fetching from API-Ninjas: {e}")
            return []
    
    # ==================== UNIFIED SEARCH ====================
    
    def search_recipes_all(self, query: str, diet: str = None) -> List[Recipe]:
        """Search dari semua API sekaligus dan gabungkan hasil"""
        all_recipes = []
        
        # Try TheMealDB
        themealdb_recipes = self.search_recipes_themealdb(query)
        all_recipes.extend(themealdb_recipes)
        
        # Try Edamam
        edamam_recipes = self.search_recipes_edamam(query, diet)
        all_recipes.extend(edamam_recipes)
        
        # Try API-Ninjas
        apininjas_recipes = self.search_recipes_apininjas(query)
        all_recipes.extend(apininjas_recipes)
        
        # Remove duplicates based on similar names
        unique_recipes = self._remove_duplicate_recipes(all_recipes)
        
        return unique_recipes[:20]  # Return top 20
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Get recipe by ID from appropriate API"""
        if recipe_id.startswith("tmd_"):
            return self.get_recipe_by_id_themealdb(recipe_id)
        elif recipe_id.startswith("eda_"):
            return self.get_recipe_by_id_edamam(recipe_id)
        else:
            return None
    
    def _remove_duplicate_recipes(self, recipes: List[Recipe]) -> List[Recipe]:
        """Remove duplicate recipes based on name similarity"""
        seen_names = set()
        unique_recipes = []
        
        for recipe in recipes:
            name_lower = recipe.name.lower()
            if name_lower not in seen_names:
                seen_names.add(name_lower)
                unique_recipes.append(recipe)
        
        return unique_recipes
    
    def filter_by_diet(self, recipes: List[Recipe], diet_tags: List[str]) -> List[Recipe]:
        """Filter resep berdasarkan tag diet"""
        if not diet_tags:
            return recipes
        
        filtered = []
        for recipe in recipes:
            for tag in diet_tags:
                recipe_tags_lower = [t.lower() for t in recipe.diet_tags]
                if tag.lower() in recipe_tags_lower:
                    filtered.append(recipe)
                    break
        
        return filtered
    
    def get_api_status(self) -> Dict[str, bool]:
        """Check status semua API"""
        status = {}
        
        # Check TheMealDB
        try:
            response = requests.get(f"{self.themealdb_base}/random.php", timeout=5)
            status["themealdb"] = response.status_code == 200
        except:
            status["themealdb"] = False
        
        # Check Edamam
        try:
            url = f"{self.edamam_base}"
            params = {
                "type": "public",
                "q": "chicken",
                "app_id": self.edamam_app_id,
                "app_key": self.edamam_app_key,
                "to": 1
            }
            response = requests.get(url, params=params, timeout=5)
            status["edamam"] = response.status_code == 200
        except:
            status["edamam"] = False
        
        # Check API-Ninjas
        try:
            headers = {"X-Api-Key": self.apininjas_key}
            params = {"query": "chicken"}
            response = requests.get(self.apininjas_base, headers=headers, params=params, timeout=5)
            status["apininjas"] = response.status_code == 200
        except:
            status["apininjas"] = False
        
        return status