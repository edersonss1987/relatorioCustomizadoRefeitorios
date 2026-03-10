import requests

BASE_URL = "https://main.idsecure.com.br:5000"

def login(email, password, tenant_id=None):

    payload = {
        "email": email,
        "password": password,
    }

    if tenant_id:
        payload["tenantId"] = tenant_id

    response = requests.post(
        f"{BASE_URL}/api/v1/operators/login",
        json=payload
    )

    if response.status_code != 200:
        return None

    return response.json()