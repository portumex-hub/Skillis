"""Export the rows you approved in an approval-queue CSV, split by channel.

Only rows whose `aprobado` column is si/sí/yes/x are exported. Nothing is sent.

    python scripts/export_approved.py output/cola_aprobacion_20261008.csv

Writes next to the input:
  *_email.csv   -> import into Instantly / Lemlist (columns: email, companyName, subject, body)
  *_manual.csv  -> WhatsApp / Instagram / LinkedIn messages to send by hand
"""
import csv
import sys
from pathlib import Path

APPROVED = {"si", "sí", "yes", "x", "ok"}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
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


if __name__ == "__main__":
    main()
