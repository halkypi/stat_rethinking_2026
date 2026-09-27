"""Keep numerical compilation and plotting caches local to the project."""
import os
from pathlib import Path


def configure_runtime():
    root = Path(os.environ.get("RETHINKING_CACHE_DIR", Path(__file__).resolve().parents[2] / ".cache"))
    root.mkdir(parents=True, exist_ok=True)
    flags = f"base_compiledir={root / 'pytensor'}"
    os.environ.setdefault("PYTENSOR_FLAGS", flags)
    os.environ.setdefault("MPLCONFIGDIR", str(root / "matplotlib"))
    os.environ.setdefault("NUMBA_CACHE_DIR", str(root / "numba"))
