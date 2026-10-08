"""Fetch Google Maps reviews for one or more places with Outscraper.

Usage:
    OUTSCRAPER_API_KEY=... python scripts/google_reviews.py "Restaurante X, Madrid" --limit 50

Outscraper bills per record returned, so keep --limit low while testing.
"""
import argparse
import csv
import os
import sys
from pathlib import Path

from outscraper import OutscraperClient


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("queries", nargs="+", help="Place name + city, Google Maps URL or place_id")
    parser.add_argument("--limit", type=int, default=20, help="Max reviews per place (default 20)")
    parser.add_argument("--sort", default="newest", choices=["most_relevant", "newest", "highest_rating", "lowest_rating"])
    parser.add_argument("--language", default="es")
    parser.add_argument("--out", default="output/reviews.csv")
    args = parser.parse_args()

    api_key = os.environ.get("OUTSCRAPER_API_KEY")
    if not api_key:
        sys.exit("OUTSCRAPER_API_KEY is not set (see .env.example)")

    client = OutscraperClient(api_key=api_key)
    places = client.google_maps_reviews(
        args.queries, reviews_limit=args.limit, sort=args.sort, language=args.language
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["place", "place_rating", "place_reviews", "author_title", "review_rating", "review_datetime_utc", "review_text"]
    rows = 0
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for place in places:
            for review in place.get("reviews_data") or []:
                writer.writerow({
                    "place": place.get("name"),
                    "place_rating": place.get("rating"),
                    "place_reviews": place.get("reviews"),
                    "author_title": review.get("author_title"),
                    "review_rating": review.get("review_rating"),
                    "review_datetime_utc": review.get("review_datetime_utc"),
                    "review_text": review.get("review_text"),
                })
                rows += 1
    print(f"{rows} reviews from {len(places)} place(s) -> {out}")


if __name__ == "__main__":
    main()
