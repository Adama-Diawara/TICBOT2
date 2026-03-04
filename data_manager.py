import json
import os
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), 'reservations.json')

def load_data() -> List[Dict]:
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_data(data: List[Dict]) -> None:
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_availability(data: List[Dict], salle: str, date: str, heure: str) -> bool:
    for r in data:
        if r.get('salle') == salle and r.get('date') == date and r.get('heure') == heure:
            return False
    return True

def add_reservation(data: List[Dict], salle: str, date: str, heure: str, nom: Optional[str] = None, email: Optional[str] = None) -> Dict:
    reservation = {
        'id': (max((r.get('id', 0) for r in data), default=0) + 1),
        'salle': salle,
        'date': date,
        'heure': heure,
        'nom': nom or '',
        'email': email or ''
    }
    data.append(reservation)
    save_data(data)
    return reservation

def list_reservations(data: List[Dict]) -> List[Dict]:
    return data

def find_reservation_by_id(data: List[Dict], rid: int) -> Optional[Dict]:
    for r in data:
        if r.get('id') == rid:
            return r
    return None

def cancel_reservation(data: List[Dict], rid: int) -> bool:
    r = find_reservation_by_id(data, rid)
    if r:
        data.remove(r)
        save_data(data)
        return True
    return False

if __name__ == '__main__':
    print('data_manager ready, DB at', DB_PATH)
