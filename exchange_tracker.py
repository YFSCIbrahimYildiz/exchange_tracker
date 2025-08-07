import requests
import csv
from datetime import datetime

API_URL = "https://open.er-api.com/v6/latest"  

def fetch_rate(base: str, symbols: list[str], timeout=5) -> dict:
    base = base.upper()
    url = f"{API_URL}/{base}"  
    headers = {"User-Agent": "ExchangeTracker/1.0"}

    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()

    if data.get("result") != "success":
        raise ValueError(f"API hata: {data.get('error-type') or data.get('result')}")


    rates_all = data.get("rates", {})
    picked = {s: rates_all[s] for s in (x.upper() for x in symbols) if s in rates_all}
    if not picked:
        raise ValueError("İstenen semboller bulunamadı / API dönmedi.")

    return {
        "date": data.get("time_last_update_utc"),   
        "base": data.get("base_code", base),       
        "rates": picked,                            
    }

def save_csv(filename: str, base: str, rates: dict, date_str: str):
    is_new = False
    try:
        with open(filename, "r", encoding="utf-8"):
            pass
    except FileNotFoundError:
        is_new = True

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["timestamp", "base", "symbol", "rate", "asof_date"])
        ts = datetime.now().isoformat(timespec="seconds")
        for sym, rate in rates.items():
            writer.writerow([ts, base, sym, rate, date_str])

def main():
    print("=== Döviz Kuru Takip Programı ===")
    base = input("Kaynak para birimi (örn: USD, EUR, TRY): ").strip().upper() or "USD"
    target_raw = input("Hedef para(lar) virgüllü (örn: TRY,EUR,GBP): ").strip()
    symbols = [s.strip().upper() for s in target_raw.split(",") if s.strip()] or ["TRY"]

    try:
        result = fetch_rate(base, symbols)
    except Exception as e:
        print(f"Hata: {e}")
        return

    print(f"\nTarih: {result['date']} | Baz: {result['base']}")
    for sym, rate in result["rates"].items():
        print(f"  1 {result['base']} = {rate:.4f} {sym}")

    save = input("\nCSV'ye kaydedilsin mi? (e/h): ").strip().lower()
    if save == "e":
        filename = "kur_kayitlari.csv"
        save_csv(filename, result["base"], result["rates"], result["date"])
        print(f"💾 Kaydedildi: {filename}")

if __name__ == "__main__":
    main()
