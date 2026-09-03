"""Dump active Polymarket tennis events to a CSV file."""

import csv
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://gamma-api.polymarket.com/events"
PAGE_SIZE = 100
OUT = "tennis_events.csv"

COLUMNS = [
    "event_id",
    "event_title",
    "event_slug",
    "event_start_date",
    "event_end_date",
    "event_volume",
    "event_liquidity",
    "market_id",
    "question",
    "outcomes",
    "outcome_prices",
    "market_volume",
    "sports_market_type",
    "updated_at",
]


def fetch_events():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    events = []
    offset = 0
    while True:
        params = {
            "tag_slug": "tennis",
            "active": "true",
            "closed": "false",
            "end_date_min": now,
            "limit": PAGE_SIZE,
            "offset": offset,
        }
        url = API + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "polymarket-tennis-export/1.0"})
        with urllib.request.urlopen(req) as resp:
            page = json.load(resp)
        events.extend(page)
        if len(page) < PAGE_SIZE:
            return events
        offset += PAGE_SIZE


def rows_from_event(event):
    rows = []
    for market in event["markets"]:
        if market["closed"]:
            continue
        rows.append({
            "event_id": event["id"],
            "event_title": event["title"],
            "event_slug": event["slug"],
            "event_start_date": event.get("startDate"),
            "event_end_date": event.get("endDate"),
            "event_volume": event.get("volume"),
            "event_liquidity": event.get("liquidity"),
            "market_id": market["id"],
            "question": market["question"],
            "outcomes": "|".join(json.loads(market.get("outcomes", "[]"))),
            "outcome_prices": "|".join(json.loads(market.get("outcomePrices", "[]"))),
            "market_volume": market.get("volume"),
            "sports_market_type": market.get("sportsMarketType"),
            "updated_at": market.get("updatedAt"),
        })
    return rows


def main():
    events = fetch_events()
    rows = []
    for event in events:
        rows.extend(rows_from_event(event))

    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(events)} events, {len(rows)} open markets -> {OUT}")


if __name__ == "__main__":
    main()
