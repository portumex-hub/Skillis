import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import prospect_pipeline as pp  # noqa: E402


class PrefilterTest(unittest.TestCase):
    def test_keeps_only_operational_places_in_range(self):
        places = [
            {"place_id": "ok", "rating": 4.3, "reviews": 500, "business_status": "OPERATIONAL"},
            {"place_id": "too_good", "rating": 4.8, "reviews": 500},
            {"place_id": "too_small", "rating": 4.0, "reviews": 10},
            {"place_id": "closed", "rating": 4.1, "reviews": 100, "business_status": "CLOSED_TEMPORARILY"},
        ]
        kept = pp.prefilter(places, min_reviews=30, max_reviews=3000, max_rating=4.6)
        self.assertEqual([p["place_id"] for p in kept], ["ok"])


class SystemPromptTest(unittest.TestCase):
    def test_includes_icp_and_offer(self):
        system = pp.build_system()
        self.assertIn("Perfil de cliente ideal", system)
        self.assertIn("Diagnóstico", system)

    def test_schema_forbids_extra_fields(self):
        schema = pp.Assessment.model_json_schema()
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["$defs"]["Draft"]["additionalProperties"])


class ExportApprovedTest(unittest.TestCase):
    def test_exports_only_approved_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "q.csv"
            with queue.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["aprobado", "canal", "negocio", "asunto", "mensaje", "email", "telefono", "instagram", "web"])
                writer.writerow(["si", "email", "A", "Hola", "Msg", "a@a.mx", "", "", ""])
                writer.writerow(["", "email", "B", "x", "y", "b@b.mx", "", "", ""])
                writer.writerow(["Sí", "whatsapp", "C", "", "Msg2", "", "81 1", "", ""])
            subprocess.run([sys.executable, str(ROOT / "scripts" / "export_approved.py"), str(queue)], check=True, capture_output=True)
            with (Path(tmp) / "q_email.csv").open(encoding="utf-8") as f:
                emails = list(csv.DictReader(f))
            with (Path(tmp) / "q_manual.csv").open(encoding="utf-8") as f:
                manual = list(csv.DictReader(f))
        self.assertEqual([r["companyName"] for r in emails], ["A"])
        self.assertEqual([r["negocio"] for r in manual], ["C"])


if __name__ == "__main__":
    unittest.main()
