import requests


def send_get_request(url, params=None, timeout=600):
    response = requests.get(url, params=params, timeout=timeout)
    if response.status_code != 200:
        response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return response.text


def send_post_request(url, data=None, timeout=600):
    response = requests.post(url, json=data, timeout=timeout)
    if response.status_code != 200:
        response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return response.text


def send_put_request(url, data=None, timeout=600):
    response = requests.put(url, json=data, timeout=timeout)
    if response.status_code != 200:
        response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return response.text


def send_delete_request(url, timeout=600):
    response = requests.delete(url, timeout=timeout)
    if response.status_code != 200:
        response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return response.text
