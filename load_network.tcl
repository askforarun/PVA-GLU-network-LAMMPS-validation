# In the VMD Tk Console: source load_network.tcl
# Then: load_pva_glu /absolute/path/to/decompressed/data.anisocompression_lammps

proc load_pva_glu {datafile} {
    package require topotools
    if {![file isfile $datafile]} {
        error "Decompress the LAMMPS data file first: $datafile"
    }
    set molid [topo readlammpsdata $datafile full]
    if {$molid < 0} {error "TopoTools could not read $datafile"}
    foreach {type element name} {
        1 C c3 2 H hc 3 H h1 4 O oh 5 H ho
        6 C c6 7 O os 8 H h2 9 C PVA_Cend 10 C GLU_Creact
    } {
        set selection [atomselect $molid "type $type"]
        $selection set element $element
        $selection set name $name
        $selection delete
    }
    # Keep numeric types and the imported Bonds section unchanged.
    while {[molinfo $molid get numreps] > 0} {mol delrep 0 $molid}
    mol representation Lines 1.0
    mol color Element
    mol selection "not element H"
    mol addrep $molid
    foreach {type color} {9 0 10 1} {
        mol representation VDW 0.35 12.0
        mol color ColorID $color
        mol selection "type $type"
        mol addrep $molid
    }
    mol top $molid
    display resetview
    puts "Loaded network: PVA crosslink carbons (type 9) blue; GLU crosslink carbons (type 10) red."
    puts "Crosslinks are bond type 18; numeric types and original bonds are preserved."
    return $molid
}
