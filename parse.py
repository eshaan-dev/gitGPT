import requests

parent_id = None 

while True:
    content = input("You: ")
    if content.lower() == "exit":
        break

    response = requests.post(
        "http://localhost:8000/chat",
        json={"content": content, "parent_id": parent_id},
    )
    response.raise_for_status()
    data = response.json()

    parent_id = data["node_id"]  # Automatically used in the next request.
    print("Assistant:", data["reply"])