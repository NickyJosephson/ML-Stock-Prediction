import requests

username = 'scraper_cjOmT'
password = '+jVj7CFX7QbXefM'
proxy = 'ddc.oxylabs.io:8005'

proxies = {
    "https": f"https://user-{username}:{password}@{proxy}"
}

try:
    response = requests.get("https://ip.oxylabs.io/location", proxies=proxies, timeout=10)
    print(response.status_code)
    print(response.content)
except requests.exceptions.ProxyError as e:
    print(f"Proxy error: {e}")
except requests.exceptions.ConnectTimeout as e:
    print(f"Connection timeout: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")