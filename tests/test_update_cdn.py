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

    def test_official_overlay_replaces_matching_cdn_entry(self):
        exams = [{
            "courseCode": "CSE110",
            "sectionName": "01",
            "midExamDate": "2026-11-07",
            "midExamTime": "08:30:00",
            "midExamRoom": None,
            "midExamSource": "cdn",
        }, {
            "courseCode": "CSE110",
            "sectionName": "02",
            "midExamDate": "2026-11-07",
            "midExamTime": "08:30:00",
            "midExamRoom": None,
            "midExamSource": "cdn",
        }]
        official = update_cdn.official_exam_index({"exams": [{
            "Course": "CSE110",
            "Section": "1",
            "Mid Date": "2026-11-09",
            "Start Time": "10:00",
            "End Time": "11:30",
            "Room.": "09A-01C",
        }]}, "midterm")

        applied = update_cdn.apply_official_overlay(exams, official, "midterm")

        self.assertEqual(applied, 1)
        self.assertEqual(exams[0]["midExamDate"], "2026-11-09")
        self.assertEqual(exams[0]["midExamTime"], "10:00-11:30")
        self.assertEqual(exams[0]["midExamRoom"], "09A-01C")
        self.assertEqual(exams[0]["midExamSource"], "pdf")
        self.assertEqual(exams[1]["midExamSource"], "cdn")

    def test_exam_source_metadata_reports_mixed_coverage(self):
        metadata = update_cdn.generate_exam_source_metadata(
            "Fall2026",
            {"midterm": (None, {"updatedAt": "2026-10-28", "dataUrl": "https://example.test"})},
            {"midterm": 1},
            {"midterm": 2},
        )

        self.assertEqual(metadata["sources"]["midterm"]["source"], "mixed")
        self.assertFalse(metadata["sources"]["midterm"]["confirmed"])
        self.assertEqual(metadata["sources"]["midterm"]["matchedEntries"], 1)


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
