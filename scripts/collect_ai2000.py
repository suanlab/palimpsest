#!/usr/bin/env python3
"""Collect AI 2000 ranking data from AMiner public APIs.

This script fetches AMiner AI 2000 domain metadata and ranking records,
stores raw API responses for reproducibility, and writes normalized parquet
tables for downstream analysis.
"""
# pyright: basic

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
from httpx import Client, HTTPError

BASE_URL = "https://apiv2.aminer.cn/magic"
USER_AGENT = "Research-SciSci/1.0 (suanlab@gmail.com)"
REQUEST_TIMEOUT_SECONDS = 30.0
REQUEST_DELAY_SECONDS = 1.0
PAGE_SIZE = 100
MAX_PAGES_PER_DOMAIN = 20

DOMAINS_ACTION = "__ranking.GetRankingDomains___"
RECORDS_ACTION = "__ranking.GetRankingRecords___"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FALLBACK_DIR = PROJECT_ROOT / "tmp" / "aminer_api_responses"
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "aminer"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RESEARCHERS_PATH = PROCESSED_DIR / "ai2000_researchers.parquet"
DOMAINS_PATH = PROCESSED_DIR / "ai2000_domains.parquet"

RESEARCHER_COLUMNS = [
    "domain_id",
    "domain_name",
    "entity_id",
    "name",
    "gender",
    "h_index",
    "n_pubs",
    "country",
    "org",
    "keywords",
    "ai2000_score",
    "ai2000_rank",
    "domain_citations",
    "domain_citation_rank",
    "normalized_citations",
]


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_fallback_json(file_name: str) -> dict[str, Any]:
    with (FALLBACK_DIR / file_name).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"Fallback file {file_name} did not contain a JSON object")
    return payload


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _extract_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data_block = payload.get("data")
    if not isinstance(data_block, list) or not data_block:
        return []
    first = data_block[0]
    if not isinstance(first, dict):
        return []
    nested = first.get("data")
    if not isinstance(nested, dict):
        return []
    records = nested.get("records")
    if not isinstance(records, list):
        return []

    parsed: list[dict[str, Any]] = []
    for record in records:
        if isinstance(record, dict):
            parsed.append(record)
    return parsed


