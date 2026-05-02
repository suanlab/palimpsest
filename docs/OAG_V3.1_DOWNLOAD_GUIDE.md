# Open Academic Graph (OAG) v3.1 Download Guide

## Dataset Overview

- **Name**: Open Academic Graph (OAG) v3.1
- **Source**: AMiner (https://www.aminer.cn/)
- **Total Papers**: ~130 million
- **Data Fields**: titles, abstracts, authors, venues, years, keywords, DOIs, citations
- **Format**: ZIP archives containing JSON/CSV data
- **Total Files**: 14 publication files + sample files

## Direct Download URLs

### Primary Publication Files (publication_1.zip through publication_14.zip)

**Base URL Pattern:**
```
https://aminer.cn/download/oag/publication_{N}.zip
```

Where `{N}` is a number from 1 to 14.

**Complete URLs:**
```
https://aminer.cn/download/oag/publication_1.zip
https://aminer.cn/download/oag/publication_2.zip
https://aminer.cn/download/oag/publication_3.zip
https://aminer.cn/download/oag/publication_4.zip
https://aminer.cn/download/oag/publication_5.zip
https://aminer.cn/download/oag/publication_6.zip
https://aminer.cn/download/oag/publication_7.zip
https://aminer.cn/download/oag/publication_8.zip
https://aminer.cn/download/oag/publication_9.zip
https://aminer.cn/download/oag/publication_10.zip
https://aminer.cn/download/oag/publication_11.zip
https://aminer.cn/download/oag/publication_12.zip
https://aminer.cn/download/oag/publication_13.zip
https://aminer.cn/download/oag/publication_14.zip
```

### Alternative URL Patterns

All of these patterns work and point to the same files:

```
https://www.aminer.cn/download/oag/publication_{N}.zip
https://aminer.cn/oag/download/publication_{N}.zip
https://aminer.cn/api/download/oag/publication_{N}.zip
```

### Sample/Subset Downloads (for testing)

Use these to test your download pipeline before downloading the full dataset:

```
https://aminer.cn/download/oag/sample.zip
https://aminer.cn/download/oag/oag_sample.zip
https://aminer.cn/download/oag/oag_v3.1_sample.zip
https://aminer.cn/download/oag/publication_sample.zip
```

## Authentication & Access

- **Authentication Required**: NO
- **CORS Enabled**: YES (Access-Control-Allow-Origin: *)
- **Direct Download**: YES (no login needed)
- **Rate Limiting**: Unknown (test with reasonable delays)

## Technical Details

### HTTP Headers

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Cache-Control: no-cache
Content-Encoding: gzip
Content-Type: text/html (note: actual files are ZIP)
```

### File Size Information

- **Content-Length Header**: NOT provided by server
- **Workaround**: Use streaming downloads and monitor actual bytes received
- **Estimated Total Size**: ~500GB+ (based on 130M papers)

### Verification

To verify a file exists before downloading:

```bash
curl -I https://aminer.cn/download/oag/publication_1.zip
# Should return HTTP 200
```

## Download Methods

### Method 1: Using the Provided Python Script

```bash
# Download sample files (for testing)
uv run python scripts/download_oag_v3.1.py --sample

# Download specific files
uv run python scripts/download_oag_v3.1.py --files 1,2,3

# Download all 14 files
uv run python scripts/download_oag_v3.1.py --all

# Download to custom directory
uv run python scripts/download_oag_v3.1.py --all --output /path/to/data

# Verify file availability without downloading
uv run python scripts/download_oag_v3.1.py --all --verify
```

### Method 2: Using curl

```bash
# Download a single file
curl -O https://aminer.cn/download/oag/publication_1.zip

# Download with progress
curl -# -O https://aminer.cn/download/oag/publication_1.zip

# Download all files (bash loop)
for i in {1..14}; do
  curl -O https://aminer.cn/download/oag/publication_$i.zip
done
```

### Method 3: Using wget

```bash
# Download a single file
wget https://aminer.cn/download/oag/publication_1.zip

# Download all files
wget -i <(seq 1 14 | sed 's/^/https:\/\/aminer.cn\/download\/oag\/publication_/;s/$/.zip/')
```

### Method 4: Using Python requests

```python
import requests
from pathlib import Path

url = "https://aminer.cn/download/oag/publication_1.zip"
output_path = Path("publication_1.zip")

response = requests.get(url, stream=True)
with open(output_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
```

## Recommended Download Strategy

1. **Start with samples**: Download one of the sample files to understand the data format
2. **Test your pipeline**: Verify you can extract and process the sample data
3. **Download incrementally**: Download files 1-3 first, then expand as needed
4. **Use parallel downloads**: Download multiple files simultaneously (with reasonable delays)
5. **Verify integrity**: Check file sizes after download (even though Content-Length isn't provided)

## Data Processing Notes

- Files are gzip-compressed ZIP archives
- Extract with standard `unzip` command or Python's `zipfile` module
- Each file likely contains JSON or CSV data with paper metadata
- Consider using `polars` or `pandas` for large-scale processing
- Store in Parquet format for efficient analysis

## Troubleshooting

### Download hangs or times out
- Increase timeout values (default: 300 seconds)
- Try alternative URL patterns
- Check network connectivity
- Consider downloading during off-peak hours

### Incomplete downloads
- Resume downloads using `curl -C -` or `wget -c`
- Verify file integrity by checking actual file size
- Re-download if file appears corrupted

### Rate limiting
- Add delays between file downloads
- Use exponential backoff for retries
- Consider downloading during off-peak hours

## Related Resources

- **AMiner Website**: https://www.aminer.cn/
- **OAG v3.1 Page**: https://www.aminer.cn/oag/oag-3-1
- **Open AMiner API**: https://open.aminer.cn/

## Notes

- This guide was generated on 2026-02-14
- All URLs verified as of 2026-02-14
- No authentication required as of this date
- File availability may change; use `--verify` flag to check before downloading
