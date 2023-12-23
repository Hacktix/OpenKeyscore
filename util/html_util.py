from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

def get_bs_for_url(url: str, headers: dict = {}) -> BeautifulSoup:
    if "Accept" not in headers: headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    if "Accept-Encoding" not in headers: headers["Accept-Encoding"] = "gzip, deflate, sdch"
    if "Accept-Language" not in headers: headers["Accept-Language"] = "en-US,en;q=0.9"
    if "Cache-Control" not in headers: headers["Cache-Control"] = "no-cache"
    if "Upgrade-Insecure-Requests" not in headers: headers["Upgrade-Insecure-Requests"] = "1"
    if "User-Agent" not in headers: headers["User-Agent"] = UserAgent().random

    res = requests.get(url, headers=headers, allow_redirects=True)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")