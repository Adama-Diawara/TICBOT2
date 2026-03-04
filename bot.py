from chatbot.text_processor import tokenize, remove_stop_words, detect_intent, extract_entities, generate_response
from chatbot.data_manager import load_data, check_availability, add_reservation, list_reservations, cancel_reservation
from typing import Dict

def _print_welcome() -> None:
    print('''\
╔═══════════════════════════════════════╗
║   ChatBot de Réservation v1.0         ║
╚═══════════════════════════════════════╝

Commandes disponibles:
 /help  - Afficher l'aide
 /list  - Liste des réservations
 /debug - Activer/désactiver le mode debug
 /reset - Réinitialiser le contexte
 /cancel <id> - Annuler une réservation
 /quit  - Quitter
''')

def main() -> None:
    _print_welcome()
    data = load_data()
    context: Dict = {}
    debug = False
    while True:
        try:
            text = input('\n> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nAu revoir !')
            break
        if not text:
            print('Bot: Message vide. Comment puis-je vous aider ?')
            continue
        if text == '/quit':
            print('Au revoir !')
            break
        if text == '/help':
            print('Commandes: /help /quit /reset /debug /list /cancel <id>')
            continue
        if text == '/debug':
            debug = not debug
            print('Mode debug {}'.format('activé' if debug else 'désactivé'))
            continue
        if text == '/reset':
            context = {}
            print('Contexte réinitialisé')
            continue
        if text.startswith('/cancel'):
            parts = text.split()
            if len(parts) == 2 and parts[1].isdigit():
                rid = int(parts[1])
                ok = cancel_reservation(data, rid)
                print('Annulation {}'.format('réussie' if ok else 'échouée'))
            else:
                print('Usage: /cancel <id>')
            continue
        if text == '/list':
            items = list_reservations(data)
            if not items:
                print('Aucune réservation enregistrée.')
            else:
                print('Réservations enregistrées:')
                for r in items:
                    print(' {}. Salle {} - {} - {}'.format(r.get('id'), r.get('salle'), r.get('date'), r.get('heure')))
            continue
        tokens = tokenize(text)
        filtered = remove_stop_words(tokens)
        intent, score = detect_intent(filtered)
        entities = extract_entities(text)
        if debug:
            print('[DEBUG] Étape 1 Tokens:', tokens)
            print('[DEBUG] Étape 2 Filtrés:', filtered)
            print('[DEBUG] Étape 3 Intent: {} ({})'.format(intent, score))
            print('[DEBUG] Étape 4 Entities:', entities)
        if intent == 'UNKNOWN':
            print('Bot:', generate_response(intent, entities))
            continue
        if 'intent' not in context:
            context['intent'] = intent
        context.update(entities)
        if context.get('intent') == 'RESERVATION' and context.get('date') and context.get('heure') and context.get('salle'):
            salle = context.get('salle')
            date = context.get('date')
            heure = context.get('heure')
            if check_availability(data, salle, date, heure):
                res = add_reservation(data, salle, date, heure, nom=context.get('nom'), email=context.get('email'))
                print('Bot: Réservation confirmée et enregistrée : Salle {}, {} à {}'.format(res.get('salle'), res.get('date'), res.get('heure')))
                context = {}
                continue
            else:
                print('Bot: Désolé, la salle {} est déjà réservée {} à {}'.format(salle, date, heure))
        resp = generate_response(intent, entities, context)
        print('Bot:', resp)

if __name__ == '__main__':
    main()
