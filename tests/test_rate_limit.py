import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost:8001/api/data"

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyb2hpdCIsImV4cCI6MTc4NjY4NzY4OX0.r7XqXeO4QWg6S6T4fie46ho_WJvDjpd_-vSBJ1UNOqk"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}


def send_request(i):
    response = requests.get(URL, headers=headers)

    return i, response.status_code, response.text


with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(send_request, range(20)))


for result in results:
    print(result)