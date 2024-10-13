import requests
import websocket
import random
import time
import threading

API_URL = "http://localhost:8080"
WEBSOCKET_URL = "ws://localhost:8080/chat/"
CHAT_NAME = "test_room"


def api_load_test():
	while True:
		cart_id = requests.post(f"{API_URL}/cart").json()["id"]
		item_id = requests.post(
			f"{API_URL}/item", json={"name": "Test item", "price": random.uniform(10, 100)}
		).json()["id"]
		requests.post(f"{API_URL}/cart/{cart_id}/add/{item_id}")
		requests.get(f"{API_URL}/cart/{cart_id}")
		requests.get(f"{API_URL}/cart", params={"min_price": 10, "max_price": 100})
		time.sleep(0.1)


def websocket_load_test():
	ws = websocket.WebSocket()
	ws.connect(f"{WEBSOCKET_URL}{CHAT_NAME}")
	for _ in range(100):
		message = f"Test message {random.randint(1, 100)}"
		ws.send(message)
		print(ws.recv())
		time.sleep(0.1)
	ws.close()


api_thread = threading.Thread(target=api_load_test)
websocket_thread = threading.Thread(target=websocket_load_test)

api_thread.start()
websocket_thread.start()

api_thread.join()
websocket_thread.join()
