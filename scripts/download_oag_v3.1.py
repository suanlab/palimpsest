#!/usr/bin/env python3
"""
Download script for Open Academic Graph (OAG) v3.1 dataset from AMiner.

Dataset: ~130M papers with titles, abstracts, authors, venues, years, keywords, DOIs, and citations
Files: publication_1.zip through publication_14.zip (14 files total)

Usage:
    uv run python scripts/download_oag_v3.1.py --help
    uv run python scripts/download_oag_v3.1.py --sample          # Download sample files
    uv run python scripts/download_oag_v3.1.py --files 1,2,3     # Download specific files
    uv run python scripts/download_oag_v3.1.py --all             # Download all 14 files
"""

import argparse
import asyncio
from pathlib import Path

import httpx

# Configuration
BASE_URL = "https://aminer.cn/download/oag"
PUBLICATION_FILES = [f"publication_{i}.zip" for i in range(1, 15)]
SAMPLE_FILES = [
    "sample.zip",
    "oag_sample.zip",
    "oag_v3.1_sample.zip",
    "publication_sample.zip",
]

# Default download directory
DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "oag_v3.1"


async def download_file(
    url: str,
    output_path: Path,
    client: httpx.AsyncClient,
    chunk_size: int = 8192,
) -> bool:
    """Download a single file with progress reporting.

    Args:
        url: Full URL to download
        output_path: Where to save the file
        client: httpx async client
        chunk_size: Size of chunks to download

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create parent directory
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file already exists
        if output_path.exists():
            print(f"  ⊘ {output_path.name} (already exists, skipping)")
            return True

        # Start download
        async with client.stream("GET", url, timeout=300) as response:
            if response.status_code != 200:
                print(f"  ✗ {output_path.name} (HTTP {response.status_code})")
                return False

            # Get total size if available
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            # Download with progress
            with open(output_path, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Print progress
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(
                            f"  ↓ {output_path.name} ({percent:.1f}%)",
                            end="\r",
                        )

            print(f"  ✓ {output_path.name}")
            return True

    except Exception as e:
        print(f"  ✗ {output_path.name} (Error: {e})")
        return False


async def verify_file_exists(url: str, client: httpx.AsyncClient) -> bool:
    """Check if a file exists at the given URL.

    Args:
        url: URL to check
        client: httpx async client

    Returns:
        True if file exists (HTTP 200), False otherwise
    """
    try:
        response = await client.head(url, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


async def main() -> None:
    """Main download orchestration."""
    parser = argparse.ArgumentParser(
        description="Download OAG v3.1 dataset from AMiner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all sample files (for testing)
  python scripts/download_oag_v3.1.py --sample

  # Download specific publication files
  python scripts/download_oag_v3.1.py --files 1,2,3

  # Download all 14 publication files
  python scripts/download_oag_v3.1.py --all

  # Download to custom directory
  python scripts/download_oag_v3.1.py --all --output /path/to/data
        """,
    )

    parser.add_argument(
        "--sample",
        action="store_true",
        help="Download sample files (for testing)",
    )
    parser.add_argument(
        "--files",
        type=str,
        help="Comma-separated list of file numbers (e.g., 1,2,3)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all 14 publication files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_DOWNLOAD_DIR,
        help=f"Output directory (default: {DEFAULT_DOWNLOAD_DIR})",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify file availability without downloading",
    )

    args = parser.parse_args()

    # Determine which files to download
    files_to_download = []

    if args.sample:
        files_to_download = SAMPLE_FILES
    elif args.files:
        try:
            file_numbers = [int(x.strip()) for x in args.files.split(",")]
            files_to_download = [
                f"publication_{n}.zip" for n in file_numbers if 1 <= n <= 14
            ]
            if not files_to_download:
                print("Error: Invalid file numbers. Use 1-14.")
                return
        except ValueError:
            print("Error: Invalid file numbers format. Use comma-separated numbers.")
            return
    elif args.all:
        files_to_download = PUBLICATION_FILES
    else:
        parser.print_help()
        return

    # Create output directory
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 70}")
    print("OAG v3.1 Dataset Downloader")
    print(f"{'=' * 70}")
    print(f"Output directory: {output_dir}")
    print(f"Files to download: {len(files_to_download)}")
    print(f"{'=' * 70}\n")

    # Create async client
    async with httpx.AsyncClient(follow_redirects=True) as client:
        if args.verify:
            # Verify file availability
            print("Verifying file availability...\n")
            for filename in files_to_download:
                url = f"{BASE_URL}/{filename}"
                exists = await verify_file_exists(url, client)
                status = "✓" if exists else "✗"
                print(f"  {status} {filename}")
            return

        # Download files
        print("Starting downloads...\n")
        successful = 0
        failed = 0

        for filename in files_to_download:
            url = f"{BASE_URL}/{filename}"
            output_path = output_dir / filename
            success = await download_file(url, output_path, client)
            if success:
                successful += 1
            else:
                failed += 1

        # Summary
        print(f"\n{'=' * 70}")
        print("Download Summary")
        print(f"{'=' * 70}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total: {successful + failed}")
        print(f"{'=' * 70}\n")

        if failed == 0:
            print("✓ All files downloaded successfully!")
        else:
            print(f"⚠ {failed} file(s) failed to download.")


if __name__ == "__main__":
    asyncio.run(main())
