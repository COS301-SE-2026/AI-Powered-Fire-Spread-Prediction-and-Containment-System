# Versioned model artifact store (How trained models move between GPUs and backend)

# Housekeeping for the geo-separated machines:
# 1. Every training run writes NEW immutable version dir (NEVER overwrite)
# 2. Promotion to production = updating latest pointer (1 atomic write)
# 3. Backend loads by pinned version name or latest (never by whichever file is newest on disk)

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path


def store_root() -> Path:
    root = os.environ.get("FIRE_ARTIFACT_STORE", "./artifact_store")
    p = Path(root)
    p.mkdir(parents=True, exist_ok=True)
    return p


# Provenance logging (logs what hardware was used to run specific job)
def gpu_name() -> str:
    """Best effort GPU identification for provenance logging"""

    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip().splitlines()[0]
    except Exception:
        pass

    return "none/cpu"


def new_version_name() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    host = platform.node().split(".")[0] or "unknown"
    salt = uuid.uuid4().hex[:6]
    return f"v{ts}-{salt}_{host}"


def publish(
    model_family: str, model_path: str | Path, metadata: dict, promote: bool = False
) -> str:
    """Copy trained model + metadata to a new immutable version dir.
    Returns version name. If promote=True, also updates latest
    """
    version = new_version_name()
    vdir = store_root() / model_family / version
    vdir.mkdir(parents=True, exist_ok=False)

    # shutil.copy2: preserves og file's metadata
    shutil.copy2(
        model_path, vdir / "model.json"
    )  # Copies newly trained model file from temporary training location to new permanent version folder called model.json

    # Ensures experiment fully reproducible. Injects system provenance date into the metadata using ** (** = dictionary unpacking operator)
    metadata = {
        **metadata,
        "version": version,
        "hostname": platform.node(),
        "gpu": gpu_name(),
        "published_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(vdir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    if promote:  # If True, update symlink/pointer LATEST to point to brand-new version
        promote_version(model_family, version)
    return version


def promote_version(
    model_family: str, version: str
) -> (
    None
):  # Actually "promptes" a specific model version to be the active/LATEST version
    """Point latest at a version"""  # (Atomic single-file write)

    family_dir = store_root() / model_family
    if not (family_dir / version).is_dir():
        raise FileNotFoundError(f"No such version to promote: {version}")

    tmp = family_dir / "LATEST.tmp"
    tmp.write_text(version)
    tmp.replace(family_dir / "LATEST")


# Retrieval mechanism when app needs to load model
def resolve(model_family: str, version: str = "LATEST") -> Path:
    """Return version directory for a family resolving LATEST"""
    family_dir = store_root() / model_family
    if version == "LATEST":
        pointer = family_dir / "LATEST"
        if not pointer.exists():
            raise FileNotFoundError(
                "No LATEST pointer for '{model_family}' in {family_dir}. Train and publish a model first or pin a version"
            )
        version = pointer.read_text().strip()
    vdir = family_dir / version
    if not vdir.is_dir():
        raise FileNotFoundError(f"Artifact version not found: {vdir}")
    return vdir


def list_versions(model_family: str) -> list[str]:
    family_dir = store_root() / model_family
    if not family_dir.is_dir():
        return []
    return sorted(
        d.name for d in family_dir.iterdir() if d.is_dir() and d.name.startswith("v")
    )
