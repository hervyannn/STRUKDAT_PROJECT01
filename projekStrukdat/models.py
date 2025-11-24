
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from queue import Queue


class User:
    
    def __init__(self, user_id: int, username: str, email: str, password_hash: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        
        
        self.favorites: List[int] = [] 
        
        
        self.history_queue = Queue(maxsize=10)
        
    def add_to_history(self, recipe_id: int):
        """Logika Queue FIFO Jeremy."""
        if self.history_queue.full():
            self.history_queue.get() 
        self.history_queue.put(recipe_id)
        
    def get_history_list(self) -> List[int]:
        
        return list(self.history_queue.queue)
        
    def to_profile_dict(self) -> Dict[str, Any]:
       
        return {
            "id": self.user_id,
            "username": self.username,
            "email": self.email,
            "favorites_count": len(self.favorites),
            "favorites_ids": self.favorites,
            "history_ids": self.get_history_list()
        }

class Recipe(BaseModel):
    """Class Recipe standar tim, hasil konversi dari API eksternal."""
    recipe_id: int
    name: str
    ingredients: List[str]
    instructions: str
    cooking_time: Optional[int] = None 
    image_url: Optional[str] = None



class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class FavoriteRequest(BaseModel):
    recipe_id: int