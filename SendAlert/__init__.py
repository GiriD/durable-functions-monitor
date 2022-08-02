import json, os

def main(messageContent: dict, message) -> str:
    payload = {
        "body": messageContent['body'],
        "to": messageContent['phone_number'],
        "from": os.environ["TwilioFromNumber"]
    }

    message.set(json.dumps(payload))
    return "Alert sent!"
