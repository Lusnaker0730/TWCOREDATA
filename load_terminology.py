#!/usr/bin/env python3
"""
台灣 FHIR 術語資源載入器
Taiwan FHIR Terminology Resource Loader

Uploads CodeSystem and ValueSet JSON files from the package/ directory
into HAPI FHIR server via PUT requests (idempotent).
"""

import json
import os
import sys
import time
import logging
from pathlib import Path

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("terminology-loader")

# Large files (>10MB) are skipped by default to avoid HAPI memory issues.
# Set LOAD_LARGE_CODESYSTEMS=true to include them.
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10 MB

# Priority CodeSystems — loaded first regardless of size
PRIORITY_IDS = [
    # Small but essential — loaded first
    "medical-treatment-department-nhi-tw",
    "medical-consultation-department-nhi-tw",
    "medcation-atc-tw",
    "medication-frequency-nhi-tw",
    "medication-path-tw",
    "health-professional-tw",
    "careplan-category-tw",
    "category-code-tw",
    "organization-identifier-tw",
    "marital-status-tw",
    # Medium — loaded after small ones
    "medical-service-payment-tw",       # NHI procedure/order codes (~5MB)
    "nhi-medication-ch-herb-tw",        # ~3MB
    "medication-nhi-tw",                # ~13MB
    "medication-fda-tw",                # ~17MB
    # Note: icd-10-cm-2023-tw (45MB) and icd-10-pcs-2023-tw (37MB) are too
    # large for default loading; use LOAD_LARGE_CODESYSTEMS=true to include.
]


def wait_for_fhir(base_url: str, max_wait: int = 180) -> bool:
    """Wait until HAPI FHIR server is ready."""
    metadata_url = f"{base_url}/metadata"
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.get(metadata_url, timeout=30)
            if resp.status_code == 200:
                log.info("HAPI FHIR server is ready")
                return True
        except Exception:
            pass
        elapsed = int(time.time() - start)
        log.info("Waiting for HAPI FHIR server at %s ... (%ds)", base_url, elapsed)
        time.sleep(10)
    log.error("HAPI FHIR server not ready after %ds", max_wait)
    return False


def resource_exists(base_url: str, resource_type: str, resource_id: str) -> bool:
    """Check if a resource already exists on the server."""
    url = f"{base_url}/{resource_type}/{resource_id}"
    try:
        resp = requests.get(url, timeout=10, headers={"Accept": "application/fhir+json"})
        return resp.status_code == 200
    except Exception:
        return False


def upload_resource(base_url: str, file_path: Path, skip_existing: bool = True) -> bool:
    """Upload a single FHIR resource file via PUT."""
    try:
        raw = file_path.read_bytes()
        # Strip trailing null bytes (corrupted files from TWCore package)
        raw = raw.rstrip(b"\x00")
        text = raw.decode("utf-8", errors="replace")
        resource = json.loads(text)
    except (json.JSONDecodeError, IOError) as e:
        log.error("  Failed to read %s: %s", file_path.name, e)
        return False

    resource_type = resource.get("resourceType")
    resource_id = resource.get("id")

    if not resource_type or not resource_id:
        log.warning("  Skipping %s — missing resourceType or id", file_path.name)
        return False

    if skip_existing and resource_exists(base_url, resource_type, resource_id):
        log.info("  [SKIP] %s/%s already exists", resource_type, resource_id)
        return True

    url = f"{base_url}/{resource_type}/{resource_id}"
    headers = {
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json",
    }

    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    timeout = max(30, int(file_size_mb * 10))  # ~10s per MB, min 30s

    try:
        resp = requests.put(url, json=resource, headers=headers, timeout=timeout)
        if resp.status_code in (200, 201):
            log.info("  [OK]   %s/%s (%.1fMB)", resource_type, resource_id, file_size_mb)
            return True
        else:
            log.error(
                "  [FAIL] %s/%s — HTTP %d: %s",
                resource_type, resource_id, resp.status_code,
                resp.text[:200],
            )
            return False
    except requests.Timeout:
        log.error("  [TIMEOUT] %s/%s (%.1fMB)", resource_type, resource_id, file_size_mb)
        return False
    except Exception as e:
        log.error("  [ERROR] %s/%s — %s", resource_type, resource_id, e)
        return False


