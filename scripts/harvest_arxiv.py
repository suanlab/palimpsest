"""Harvest arXiv metadata via OAI-PMH for CS and Statistics papers.

The new arXiv OAI-PMH endpoint (oaipmh.arxiv.org) only supports top-level
sets (cs, stat, etc.), not sub-categories. We harvest cs and stat fully,
then filter AI-related sub-categories (cs:cs:AI, cs:cs:LG, etc.) in post.
"""

import json
import logging
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

BASE_URL = "https://oaipmh.arxiv.org/oai"

AI_SETSPEC_PREFIXES = {
    "cs:cs:AI",
    "cs:cs:LG",
    "cs:cs:CV",
    "cs:cs:CL",
    "cs:cs:NE",
    "stat:stat:ML",
}

HARVEST_SETS = ["cs", "stat"]

OUTPUT_DIR = Path("/home/suanlab/Projects/research/data/raw/arxiv")

OAI_NS = "{http://www.openarchives.org/OAI/2.0/}"
DC_NS = "{http://purl.org/dc/elements/1.1/}"
OAIDC_NS = "{http://www.openarchives.org/OAI/2.0/oai_dc/}"


def parse_record(record: ET.Element) -> dict | None:
    """Parse a single OAI-PMH record into a dict."""
    header = record.find(f"{OAI_NS}header")
    if header is None:
        return None

    status = header.get("status", "")
    if status == "deleted":
        return None

    identifier = header.findtext(f"{OAI_NS}identifier", "")
    datestamp = header.findtext(f"{OAI_NS}datestamp", "")
    set_specs = [s.text for s in header.findall(f"{OAI_NS}setSpec") if s.text]

    metadata = record.find(f"{OAI_NS}metadata")
    if metadata is None:
        return None

    dc = metadata.find(f"{OAIDC_NS}dc")
    if dc is None:
        return None

    title = dc.findtext(f"{DC_NS}title", "")
    creators = [c.text for c in dc.findall(f"{DC_NS}creator") if c.text]
    subjects = [s.text for s in dc.findall(f"{DC_NS}subject") if s.text]
    description = dc.findtext(f"{DC_NS}description", "")
    dates = [d.text for d in dc.findall(f"{DC_NS}date") if d.text]
    identifiers = [i.text for i in dc.findall(f"{DC_NS}identifier") if i.text]

    return {
        "oai_identifier": identifier,
        "datestamp": datestamp,
        "set_specs": set_specs,
        "title": title,
        "creators": creators,
        "subjects": subjects,
        "abstract": description,
        "dates": dates,
        "identifiers": identifiers,
    }


def is_ai_related(set_specs: list[str]) -> bool:
    """Check if any set_spec matches AI-related sub-categories."""
    return any(s in AI_SETSPEC_PREFIXES for s in set_specs)


