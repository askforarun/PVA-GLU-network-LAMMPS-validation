# PVA--GLU network LAMMPS validation

Post-anisocompression atomistic configurations for dry, idealized PVA--GLU
networks with prescribed tetrafunctional junction connectivity. These are
model-specific C--C-linked junction surrogates, not atom-for-atom models of
experimental glutaraldehyde acetalization products.

## Dataset

Each folder contains one coefficient-bearing LAMMPS data file compressed
with gzip. There are three independently prepared replicas per strand length.
Here `n` counts hydroxyl-bearing PVA repeat units between terminal methylene
groups; each strand contains `2n+1` backbone carbons.

| n | PVA strands | GLU junctions | Atoms per replica |
| --- | --- | --- | --- |
| 17 | 2700 | 1350 | 371250 |
| 21 | 2100 | 1050 | 347550 |
| 25 | 1800 | 900 | 348300 |

These configurations precede GROMACS relaxation, staged equilibration, and
production. They are not final production configurations. The data files
include coordinates, topology, masses, and nonbonded and bonded coefficients.
No additional force-field parameter file is required.

`manifest.json` records source signac job IDs, statepoints, file sizes, atom
counts, and compressed and uncompressed SHA-256 hashes. `SHA256SUMS` verifies
the distributed compressed files:

```bash
sha256sum -c SHA256SUMS
```

## Initialization check

Use a LAMMPS build supporting `atom_style full`, harmonic bonds and angles,
Fourier dihedrals, `lj/cut/coul/long`, and PPPM (including the MOLECULE,
EXTRA-MOLECULE, and KSPACE capabilities as applicable to your build).
The archived original check used LAMMPS 2 Aug 2023.

From the repository root, for example:

```bash
gunzip -k configurations/n21/replica2/data.anisocompression_lammps.gz
lmp -in in.validate -var data configurations/n21/replica2/data.anisocompression_lammps -var output /tmp/n21-replica2-checked.data
```

The executable may be named `lmp_mpi` on some installations. MPI execution
is optional; the original check requested 16 ranks:

```bash
mpirun -np 16 lmp -in in.validate -var data configurations/n21/replica2/data.anisocompression_lammps -var output /tmp/n21-replica2-checked.data
```

The input reproduces the `run 0` initialization check from the signac
operation `validate_lammps_postcrosslinked_simulation`. It initializes forces
and writes a new data file without advancing dynamics. Successful execution
checks standalone readability and force-field initialization, not dynamical
stability, equilibration, or mechanical validity.

The source workspace contained a successful saved validation output for
`n21/replica2` only. This repository does not claim that all nine
configurations have already passed a new LAMMPS execution check. Compression,
hash integrity, and required coefficient-section checks were performed for
all distributed files.

## Rebuilding the export

`prepare_dataset.py` regenerates the compressed dataset, manifest, and
checksums from a signac project containing the nine source files:

```bash
python prepare_dataset.py /path/to/hydrogel_simulation
```

It uses only the Python standard library and deterministic gzip headers.
Generated uncompressed data, LAMMPS outputs, and logs are ignored by Git.
No proprietary network-formation implementation or trajectories are included.
