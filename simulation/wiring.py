"""The wire bundles the design draws with ``wiring.scad``.

``wiring(path, wires, wirediam, fillet, wirenum)`` sweeps a hex-packed
bundle of round wires along a filleted polyline, colouring wire `i`
from a table of seventeen.  A bundle is one leaf here -- a harness is
handled as one thing -- so it takes one colour, and the colour it takes
is the first wire's, `wirenum`'s entry in that table.  A class per
starting colour keeps that a class attribute, as a node's colour is.

Four of the design's runs are not drawn here: the extruder motor's
wires, the harness down the bridge's left span, and the bridge harness
down the left tower with its pigtail.  ``wiring()`` fillets its
polyline into a bezier and sweeps a section along it, and on those
four paths the fillet comes out ``[nan, nan, nan]`` under OpenSCAD
2021.01 -- in the design's own ``full_assembly.scad`` as much as here
-- so OpenSCAD draws nothing for them.  A leaf with no geometry is
worse than an absent one, so they are left out and named.

Every wiring run of the design lives inside one rigid group -- a motor
segment, a tower base, the bridge -- and travels with it.  The runs
that had to cross between moving parts go through the cable chains,
and those are drawn as flexible leaves in `cable_chain`.
"""

from simulation import colors
from simulation.part import ScadPart
from simulation.scad import wiring as wiring_scad


class Wiring(ScadPart):
    """A bundle of `wires` wires along `path`, the design's own call.

    Constructor form: the path and the counts are what the part is, so
    every one of them is forwarded to the artifact key.
    """

    def __init__(self, path, wires, wirediam=2, fillet=10, wirenum=0,
                 name=None):
        self.path = [list(point) for point in path]
        self.wires = wires
        self.wirediam = wirediam
        self.fillet = fillet
        self.wirenum = wirenum
        super().__init__(path=self.path, wires=wires, wirediam=wirediam,
                         fillet=fillet, wirenum=wirenum, name=name)

    def render(self):
        return wiring_scad.wiring(self.path, self.wires,
                                  wirediam=self.wirediam,
                                  fillet=self.fillet, wirenum=self.wirenum)


_BUNDLES = {}


def Bundle(wirenum=0):
    """The `Wiring` class whose colour is the table's `wirenum` entry."""
    if wirenum not in _BUNDLES:
        _BUNDLES[wirenum] = type(
            f'Wiring{wirenum}', (Wiring,),
            {'color': colors.wire(0, wirenum), '__module__': __name__})
    return _BUNDLES[wirenum]
