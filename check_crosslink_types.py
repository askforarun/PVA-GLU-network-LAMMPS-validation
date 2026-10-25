"""Verify the documented crosslink mapping in all nine compressed datasets."""

import gzip
import json
from collections import Counter
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    for record in json.loads((root / "manifest.json").read_text()):
        atom_types = {}
        endpoints = Counter()
        crosslinks = 0
        section = ""
        with gzip.open(root / record["path"], "rt") as handle:
            for line in handle:
                content = line.split("#", 1)[0].strip()
                if not content:
                    continue
                if content[0].isalpha():
                    section = content
                    continue
                fields = content.split()
                if section == "Atoms":
                    atom_types[int(fields[0])] = int(fields[2])
                elif section == "Bonds" and int(fields[1]) == 18:
                    a, b = int(fields[2]), int(fields[3])
                    if sorted((atom_types[a], atom_types[b])) != [9, 10]:
                        raise ValueError(f"Unexpected crosslink endpoints in {record['path']}")
                    endpoints.update((a, b))
                    crosslinks += 1
        strands = {17: 2700, 21: 2100, 25: 1800}[record["n"]]
        expected_atoms = {a for a, t in atom_types.items() if t in (9, 10)}
        if (crosslinks != 2 * strands or set(endpoints) != expected_atoms
                or any(count != 1 for count in endpoints.values())):
            raise ValueError(f"Crosslink count or endpoint coverage mismatch: {record['path']}")
        print(f"n={record['n']} replica={record['replica']}: {crosslinks} type-18 bonds, all 9--10; PASS")


if __name__ == "__main__":
    main()
