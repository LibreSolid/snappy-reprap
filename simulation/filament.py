"""The stock the machine eats, from the spool to where it goes in.

The design draws an empty spool on the stand and cuts a filament
channel down the extruder, and draws no filament: ``filament_diam`` is
declared and used only to size holes.  So the strand is the one part
here that is neither a module of the design nor a placement of one.

It is a flexible leaf, and the plain case of one: a length of stock
hanging between a spool that never moves and an extruder that moves in
Z, so its shape at any height is a function of the height.  Drive Z
and the free run is drawn again from wherever the bridge has got to,
while the turns on the spool stay exactly where they are.

What the layer is
-----------------

The outermost layer of stock on the spool's hub, drawn as the strand
it really is: turns lying against each other at the stock's own
diameter, as many whole ones as the hub holds between the flanges, and
the free run continues from the last of them.  Whole turns matter: a
molejo helix ends at the angular position it started at, which is
what lets one placement put both the spool's axis and the take-off
point where they belong.

How the run goes
----------------

The spool stands on top of the right tower and the extruder is at the
middle of the bridge, and between them, at the height the run has to
cross, the top brace spans the whole machine along its centre line --
with a 10 mm hole through the middle of its centre piece, filleted
both sides, on the machine's own axis.  That hole is the design saying
where the filament goes: straight down through the brace and into the
extruder below it.  So the run leaves the top of the spool towards the
machine, curves over until it is coming straight down on the axis
above the brace, and drops through the hole and into the inlet.  The
turn never moves; the inlet rises and falls with Z, and the straight
drop from above the brace to it is what gets longer and shorter.
"""

from molejo import Circle, Helix, Line, P, Shape, Spline
from solid_node.node import MolejoNode
from solid_node.motion.ports import TranslationalPort

from simulation import colors
from simulation.params import (
    filament_diam,
    spool_flange_thick,
    spool_hub_diam,
    spool_hub_length,
)
from simulation.scad import scad_sources


#: The radius the stock's centre line runs at on the hub: the hub's,
#: plus half a stock.
RADIUS = (spool_hub_diam + filament_diam) / 2

#: How much of the hub lies between the flanges' inner faces.
HUB_WIDTH = spool_hub_length - spool_flange_thick

#: How many turns the layer is: the most whole ones the hub holds at
#: the stock's own pitch, one fewer than the width divides by because a
#: helix occupies its rise plus one stock.
TURNS = int(HUB_WIDTH / filament_diam) - 1

#: How far along the hub the layer travels.
TRAVERSE = TURNS * filament_diam

#: How many rings of mesh each turn is drawn with, and how many points
#: go round the stock.
RINGS_PER_TURN = 36
PATH_SAMPLES = RINGS_PER_TURN * TURNS
PROFILE_SAMPLES = 8

#: Which way is down, read in the strand's own frame.
DOWN = [-1, 0, 0]


def in_strand_frame(point, origin):
    """Read a machine point in the strand's own frame.

    The strand is placed with ``zrot(90) yrot(-90)``, which turns its x
    onto the machine's z, its y onto the machine's -x and its z onto
    the machine's -y; reading a machine point back is that permutation
    the other way round -- a reordering and two sign changes, which is
    what lets the machine hand these to the ports as expressions over
    its own driver rather than as numbers.
    """
    dx, dy, dz = (point[0] - origin[0], point[1] - origin[1],
                  point[2] - origin[2])
    return [dz, -dx, -dy]


class Filament(MolejoNode):
    """The loaded machine's filament: a layer on the spool and the run.

    One strand: the turns on the hub and the free run are the same
    length of stock, so they are one sweep, a helix continued by a
    spline that leaves it the way it came.

    Its ports are where the run has turned down -- two points on the
    machine's axis above the brace's hole, constants of the machine
    that the machine's frame is the one to know, from the second of
    which the stock drops straight through the hole -- and where it
    goes in, which moves with Z.
    All of them are read in the strand's own frame, and the inlet and
    the hole share two of their three coordinates because both stand
    on the machine's own axis.
    """

    color = colors.FILAMENT

    high_x = TranslationalPort(unit='mm')
    above_x = TranslationalPort(unit='mm')
    head = TranslationalPort(unit='mm')
    axis_y = TranslationalPort(unit='mm')
    axis_z = TranslationalPort(unit='mm')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()

    def render(self):
        return Shape(
            profile=Circle(radius=filament_diam / 2),
            path=[
                Helix(radius=RADIUS, turns=TURNS, height=TRAVERSE),
                Spline(points=[[P.high_x, P.axis_y, P.axis_z],
                               [P.above_x, P.axis_y, P.axis_z]],
                       end_tangent=DOWN),
                Line(to=[P.head, P.axis_y, P.axis_z]),
            ],
            path_samples=PATH_SAMPLES,
            profile_samples=PROFILE_SAMPLES,
        )
