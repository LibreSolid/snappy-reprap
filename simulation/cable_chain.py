"""A cable chain, as a chain: links that follow the sled, and the wires
through them drawn afresh at every position.

The design's ``cable_chain_assembly`` is the one module of
``full_assembly.scad`` that is a function of the axis position rather
than a placement of it: it counts how many links lie on the fixed run,
how many on the moving run and how many in the bend between, and draws
each at its station.  It is drawn for the position it is asked at,
with ``ceil`` and ``floor`` deciding the counts, so a link jumps from
the run into the bend as the sled passes it, and the chain it draws is
not always the same number of links long.  A real chain is: it has the
links a builder snapped together, and what changes as the sled travels
is only where each of them stands.

So the chain here is that.  It has `links` links, each a rigid leaf,
and its shape at any position is the one curve a chain of that length
can make between its two anchors: a straight run out from the fixed
anchor, a half turn up on the radius the two anchors' heights set, and
a straight run back to the moving anchor.  Every link is placed at its
own station along that curve, facing along it, and turned over in the
top run as the design turns them.  The whole of the motion is the split
of the chain's length between the two runs, which is linear in the
sled's position, so it is one number the axis binds and every link
follows it symbolically.

The wires inside are the other half, and the design draws them a link
at a time: a short bundle in each link, ending at the pivots.  Here the
bundle is drawn once, through the whole chain, as flexible leaves: one
molejo path per wire, a line, a half turn and a line, bound to the
same split the links are.  It is the same curve the links lie on, so
the wires are always inside the chain, whatever the position.

What is approximate about the links is the bend.  The real chain
pivots at pins spaced one pitch apart, so in the bend it is a polygon
inscribed in the circle and not the circle; a link is placed here at
its centre on the arc, facing along the arc's tangent there, which
puts its two pins a fraction of a millimetre inside the pins of its
neighbours.  The design's own bend is a fudge of the same size the
other way.  Neither is what a pinned chain does exactly, and the
contracts ask only what matters of it: that every link is on the
curve, that the two end links seat in their anchors, and that no link
fouls the machine anywhere in the travel.
"""

import math

from molejo import Arc, Circle, Line, P, Shape
from solid_node.math import cos, max, min, sin
from solid_node.node import AssemblyNode, MolejoNode
from solid_node.motion.ports import TranslationalPort
from solid_node.parameters import Count, Length

from simulation import colors
from simulation.chain_parts import CableChainLink
from simulation.params import cable_chain_height, cable_chain_pitch
from simulation.place import Y, place, translate, yrot, zrot
from simulation.scad import scad_sources


#: How many links a chain may be declared with: enough for either of
#: this machine's, with room for a longer travel.
MOST_LINKS = 24

#: How thick each wire is, ``wiring.scad``'s default.
WIRE_DIAMETER = 2.0

#: The most wires a chain carries: one per colour of the design's table.
MOST_WIRES = len(colors.WIRES)

#: How many rings of mesh molejo spends on each element of a wire's
#: path -- there are three, and the half turn is the one that needs
#: them: thirty-two puts a ring every six degrees of it.
PATH_SAMPLES = 32
PROFILE_SAMPLES = 8


def hex_offsets(count, diameter=WIRE_DIAMETER):
    """Where each of `count` wires sits in a hex-packed bundle.

    ``hex_offsets`` of ``wiring.scad``, restated: a wire at the centre,
    then rings of six, twelve, ... around it, each wire one diameter
    from its neighbours.
    """
    offsets = [(0.0, 0.0)]
    level = 1
    while len(offsets) < count:
        for side in range(6):
            for wire in range(1, level + 1):
                angle = side * 60
                offsets.append((
                    level * diameter * math.cos(math.radians(angle))
                    + wire * diameter * math.cos(math.radians(angle + 120)),
                    level * diameter * math.sin(math.radians(angle))
                    + wire * diameter * math.sin(math.radians(angle + 120))))
        level += 1
    return offsets[:count]


class Wire(MolejoNode):
    """One wire through the chain, as a flexible leaf.

    Its path is the chain's curve in the wire's own frame, which starts
    at the fixed anchor and runs along +z: out for `bottom`, a half
    turn about the axis a `bend` away in +x, and back to `top_end`.
    The chain places each wire at its offset in the bundle and binds
    all four numbers, because a molejo parameter is a plain number and
    the offset wire's bend is the chain's less its offset.
    """

    bottom = TranslationalPort(unit='mm')
    top_end = TranslationalPort(unit='mm')
    bend = TranslationalPort(unit='mm')
    span = TranslationalPort(unit='mm')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()

    def render(self):
        return Shape(
            profile=Circle(radius=WIRE_DIAMETER / 2),
            path=[
                Line(to=[0, 0, P.bottom]),
                Arc(center=[P.bend, 0, P.bottom], axis=[0, 1, 0],
                    angle=math.pi),
                Line(to=[P.span, 0, P.top_end]),
            ],
            path_samples=PATH_SAMPLES,
            profile_samples=PROFILE_SAMPLES,
        )


