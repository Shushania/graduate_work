import requests

def handler(event, context):
    text = 'Hello! I\'ll repeat anything you say to me.'
    if 'request' in event and \
            'original_utterance' in event['request'] \
            and len(event['request']['original_utterance']) > 0:
        text = event['request']['original_utterance']
        intents = event.get("request", {}).get("nlu", {}).get("intents", {})
        if intents.get("exit"):
            text = "Exit"
        elif intents.get("who_is_the_author"):
            film = intents.get("who_is_the_author", {}).get("slots", {}).get("piece", {}).get("value", "")
            response = requests.get(f"http://51.250.96.235:8000/api/v1/films/search/?query={film}")
            if response.status_code == 200:
                data = response.json()
                directors = ", ".join(data.get("values")[0].get("director"))
                if directors != "":
                    text = directors
                else:
                    text = "Фильм без режиссера..."
            else:
                text = "Фильм не найден"
    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': text,
            'end_session': 'false'
        },
    }
