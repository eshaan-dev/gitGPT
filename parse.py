import requests
parent_id = None 

while True:
    content = input("You: ")
    if content.lower() == "exit":
        break

    elif content.lower()[:9] == "/rollback":
        parent_id = content.lower()[10:]
        print("Rollback Successful!")

    
    elif content.lower()[:8] == "/branch":
        response = requests.post(
                    "http://localhost:8000/branch",
                    json={"node_id": parent_id},
                )
        response.raise_for_status()
        print("Branch successful!")
    else:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"content": content, "parent_id": parent_id},
        )
        response.raise_for_status()
        data = response.json()

        parent_id = data["node_id"]
        print("Assistant:", data["reply"], "id:", parent_id)