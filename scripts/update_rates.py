"""Тягне курси валют з відкритого API НБУ і дописує їх у CSV."""

import csv
import json
import os
import urllib.request

API_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
CURRENCIES = ("USD", "EUR", "PLN")   # які валюти зберігаємо
DATA_FILE = "data/rates.csv"


def fetch_rates():
    """Повертає {код валюти: (курс, дата)} з API НБУ."""
    with urllib.request.urlopen(API_URL, timeout=30) as response:
        payload = json.load(response)

    return {
        item["cc"]: (item["rate"], item["exchangedate"])
        for item in payload
        if item["cc"] in CURRENCIES
    }


def existing_dates():
    """Дати, які вже є у файлі — щоб не дублювати записи."""
    if not os.path.exists(DATA_FILE):
        return set()

    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        return {row["date"] for row in csv.DictReader(f)}


def main():
    rates = fetch_rates()
    if not rates:
        print("API не повернуло потрібних валют — виходимо.")
        return

    # Дата у форматі НБУ (DD.MM.YYYY) — беремо з будь-якого запису
    date_str = next(iter(rates.values()))[1]

    if date_str in existing_dates():
        print(f"Дані за {date_str} вже є. Нового коміту не буде.")
        return

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    file_is_new = not os.path.exists(DATA_FILE)

    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if file_is_new:
            writer.writerow(["date", *CURRENCIES])   # заголовок
        writer.writerow([date_str, *(rates[c][0] for c in CURRENCIES)])

    print(f"Додано рядок за {date_str}: {rates}")


if __name__ == "__main__":
    main()
