import json
from datetime import datetime, timedelta
from typing import List, Dict, Union, Any
import streamlit as st  # <-- Necesario para leer los secrets
from supabase import create_client, Client # <-- pip install supabase

# --- 1. Flashcard Class (MODIFICADA) ---

class Flashcard:
    """Representa una flashcard. Ahora incluye un 'id' de la base de datos."""
    def __init__(self, front: str, back: str, 
                 next_review_date: str = None, 
                 interval: float = 0.0, 
                 easiness_factor: float = 2.5, 
                 repetitions: int = 0,
                 id: int = None): # <-- AÑADIDO: id de la base de datos
        
        self.id = id # <-- AÑADIDO
        self.front = front
        self.back = back
        self.next_review_date = next_review_date or datetime.now().isoformat()
        self.interval = interval
        self.easiness_factor = easiness_factor
        self.repetitions = repetitions
        
    def to_dict(self) -> Dict[str, Union[str, float, int]]:
        """Convierte a dict. Usado para ENVIAR a Supabase."""
        # Excluimos el 'id' al crear/actualizar, 
        # Supabase lo maneja (o se usa en el 'where' de la consulta)
        return {
            'front': self.front,
            'back': self.back,
            'next_review_date': self.next_review_date,
            'interval': self.interval,
            'easiness_factor': self.easiness_factor,
            'repetitions': self.repetitions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Crea un Flashcard desde un dict (cargado de SupABASE)."""
        # data['id'] existirá al venir de Supabase
        return cls(**data)

    def __repr__(self):
        return (f"Flashcard(id={self.id}, front='{self.front[:20]}...', "
                f"due={self.next_review_date[:10]}, EF={self.easiness_factor:.2f})")

# --- 2. Flashcard Manager Class (MODIFICADA) ---

class FlashcardsManager:
    """
    Gestiona las Flashcards usando Supabase como backend.
    """
    def __init__(self):
        # Ya no necesita 'filename'
        self.cards: List[Flashcard] = []
        self.supabase: Client = self._get_supabase_client()
        self._load_cards()

    def _get_supabase_client(self) -> Client:
        """Inicializa y devuelve el cliente de Supabase usando st.secrets."""
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            return create_client(url, key)
        except Exception as e:
            print(f"Error conectando a Supabase: {e}")
            # Esto detendrá la app si los secrets no están, lo cual es bueno.
            st.error("Error al conectar con Supabase. Revisa tus .streamlit/secrets.toml")
            st.stop()

    def _load_cards(self):
        """Carga las flashcards desde la base de datos de Supabase."""
        try:
            response = self.supabase.table("flashcards").select("*").order("next_review_date").execute()
            data = response.data
            self.cards = [Flashcard.from_dict(card_data) for card_data in data]
            print(f"Cargadas {len(self.cards)} tarjetas desde Supabase.")
        except Exception as e:
            print(f"Error al cargar tarjetas de Supabase: {e}")
            self.cards = [] # Empezar con lista vacía si falla la carga

    def save_cards(self):
        """
        ¡OBSOLETO! Esta función ya no es necesaria.
        Cada acción (add, update, review) se guarda en Supabase al instante.
        """
        pass

    def add_card(self, front: str, back: str):
        """Añade una nueva flashcard a Supabase y a la lista local."""
        new_card = Flashcard(front, back)
        
        try:
            # Inserta en Supabase (solo los datos, sin el 'id=None')
            data_to_insert = new_card.to_dict()
            response = self.supabase.table("flashcards").insert(data_to_insert).execute()
            
            # Obtiene la tarjeta completa (con el 'id' generado) de la respuesta
            new_card_data_from_db = response.data[0]
            new_card_obj = Flashcard.from_dict(new_card_data_from_db)
            
            # Añade el objeto completo a la lista local
            self.cards.append(new_card_obj)
            return new_card_obj
        
        except Exception as e:
            print(f"Error al añadir tarjeta a Supabase: {e}")
            return None

    def update_card(self, index: int, new_front: str = None, new_back: str = None) -> bool:
        """Actualiza el texto de una flashcard en Supabase y localmente."""
        if not (0 <= index < len(self.cards)):
            print(f"Error: Card index {index} out of bounds.")
            return False

        card = self.cards[index]
        if card.id is None:
            print("Error: La tarjeta no tiene ID, no se puede actualizar.")
            return False

        updates = {}
        if new_front is not None and card.front != new_front:
            updates['front'] = new_front
            card.front = new_front # Actualiza localmente
            
        if new_back is not None and card.back != new_back:
            updates['back'] = new_back
            card.back = new_back # Actualiza localmente

        if updates:
            try:
                # Actualiza en Supabase usando el ID
                self.supabase.table("flashcards").update(updates).eq("id", card.id).execute()
                print(f"Tarjeta {card.id} actualizada en Supabase.")
                return True
            except Exception as e:
                print(f"Error al actualizar tarjeta {card.id}: {e}")
                return False
        
        return False # No hubo cambios

    def review_card(self, card_index: int, grade: int):
        """Aplica SM-2 y actualiza la tarjeta en Supabase y localmente."""
        if not (0 <= card_index < len(self.cards)):
            print(f"Error: Card index {card_index} out of bounds.")
            return

        card = self.cards[card_index]
        if card.id is None:
            print("Error: La tarjeta no tiene ID, no se puede revisar.")
            return
            
        # --- Misma lógica SM-2 que tenías antes ---
        if grade == 0: q = 1
        elif grade == 1: q = 3
        elif grade == 2: q = 4
        elif grade == 3: q = 5
        else: return

        new_ef = card.easiness_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        card.easiness_factor = max(1.3, new_ef)

        if q >= 3:
            card.repetitions += 1
            if card.repetitions == 1: new_interval = 1.0
            elif card.repetitions == 2: new_interval = 6.0
            else: new_interval = card.interval * card.easiness_factor
            card.interval = new_interval
        else:
            card.repetitions = 0
            card.interval = 1.0
            
        days_to_add = int(round(card.interval))
        card.next_review_date = (datetime.now() + timedelta(days=days_to_add)).isoformat()
        
        # --- FIN Lógica SM-2 ---

        # Ahora, guarda estos cambios en Supabase
        try:
            updates_to_send = {
                'next_review_date': card.next_review_date,
                'interval': card.interval,
                'easiness_factor': card.easiness_factor,
                'repetitions': card.repetitions
            }
            self.supabase.table("flashcards").update(updates_to_send).eq("id", card.id).execute()
            print(f"Revisión de tarjeta {card.id} guardada en Supabase.")
            return days_to_add
        except Exception as e:
            print(f"Error al guardar revisión de tarjeta {card.id}: {e}")
            
    def delete_card_by_index(self, index: int):
        """Elimina una tarjeta de Supabase y de la lista local."""
        if not (0 <= index < len(self.cards)):
            print(f"Error: Card index {index} out of bounds.")
            return False
            
        card = self.cards[index]
        if card.id is None:
            print("Error: La tarjeta no tiene ID, no se puede eliminar.")
            return False
            
        try:
            # 1. Eliminar de Supabase
            self.supabase.table("flashcards").delete().eq("id", card.id).execute()
            
            # 2. Eliminar de la lista local
            del self.cards[index]
            print(f"Tarjeta {card.id} eliminada.")
            return True
        except Exception as e:
            print(f"Error al eliminar tarjeta {card.id}: {e}")
            return False

# --- 3. Global Manager Instance and Streamlit Wrapper Functions ---

# Inicializa el manager. 
# Esto se ejecutará una vez cuando Streamlit corra el script.
manager = FlashcardsManager()

# ---
# ¡BUENAS NOTICIAS!
# Todas tus funciones wrapper (las que usan tus páginas de Streamlit)
# deberían funcionar EXACTAMENTE IGUAL, excepto 'delete_card_by_index'
# que moví dentro del manager para que tenga acceso a 'self.supabase'.
# ---

def load_all_cards() -> List[Dict[str, Any]]:
    """Carga todas las tarjetas (como dicts) desde el manager (que está en memoria)."""
    # La 'card_index' ahora es el índice de la lista local 'manager.cards'
    return [{'card': card.to_dict(), 'card_index': i} 
            for i, card in enumerate(manager.cards)]

def add_new_card(front: str, back: str):
    """Wrapper para añadir tarjeta."""
    manager.add_card(front, back)

def update_card_by_index(index: int, new_front: str = None, new_back: str = None) -> bool:
    """Wrapper para actualizar tarjeta."""
    return manager.update_card(index, new_front, new_back)

def delete_card_by_index(index: int):
    """Wrapper para eliminar tarjeta."""
    # Llama al nuevo método del manager
    return manager.delete_card_by_index(index)

def get_due_cards() -> List[Dict[str, Any]]:
    """Obtiene tarjetas vencidas desde la lista en memoria del manager."""
    now = datetime.now()
    due_cards_with_index = []
    
    # Itera sobre la lista local 'manager.cards'
    for i, card in enumerate(manager.cards):
        try:
            # Asegúrate de que la fecha sea 'aware' (con timezone) o 'naive' de forma consistente
            # datetime.now() es 'naive', así que convirtamos la de la BD a 'naive'
            due_date = datetime.fromisoformat(card.next_review_date)
            if due_date.tzinfo:
                due_date = due_date.replace(tzinfo=None) # Hacerla naive para comparar
                
            if due_date <= now:
                due_cards_with_index.append({
                    'card': card.to_dict(),
                    'card_index': i
                })
        except ValueError:
            due_cards_with_index.append({
                'card': card.to_dict(),
                'card_index': i
            })

    due_cards_with_index.sort(key=lambda item: datetime.fromisoformat(item['card']['next_review_date']))
    
    return due_cards_with_index

def update_review_status(card_index: int, grade_string: str) -> int:
    """Wrapper para revisar tarjeta."""
    grade_map = {"Again": 0, "Hard": 1, "Good": 2, "Easy": 3}
    grade = grade_map.get(grade_string, -1)
    
    if grade == -1: return 0
    
    return manager.review_card(card_index, grade)