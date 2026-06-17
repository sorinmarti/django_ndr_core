import json

import requests

url = "https://api.nodegoat.dasch.swiss/?id=ngSZ0K68dTZE6TfW1SL4fhZFpUMPiEZLfTW"
url = "https://api.nodegoat.dasch.swiss/?search=Adolf" # --> []
url = "https://api.nodegoat.dasch.swiss/data/type/11679/?search=adolf&limit=10&offset=0"  # --> invalid request
url = "https://api.nodegoat.dasch.swiss/data/type/11679/object?search=adolf&limit=10&offset=0&order=element:ASC"  # Success
url = 'https://api.nodegoat.dasch.swiss/data/type/11679/object?filter={"form": {"filter_1": {"type_id": 11679, "object_definitions": {"34189": [{"equality": "=", "value": "Elise"}], "34531": [12018279]}}}}'  #

url = "https://api.nodegoat.dasch.swiss/model/type/11679/"
#url = ' https://api.nodegoat.dasch.swiss/data/type/11679/object?filter={"form": {"filter_1": {"type_id": "11679", "object_definitions": {"34189": [{"equality": "*", "value": "otto"}]}}}}'

token = "xxx"  # Replace with your actual bearer token

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)

try:
    data = response.json()
except Exception:
    print("Response was not valid JSON")
    print(response.text)
    exit()

if "error" in data:
    print("Error:", data["error"])
    print("Description:", data.get("error_description", ""))
    for msg in data.get("msg", []):
        print(f"{msg['type'].upper()}: {msg['label']} — {msg['description']}")
else:
    print(f"Success items):")
    with open("nodegoat_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(data)