import time
import random
import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flask import Flask

app = Flask(__name__)

NTFY_TOPIC = "alert_ecrl_1688"  # TUKAR KEPADA TOPIK UNIK ANDA
URL_ECRL = "https://ecrl.com.my"
KATA_KUNCI = ["beli tiket", "buy ticket", "booking", "tempahan", "ticketing", "e-ticket", "ticket"]

@app.route("/")
def status():
    return "Pemantau ECRL sedang aktif 24/7!"

def pemantau_ecrl():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cache-Control": "no-cache"
    })
    sudah_jumpa = False

    while True:
        try:
            url_semak = f"{URL_ECRL}?t={int(time.time() * 1000)}"
            response = session.get(url_semak, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                link_ditemui = None

                for a in soup.find_all("a", href=True):
                    teks_link = a.get_text(" ", strip=True).lower()
                    href = a["href"].strip()
                    if any(k in teks_link or k in href.lower() for k in KATA_KUNCI):
                        if "news" not in href.lower() and "article" not in href.lower():
                            link_ditemui = urljoin(URL_ECRL, href)
                            break

                if link_ditemui and not sudah_jumpa:
                    for _ in range(3):
                        requests.post(
                            f"https://ntfy.sh{NTFY_TOPIC}",
                            data=f"TIKET ECRL DIBUKA! Klik: {link_ditemui}".encode("utf-8"),
                            headers={
                                "Title": "🚨 BELI TIKET ECRL SEKARANG!",
                                "Priority": "max",
                                "Tags": "rotating_light,train",
                                "Click": link_ditemui,
                                "Actions": f"view, BELI TIKET TERUS, {link_ditemui}"
                            }
                        )
                        time.sleep(5)
                    sudah_jumpa = True
                    break
        except Exception:
            pass
        time.sleep(random.uniform(1.5, 2.5))

threading.Thread(target=pemantau_ecrl, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
