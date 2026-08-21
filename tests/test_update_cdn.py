import json
import tempfile
import unittest
from pathlib import Path

import update_cdn


class UpdateCdnCompatibilityTests(unittest.TestCase):
    def test_extract_sections_accepts_all_supported_payload_shapes(self):
        sections = [{"sectionId": 1}]

        self.assertEqual(update_cdn.extract_sections(sections), sections)
        self.assertEqual(update_cdn.extract_sections({"data": sections}), sections)
        self.assertEqual(update_cdn.extract_sections({"sections": sections}), sections)

    def test_extract_sections_rejects_unknown_payload_shape(self):
        with self.assertRaises(ValueError):
            update_cdn.extract_sections({"metadata": {}})

    def test_status_update_preserves_manual_exam_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            status_path = Path(tmp) / "exam_status.json"
            status_path.write_text(json.dumps({
                "schemaVersion": 1,
                "semesters": {
                    "summer2026": {
                        "midterm": {
                            "confirmed": True,
                            "dataUrl": "https://example.test/exam_data.json"
                        }
                    }
                }
            }))

            status = update_cdn.build_status_document(
                {"midExamStartDate": "2026-07-24", "finalExamEndDate": "2026-12-21"},
                str(status_path),
            )

            self.assertTrue(status["semesters"]["summer2026"]["midterm"]["confirmed"])
            self.assertEqual(status["currentSemesterKey"], "summer2026")
            self.assertEqual(status["liveDataUrl"], "https://usis-cdn.eniamza.com/connect.json")

    def test_status_update_rejects_invalid_confirmed_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            status_path = Path(tmp) / "exam_status.json"
            status_path.write_text(json.dumps({
                "schemaVersion": 1,
                "semesters": {
                    "summer2026": {"midterm": {"confirmed": True}}
                }
            }))

            with self.assertRaises(ValueError):
                update_cdn.build_status_document(
                    {"midExamStartDate": "2026-07-24"},
                    str(status_path),
                )

    def test_status_update_rejects_malformed_json_instead_of_erasing_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            status_path = Path(tmp) / "exam_status.json"
            status_path.write_text("{not-json")

            with self.assertRaises(ValueError):
                update_cdn.build_status_document(
                    {"midExamStartDate": "2026-07-24"},
                    str(status_path),
                )


if __name__ == "__main__":
    unittest.main()
