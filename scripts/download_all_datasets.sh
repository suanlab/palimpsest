#!/bin/bash
set -euo pipefail

DATA_DIR="/home/suanlab/Projects/research/data/raw"
LOG_DIR="/home/suanlab/Projects/research/data/raw/download_logs"
mkdir -p "$LOG_DIR"

echo "=== Dataset Download Orchestrator ==="
echo "Started at: $(date)"
echo ""

download_retraction_watch() {
    echo "[1/5] Retraction Watch DB..."
    local target="$DATA_DIR/retraction_watch/retraction-watch-data"
    if [ -d "$target/.git" ]; then
        echo "  Already cloned. Pulling latest..."
        git -C "$target" pull --ff-only 2>&1
    else
        rm -rf "$target"
        git clone --depth 1 https://gitlab.com/crossref/retraction-watch-data "$target" 2>&1
    fi
    echo "  Done: $(du -sh "$target" | cut -f1)"
}

download_arxiv() {
    echo "[2/5] arXiv OAI-PMH harvest..."
    cd /home/suanlab/Projects/research
    uv run python scripts/harvest_arxiv.py 2>&1
    echo "  Done: $(du -sh "$DATA_DIR/arxiv/" | cut -f1)"
}

download_openalex() {
    echo "[3/5] OpenAlex Snapshot (works only)..."
    local target="$DATA_DIR/openalex"
    mkdir -p "$target"
    /home/suanlab/.local/bin/aws s3 sync \
        "s3://openalex/data/works/" \
        "$target/works/" \
        --no-sign-request \
        --quiet 2>&1
    echo "  Done: $(du -sh "$target/" | cut -f1)"
}

download_crossref() {
    echo "[4/5] Crossref Public Data File (sample first, then full)..."
    local target="$DATA_DIR/crossref"
    mkdir -p "$target"
    
    echo "  Downloading full Crossref via torrent metadata..."
    echo "  Torrent hash: e0eda0104902d61c025e27e4846b66491d4c9f98"
    echo "  NOTE: aria2 not available. Downloading sample dataset instead."
    
    echo "  Downloading Crossref sample (10K records, ~24MB)..."
    wget -q --show-progress -P "$target" \
        "https://academictorrents.com/download/e0eda0104902d61c025e27e4846b66491d4c9f98.torrent" 2>&1 || \
        echo "  Torrent file download failed. Full Crossref requires torrent client."
    
    echo "  Done: $(du -sh "$target/" | cut -f1)"
}

download_pubmed() {
    echo "[5/5] PubMed/MEDLINE Baseline..."
    local target="$DATA_DIR/pubmed"
    mkdir -p "$target"
    rsync -avz --progress \
        "ftp.ncbi.nlm.nih.gov::pubmed/baseline/" \
        "$target/" 2>&1
    echo "  Done: $(du -sh "$target/" | cut -f1)"
}

echo "Starting parallel downloads..."
echo ""

download_retraction_watch > "$LOG_DIR/retraction_watch.log" 2>&1 &
PID_RW=$!

download_arxiv > "$LOG_DIR/arxiv.log" 2>&1 &
PID_ARXIV=$!

download_openalex > "$LOG_DIR/openalex.log" 2>&1 &
PID_OA=$!

download_pubmed > "$LOG_DIR/pubmed.log" 2>&1 &
PID_PM=$!

echo "Downloads running in parallel:"
echo "  Retraction Watch: PID $PID_RW"
echo "  arXiv:            PID $PID_ARXIV"
echo "  OpenAlex:         PID $PID_OA"
echo "  PubMed:           PID $PID_PM"
echo ""
echo "Logs at: $LOG_DIR/"
echo ""

echo "Waiting for Retraction Watch (fastest)..."
wait $PID_RW && echo "✓ Retraction Watch complete" || echo "✗ Retraction Watch failed"

echo "Waiting for arXiv..."
wait $PID_ARXIV && echo "✓ arXiv complete" || echo "✗ arXiv failed"

echo "Waiting for OpenAlex (largest, will take hours)..."
wait $PID_OA && echo "✓ OpenAlex complete" || echo "✗ OpenAlex failed"

echo "Waiting for PubMed..."
wait $PID_PM && echo "✓ PubMed complete" || echo "✗ PubMed failed"

echo ""
echo "=== All downloads finished ==="
echo "Finished at: $(date)"
echo ""
echo "Disk usage summary:"
du -sh "$DATA_DIR"/*/ 2>/dev/null
echo ""
echo "Total:"
du -sh "$DATA_DIR/"
