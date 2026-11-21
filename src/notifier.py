import requests


class TelegramNotifier:
    def __init__(self, token: str = "", chat_id: str = ""):
        self.token = token
        self.chat_id = chat_id

    def send(self, message: str):
        if not self.token or not self.chat_id:
            print(message)
            return

        response = requests.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            json={"chat_id": self.chat_id, "text": message},
            timeout=15,
        )
        response.raise_for_status()
