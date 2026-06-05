"""Internet bilan ishlash: qidirish va sayt ochish."""

import urllib.parse
import webbrowser


def web_search(query: str) -> str:
    query = (query or "").strip()
    if not query:
        return "Nimani qidirishni aytmadingiz."
    url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    webbrowser.open(url)
    return f"'{query}' bo'yicha qidiryapman."


def open_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return "Qaysi saytni ochishni aytmadingiz."
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"{url} ochildi."
