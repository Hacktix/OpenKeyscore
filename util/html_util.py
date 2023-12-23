from bs4 import BeautifulSoup
import requests

def get_bs_for_url(url: str, headers = None) -> BeautifulSoup:
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")