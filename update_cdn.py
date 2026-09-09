#!/usr/bin/env python3
"""
MRZ Connect CDN Data Update Script
Fetches course data from MRZ Connect API and generates static CDN files with metadata.
"""

import json
import os
import sys
import gzip
import requests
import glob
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUPS_DIR = os.path.join(SCRIPT_DIR, "backups")
VERSION_FILE = os.path.join(SCRIPT_DIR, "version.json")
EXAM_STATUS_FILE = os.path.join(SCRIPT_DIR, "exam_status.json")
STATUS_FILE = os.path.join(SCRIPT_DIR, "status.json")
LIVE_DATA_URL = "https://usis-cdn.eniamza.com/connect.json"


def load_version() -> Dict:
    """Load version info from version.json."""
    try:
        with open(VERSION_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"major": 2, "semester": 0, "daily": 0}


def bump_version(semester_changed: bool) -> str:
    """Bump version and return version string (MAJOR.SEMESTER.DAILY)."""
    v = load_version()

    if semester_changed:
        v["semester"] += 1
        v["daily"] = 0
    else:
        v["daily"] += 1

    with open(VERSION_FILE, 'w') as f:
        json.dump(v, f, indent=2)

    version_str = f"{v['major']}.{v['semester']}.{v['daily']}"
    print(f"✓ Version bumped to {version_str}")
    return version_str


def fetch_mrz_data(force: bool = False) -> Optional[List[Dict]]:
    """Fetch course data from MRZ Connect API with conditional GET."""
    url = LIVE_DATA_URL
    etag_file = os.path.join(SCRIPT_DIR, "connect.etag")
    headers = {}

    # Load stored ETag (skip if force mode)
    if not force and os.path.exists(etag_file):
        with open(etag_file, 'r') as f:
            stored_etag = f.read().strip()
            if stored_etag:
                headers['If-None-Match'] = stored_etag

    print(f"Fetching data from {url}...")
    if force:
        print("  (force mode - ignoring cached ETag)")

    try:
        response = requests.get(url, headers=headers, timeout=30)

        # Check for 304 Not Modified
        if response.status_code == 304:
            print("✓ Data not modified (304). Skipping update.")
            return None

        response.raise_for_status()

        # Save new ETag
        if 'ETag' in response.headers:
            with open(etag_file, 'w') as f:
                f.write(response.headers['ETag'])

        data = extract_sections(response.json())
        print(f"✓ Successfully fetched {len(data)} sections")
        return data
    except requests.RequestException as e:
        print(f"✗ Error fetching data: {e}")
        raise


