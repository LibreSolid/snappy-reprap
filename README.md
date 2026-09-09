![Snappy Full Rendering](https://github.com/revarbat/snappy-reprap/wiki/v3.0-snappy_small.png)

Snappy-Reprap 3
===============

A parametric design for a cheap self-replicating 3D printer (reprap) that snaps together to minimize screws and non-printed parts.

Important Links:

What                 | URL
-------------------- | -------------------------------------------------------
GitHub Repository    | https://github.com/revarbat/snappy-reprap
Project Wiki         | https://github.com/revarbat/snappy-reprap/wiki/v3.0-Home
Bill of Materials    | https://github.com/revarbat/snappy-reprap/wiki/v3.0-BOM
How to Assemble      | https://github.com/revarbat/snappy-reprap/wiki/v3.0-Assembly
RepRap.org Wiki Page | http://reprap.org/wiki/Snappy
Dev Forum            | https://groups.google.com/forum/#!forum/snappy-reprap-dev

[![Join the chat at https://gitter.im/revarbat/snappy-reprap](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/revarbat/snappy-reprap?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


Generating STL Files
====================
For all platforms, you will need to have OpenSCAD installed. You can download OpenSCAD from their website at [http://www.openscad.org](http://www.openscad.org)

To insure the best fit of parts, print the [slop calibrator STL file](https://github.com/revarbat/snappy-reprap/blob/master/STLs/slop_calibrator_parts.stl) on the parent printer using the desired print settings. Then update the printer_slop variable in the config.scad file on line 130. Then proceed to generating STL files.

OS X:
-----
Under OS X, you'll need to make sure you have the Xcode command-line tools installed first.  You can get them by installing Xcode from the App Store.

You shouldn't need to change the Makefile.  It should set $OPENSCAD as:
```
OPENSCAD=/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD
```

To generate the STL model files, open a terminal to the snappy-reprap directory and type:
```
make
```


Linux:
------
Under Linux, you will need to edit the Makefile, and change $OPENSCAD to:
```
OPENSCAD=openscad
```
To generate the STL model files, open a terminal to the snappy-reprap directory and type:
```
make
```


Windows:
--------
Under Windows, you'll probably have to open and compile each `*_parts.scad` file individually and manually export the STL files.

You _might_ be able to run the makefile under CygWin, if you set $OPENSCAD to something like:
```
OPENSCAD="/Program Files/OpenSCAD/openscad.exe"
```



The machine as a simulation
===========================

Beside the OpenSCAD design there is a second reading of it: a
[solid-node](https://pypi.org/project/solid-node/) tree in `simulation/`,
in which every part a builder handles is a leaf calling the design's own
module, coloured as the design paints it, every group snapped together
before it goes into something bigger is an assembly, and the machine's
motion is three drivers on the root.  The geometry is the .scad design's;
what the tree adds is where every part goes and what moves.

    solid build                                  # build the machine
    solid test --faceted simulation/snappy_reprap.py   # the contracts
    solid develop                                # watch and serve it

The three drivers are the design's own `xslidepos`, `yslidepos` and
`zslidepos`, in millimetres: how far the X sled stands to the left of
its rail's middle, how far the Y sled stands forward of its, and how
high the bridge stands above the middle of the towers' rails.  Each
ranges from where its limit switch is first touched to where its travel
physically ends -- numbers read off the built parts, not the firmware,
which believes in three millimetres more of X and Y and thirteen of Z
than the parts allow.  The `HomeX`, `HomeY` and `HomeZ` buttons run each
axis to its own switch at the firmware's homing feedrate for that axis:
50 mm/s for the racks, 4 mm/s for the screws, which is why homing Z is
slow.  `Rest` goes back to the pose the design draws.

The machine's seven freedoms are joints on the bodies that have them and
every transmission between them is a `drives` relation, except the cable
chains' link stations, which are still placed by hand.

What the design leaves standing still under a moving part moves with it
here.  The pinion under each rack turns with its sled, one turn per 80 mm.
The lifter rods turn as the bridge rises, one turn per 8 mm, clockwise
from above, couplers and all, and the bridge hangs on their thread.  The
two cable chains are chains: nineteen links each, placed on the curve a
chain of that length makes between its anchors, with the six and twelve
wires through them drawn as flexible strands in the design's own wire
colours.  The filament, which the design never draws, is wound
on the spool's hub and runs through the hole in the brace centre and
down into the extruder, redrawn wherever the bridge stands.

Reading the design this closely found a few things in it, all recorded
where they are met and none of them changed in the .scad sources:

- `lifter_assembly_5` turns the rods `-90` degrees to line their thread
  up with the Z sleds' sockets.  Under OpenSCAD 2021.01 that leaves the
  thread running through both sockets at every height; the sockets
  clear the rods only for rods turned 174 to 213 degrees further, and the
  simulation turns them 193.5 further (`simulation/z_screw.py`).
- The herringbone pair does not quite mesh over the whole tooth: the
  pinion is an involute extruded with a twist and the rack a straight
  rack skewed, and their flanks drift apart along the tooth, so the pair
  shares some 45 mm^3 at its best phase.  The author's shipped STLs are
  the same geometry.  At any one height the teeth interleave cleanly
  (`simulation/pinion.py`).
- Four of the design's harness runs render as nothing under this
  OpenSCAD -- `wiring()`'s fillet yields `nan` on their paths -- and are
  left out (`simulation/wiring.py`).
- The assembly text's link counts (13 or 14 for the X chain, 18 for the
  Z chain) are short for the travel; a chain reaching both ends of it
  with a straight link in each anchor needs 19 (`simulation/cable_chain.py`).
- The Y sled's two halves are drawn half a millimetre apart where the X
  sled's touch, so the Y racks are a quarter of a millimetre out of pitch
  with each other; the assembly text says to line the racks up
  (`simulation/test_snappy_reprap.py`).

The design record is under `openspec/`.