#: One class per colour of the design's wire table, so a node's colour
#: stays what it is: a class attribute.
WIRES = [type(f'Wire{index}', (Wire,),
              {'color': colors.WIRES[index], '__module__': __name__})
         for index in range(MOST_WIRES)]


class CableChain(AssemblyNode):
    """A chain of links between two anchors, in the design's own frame.

    The frame is ``cable_chain_assembly``'s: the chain lies in the XZ
    plane, runs out from the fixed anchor `bottom` along -x, turns up
    and comes back along +x to the moving anchor, which stands at `top`
    less `offset` along x.  `least` and `most` are the ends of the
    moving anchor's run, and they decide how many links the chain has:
    the bend, the farthest reach, and a whole link lying straight in
    each anchor at either end.  `wires` is how many wires run through
    it.

    `offset` is the design's ``off``: the sled's own position.
    """

    top_x = Length()
    top_z = Length()
    bottom_x = Length()
    bottom_z = Length()
    least = Length()
    most = Length()
    wires = Count(0, min=0, max=MOST_WIRES)

    offset = TranslationalPort(unit='mm')

    links = CableChainLink().repeat(MOST_LINKS)
    strands = [cls() for cls in WIRES]

    def __init__(self, top=None, bottom=None, **kwargs):
        if top is not None:
            kwargs.update(top_x=top[0], top_z=top[2])
        if bottom is not None:
            kwargs.update(bottom_x=bottom[0], bottom_z=bottom[2])
        super().__init__(**kwargs)

    @property
    def radius(self):
        """The bend's radius: half the height between the anchors."""
        return (self.top_z - self.bottom_z) / 2

    @property
    def reach(self):
        """The farthest the two runs differ over the travel: the
        moving anchor's farthest stand beyond the fixed one, or short
        of it, whichever is more."""
        apart = self.bottom_x - self.top_x
        return max(abs(apart + self.least), abs(apart + self.most))

    @property
    def count(self):
        """How many links: the bend, the farthest reach and a straight
        link at each end, in whole links, rounded up.

        The design's assembly text says thirteen or fourteen for the X
        chain and eighteen for the Z chain; its own module draws
        fifteen at the end of the X travel and skips the moving run.
        Both chains here come to nineteen."""
        return math.ceil((math.pi * self.radius + self.reach)
                         / cable_chain_pitch) + 2

    @property
    def length(self):
        return self.count * cable_chain_pitch

    def check(self):
        super().check()
        if self.top_z <= self.bottom_z:
            raise ValueError('the moving anchor must stand above the fixed one')
        if self.count > MOST_LINKS:
            raise ValueError(
                f'{self.count} links wanted, {MOST_LINKS} declared')

    def split(self, offset):
        """How much chain lies on the fixed run at `offset`.

        The two runs together are the chain less its bend, and they
        differ by how far the moving anchor stands beyond the fixed one
        -- the design's ``basex`` and ``off`` -- so the fixed run is
        half their sum.
        """
        return (self.length - math.pi * self.radius
                + self.bottom_x - self.top_x + offset) / 2

    def station(self, distance, bottom):
        """Where a point `distance` along the chain stands, and which
        way the chain faces there, for a fixed run of `bottom`.

        Returns ``(x, z, angle)``: the angle is how far the chain has
        turned over, nought on the fixed run and a half turn on the
        moving one.  Every clamp is the framework's own ``min``/``max``,
        which take the symbolic face as readily as the numeric one, so
        the same formula serves a number and a symbolic position.
        """
        radius = self.radius
        along = min(distance, bottom)
        turned = min(max(distance - bottom, 0),
                     math.pi * radius)
        back = max(distance - bottom - math.pi * radius, 0)
        angle = turned / radius * 180 / math.pi
        x = self.bottom_x - along - radius * sin(angle) + back
        z = self.bottom_z + radius * (1 - cos(angle))
        return x, z, angle

    def render(self):
        for index, link in enumerate(self.links):
            if index >= self.count:
                link.omit()
        offsets = hex_offsets(self.wires)
        for index, strand in enumerate(self.strands):
            if index >= self.wires:
                strand.omit()
                continue
            across, sideways = offsets[index]
            place(strand, translate([self.bottom_x, sideways,
                                     self.bottom_z + across]),
                  yrot(-90))

    def simulate(self):
        bottom = self.split(self.offset.value)
        for index, link in enumerate(self.links):
            if index >= self.count:
                continue
            x, z, angle = self.station(
                (index + 0.5) * cable_chain_pitch, bottom)
            place(link, translate([x, 0, z]), yrot(angle), zrot(90),
                  translate([0, 0, -cable_chain_height / 2]))
        top_end = self.bottom_x - self.top_x + self.offset.value
        offsets = hex_offsets(self.wires)
        for index, strand in enumerate(self.strands):
            if index >= self.wires:
                continue
            across = offsets[index][0]
            self.connect(bottom, strand.bottom)
            self.connect(top_end, strand.top_end)
            self.connect(self.radius - across, strand.bend)
            self.connect(2 * (self.radius - across), strand.span)