def extract_sections(payload) -> List[Dict]:
    """Accept the upstream list and the wrapped payloads used by clients."""
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("sections", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return value

    raise ValueError("Unsupported Connect payload. Expected a list, {data: []}, or {sections: []}.")


def validate_exam_status_document(document: Dict) -> None:
    if not isinstance(document, dict):
        raise ValueError("exam_status.json must be an object")

    semesters = document.get("semesters", {})
    if not isinstance(semesters, dict):
        raise ValueError("exam_status.json semesters must be an object")

    for semester, exams in semesters.items():
        if not isinstance(exams, dict):
            raise ValueError(f"exam_status.json entry {semester} must be an object")
        for exam_type, record in exams.items():
            if not isinstance(record, dict):
                raise ValueError(f"exam_status.json {semester}.{exam_type} must be an object")
            if record.get("confirmed") is True and not isinstance(record.get("dataUrl"), str):
                raise ValueError(f"confirmed exam {semester}.{exam_type} requires dataUrl")


def build_status_document(metadata: Dict, status_path: str = EXAM_STATUS_FILE) -> Dict:
    """Build additive status metadata without changing existing API payloads."""
    existing = {}
    try:
        with open(status_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = {"schemaVersion": 1, "semesters": {}}
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid exam_status.json: {error}") from error

    validate_exam_status_document(existing)

    semester = get_current_semester(metadata.get("midExamStartDate"))
    semester_key = semester.lower()
    semesters = existing.get("semesters")
    if not isinstance(semesters, dict):
        semesters = {}

    return {
        "schemaVersion": 1,
        "currentSemester": semester,
        "currentSemesterKey": semester_key,
        "liveDataUrl": LIVE_DATA_URL,
        "stableDataUrl": "https://connect-cdn.itzmrz.xyz/stable.json",
        "lastUpdated": metadata.get("lastUpdated"),
        "semesters": semesters,
    }


def write_json_file(path: str, data: Dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def calculate_connect_metadata(sections: List[Dict]) -> Dict:
    """Calculate metadata for connect.json."""
    print("Calculating connect.json metadata...")

    # Initialize values
    section_ids = []
    total_consumed = 0
    total_capacity = 0
    mid_dates = []
    final_dates = []

    # Process each section
    for section in sections:
        section_ids.append(section['sectionId'])
        total_consumed += section.get('consumedSeat', 0)
        total_capacity += section.get('capacity', 0)

        # Extract exam dates
        schedule = section.get('sectionSchedule', {})
        if schedule:
            mid_date = schedule.get('midExamDate')
            final_date = schedule.get('finalExamDate')

            if mid_date:
                mid_dates.append(mid_date)
            if final_date:
                final_dates.append(final_date)

    # Sort dates
    mid_dates.sort()
    final_dates.sort()

    metadata = {
        "firstSectionId": min(section_ids) if section_ids else None,
        "lastSectionId": max(section_ids) if section_ids else None,
        "totalSections": len(sections),
        "totalConsumedSeats": total_consumed,
        "totalEmptySeats": total_capacity - total_consumed,
        "totalCapacity": total_capacity,
        "midExamStartDate": mid_dates[0] if mid_dates else None,
        "midExamEndDate": mid_dates[-1] if mid_dates else None,
        "finalExamStartDate": final_dates[0] if final_dates else None,
        "finalExamEndDate": final_dates[-1] if final_dates else None,
        "lastUpdated": datetime.now(timezone.utc).isoformat()
    }

    print(f"✓ Metadata calculated:")
    print(f"  - Total sections: {metadata['totalSections']}")
    print(f"  - Total consumed seats: {metadata['totalConsumedSeats']}")
    print(f"  - Total empty seats: {metadata['totalEmptySeats']}")
    print(
        f"  - Mid exams: {metadata['midExamStartDate']} to {metadata['midExamEndDate']}")
    print(
        f"  - Final exams: {metadata['finalExamStartDate']} to {metadata['finalExamEndDate']}")

    return metadata


def get_current_semester(mid_exam_start: Optional[str]) -> str:
    """Determine current semester based on mid exam start date."""
    if not mid_exam_start:
        return "Unknown"

    try:
        date = datetime.strptime(mid_exam_start, "%Y-%m-%d")
        month = date.month
        year = date.year

        # Determine semester
        if 1 <= month <= 4:
            return f"Spring{year}"
        elif 5 <= month <= 8:
            return f"Summer{year}"
        else:  # 9-12
            return f"Fall{year}"
    except:
        return "Unknown"


def semester_to_filename(semester: str) -> str:
    """Convert semester name to clean filename: Spring2026 → spring2026.json"""
    return semester.lower() + ".json"


def manage_current_backup(metadata: Dict, sections: List[Dict]):
    """Manage current semester backup."""
    print("\n" + "=" * 60)
    print("Managing Current Semester Backup")
    print("=" * 60)

    # Ensure backups directory exists
    os.makedirs(BACKUPS_DIR, exist_ok=True)

    # Get current semester info
    mid_exam_start = metadata.get('midExamStartDate')
    current_semester = get_current_semester(mid_exam_start)
    semester_changed = False

    print(f"\nCurrent Semester: {current_semester}")
    print(f"Mid Exam Start: {mid_exam_start}")

    # Check for existing backup of this semester
    backup_name = semester_to_filename(current_semester)
    backup_path = os.path.join(BACKUPS_DIR, backup_name)

    # Find all existing backup files to detect semester change
    existing_backups = glob.glob(os.path.join(BACKUPS_DIR, "*.json"))

    if existing_backups:
        # Check the most recent backup's semester
        latest_backup = max(existing_backups, key=os.path.getmtime)
        try:
            with open(latest_backup, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                old_mid_exam = old_data['metadata'].get('midExamStartDate')
                old_semester = get_current_semester(old_mid_exam)

            if mid_exam_start != old_mid_exam and old_semester != current_semester:
                semester_changed = True
                print(f"\n📅 Semester changed!")
                print(f"   Old: {old_mid_exam} ({old_semester})")
                print(f"   New: {mid_exam_start} ({current_semester})")
                print(f"✓ Previous backup preserved: {os.path.basename(latest_backup)}")
            else:
                print(f"✓ Same semester, updating backup...")
        except Exception as e:
            print(f"⚠️  Error reading old backup: {e}")
    else:
        semester_changed = True

    # Write current semester backup
    backup_data = {
        "metadata": metadata,
        "sections": sections
    }

    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(backup_path) / 1024
    print(f"\n✓ Created/Updated: {backup_name} ({file_size:.1f} KB)")

    return backup_name, semester_changed


def manage_stable_json(metadata: Dict, sections: List[Dict]):
    """Manage stable.json — stays on current semester until final exams end.

    connect.json always has the latest API data (could be next semester mid-current).
    stable.json only updates when:
      - Same semester as current stable (daily seat/schedule changes are fine)
      - Different semester AND stable's final exams have ended

    Semester end is detected by: today > finalExamEndDate
    """
    stable_path = os.path.join(SCRIPT_DIR, "stable.json")
    incoming_semester = get_current_semester(metadata.get('midExamStartDate'))

    print("\n" + "=" * 60)
    print("Managing stable.json")
    print("=" * 60)

    if os.path.exists(stable_path):
        try:
            with open(stable_path, 'r', encoding='utf-8') as f:
                stable_data = json.load(f)

            stable_mid = stable_data['metadata'].get('midExamStartDate')
            stable_semester = get_current_semester(stable_mid)

            if incoming_semester == stable_semester:
                print(f"\n  Same semester ({stable_semester}) — updating with latest data")
            else:
                # Different semester — only switch after finals end
                final_end = stable_data['metadata'].get('finalExamEndDate')
                if final_end:
                    today = datetime.now(timezone.utc).date()
                    final_end_date = datetime.strptime(final_end, "%Y-%m-%d").date()

                    if today <= final_end_date:
                        stable_size = os.path.getsize(stable_path) / 1024
                        print(f"\n  ⏸ Frozen on {stable_semester} (finals end {final_end})")
                        print(f"  API has {incoming_semester} data, but {stable_semester} finals haven't ended")
                        print(f"  stable.json unchanged ({stable_size:.1f} KB)")
                        return

                print(f"\n  Switching: {stable_semester} → {incoming_semester} (previous finals ended)")
        except Exception as e:
            print(f"\n  ⚠️  Error reading stable.json: {e}, recreating")
    else:
        print(f"\n  Creating stable.json ({incoming_semester})")

    # Write stable.json
    stable_data = {"metadata": metadata, "sections": sections}

    with open(stable_path, 'w', encoding='utf-8') as f:
        json.dump(stable_data, f, indent=2, ensure_ascii=False)

    # Write gzipped version
    gz_path = stable_path + '.gz'
    with gzip.open(gz_path, 'wt', encoding='utf-8') as f:
        json.dump(stable_data, f, separators=(',', ':'), ensure_ascii=False)

    file_size = os.path.getsize(stable_path) / 1024
    gz_size = os.path.getsize(gz_path) / 1024
    print(f"  ✓ stable.json written ({file_size:.1f} KB, gzipped: {gz_size:.1f} KB)")


def load_confirmed_exam_overlay(semester: str, exam_type: str) -> tuple[dict | None, dict | None]:
    """Fetch a confirmed official PDF-derived schedule when configured."""
    try:
        with open(EXAM_STATUS_FILE, "r", encoding="utf-8") as f:
            status = json.load(f)
        validate_exam_status_document(status)
        record = status.get("semesters", {}).get(semester.lower(), {}).get(exam_type)
        if not isinstance(record, dict) or record.get("confirmed") is not True:
            return None, None

        data_url = record.get("dataUrl")
        if not isinstance(data_url, str) or not data_url.startswith("https://"):
            return None, None

        response = requests.get(data_url, timeout=30)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("exams"), list):
            raise ValueError("official exam payload must contain an exams list")
        return payload, record
    except (FileNotFoundError, json.JSONDecodeError, ValueError, requests.RequestException) as error:
        print(f"  Official {exam_type} overlay unavailable; keeping CDN data: {error}")
        return None, None


def official_exam_index(payload: dict | None, exam_type: str) -> dict[tuple[str, str], dict]:
    if not payload:
        return {}

    date_key = "Final Date" if exam_type == "final" else "Mid Date"
    result = {}
    for exam in payload.get("exams", []):
        if not isinstance(exam, dict):
            continue
        course = exam.get("Course") or exam.get("courseCode")
        section = exam.get("Section") or exam.get("sectionName")
        date = exam.get(date_key) or exam.get("finalExamDate" if exam_type == "final" else "midExamDate")
        if course and section and date:
            result[(str(course).strip().upper(), str(section).strip().zfill(2))] = exam
    return result


def apply_official_overlay(exams: List[Dict], official: dict[tuple[str, str], dict], exam_type: str) -> int:
    date_key = "Final Date" if exam_type == "final" else "Mid Date"
    time_start_key = "finalExamTime" if exam_type == "final" else "midExamTime"
    room_key = "finalExamRoom" if exam_type == "final" else "midExamRoom"
    applied = 0

    for exam in exams:
        key = (str(exam.get("courseCode", "")).strip().upper(), str(exam.get("sectionName", "")).strip().zfill(2))
        official_exam = official.get(key)
        if not official_exam:
            continue

        official_date = official_exam.get(date_key) or official_exam.get(
            "finalExamDate" if exam_type == "final" else "midExamDate"
        )
        official_time = official_exam.get("Start Time") or official_exam.get(time_start_key)
        official_end = official_exam.get("End Time")
        official_room = official_exam.get("Room.") or official_exam.get(room_key)
        source_key = "finalExamSource" if exam_type == "final" else "midExamSource"
        date_output_key = "finalExamDate" if exam_type == "final" else "midExamDate"
        if official_date:
            exam[date_output_key] = official_date
        if official_time:
            if exam_type == "final":
                exam["finalExamTime"] = official_time if not official_end else f"{official_time}-{official_end}"
            else:
                exam["midExamTime"] = official_time if not official_end else f"{official_time}-{official_end}"
        if official_room:
            exam[room_key] = official_room
        exam[source_key] = "pdf"
        applied += 1

    return applied


def generate_exam_source_metadata(semester: str, overlays: dict[str, tuple[dict | None, dict | None]], applied: dict[str, int], totals: dict[str, int]) -> Dict:
    sources = {}
    for exam_type, (payload, record) in overlays.items():
        matched = applied.get(exam_type, 0)
        total = totals.get(exam_type, 0)
        source = "pdf" if total and matched == total else "mixed" if matched else "cdn"
        sources[exam_type] = {
            "source": source,
            "confirmed": source == "pdf",
            "matchedEntries": matched,
            "totalEntries": total,
            "updatedAt": record.get("updatedAt") if record else None,
            "dataUrl": record.get("dataUrl") if record and matched else None,
        }
    return {"semester": semester, "sources": sources}


# Grace windows around a confirmed official exam period during which it is
# considered "active": show it a few days before it starts and keep serving it
# briefly after it ends.
ACTIVE_EXAM_GRACE_BEFORE_DAYS = 14
ACTIVE_EXAM_GRACE_AFTER_DAYS = 2


def _fetch_payload(url: str) -> Dict:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def official_exam_window(payload: dict | None, exam_type: str) -> tuple[str, str] | None:
    """Return (start, end) of the official exam window for exam_type from a
    PDF-derived payload, or None when no usable dates exist."""
    if not payload or not isinstance(payload.get("exams"), list):
        return None
    date_key = "Final Date" if exam_type == "final" else "Mid Date"
    alt_key = "finalExamDate" if exam_type == "final" else "midExamDate"
    dates = []
    for exam in payload["exams"]:
        if not isinstance(exam, dict):
            continue
        value = (exam.get(date_key) or exam.get(alt_key) or "").strip()
        if value:
            dates.append(value)
    if not dates:
        return None
    dates.sort()
    return dates[0], dates[-1]


def find_active_confirmed_exam(now=None, status_path: str = EXAM_STATUS_FILE, fetch_payload=None):
    """Find a confirmed official exam record whose exam window is active or
    imminent, across ALL semesters in exam_status.json.

    Returns a dict with semester_key/exam_type/payload/record/window, preferring
    the record whose window ends latest. Returns None when nothing qualifies.

    This is what keeps exams.json on the real exam period during the transition
    window (e.g. Summer finals while USIS has already published the next
    semester), where the same-semester overlay merge cannot apply.
    """
    fetch = fetch_payload or _fetch_payload
    today = (now or datetime.now(timezone.utc).date())
    grace_before = (today + timedelta(days=ACTIVE_EXAM_GRACE_BEFORE_DAYS)).isoformat()
    grace_after = (today - timedelta(days=ACTIVE_EXAM_GRACE_AFTER_DAYS)).isoformat()
    try:
        with open(status_path, "r", encoding="utf-8") as f:
            status = json.load(f)
        validate_exam_status_document(status)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
        print(f"  Confirmed-exam lookup skipped: {error}")
        return None

    candidates = []
    for semester_key, exams in status.get("semesters", {}).items():
        if not isinstance(exams, dict):
            continue
        for exam_type, record in exams.items():
            if not isinstance(record, dict) or record.get("confirmed") is not True:
                continue
            data_url = record.get("dataUrl")
            if not isinstance(data_url, str) or not data_url.startswith("https://"):
                continue
            try:
                payload = fetch(data_url)
            except Exception as error:
                print(f"  Official {exam_type} overlay unavailable ({semester_key}): {error}")
                continue
            window = official_exam_window(payload, exam_type)
            if not window:
                continue
            start, end = window
            if start <= grace_before and end >= grace_after:
                candidates.append({
                    "semester_key": semester_key,
                    "exam_type": exam_type,
                    "payload": payload,
                    "record": record,
                    "window": window,
                    "window_end": end,
                })

    if not candidates:
        return None
    return max(candidates, key=lambda c: c["window_end"])


def build_foreign_semester_exams_json(payload: Dict, record: Dict, semester_key: str, exam_type: str) -> tuple[List[Dict], Dict]:
    """Build an exams.json payload entirely from a confirmed official PDF
    payload for a semester other than the one USIS currently publishes."""
    date_key = "Final Date" if exam_type == "final" else "Mid Date"
    out_date_key = "finalExamDate" if exam_type == "final" else "midExamDate"
    out_time_key = "finalExamTime" if exam_type == "final" else "midExamTime"
    out_room_key = "finalExamRoom" if exam_type == "final" else "midExamRoom"
    source_key = "finalExamSource" if exam_type == "final" else "midExamSource"
    other_out_date_key = "midExamDate" if exam_type == "final" else "finalExamDate"
    other_out_time_key = "midExamTime" if exam_type == "final" else "finalExamTime"
    other_out_room_key = "midExamRoom" if exam_type == "final" else "finalExamRoom"
    other_source_key = "midExamSource" if exam_type == "final" else "finalExamSource"

    exams = []
    for exam in payload.get("exams", []):
        if not isinstance(exam, dict):
            continue
        course = exam.get("Course") or exam.get("courseCode")
        section = exam.get("Section") or exam.get("sectionName")
        date = exam.get(date_key) or exam.get(out_date_key)
        if not course or not section or not date:
            continue

        start = exam.get("Start Time")
        end = exam.get("End Time")
        time_value = exam.get(out_time_key)
        if start and end:
            time_value = f"{start}-{end}"
        elif start and not time_value:
            time_value = start

        exams.append({
            "courseCode": str(course).strip(),
            "sectionName": str(section).strip(),
            "sectionId": None,
            "sectionType": "THEORY",
            other_out_date_key: None,
            other_out_time_key: None,
            other_out_room_key: None,
            other_source_key: None,
            out_date_key: str(date).strip(),
            out_time_key: time_value,
            out_room_key: exam.get("Room.") or exam.get(out_room_key) or None,
            source_key: "pdf",
        })

    window = official_exam_window(payload, exam_type)
    if not window:
        raise ValueError("official payload has no usable exam window")
    if exam_type == "final":
        mid_start = record.get("midExamStartDate")
        mid_end = record.get("midExamEndDate")
        final_start, final_end = window
    else:
        mid_start, mid_end = window
        final_start = record.get("finalExamStartDate")
        final_end = record.get("finalExamEndDate")

    metadata = {
        "totalExams": len(exams),
        "midExamStartDate": mid_start,
        "midExamEndDate": mid_end,
        "finalExamStartDate": final_start,
        "finalExamEndDate": final_end,
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "semester": semester_key[0].upper() + semester_key[1:],
        "sources": {
            exam_type: {
                "source": "pdf",
                "confirmed": True,
                "matchedEntries": len(exams),
                "totalEntries": len(exams),
                "updatedAt": record.get("updatedAt"),
                "dataUrl": record.get("dataUrl"),
            },
            ("midterm" if exam_type == "final" else "final"): {
                "source": "cdn",
                "confirmed": False,
                "matchedEntries": 0,
                "totalEntries": 0,
                "updatedAt": None,
                "dataUrl": None,
            },
        },
    }
    return exams, metadata


def write_exams_files(output_data: Dict, output_path: str) -> None:
    """Write exams.json and its gzipped variant, printing size stats."""
    if not os.path.isabs(output_path):
        output_path = os.path.join(SCRIPT_DIR, output_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    gzip_path = output_path + '.gz'
    with gzip.open(gzip_path, 'wt', encoding='utf-8') as f:
        json.dump(output_data, f, separators=(',', ':'), ensure_ascii=False)

    regular_size = os.path.getsize(output_path) / 1024  # KB
    gzip_size = os.path.getsize(gzip_path) / 1024  # KB
    compression_ratio = ((regular_size - gzip_size) / regular_size * 100)

    print(f"✓ {output_path} created successfully")
    print(f"  Regular: {regular_size:.1f} KB | Gzipped: {gzip_size:.1f} KB (saved {compression_ratio:.1f}%)")
    metadata = output_data.get("metadata", {})
    print(f"  Total exams: {metadata.get('totalExams')}")
    print(f"  Mid exams: {metadata.get('midExamStartDate')} to {metadata.get('midExamEndDate')}")
    print(f"  Final exams: {metadata.get('finalExamStartDate')} to {metadata.get('finalExamEndDate')}")



def generate_exams_json(sections: List[Dict], output_path: str = "exams.json"):
    """Generate exams.json with exam schedule data."""
    # Ensure output path is in the script directory
    if not os.path.isabs(output_path):
        output_path = os.path.join(SCRIPT_DIR, output_path)

    print(f"\nGenerating {output_path}...")

    exams = []
    mid_dates = []
    final_dates = []

    for section in sections:
        schedule = section.get('sectionSchedule', {})
        if not schedule:
            continue

        mid_date = schedule.get('midExamDate')
        mid_time = schedule.get('midExamStartTime')
        final_date = schedule.get('finalExamDate')
        final_time = schedule.get('finalExamStartTime')

        # Skip sections without exam dates (typically LAB sections)
        if not mid_date and not final_date:
            continue

        section_type = section.get('sectionType')
        normalized_section_type = "LAB" if section_type == "LAB" else "THEORY"

        exam_entry = {
            "courseCode": section.get('courseCode'),
            "sectionName": section.get('sectionName'),
            "sectionId": section.get('sectionId'),
            "sectionType": normalized_section_type,
            "midExamDate": mid_date,
            "midExamTime": mid_time,
            "midExamRoom": None,
            "midExamSource": "cdn" if mid_date else None,
            "finalExamDate": final_date,
            "finalExamTime": final_time,
            "finalExamRoom": None,
            "finalExamSource": "cdn" if final_date else None
        }

        exams.append(exam_entry)

        # Collect dates for metadata
        if mid_date:
            mid_dates.append(mid_date)
        if final_date:
            final_dates.append(final_date)

    semester = get_current_semester(mid_dates[0] if mid_dates else final_dates[0] if final_dates else None)

    # If a confirmed official exam for a semester OTHER than the one USIS is
    # currently publishing has an active or imminent exam window, serve that
    # official schedule directly. This keeps exams.json on the real exam period
    # during the transition window (e.g. Summer finals while USIS has already
    # published the next semester) instead of falling back to tentative data.
    # The same-semester overlay merge below remains the path when USIS and the
    # confirmed record agree on the semester.
    try:
        active_confirmed = find_active_confirmed_exam()
    except Exception as error:
        print(f"  Confirmed-exam lookup failed; using USIS-derived schedule: {error}")
        active_confirmed = None
    if active_confirmed and active_confirmed["semester_key"] != semester.lower():
        print(f"  Serving active official {active_confirmed['exam_type']} schedule for "
              f"{active_confirmed['semester_key']} (window {active_confirmed['window'][0]} to "
              f"{active_confirmed['window'][1]}) instead of USIS {semester} data")
        exams, metadata = build_foreign_semester_exams_json(
            active_confirmed["payload"],
            active_confirmed["record"],
            active_confirmed["semester_key"],
            active_confirmed["exam_type"],
        )
        write_exams_files({"metadata": metadata, "exams": exams}, output_path)
        return

    overlays = {
        "midterm": load_confirmed_exam_overlay(semester, "midterm"),
        "final": load_confirmed_exam_overlay(semester, "final"),
    }
    applied = {
        exam_type: apply_official_overlay(exams, official_exam_index(payload, exam_type), exam_type)
        for exam_type, (payload, record) in overlays.items()
    }
    totals = {
        "midterm": sum(1 for exam in exams if exam.get("midExamDate")),
        "final": sum(1 for exam in exams if exam.get("finalExamDate")),
    }

    # Sort dates
    mid_dates = sorted(exam["midExamDate"] for exam in exams if exam.get("midExamDate"))
    final_dates = sorted(exam["finalExamDate"] for exam in exams if exam.get("finalExamDate"))

    metadata = {
        "totalExams": len(exams),
        "midExamStartDate": mid_dates[0] if mid_dates else None,
        "midExamEndDate": mid_dates[-1] if mid_dates else None,
        "finalExamStartDate": final_dates[0] if final_dates else None,
        "finalExamEndDate": final_dates[-1] if final_dates else None,
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        **generate_exam_source_metadata(semester, overlays, applied, totals)
    }

    output_data = {
        "metadata": metadata,
        "exams": exams
    }

    write_exams_files(output_data, output_path)


def main():
    """Main execution function."""
    force = '--force' in sys.argv

    print("=" * 60)
    print("MRZ Connect CDN Data Update Script")
    print("=" * 60)

    try:
        # Fetch data from API
        sections = fetch_mrz_data(force=force)

        if sections is None:
            print("\n✓ No changes detected. Exiting.")
            return 0

        # Calculate metadata first (needed for backup management)
        metadata = calculate_connect_metadata(sections)

        # Manage current semester backup
        curr_backup_name, semester_changed = manage_current_backup(
            metadata, sections)

        # Bump version (daily +1, or semester +1 & daily reset)
        version = bump_version(semester_changed)
        metadata["version"] = version

        # Write additive detection/confirmation metadata. Existing public
        # payloads remain unchanged for backwards compatibility.
        status_document = build_status_document(metadata)
        write_json_file(STATUS_FILE, status_document)
        print("✓ status.json updated (live-data detection metadata)")

        # Generate both JSON files
        output_data = {
            "metadata": metadata,
            "sections": sections
        }

        # Write connect.json
        connect_path = os.path.join(SCRIPT_DIR, "connect.json")
        with open(connect_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        # Write gzipped version
        gzip_path = connect_path + '.gz'
        with gzip.open(gzip_path, 'wt', encoding='utf-8') as f:
            json.dump(output_data, f, separators=(
                ',', ':'), ensure_ascii=False)

        # Write metadata only JSON (optimization for landing page)
        metadata_path = os.path.join(SCRIPT_DIR, "connect_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({"metadata": metadata}, f, indent=2, ensure_ascii=False)

        # Write gzipped metadata version
        metadata_gzip_path = metadata_path + '.gz'
        with gzip.open(metadata_gzip_path, 'wt', encoding='utf-8') as f:
            json.dump({"metadata": metadata}, f, separators=(
                ',', ':'), ensure_ascii=False)

        regular_size = os.path.getsize(connect_path) / 1024
        gzip_size = os.path.getsize(gzip_path) / 1024
        metadata_size = os.path.getsize(metadata_path) / 1024
        compression_ratio = ((regular_size - gzip_size) / regular_size * 100)

        print(f"\n✓ connect.json created successfully")
        print(
            f"✓ connect_metadata.json created successfully ({metadata_size:.2f} KB)")
        print(f"  Regular: {regular_size:.1f} KB")
        print(
            f"  Gzipped: {gzip_size:.1f} KB (saved {compression_ratio:.1f}%)")

        # Manage stable.json — stays on current semester until finals end
        manage_stable_json(metadata, sections)

        # Generate exams.json
        generate_exams_json(sections)

        # Generate backup index
        print("\n" + "=" * 60)
        print("Generating Backup Index")
        print("=" * 60)

        from generate_backup_index import generate_backup_index
        generate_backup_index()

        # Generate free/open labs CDN (always refresh — schedules can change mid-semester)
        print("\n" + "=" * 60)
        print("Generating Open Labs CDN")
        print("=" * 60)
        try:
            from generate_free_labs import generate_free_labs_json
            generate_free_labs_json()
        except Exception as e:
            print(f"⚠️  Error generating open labs: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 60)
        print("✓ All files generated successfully!")
        print("=" * 60)
        print(f"\nFiles:")
        print(f"  connect.json  — latest API data (always up-to-date)")
        print(f"  stable.json   — current semester (frozen until finals end)")
        print(f"  exams.json    — exam schedules")
        print(f"  open_labs.json — lab availability")
        print(f"  Backup: {curr_backup_name}")

        print("\nNext steps:")
        print("1. Review the generated JSON files")
        print("2. Commit and push to GitHub")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
