"""Export the rows you approved in an approval-queue CSV, split by channel.

Only rows whose `aprobado` column is si/sí/yes/x/ok are exported.

    python scripts/export_approved.py output/cola_aprobacion_20261008.csv
    python scripts/export_approved.py output/cola_aprobacion_20261008.csv --lemlist-campaign cam_XXXX

Writes next to the input:
  *_email.csv   -> import into Instantly / Lemlist (columns: email, companyName, subject, body)
  *_manual.csv  -> WhatsApp / Instagram / LinkedIn messages to send by hand

With --lemlist-campaign (and LEMLIST_API_KEY set), the approved email rows are also
added as leads to that Lemlist campaign, which sends them on its own schedule. The
lead carries `asunto` and `mensaje` as custom variables: use {{asunto}} and
{{mensaje}} in the campaign's email step.
"""
import argparse
import csv
import os
import sys
from pathlib import Path

APPROVED = {"si", "sí", "yes", "x", "ok"}


def push_to_lemlist(rows, campaign_id, api_key):
    from lemlist import Campaigns, Client

    campaigns = Campaigns(Client(api_key=api_key))
    pushed = 0
    for r in rows:
        lead = {
            "email": r["email"],
            "companyName": r["negocio"],
            "asunto": r["asunto"],
            "mensaje": r["mensaje"],
        }
        try:
            campaigns.add_a_lead(campaign_id, lead)
            pushed += 1
        except Exception as e:  # keep going: one bad address must not block the batch
            print(f"lemlist: {r['email']} not added: {e}", file=sys.stderr)
    return pushed


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("queue", type=Path)
    parser.add_argument("--lemlist-campaign", help="Lemlist campaign id to add approved email leads to")
    args = parser.parse_args()

    src = args.queue
    with src.open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("aprobado", "").strip().lower() in APPROVED]

    email_rows = [r for r in rows if r["canal"] == "email" and r.get("email")]
    manual_rows = [r for r in rows if r not in email_rows]

    email_out = src.with_name(src.stem + "_email.csv")
    with email_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "companyName", "subject", "body"])
        for r in email_rows:
            writer.writerow([r["email"], r["negocio"], r["asunto"], r["mensaje"]])

    manual_out = src.with_name(src.stem + "_manual.csv")
    with manual_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["canal", "negocio", "telefono", "instagram", "web", "mensaje"])
        for r in manual_rows:
            writer.writerow([r["canal"], r["negocio"], r["telefono"], r["instagram"], r["web"], r["mensaje"]])

    print(f"{len(rows)} approved: {len(email_rows)} email -> {email_out}, {len(manual_rows)} manual -> {manual_out}")

    if args.lemlist_campaign:
        api_key = os.environ.get("LEMLIST_API_KEY")
        if not api_key:
            sys.exit("LEMLIST_API_KEY is not set (see .env.example)")
        pushed = push_to_lemlist(email_rows, args.lemlist_campaign, api_key)
        print(f"{pushed}/{len(email_rows)} approved email leads added to Lemlist campaign {args.lemlist_campaign}")


if __name__ == "__main__":
    main()
