import json

from app.db.schemas import UserCreate

d = {"username":"alice", "is_admin":False, "password": "sefr"}
d1 = {"username":"alice", "is_admin":False, "password": "sefr"}

md = UserCreate.model_validate(d)
md1 = UserCreate.model_validate(d1)
l = []

# Serialize the list of models to JSON
json_data = json.dumps([model.model_dump() for model in l])

# Encode the JSON string to bytes
bytes_data = json_data.encode('utf-8')
print(bytes_data)