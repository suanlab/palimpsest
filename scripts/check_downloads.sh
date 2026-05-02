#!/bin/bash
echo "=== Dataset Download Status ($(date)) ==="
echo ""

echo "1. DBLP XML (COMPLETED)"
ls -lh /home/suanlab/Projects/research/data/raw/dblp/dblp.xml.gz 2>/dev/null | awk '{print "   Size:", $5}'
echo ""

echo "2. Retraction Watch (COMPLETED)"
wc -l /home/suanlab/Projects/research/data/raw/retraction_watch/retraction-watch-data/retraction_watch.csv 2>/dev/null | awk '{print "   Records:", $1}'
echo ""

echo "3. arXiv OAI-PMH"
if pgrep -f "harvest_arxiv" > /dev/null 2>&1; then
    echo "   Status: RUNNING"
else
    echo "   Status: STOPPED"
fi
for f in /home/suanlab/Projects/research/data/raw/arxiv/*_all.jsonl; do
    [ -f "$f" ] && echo "   $(basename "$f"): $(wc -l < "$f") records"
done
for f in /home/suanlab/Projects/research/data/raw/arxiv/*_ai.jsonl; do
    [ -f "$f" ] && echo "   $(basename "$f"): $(wc -l < "$f") records"
done
echo ""

echo "4. OpenAlex Snapshot"
if pgrep -f "aws.*s3.*openalex" > /dev/null 2>&1; then
    echo "   Status: RUNNING"
else
    echo "   Status: STOPPED"
fi
echo "   Size: $(du -sh /home/suanlab/Projects/research/data/raw/openalex/ 2>/dev/null | cut -f1)"
echo "   Files: $(find /home/suanlab/Projects/research/data/raw/openalex/ -name '*.gz' 2>/dev/null | wc -l)"
echo ""

echo "5. PubMed Baseline"
if pgrep -f "rsync.*pubmed" > /dev/null 2>&1; then
    echo "   Status: RUNNING"
else
    echo "   Status: STOPPED"
fi
echo "   Size: $(du -sh /home/suanlab/Projects/research/data/raw/pubmed/ 2>/dev/null | cut -f1)"
echo "   Files: $(ls /home/suanlab/Projects/research/data/raw/pubmed/*.gz 2>/dev/null | wc -l)"
echo ""

echo "6. Crossref: PENDING (requires torrent client)"
echo ""
echo "Disk free: $(df -h /home/suanlab/Projects/research/ | tail -1 | awk '{print $4}')"
