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

## Visualizing crosslinks in VMD / TopoTools

`atom_types.csv` maps all ten numeric LAMMPS atom types to their GAFF2
labels and elements. The crosslink is **bond type 18**, connecting:

- **Atom type 9:** PVA terminal carbon, GAFF2 `c3`.
- **Atom type 10:** GLU reactive carbon, GAFF2 `c6`.

Types 9 and 10 are bookkeeping labels for reacted sites, not new elements
or distinct nonbonded parameter sets. Their nonbonded coefficients match
ordinary `c3` (type 1) and `c6` (type 6), respectively. Bond type 18 uses
`U = K*(r-r0)^2`, with `K = 300.9 kcal mol^-1 angstrom^-2` and
`r0 = 1.538 angstrom`. Bond type IDs and atom type IDs are different
quantities. Identical bond coefficients alone do not identify a crosslink.

After decompressing a dataset, start VMD and enter in its Tk Console:

```tcl
source /absolute/path/to/load_network.tcl
load_pva_glu /absolute/path/to/data.anisocompression_lammps
```

The loader uses `topo readlammpsdata ... full`, preserves the imported
bonds and numeric atom types, assigns element/name labels for display,
and highlights type-9 carbons in blue and type-10 carbons in red.
In Graphics > Representations, `type 9 10` selects the crosslink atoms.
This selects atoms, not an isolated bond-type representation. The complete
network is shown as heavy-atom lines; other bonds between selected atoms
should not be mistaken for type-18 crosslinks. No distance-based bond
guessing is needed. Periodic boundary-crossing bonds may appear as long
lines in the wrapped cell; a percolating network cannot generally be made
whole inside a single periodic image. Avoid overwriting simulation inputs
with visualization exports.

The exact type-18 endpoint mapping and counts can be checked reproducibly:

```bash
python check_crosslink_types.py
```

Expected crosslink counts per replica are 5400, 4200, and 3600 for `n=17`,
21, and 25, respectively. The VMD loader itself requires VMD and TopoTools;
it has not been GUI-tested on the export host.
See the [official TopoTools documentation](https://www.ks.uiuc.edu/Research/vmd/plugins/topotools/).