def _request_json(
    client: Client,
    action: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    request_params: dict[str, Any] = {"a": action}
    if params:
        request_params.update(params)

    last_error: Exception | None = None
    for attempt in range(1, 3):
        try:
            response = client.get(BASE_URL, params=request_params)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Response JSON root is not an object")
            return payload
        except (HTTPError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == 2:
                break
            print(
                f"Request failed for action={action} params={params}. Retrying once..."
            )
        finally:
            time.sleep(REQUEST_DELAY_SECONDS)

    print(
        f"Request failed after retry for action={action} params={params}: {last_error}"
    )
    return None


def _extract_domain_tree(domains_payload: dict[str, Any]) -> dict[str, Any]:
    data_block = domains_payload.get("data")
    if not isinstance(data_block, list) or not data_block:
        raise ValueError("Domain payload missing top-level data list")
    first = data_block[0]
    if not isinstance(first, dict):
        raise ValueError("Domain payload has invalid first data item")
    nested = first.get("data")
    if not isinstance(nested, list) or not nested:
        raise ValueError("Domain payload missing nested domain tree")
    root = nested[0]
    if not isinstance(root, dict):
        raise ValueError("Domain root is not an object")
    return root


def _name_en(node: dict[str, Any]) -> str:
    name = node.get("name")
    if isinstance(name, dict):
        value = name.get("en")
        if isinstance(value, str):
            return value
    return ""


def _flatten_domains(
    node: dict[str, Any],
    parent_id: str | None,
    parent_name: str | None,
    level: int,
) -> list[dict[str, Any]]:
    node_id = node.get("id")
    domain_id = str(node_id) if isinstance(node_id, str) else ""
    domain_name = _name_en(node)

    name_obj = node.get("name")
    abbr = None
    if isinstance(name_obj, dict):
        abbr_raw = name_obj.get("abbr")
        if isinstance(abbr_raw, str):
            abbr = abbr_raw

    children = node.get("children")
    child_list = children if isinstance(children, list) else []

    annual_detail = node.get("annual_detail")
    annual_list = annual_detail if isinstance(annual_detail, list) else []

    rows: list[dict[str, Any]] = []
    if annual_list:
        for detail in annual_list:
            if not isinstance(detail, dict):
                continue
            rows.append(
                {
                    "domain_id": domain_id,
                    "domain_name": domain_name,
                    "domain_abbr": abbr,
                    "level": level,
                    "parent_id": parent_id,
                    "parent_name": parent_name,
                    "year": _safe_int(detail.get("year")),
                    "pubs": _safe_int(detail.get("pubs")),
                    "scholars": _safe_int(detail.get("scholars")),
                    "children_count": len(child_list),
                },
            )
    else:
        rows.append(
            {
                "domain_id": domain_id,
                "domain_name": domain_name,
                "domain_abbr": abbr,
                "level": level,
                "parent_id": parent_id,
                "parent_name": parent_name,
                "year": None,
                "pubs": None,
                "scholars": None,
                "children_count": len(child_list),
            },
        )

    for child in child_list:
        if not isinstance(child, dict):
            continue
        rows.extend(
            _flatten_domains(
                node=child,
                parent_id=domain_id,
                parent_name=domain_name,
                level=level + 1,
            ),
        )
    return rows


def _extract_major_subfields(root: dict[str, Any]) -> list[dict[str, str]]:
    children = root.get("children")
    level1 = children if isinstance(children, list) else []

    major: list[dict[str, str]] = []
    for parent in level1:
        if not isinstance(parent, dict):
            continue
        for subfield in parent.get("children", []):
            if not isinstance(subfield, dict):
                continue
            subfield_id = subfield.get("id")
            if not isinstance(subfield_id, str):
                continue
            major.append(
                {
                    "domain_id": subfield_id,
                    "domain_name": _name_en(subfield),
                },
            )
    return major


def _parse_researcher_record(
    record: dict[str, Any],
    domain_id: str,
    domain_name: str,
) -> dict[str, Any]:
    content = record.get("content")
    person = content.get("person") if isinstance(content, dict) else {}
    person_dict = person if isinstance(person, dict) else {}

    metrics = record.get("metrics")
    metrics_dict = metrics if isinstance(metrics, dict) else {}

    name_en = ""
    name_obj = person_dict.get("name")
    if isinstance(name_obj, dict):
        name_value = name_obj.get("en")
        if isinstance(name_value, str):
            name_en = name_value

    country = ""
    country_obj = person_dict.get("country")
    if isinstance(country_obj, dict):
        country_name_obj = country_obj.get("name")
        if isinstance(country_name_obj, dict):
            country_value = country_name_obj.get("en")
            if isinstance(country_value, str):
                country = country_value

    org = ""
    org_obj = person_dict.get("org")
    if isinstance(org_obj, dict):
        org_name_obj = org_obj.get("name")
        if isinstance(org_name_obj, dict):
            org_value = org_name_obj.get("en")
            if isinstance(org_value, str):
                org = org_value

    keywords_raw = person_dict.get("keywords")
    keywords_list: list[str] = []
    if isinstance(keywords_raw, list):
        for keyword in keywords_raw:
            if isinstance(keyword, dict):
                keyword_en = keyword.get("en")
                if isinstance(keyword_en, str) and keyword_en:
                    keywords_list.append(keyword_en)

    ai2000_index = metrics_dict.get("ai2000_index_classic")
    ai2000_dict = ai2000_index if isinstance(ai2000_index, dict) else {}

    domain_citations = metrics_dict.get("domain_pubs_citations")
    domain_citations_dict = (
        domain_citations if isinstance(domain_citations, dict) else {}
    )

    normalized_citations = metrics_dict.get("normalized_citations")
    normalized_citations_dict = (
        normalized_citations if isinstance(normalized_citations, dict) else {}
    )

    entity_id = record.get("entity_id")
    entity_value = str(entity_id) if isinstance(entity_id, str) else ""

    return {
        "domain_id": domain_id,
        "domain_name": domain_name,
        "entity_id": entity_value,
        "name": name_en,
        "gender": person_dict.get("gender")
        if isinstance(person_dict.get("gender"), str)
        else None,
        "h_index": _safe_int(person_dict.get("h_index")),
        "n_pubs": _safe_int(person_dict.get("n_pubs")),
        "country": country,
        "org": org,
        "keywords": "; ".join(keywords_list),
        "ai2000_score": _safe_float(ai2000_dict.get("score")),
        "ai2000_rank": _safe_int(ai2000_dict.get("rank")),
        "domain_citations": _safe_float(domain_citations_dict.get("score")),
        "domain_citation_rank": _safe_int(domain_citations_dict.get("rank")),
        "normalized_citations": _safe_float(normalized_citations_dict.get("score")),
    }


def _fetch_records_page(
    client: Client,
    domain_id: str,
    offset: int,
    size: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]] | None:
    candidate_params = [
        {"domain_id": domain_id, "offset": offset, "size": size},
        {"domain_id": domain_id, "offset": offset, "limit": size},
        {"id": domain_id, "offset": offset, "size": size},
        {"id": domain_id, "offset": offset, "limit": size},
        {"domainId": domain_id, "offset": offset, "size": size},
    ]

    for params in candidate_params:
        payload = _request_json(client=client, action=RECORDS_ACTION, params=params)
        if payload is None:
            continue
        records = _extract_records(payload)
        if records:
            return payload, records, params

    return None


def collect_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    with Client(
        timeout=REQUEST_TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT}
    ) as client:
        domains_payload = _request_json(client=client, action=DOMAINS_ACTION)

        domain_source = "api"
        if domains_payload is None:
            domain_source = "fallback"
            domains_payload = _load_fallback_json("domains.json")

        _write_json(RAW_DIR / "domains.json", domains_payload)

        root = _extract_domain_tree(domains_payload)
        major_subfields = _extract_major_subfields(root)

        print(f"Found {len(major_subfields)} major subfields.")

        domain_rows = _flatten_domains(
            node=root,
            parent_id=None,
            parent_name=None,
            level=0,
        )

        researcher_rows: list[dict[str, Any]] = []
        records_api_available = True
        for index, domain in enumerate(major_subfields, start=1):
            domain_id = domain["domain_id"]
            domain_name = domain["domain_name"]
            print(f"Collecting domain {index}/{len(major_subfields)}: {domain_name}...")

            seen_entity_ids: set[str] = set()
            page = 0
            offset = 0
            used_fallback = False

            while page < MAX_PAGES_PER_DOMAIN:
                if records_api_available:
                    page_result = _fetch_records_page(
                        client=client,
                        domain_id=domain_id,
                        offset=offset,
                        size=PAGE_SIZE,
                    )
                else:
                    page_result = None

                records_payload: dict[str, Any]
                records: list[dict[str, Any]]
                params_used: dict[str, Any]

                if page_result is None:
                    records_api_available = False
                    if page == 0:
                        print(
                            f"Warning: API records unavailable for {domain_name}. "
                            "Using fallback sample response."
                        )
                        records_payload = _load_fallback_json("records.json")
                        records = _extract_records(records_payload)
                        params_used = {"fallback": True}
                        used_fallback = True
                    else:
                        break
                else:
                    records_payload, records, params_used = page_result

                raw_file = RAW_DIR / f"records_{domain_id}_offset_{offset}.json"
                _write_json(raw_file, records_payload)

                if not records:
                    break

                before_count = len(seen_entity_ids)
                for record in records:
                    parsed = _parse_researcher_record(
                        record=record,
                        domain_id=domain_id,
                        domain_name=domain_name,
                    )
                    entity = parsed["entity_id"]
                    if (
                        isinstance(entity, str)
                        and entity
                        and entity not in seen_entity_ids
                    ):
                        seen_entity_ids.add(entity)
                        researcher_rows.append(parsed)

                new_entities = len(seen_entity_ids) - before_count
                print(
                    f"  page={page + 1}, offset={offset}, received={len(records)}, "
                    f"new={new_entities}, params={params_used}"
                )

                if used_fallback:
                    break
                if len(records) < PAGE_SIZE:
                    break
                if new_entities == 0:
                    break

                page += 1
                offset += PAGE_SIZE

        domains_df = pd.DataFrame(domain_rows)
        researchers_df = pd.DataFrame(researcher_rows)

        if researchers_df.empty:
            researchers_df = pd.DataFrame(columns=RESEARCHER_COLUMNS)
        else:
            researchers_df = researchers_df[RESEARCHER_COLUMNS]

        domains_df.to_parquet(DOMAINS_PATH, index=False)
        researchers_df.to_parquet(RESEARCHERS_PATH, index=False)

        metadata = {
            "domain_source": domain_source,
            "n_major_subfields": len(major_subfields),
            "n_domain_rows": len(domains_df),
            "n_researcher_rows": len(researchers_df),
            "columns": RESEARCHER_COLUMNS,
        }
        _write_json(RAW_DIR / "collection_metadata.json", metadata)

    return researchers_df, domains_df


def main() -> None:
    researchers_df, domains_df = collect_data()
    print("=" * 88)
    print("AI2000 collection complete")
    print(f"Researchers: {len(researchers_df)} rows -> {RESEARCHERS_PATH}")
    print(f"Domains:     {len(domains_df)} rows -> {DOMAINS_PATH}")
    print(f"Raw JSON dir: {RAW_DIR}")
    print("=" * 88)


if __name__ == "__main__":
    main()
