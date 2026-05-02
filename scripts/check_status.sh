#!/bin/bash
# Quick status check for all running processes and data

echo "=== DISK ==="
df -h /home/suanlab/Projects/research/ | tail -1

echo ""
echo "=== DOWNLOADS ==="
echo -n "OpenAlex: "; du -sh /home/suanlab/Projects/research/data/raw/openalex/works/ 2>/dev/null | cut -f1
echo -n "Crossref: "; du -sh /home/suanlab/Projects/research/data/raw/crossref/ 2>/dev/null | cut -f1
echo -n "PubMed:   "; du -sh /home/suanlab/Projects/research/data/raw/pubmed/ 2>/dev/null | cut -f1

echo ""
echo "=== ETL PROGRESS ==="
python3 -c "
import json
with open('/home/suanlab/Projects/research/data/processed/graph/etl_openalex_snapshot_progress.json') as f:
    data = json.load(f)
dirs = data.get('processed_directories', [])
totals = data.get('totals', {})
print(f'Dirs: {len(dirs)} / 248')
print(f'Works:     {totals.get(\"works\", 0):>12,}')
print(f'Papers:    {totals.get(\"papers\", 0):>12,}')
print(f'Citations: {totals.get(\"citations\", 0):>12,}')
print(f'Authors:   {totals.get(\"authorships\", 0):>12,}')
print(f'CoAuth:    {totals.get(\"coauthorship_edges\", 0):>12,}')
print(f'Warnings:  {totals.get(\"warnings\", 0):>12,}')
" 2>/dev/null || echo "ETL not started"

echo ""
echo "=== STAGING ==="
du -sh /home/suanlab/Projects/research/data/processed/graph/_staging/*/ 2>/dev/null || echo "No staging"

echo ""
echo "=== NEO4J ==="
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | grep neo4j || echo "Not running"

echo ""
echo "=== PROCESSES ==="
ps aux | grep -E "(aws s3|aria2|rsync|etl_openalex|import_to_neo4j|uvicorn)" | grep -v grep | awk '{printf "%-8s %s %s\n", $1, $11, $12}'
