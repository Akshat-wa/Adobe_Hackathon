import json
from datetime import datetime

def load_input_spec(json_path):
    with open(json_path) as f:
        data = json.load(f)
    persona = data["persona"]["role"]
    job = data["job_to_be_done"]["task"]
    doc_list = [d["filename"] for d in data["documents"]]
    return persona, job, doc_list

def get_timestamp():
    return datetime.now().isoformat()