def harvest_set(
    set_name: str,
    from_date: str = "2000-01-01",
    until_date: str | None = None,
) -> tuple[int, int]:
    """Harvest all records for a top-level arXiv set.

    Saves ALL records to {set_name}_all.jsonl and AI-filtered records
    to {set_name}_ai.jsonl.

    Args:
        set_name: Top-level arXiv set (e.g., "cs", "stat").
        from_date: Start date for harvesting (YYYY-MM-DD).
        until_date: End date. Defaults to today.

    Returns:
        Tuple of (total_records, ai_records) counts.
    """
    if until_date is None:
        until_date = datetime.now().strftime("%Y-%m-%d")

    all_file = OUTPUT_DIR / f"{set_name}_all.jsonl"
    ai_file = OUTPUT_DIR / f"{set_name}_ai.jsonl"

    params: dict[str, str] = {
        "verb": "ListRecords",
        "metadataPrefix": "oai_dc",
        "set": set_name,
        "from": from_date,
        "until": until_date,
    }

    total_records = 0
    ai_records = 0
    request_count = 0
    consecutive_errors = 0

    with (
        open(all_file, "w") as f_all,
        open(ai_file, "w") as f_ai,
        httpx.Client(timeout=120.0, follow_redirects=True) as client,
    ):
        while True:
            request_count += 1
            if request_count % 10 == 0:
                logger.info(
                    "[%s] Request %d — total: %d, AI: %d",
                    set_name,
                    request_count,
                    total_records,
                    ai_records,
                )

            try:
                response = client.get(BASE_URL, params=params)
                response.raise_for_status()
                consecutive_errors = 0
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 503:
                    retry_after = int(e.response.headers.get("Retry-After", "30"))
                    logger.warning(
                        "Rate limited (%s). Waiting %ds...",
                        set_name,
                        retry_after,
                    )
                    time.sleep(retry_after)
                    continue
                consecutive_errors += 1
                if consecutive_errors >= 5:
                    logger.error(
                        "Too many consecutive errors for %s. Stopping.",
                        set_name,
                    )
                    break
                logger.warning(
                    "HTTP %d for %s. Retrying in 10s...",
                    e.response.status_code,
                    set_name,
                )
                time.sleep(10)
                continue
            except (httpx.ReadTimeout, httpx.ConnectTimeout):
                consecutive_errors += 1
                if consecutive_errors >= 5:
                    logger.error(
                        "Too many timeouts for %s. Stopping.",
                        set_name,
                    )
                    break
                logger.warning("Timeout for %s. Retrying in 30s...", set_name)
                time.sleep(30)
                continue

            root = ET.fromstring(response.text)

            error = root.find(f"{OAI_NS}error")
            if error is not None:
                error_code = error.get("code", "unknown")
                if error_code == "noRecordsMatch":
                    logger.info("No records match for %s", set_name)
                    break
                logger.error(
                    "OAI-PMH error for %s: %s - %s",
                    set_name,
                    error_code,
                    error.text,
                )
                break

            list_records = root.find(f"{OAI_NS}ListRecords")
            if list_records is None:
                logger.warning("No ListRecords element for %s", set_name)
                break

            records = list_records.findall(f"{OAI_NS}record")
            for record in records:
                parsed = parse_record(record)
                if parsed:
                    line = json.dumps(parsed, ensure_ascii=False) + "\n"
                    f_all.write(line)
                    total_records += 1
                    if is_ai_related(parsed["set_specs"]):
                        f_ai.write(line)
                        ai_records += 1

            token_elem = list_records.find(f"{OAI_NS}resumptionToken")
            if token_elem is None or not token_elem.text:
                break

            params = {
                "verb": "ListRecords",
                "resumptionToken": token_elem.text,
            }

            time.sleep(3)

    logger.info(
        "Completed %s: %d total, %d AI-related → %s, %s",
        set_name,
        total_records,
        ai_records,
        all_file,
        ai_file,
    )
    return total_records, ai_records


def main() -> None:
    """Harvest CS and Statistics from arXiv, filter AI sub-categories."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary: dict[str, dict[str, int]] = {}

    for set_name in HARVEST_SETS:
        logger.info("=" * 60)
        logger.info("Starting harvest for set: %s", set_name)
        logger.info("=" * 60)

        try:
            total, ai = harvest_set(set_name, from_date="2005-09-16")
            summary[set_name] = {"total": total, "ai_related": ai}
        except Exception:
            logger.exception("Failed to harvest %s", set_name)
            summary[set_name] = {"total": -1, "ai_related": -1}

    summary_file = OUTPUT_DIR / "harvest_summary.json"
    with open(summary_file, "w") as f:
        json.dump(
            {
                "harvested_at": datetime.now().isoformat(),
                "sets": summary,
                "ai_filter_categories": sorted(AI_SETSPEC_PREFIXES),
            },
            f,
            indent=2,
        )

    logger.info("=" * 60)
    logger.info("HARVEST SUMMARY")
    grand_total = 0
    grand_ai = 0
    for s, counts in summary.items():
        logger.info(
            "  %s: %d total, %d AI-related",
            s,
            counts["total"],
            counts["ai_related"],
        )
        if counts["total"] > 0:
            grand_total += counts["total"]
            grand_ai += counts["ai_related"]
    logger.info("  GRAND TOTAL: %d total, %d AI-related", grand_total, grand_ai)
    logger.info("Summary saved to %s", summary_file)


if __name__ == "__main__":
    main()
