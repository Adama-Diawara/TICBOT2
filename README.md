# ChatBot de Réservation (simple)

Petit projet pédagogique implémentant un chatbot de réservation sans ML, étape par étape.

Fichiers principaux:
- `bot.py` : interface CLI
- `text_processor.py` : tokenization, stop-words, intent detection, extraction, réponses
- `data_manager.py` : stockage JSON simple (`reservations.json`)

Usage rapide:

```bash
python chatbot/bot.py
```

Commandes utiles:
- `/help` - affiche l'aide
- `/list` - liste les réservations
- `/debug` - bascule le mode debug (affiche étapes intermédiaires)
- `/reset` - réinitialise le contexte
- `/quit` - quitter
 - `/cancel <id>` - annule la réservation identifiée par `<id>` (voir `/list` pour les ids)

Notes:
- Les réservations sont sauvegardées dans `chatbot/reservations.json`.
- Le traitement est purement algorithmique (regex + keywords).
