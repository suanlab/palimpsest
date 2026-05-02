#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/home/suanlab/Projects/research/data/raw/download_logs"
NAS_BASE="/mnt/nas/research_backup/raw"
RAW_BASE="/home/suanlab/Projects/research/data/raw"

echo "[$(date)] Waiting for openalex rsync (PID 201531) to finish..."
while kill -0 201531 2>/dev/null; do
    sleep 60
done
echo "[$(date)] openalex rsync finished."

echo "[$(date)] Starting crossref rsync (184GB)..."
rsync -av --remove-source-files \
    "${RAW_BASE}/crossref/" \
    "${NAS_BASE}/crossref/" \
    > "${LOG_DIR}/rsync_crossref.log" 2>&1
echo "[$(date)] crossref rsync finished."

echo "[$(date)] Starting pubmed rsync (51GB)..."
rsync -av --remove-source-files \
    "${RAW_BASE}/pubmed/" \
    "${NAS_BASE}/pubmed/" \
    > "${LOG_DIR}/rsync_pubmed.log" 2>&1
echo "[$(date)] pubmed rsync finished."

echo "[$(date)] All rsyncs complete. Disk freed: crossref + pubmed (~235GB)"