def load_all(base_url: str, package_dir: str = "package", skip_existing: bool = True) -> dict:
    """Load all CodeSystem and ValueSet files into HAPI FHIR."""
    pkg = Path(package_dir)
    if not pkg.is_dir():
        log.error("Package directory not found: %s", package_dir)
        return {"loaded": 0, "skipped": 0, "failed": 0}

    load_large = os.environ.get("LOAD_LARGE_CODESYSTEMS", "").lower() in ("true", "1", "yes")

    # Collect files
    cs_files = sorted(pkg.glob("CodeSystem-*.json"))
    vs_files = sorted(pkg.glob("ValueSet-*.json"))
    all_files = cs_files + vs_files

    # Separate into priority, normal, and large
    priority_files = []
    normal_files = []
    large_files = []

    for f in all_files:
        stem = f.stem  # e.g. "CodeSystem-medical-service-payment-tw"
        # Extract ID from filename (remove "CodeSystem-" or "ValueSet-" prefix)
        parts = stem.split("-", 1)
        resource_id = parts[1] if len(parts) > 1 else stem

        if resource_id in PRIORITY_IDS:
            priority_files.append(f)
        elif f.stat().st_size > LARGE_FILE_THRESHOLD:
            large_files.append(f)
        else:
            normal_files.append(f)

    # Sort priority files by PRIORITY_IDS order
    priority_order = {pid: i for i, pid in enumerate(PRIORITY_IDS)}
    priority_files.sort(key=lambda f: priority_order.get(f.stem.split("-", 1)[-1], 999))

    log.info("=" * 60)
    log.info("Taiwan FHIR Terminology Loader")
    log.info("=" * 60)
    log.info("Server:   %s", base_url)
    log.info("Package:  %s", pkg.resolve())
    log.info("Priority: %d files", len(priority_files))
    log.info("Normal:   %d files", len(normal_files))
    log.info("Large:    %d files (>%.0fMB) %s",
             len(large_files), LARGE_FILE_THRESHOLD / 1024 / 1024,
             "[WILL LOAD]" if load_large else "[SKIPPED — set LOAD_LARGE_CODESYSTEMS=true to include]")
    log.info("-" * 60)

    stats = {"loaded": 0, "skipped": 0, "failed": 0}

    # Upload in order: priority → normal → large (if enabled)
    upload_list = priority_files + normal_files
    if load_large:
        upload_list += large_files

    consecutive_fails = 0
    for f in upload_list:
        result = upload_resource(base_url, f, skip_existing=skip_existing)
        if result:
            stats["loaded"] += 1
            consecutive_fails = 0
        else:
            stats["failed"] += 1
            consecutive_fails += 1
            # Give HAPI time to recover after failures (GC, etc.)
            if consecutive_fails >= 2:
                pause = min(30, consecutive_fails * 10)
                log.info("  Pausing %ds to let HAPI recover...", pause)
                time.sleep(pause)

    if not load_large and large_files:
        stats["skipped"] += len(large_files)
        for f in large_files:
            size_mb = f.stat().st_size / (1024 * 1024)
            log.info("  [SKIP] %s (%.1fMB — too large)", f.name, size_mb)

    log.info("-" * 60)
    log.info("Done: %d loaded, %d skipped, %d failed",
             stats["loaded"], stats["skipped"], stats["failed"])
    log.info("=" * 60)
    return stats


def main():
    fhir_url = os.environ.get("FHIR_SERVER_URL", "http://hapi-fhir:8080/fhir")
    package_dir = os.environ.get("TERMINOLOGY_PACKAGE_DIR", "package")

    log.info("Starting terminology loading to %s", fhir_url)

    if not wait_for_fhir(fhir_url):
        log.error("Aborting: FHIR server not available")
        sys.exit(1)

    stats = load_all(fhir_url, package_dir)

    if stats["failed"] > 0:
        log.warning("Some resources failed to load — check logs above")


if __name__ == "__main__":
    main()
