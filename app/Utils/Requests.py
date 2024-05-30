import requests

backend_url = "https://backend.getdelmar.com/api/v1/update-scraping-status"

def send_buildertrend(total: int, current: int):
    data = {"buildertrend_total": total, "buildertrend_current": current}
    print('====Builder====', data)
    try:
        response = requests.post(backend_url, json=data)
        response.raise_for_status()  # This will raise an exception for HTTP error responses
    except requests.RequestException as e:
        print("requests error: ", e)

def send_xactanalysis(total: int, current: int):
    data = {"xactanalysis_total": total, "xactanalysis_current": current}
    try:
        response = requests.post(backend_url, json=data)
        response.raise_for_status()  # This will raise an exception for HTTP error responses
    except requests.RequestException as e:
        print("requests error: ", e)