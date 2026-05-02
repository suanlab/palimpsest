#!/bin/bash
set -euo pipefail

# Neo4j bulk import script for 360M+ papers from per-directory parquet files.
# Prerequisites: prepare_neo4j_import.py must have completed successfully.
#
# Directory structure expected:
#   data/processed/neo4j_import/
#     papers/          248 parquet files (one per updated_date dir)
#     cites/           248 parquet files
#     authored/        248 parquet files
#     belongs_to/      248 parquet files
#     author_nodes.parquet   (deduplicated)
#     field_nodes.parquet     (deduplicated)

IMPORT_DIR="/home/suan/Projects/research/data/processed/neo4j_import"
NEO4J_IMPORT="/home/suan/Projects/research/data/neo4j/import"
NEO4J_DATA="/home/suan/Projects/research/data/neo4j/data"

echo "=== Step 1: Symlink import directories ==="
mkdir -p "$NEO4J_IMPORT"

# Symlink subdirectories (papers/, cites/, authored/, belongs_to/)
for sub in papers cites authored belongs_to; do
    if [ -d "$IMPORT_DIR/$sub" ]; then
        ln -sfn "$IMPORT_DIR/$sub" "$NEO4J_IMPORT/$sub"
        count=$(ls "$IMPORT_DIR/$sub"/*.parquet 2>/dev/null | wc -l)
        echo "  $sub: $count parquet files"
    else
        echo "  WARNING: $IMPORT_DIR/$sub does not exist!"
    fi
done

# Symlink single-file node tables
for f in author_nodes.parquet field_nodes.parquet; do
    if [ -f "$IMPORT_DIR/$f" ]; then
        ln -sf "$IMPORT_DIR/$f" "$NEO4J_IMPORT/$f"
        echo "  $f: linked"
    else
        echo "  WARNING: $IMPORT_DIR/$f does not exist!"
    fi
done

echo ""
echo "=== Step 2: Stop Neo4j ==="
docker stop research-neo4j 2>/dev/null || true
sleep 5
echo "Neo4j stopped"

echo ""
echo "=== Step 3: Clear existing database ==="
rm -rf "$NEO4J_DATA/databases/neo4j"
rm -rf "$NEO4J_DATA/transactions/neo4j"
echo "Database cleared"

echo ""
echo "=== Step 4: Run neo4j-admin import ==="
echo "Starting import at $(date)"
time docker run --rm \
    -v "$NEO4J_DATA:/data" \
    -v "$NEO4J_IMPORT:/var/lib/neo4j/import" \
    neo4j:5-community \
    neo4j-admin database import full neo4j \
    --input-type=parquet \
    --overwrite-destination=true \
    --skip-bad-relationships=true \
    --skip-duplicate-nodes=true \
    --bad-tolerance=1000000 \
    --high-parallel-io=on \
    --threads=$(nproc) \
    --max-off-heap-memory=32g \
    --nodes=Paper="/var/lib/neo4j/import/papers/.*" \
    --nodes=Author=/var/lib/neo4j/import/author_nodes.parquet \
    --nodes=Field=/var/lib/neo4j/import/field_nodes.parquet \
    --relationships=CITES="/var/lib/neo4j/import/cites/.*" \
    --relationships=AUTHORED="/var/lib/neo4j/import/authored/.*" \
    --relationships=BELONGS_TO="/var/lib/neo4j/import/belongs_to/.*"

echo ""
echo "Import finished at $(date)"

echo ""
echo "=== Step 5: Restart Neo4j ==="
docker start research-neo4j
echo "Neo4j started. Waiting 60s for startup..."
sleep 60

echo ""
echo "=== Step 6: Create indexes ==="
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.openalex_id IS UNIQUE;"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "CREATE INDEX paper_doi IF NOT EXISTS FOR (p:Paper) ON (p.doi);"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "CREATE INDEX paper_year IF NOT EXISTS FOR (p:Paper) ON (p.year);"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "CREATE INDEX paper_retracted IF NOT EXISTS FOR (p:Paper) ON (p.is_retracted);"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "CREATE INDEX paper_title IF NOT EXISTS FOR (p:Paper) ON (p.title);"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "CREATE CONSTRAINT author_id IF NOT EXISTS FOR (a:Author) REQUIRE a.author_id IS UNIQUE;"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "CREATE INDEX author_name IF NOT EXISTS FOR (a:Author) ON (a.author_name);"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "CREATE CONSTRAINT field_id IF NOT EXISTS FOR (f:Field) REQUIRE f.field_id IS UNIQUE;"
echo "Indexes created. Waiting 30s for index population..."
sleep 30

echo ""
echo "=== Step 7: Verify ==="
echo "--- Node counts ---"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC;"
echo ""
echo "--- Relationship counts ---"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC;"
echo ""
echo "--- Sample Paper ---"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "MATCH (p:Paper) RETURN p.openalex_id, p.title, p.year, p.cited_by_count LIMIT 3;"
echo ""
echo "--- Sample Citation ---"
docker exec research-neo4j cypher-shell -u neo4j -p research2026 \
    "MATCH (a:Paper)-[:CITES]->(b:Paper) RETURN a.openalex_id, b.openalex_id LIMIT 3;"

echo ""
echo "=== DONE ==="
echo "Completed at $(date)"
