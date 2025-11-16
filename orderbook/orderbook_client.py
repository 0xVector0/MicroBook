import requests

class orderbook_client:
    def __init__(self, ip:str, port:int):
        self.ip = ip
        self.port = port

    def new_limit_order(self, amount: float, price: float, type: str):
        response = requests.post(f"http://{self.ip}:{self.port}/limit-order", json={
            "amount": amount,
            "price": price,
            "type": type
        })

        return response.json()

    def new_order(self, amount: float, type: str):
        response = requests.post(f"http://{self.ip}:{self.port}/order", json={
            "amount": amount,
            "type": type
        })

        return response.json()

    def get_order_book(self):
        try:
            response = requests.get(f"http://{self.ip}:{self.port}/orderbook")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting orderbook: {response.status_code}")
                return {"ask": [], "bid": []}
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return {"ask": [], "bid": []}

    def get_logs(self):
        response = requests.get(f"http://{self.ip}:{self.port}/logs")

        return response.json()