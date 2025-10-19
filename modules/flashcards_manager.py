import json
from datetime import datetime, timedelta
from typing import List, Dict, Union, Any

# --- 1. Flashcard Class ---

class Flashcard:
    """Represents a single flashcard with Spaced Repetition data."""
    def __init__(self, front: str, back: str, 
                 next_review_date: str = None, 
                 interval: float = 0.0, 
                 easiness_factor: float = 2.5, 
                 repetitions: int = 0):
        
        self.front = front
        self.back = back
        # The date the card is due for review. Stored as an ISO format string.
        self.next_review_date = next_review_date or datetime.now().isoformat()
        
        # SM-2 Parameters
        self.interval = interval            # The number of days until the next review
        self.easiness_factor = easiness_factor # The factor (EF) that determines interval growth
        self.repetitions = repetitions      # Consecutive successful reviews (used by SM-2)
        
    def to_dict(self) -> Dict[str, Union[str, float, int]]:
        """Converts the Flashcard object to a dictionary for JSON serialization."""
        return {
            'front': self.front,
            'back': self.back,
            'next_review_date': self.next_review_date,
            'interval': self.interval,
            'easiness_factor': self.easiness_factor,
            'repetitions': self.repetitions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, float, int]]):
        """Creates a Flashcard object from a dictionary loaded from JSON."""
        return cls(**data)

    def __repr__(self):
        return (f"Flashcard(front='{self.front[:20]}...', "
                f"due={self.next_review_date[:10]}, EF={self.easiness_factor:.2f})")

# --- 2. Flashcard Manager Class ---

class FlashcardsManager:
    """
    Manages a collection of Flashcards using the SM-2 Spaced Repetition algorithm.
    Persistence is handled via JSON file storage.
    """
    def __init__(self, filename: str = 'data/flashcards.json'):
        self.filename = filename
        self.cards: List[Flashcard] = []
        self._load_cards()

    def _load_cards(self):
        """Loads flashcards from the JSON file."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cards = [Flashcard.from_dict(card_data) for card_data in data]
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.filename}. Data might be corrupted.")

    def save_cards(self):
        """Saves all flashcards to the JSON file."""
        data = [card.to_dict() for card in self.cards]
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving file: {e}")

    def add_card(self, front: str, back: str):
        """Adds a new flashcard to the manager."""
        new_card = Flashcard(front, back)
        self.cards.append(new_card)
        self.save_cards()
        return new_card

    def review_card(self, card_index: int, grade: int):
        """
        Applies the SM-2 algorithm to a card by its index in the main list.
        Grade mapping: 0=Again, 1=Hard, 2=Good, 3=Easy.
        """
        if not (0 <= card_index < len(self.cards)):
            print(f"Error: Card index {card_index} out of bounds.")
            return

        card = self.cards[card_index]
        
        # --- Map Integer Grade to SM-2 Quality (q) ---
        if grade == 0:
            q = 1  # Again/Forgotten (Failure, q < 3)
        elif grade == 1:
            q = 3  # Hard/Difficult (Success, q >= 3)
        elif grade == 2:
            q = 4  # Good/OK (Success, q >= 3)
        elif grade == 3:
            q = 5  # Easy/Perfect (Success, q >= 3)
        else:
            print(f"Invalid integer grade '{grade}'. Must be 0, 1, 2, or 3. Card state unchanged.")
            return

        # 1. Calculate new Easiness Factor (EF)
        new_ef = card.easiness_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        card.easiness_factor = max(1.3, new_ef)

        # 2. Update Repetitions and Interval
        if q >= 3: # Successful Recall (Hard, Good, or Easy)
            card.repetitions += 1
            
            if card.repetitions == 1:
                new_interval = 1.0 
            elif card.repetitions == 2:
                new_interval = 6.0 
            else:
                new_interval = card.interval * card.easiness_factor
                
            card.interval = new_interval
        else: # If q < 3 (Only 'Again' / grade 0), the card failed.
            card.repetitions = 0      # Reset successful repetitions count
            card.interval = 1.0       # Reset interval to 1 day
            
        # 3. Set the next review date
        days_to_add = int(round(card.interval))
        card.next_review_date = (datetime.now() + timedelta(days=days_to_add)).isoformat()
        
        self.save_cards()
        return days_to_add # Return the interval for confirmation

# --- 3. Global Manager Instance and Streamlit Wrapper Functions ---

# Initialize the single manager instance globally
manager = FlashcardsManager()

def load_all_cards() -> List[Dict[str, Any]]:
    """Loads all cards (as dictionaries) from the manager for display."""
    # We include the original index for easy mapping back in review/delete actions
    return [{'card': card.to_dict(), 'original_index': i} 
            for i, card in enumerate(manager.cards)]

def add_new_card(front: str, back: str):
    """Wrapper to add a card to the manager."""
    manager.add_card(front, back)

def delete_card_by_index(index: int):
    """Deletes a card from the manager's list by its index."""
    if 0 <= index < len(manager.cards):
        del manager.cards[index]
        manager.save_cards()

def get_due_cards() -> List[Dict[str, Any]]:
    """
    Returns only cards due for review, along with their original index,
    for the Streamlit review view.
    """
    now = datetime.now()
    due_cards_with_index = []
    
    for i, card in enumerate(manager.cards):
        try:
            due_date = datetime.fromisoformat(card.next_review_date)
            if due_date <= now:
                due_cards_with_index.append({
                    'card': card.to_dict(),
                    'original_index': i
                })
        except ValueError:
            # Card has a malformed date, treat as due immediately
            due_cards_with_index.append({
                'card': card.to_dict(),
                'original_index': i
            })

    # Sort by due date (oldest first)
    due_cards_with_index.sort(key=lambda item: datetime.fromisoformat(item['card']['next_review_date']))
    
    return due_cards_with_index

def update_review_status(original_index: int, grade_string: str) -> int:
    """
    Maps string grade to integer grade (0-3) and calls the manager's review logic.
    """
    # Map Streamlit UI strings to SM-2 integer grades (0-3)
    grade_map = {
        "Again": 0,
        "Hard": 1,
        "Good": 2,
        "Easy": 3,
    }
    grade = grade_map.get(grade_string, -1)
    
    if grade == -1:
        print(f"Error: Unknown grade string '{grade_string}'.")
        return 0
    
    # Call the manager's core review logic
    return manager.review_card(original_index, grade)
