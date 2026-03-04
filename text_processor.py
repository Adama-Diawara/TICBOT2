import re
import string
import unicodedata
from typing import List, Tuple, Dict, Optional

STOP_WORDS = set([
    'le', 'la', 'les', 'un', 'une', 'de', 'du', 'des', 'et', 'en', 'a', 'au', 'aux',
    'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'que', 'qui', 'pour',
    'dans', 'sur', 'par', 'avec', 'sans', 'ce', 'ces', 'ses', 'son', 'sa', 'mais',
    'ou', 'donc', 'or', 'ni', 'car', 'si', 'bien', 'ne', 'pas', 'plus', 'moins', 'tres',
    'ici', 'la', 'là', 'svp', 'merci'
])

INTENTS = {
    'RESERVATION': ['reserver', 'reservation', 'book', 'prendre'],
    'HORAIRES': ['horaire', 'ouvert', 'ferme', 'heure', 'horaires'],
    'ANNULATION': ['annuler', 'supprimer', 'cancel', 'annulation']
}

RESPONSES = {
    'RESERVATION': {
        'complete': 'Réservation confirmée pour {date} à {heure} en salle {salle}.',
        'partial': 'Réservation pour {date} à {heure}. Quelle salle souhaitez-vous ?',
        'missing': "Pour réserver, j'ai besoin de la date et de l'heure."
    },
    'HORAIRES': {'default': "Nous sommes ouverts de 9h à 18h du lundi au vendredi."},
    'ANNULATION': {'default': 'Pour annuler une réservation, indiquez l\'ID ou utilisez /cancel <id>.'},
    'UNKNOWN': {'default': "Je n'ai pas compris. Demandez : réserver une salle, consulter les horaires, ou annuler."}
}

CORRECTIONS = {'vx': 'veux', 'dmain': 'demain', 'demai': 'demain'}

def _strip_accents(text: str) -> str:
    nkfd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nkfd if not unicodedata.combining(c)])

def tokenize(text: str) -> List[str]:
    if not text:
        return []
    text = text.strip()
    text = _strip_accents(text)
    text = text.lower()
    translator = str.maketrans({p: ' ' for p in string.punctuation})
    text = text.translate(translator)
    tokens = [t for t in text.split() if t]
    tokens = [CORRECTIONS.get(t, t) for t in tokens]
    return tokens

def remove_stop_words(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t and t not in STOP_WORDS]

def detect_intent(tokens: List[str], threshold: float = 0.2) -> Tuple[str, float]:
    if not tokens:
        return 'UNKNOWN', 0.0
    counts = {intent: 0 for intent in INTENTS}
    for t in tokens:
        for intent, kws in INTENTS.items():
            if t in kws:
                counts[intent] += 1
    best_intent = max(counts, key=counts.get)
    score = counts[best_intent] / len(tokens)
    if counts[best_intent] == 0 or score < threshold:
        return 'UNKNOWN', 0.0
    return best_intent, round(score, 2)

def extract_entities(text: str) -> Dict[str, str]:
    entities: Dict[str, str] = {}
    if not text:
        return entities
    text_norm = text
    date_re = re.search(r"\b(demain|aujourd'hui|aujourd hui|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b", text_norm, re.I)
    if date_re:
        entities['date'] = date_re.group(1).lower().replace("'", '')
    heure_re = re.search(r"\b(\d{1,2}h\d{0,2}|\d{1,2}:\d{2})\b", text_norm)
    if heure_re:
        h = heure_re.group(1).replace(':', 'h')
        entities['heure'] = h
    email_re = re.search(r"\b\S+@\S+\.\S+\b", text_norm)
    if email_re:
        entities['email'] = email_re.group(0)
    name_re = re.search(r"\b([A-ZÉÈÊÀÙÂÄÔÛÇ][a-zéèêëàâäôûùç-]+\s+[A-ZÉÈÊÀÙÂÄÔÛÇ][a-zéèêëàâäôûùç-]+)\b", text_norm)
    if name_re:
        entities['nom'] = name_re.group(1)
    salle_re = re.search(r"\bsalle\s*([A-Ca-c])\b", text_norm, re.I)
    if salle_re:
        entities['salle'] = salle_re.group(1).upper()
    return entities

def _valid_hour(heure: str) -> bool:
    m = re.match(r"^(\d{1,2})h(\d{0,2})$", heure)
    if not m:
        return False
    h = int(m.group(1))
    mnt = int(m.group(2)) if m.group(2) else 0
    return 0 <= h <= 23 and 0 <= mnt <= 59

def generate_response(intent: str, entities: Dict[str, str], context: Optional[Dict] = None) -> str:
    ctx = context or {}
    if intent not in RESPONSES:
        intent = 'UNKNOWN'
    if intent == 'RESERVATION':
        date = entities.get('date') or ctx.get('date')
        heure = entities.get('heure') or ctx.get('heure')
        salle = entities.get('salle') or ctx.get('salle')
        if date and heure and salle:
            return RESPONSES['RESERVATION']['complete'].format(date=date, heure=heure, salle=salle)
        if date and heure:
            return RESPONSES['RESERVATION']['partial'].format(date=date, heure=heure)
        return RESPONSES['RESERVATION']['missing']
    if intent == 'HORAIRES':
        return RESPONSES['HORAIRES']['default']
    if intent == 'ANNULATION':
        return RESPONSES['ANNULATION']['default']
    return RESPONSES['UNKNOWN']['default']

if __name__ == '__main__':
    sample = "Je veux reserver pour demain à 14h30 pour Marc Dupont (marc@email.com)"
    print('Tokens:', tokenize(sample))
    print('Filtrés:', remove_stop_words(tokenize(sample)))
    print('Intent:', detect_intent(remove_stop_words(tokenize(sample))))
    print('Entities:', extract_entities(sample))
