"""Export the nine coefficient-bearing data files without changing sources."""

import argparse
import gzip
import hashlib
import json
import shutil
from pathlib import Path


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    records = []
    for state_file in sorted((args.project / "workspace").glob("*/signac_statepoint.json")):
        state = json.loads(state_file.read_text())
        n, replica = state.get("pva_chain_length"), state.get("replica")
        if n not in (17, 21, 25) or replica not in (1, 2, 3):
            continue
        source = state_file.parent / "data.anisocompression_lammps"
        headers = set()
        atoms = None
        with source.open() as handle:
            for line in handle:
                content = line.split("#", 1)[0].strip()
                headers.add(content) if content.endswith("Coeffs") or content == "Masses" else None
                if content.endswith(" atoms"):
                    atoms = int(content.split()[0])
        required = {"Masses", "Pair Coeffs", "Bond Coeffs", "Angle Coeffs", "Dihedral Coeffs"}
        if not required <= headers or atoms != {17: 371250, 21: 347550, 25: 348300}[n]:
            raise ValueError(f"Unexpected data-file contents: {source}")
        destination = root / f"configurations/n{n}/replica{replica}/data.anisocompression_lammps.gz"
        destination.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as incoming, destination.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as outgoing:
                shutil.copyfileobj(incoming, outgoing)
        source_hash = digest(source)
        checksum = hashlib.sha256()
        with gzip.open(destination, "rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                checksum.update(block)
        if checksum.hexdigest() != source_hash or destination.stat().st_size >= 100 * 1024**2:
            raise ValueError(f"Integrity or size check failed: {destination}")
        records.append(dict(n=n, replica=replica, job_id=state_file.parent.name,
                            statepoint=state, atoms=atoms,
                            path=destination.relative_to(root).as_posix(),
                            source_bytes=source.stat().st_size,
                            compressed_bytes=destination.stat().st_size,
                            source_sha256=source_hash, compressed_sha256=digest(destination)))
        print(f"Verified n={n}, replica={replica}: {destination.stat().st_size} bytes", flush=True)
    if {(r["n"], r["replica"]) for r in records} != {(n, r) for n in (17, 21, 25) for r in (1, 2, 3)} or len(records) != 9:
        raise ValueError("Expected exactly nine unique production replicas")
    records.sort(key=lambda r: (r["n"], r["replica"]))
    (root / "manifest.json").write_text(json.dumps(records, indent=2) + "\n")
    (root / "SHA256SUMS").write_text("".join(f'{r["compressed_sha256"]}  {r["path"]}\n' for r in records))


if __name__ == "__main__":
    main()
