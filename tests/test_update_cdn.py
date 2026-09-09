import json
import tempfile
import unittest
import unittest.mock
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


def _official_payload(course="CSE340", section="3", date="2026-09-18",
                      start="11:00", end="13:00", room="07B-17C"):
    return {"exams": [{
        "Course": course, "Section": section, "Final Date": date,
        "Start Time": start, "End Time": end, "Room.": room,
    }]}


def _status_document(semesters):
    return {"schemaVersion": 1, "semesters": semesters}


class ActiveConfirmedExamTests(unittest.TestCase):
    def _record(self, confirmed=True, data_url="https://example.test/exam_data.json", **extra):
        record = {"confirmed": confirmed, "dataUrl": data_url, "updatedAt": "2026-09-09T09:35:35Z"}
        record.update(extra)
        return record

    def _write_status(self, tmp, semesters):
        path = Path(tmp) / "exam_status.json"
        path.write_text(json.dumps(_status_document(semesters)))
        return str(path)

    def test_picks_active_record_within_grace(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_status(tmp, {
                "summer2026": {"final": self._record()},
            })
            result = update_cdn.find_active_confirmed_exam(
                now=__import__("datetime").date(2026, 9, 9),
                status_path=path,
                fetch_payload=lambda url: _official_payload(),
            )
            self.assertIsNotNone(result)
            self.assertEqual(result["semester_key"], "summer2026")
            self.assertEqual(result["exam_type"], "final")
            self.assertEqual(result["window"], ("2026-09-18", "2026-09-18"))

    def test_ignores_expired_record_after_grace(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_status(tmp, {
                "summer2026": {"final": self._record()},
            })
            # Window ended Sep 18; 3 days later is past the 2-day grace.
            result = update_cdn.find_active_confirmed_exam(
                now=__import__("datetime").date(2026, 9, 21),
                status_path=path,
                fetch_payload=lambda url: _official_payload(),
            )
            self.assertIsNone(result)

    def test_ignores_future_record_beyond_grace(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_status(tmp, {
                "fall2026": {"midterm": self._record()},
            })
            # Midterm window Nov 7-29: more than 14 days out from Sep 9.
            result = update_cdn.find_active_confirmed_exam(
                now=__import__("datetime").date(2026, 9, 9),
                status_path=path,
                fetch_payload=lambda url: {"exams": [{
                    "Course": "CSE110", "Section": "1", "Mid Date": "2026-11-07",
                    "Start Time": "10:00", "End Time": "11:30", "Room.": "09A-01C",
                }]},
            )
            self.assertIsNone(result)

    def test_ignores_unconfirmed_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_status(tmp, {
                "summer2026": {"final": self._record(confirmed=False)},
            })
            result = update_cdn.find_active_confirmed_exam(
                now=__import__("datetime").date(2026, 9, 9),
                status_path=path,
                fetch_payload=lambda url: _official_payload(),
            )
            self.assertIsNone(result)

    def test_picks_latest_ending_window_when_multiple_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_status(tmp, {
                "summer2026": {"final": self._record()},
                "spring2026": {"final": self._record()},
            })
            spring_payload = _official_payload(date="2026-04-20")
            result = update_cdn.find_active_confirmed_exam(
                now=__import__("datetime").date(2026, 9, 9),
                status_path=path,
                fetch_payload=lambda url: spring_payload if "spring" in url else _official_payload(),
            )
            self.assertEqual(result["semester_key"], "summer2026")

    def test_unavailable_payload_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_status(tmp, {
                "summer2026": {"final": self._record()},
            })
            def boom(url):
                raise ValueError("network down")
            result = update_cdn.find_active_confirmed_exam(
                now=__import__("datetime").date(2026, 9, 9),
                status_path=path,
                fetch_payload=boom,
            )
            self.assertIsNone(result)

    def test_missing_status_file_returns_none(self):
        result = update_cdn.find_active_confirmed_exam(
            now=__import__("datetime").date(2026, 9, 9),
            status_path="/nonexistent/exam_status.json",
        )
        self.assertIsNone(result)


class ForeignSemesterExamsTests(unittest.TestCase):
    def test_builds_all_pdf_finals_with_record_mid_dates(self):
        payload = _official_payload()
        record = {
            "confirmed": True,
            "dataUrl": "https://example.test/exam_data.json",
            "updatedAt": "2026-09-09T09:35:35Z",
            "midExamStartDate": "2026-07-25",
            "midExamEndDate": "2026-08-02",
        }
        exams, metadata = update_cdn.build_foreign_semester_exams_json(
            payload, record, "summer2026", "final")

        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0]["courseCode"], "CSE340")
        self.assertEqual(exams[0]["sectionName"], "3")
        self.assertEqual(exams[0]["finalExamDate"], "2026-09-18")
        self.assertEqual(exams[0]["finalExamTime"], "11:00-13:00")
        self.assertEqual(exams[0]["finalExamRoom"], "07B-17C")
        self.assertEqual(exams[0]["finalExamSource"], "pdf")
        self.assertIsNone(exams[0]["midExamDate"])

        self.assertEqual(metadata["semester"], "Summer2026")
        self.assertEqual(metadata["midExamStartDate"], "2026-07-25")
        self.assertEqual(metadata["midExamEndDate"], "2026-08-02")
        self.assertEqual(metadata["finalExamStartDate"], "2026-09-18")
        self.assertEqual(metadata["finalExamEndDate"], "2026-09-18")
        self.assertEqual(metadata["sources"]["final"]["source"], "pdf")
        self.assertTrue(metadata["sources"]["final"]["confirmed"])
        self.assertEqual(metadata["sources"]["final"]["matchedEntries"], 1)
        self.assertEqual(metadata["sources"]["final"]["totalEntries"], 1)
        self.assertFalse(metadata["sources"]["midterm"]["confirmed"])

    def test_generate_exams_json_uses_foreign_active_record(self):
        sections = [{
            "courseCode": "CSE110", "sectionName": "01", "sectionId": 1, "sectionType": "THEORY",
            "sectionSchedule": {"midExamDate": "2026-11-07", "midExamStartTime": "08:30",
                                "finalExamDate": "2026-12-31", "finalExamStartTime": "09:00"},
        }]
        active = {
            "semester_key": "summer2026", "exam_type": "final",
            "payload": _official_payload(),
            "record": {"confirmed": True, "dataUrl": "https://example.test/exam_data.json",
                       "updatedAt": "2026-09-09T09:35:35Z",
                       "midExamStartDate": "2026-07-25", "midExamEndDate": "2026-08-02"},
            "window": ("2026-09-18", "2026-09-18"), "window_end": "2026-09-18",
        }
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "exams.json"
            with unittest.mock.patch.object(update_cdn, "find_active_confirmed_exam", return_value=active):
                update_cdn.generate_exams_json(sections, str(out))

            data = json.loads(out.read_text())
            self.assertEqual(data["metadata"]["semester"], "Summer2026")
            self.assertEqual(data["metadata"]["totalExams"], 1)
            self.assertEqual(data["metadata"]["sources"]["final"]["source"], "pdf")
            self.assertTrue(data["metadata"]["sources"]["final"]["confirmed"])
            self.assertEqual(data["exams"][0]["courseCode"], "CSE340")
            self.assertEqual(data["exams"][0]["finalExamSource"], "pdf")
            self.assertNotEqual(data["exams"][0]["courseCode"], "CSE110")
            self.assertTrue(Path(str(out) + ".gz").exists())

    def test_generate_exams_json_keeps_usis_when_no_active_record(self):
        sections = [{
            "courseCode": "CSE110", "sectionName": "01", "sectionId": 1, "sectionType": "THEORY",
            "sectionSchedule": {"midExamDate": "2026-11-07", "midExamStartTime": "08:30",
                                "finalExamDate": "2026-12-31", "finalExamStartTime": "09:00"},
        }]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "exams.json"
            with unittest.mock.patch.object(update_cdn, "find_active_confirmed_exam", return_value=None):
                update_cdn.generate_exams_json(sections, str(out))

            data = json.loads(out.read_text())
            self.assertEqual(data["metadata"]["semester"], "Fall2026")
            self.assertEqual(data["metadata"]["totalExams"], 1)
            self.assertEqual(data["exams"][0]["courseCode"], "CSE110")
            self.assertEqual(data["exams"][0]["midExamSource"], "cdn")
            self.assertFalse(data["metadata"]["sources"]["midterm"]["confirmed"])

    def test_generate_exams_json_keeps_overlay_merge_for_same_semester(self):
        sections = [{
            "courseCode": "CSE110", "sectionName": "01", "sectionId": 1, "sectionType": "THEORY",
            "sectionSchedule": {"midExamDate": "2026-11-07", "midExamStartTime": "08:30",
                                "finalExamDate": "2026-12-31", "finalExamStartTime": "09:00"},
        }]
        active = {
            "semester_key": "fall2026", "exam_type": "midterm",
            "payload": {"exams": [{"Course": "CSE110", "Section": "1", "Mid Date": "2026-11-09",
                                   "Start Time": "10:00", "End Time": "11:30", "Room.": "09A-01C"}]},
            "record": {"confirmed": True, "dataUrl": "https://example.test/exam_data.json", "updatedAt": "2026-09-09"},
            "window": ("2026-11-09", "2026-11-09"), "window_end": "2026-11-09",
        }
        overlay = (active["payload"], active["record"])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "exams.json"
            with unittest.mock.patch.object(update_cdn, "find_active_confirmed_exam", return_value=active), \
                 unittest.mock.patch.object(update_cdn, "load_confirmed_exam_overlay", return_value=overlay):
                update_cdn.generate_exams_json(sections, str(out))

            data = json.loads(out.read_text())
            self.assertEqual(data["metadata"]["semester"], "Fall2026")
            # Same-semester record: the overlay merge path replaces the CDN value.
            self.assertEqual(data["exams"][0]["midExamDate"], "2026-11-09")
            self.assertEqual(data["exams"][0]["midExamTime"], "10:00-11:30")
            self.assertEqual(data["exams"][0]["midExamSource"], "pdf")


if __name__ == "__main__":
    unittest.main()
