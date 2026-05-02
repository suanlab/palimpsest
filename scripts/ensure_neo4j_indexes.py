#!/usr/bin/env python3
"""Ensure all Neo4j indexes required by the SciGraph API exist.

Run after bulk import or on a fresh deployment. Indexes are created with
``IF NOT EXISTS`` so the script is idempotent. Index population is
asynchronous on Neo4j 5; the script optionally waits for ONLINE status.

Critical indexes:
  - Paper.openalex_id  (used by every /api/graph endpoint to look up
    a focal paper; without this, queries trigger a full 479M-node scan
    and time out at 120s with HTTP 502)
  - Author.author_id, Author.openalex_id
  - Field.field_id

Usage:
    uv run python scripts/ensure_neo4j_indexes.py [--wait]
"""
from __future__ import annotations

import argparse
import sys
import time

from neo4j import GraphDatabase

from palimpsest.utils.config import settings

INDEX_DEFS = [
    ("paper_openalex_id", "Paper", "openalex_id"),
    ("author_author_id", "Author", "author_id"),
    ("author_openalex_id", "Author", "openalex_id"),
    ("field_field_id", "Field", "field_id"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Block until every index reaches ONLINE state.",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help="Seconds between status checks when --wait is set.",
    )
    args = parser.parse_args()

    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )

    try:
        driver.verify_connectivity()
    except Exception as exc:
        print(f"ERROR: cannot connect to Neo4j at {settings.neo4j_uri}: {exc}",
              file=sys.stderr)
        return 1

    with driver.session() as session:
        print("Ensuring indexes exist...")
        for name, label, prop in INDEX_DEFS:
            cypher = (
                f"CREATE INDEX {name} IF NOT EXISTS "
                f"FOR (n:{label}) ON (n.{prop})"
            )
            session.run(cypher).consume()
            print(f"  - {name} on :{label}({prop})")

        if not args.wait:
            print("\nIndexes issued. Population is asynchronous.")
            print("Run with --wait to block until ONLINE.")
            return 0

        names = [d[0] for d in INDEX_DEFS]
        names_quoted = ", ".join(f"'{n}'" for n in names)
        print(f"\nWaiting for indexes to reach ONLINE state...")
        last_log = 0.0
        while True:
            status_cypher = (
                f"SHOW INDEXES YIELD name, state, populationPercent "
                f"WHERE name IN [{names_quoted}]"
            )
            rows = list(session.run(status_cypher))
            total_pct = sum(r["populationPercent"] for r in rows)
            avg_pct = total_pct / len(rows) if rows else 0.0
            states = {r["name"]: (r["state"], r["populationPercent"]) for r in rows}
            all_online = all(s[0] == "ONLINE" for s in states.values())

            now = time.time()
            if all_online or now - last_log >= 30:
                print(f"  [{time.strftime('%H:%M:%S')}] avg={avg_pct:.1f}% "
                      + " ".join(
                          f"{n}={s[0]}({s[1]:.0f}%)" for n, s in states.items()
                      ))
                last_log = now

            if all_online:
                print("\nAll indexes ONLINE.")
                return 0
            time.sleep(args.poll_interval)


if __name__ == "__main__":
    sys.exit(main())
