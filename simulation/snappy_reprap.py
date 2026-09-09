"""The Snappy RepRap, as a machine.

The printer is designed in OpenSCAD, in the .scad files beside this
package, and that design is left exactly as it is.  What this package
adds is a second reading of it: a tree of nodes in which every part a
builder handles is a leaf coloured as the design colours it, every
group snapped together before it goes into something bigger is an
assembly, and the machine's motion is three drivers on the root.  The
geometry is the design's own modules; the layer says where each part
goes and what moves.

The tree follows ``full_assembly.scad``, which follows the build: the X
axis rail first, with its sled and the whole Y axis riding on that;
the two Z towers snapped onto its ends; the bridge carrying the
extruder between them; the brace over the top; the spool stand on the
right tower and the controller mount on the left.

The design's ``final_assembly_9`` takes ``xslidepos``, ``yslidepos`` and
``zslidepos``, and ``full_rendering()`` animates them.  Here they are
drivers, in the same coordinates, and what the design leaves standing
still under a moving sled now moves with it: the pinion under each
rack turns as its sled travels, the lifter rods turn as the bridge
rises, the cable chains follow the sled and the bridge link by link
with their wires drawn through them, and the filament runs from the
spool to the extruder wherever the bridge has got to.

Z is the odd axis and is meant to be.  X and Y are racks, and a rack
has no state a millimetre does not already say; Z is two screws, and a
screw's state is an angle.  So `z` holds degrees and declares the
`scale` that makes them millimetres, which is exactly the machine: an
8 mm lead, right-handed.  A maker never sees that -- the slider and
every instruction target are in millimetres -- but the rods do, and it
is why they can be drawn turning; `z_screw` holds the arithmetic.

Each axis homes on its own, to its own limit switch, at the feedrate
the firmware shipped with the design homes it at.
"""

from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, Instruction

from simulation import z_screw
from simulation.brace import TopBrace
from simulation.bridge import Bridge
from simulation.cable_chain import CableChain
from simulation.bridge import ARCH_OFFSET
from simulation.extruder import INLET
from simulation.electronics import RampsMount
from simulation.filament import (
    RADIUS as STRAND_RADIUS, TRAVERSE, Filament, in_strand_frame)
from simulation.homing import (
    X_HOME, X_MAX, Y_HOME, Y_MAX, Z_HOME, Z_MAX,
    X_HOMING_TIME, Y_HOMING_TIME, Z_HOMING_TIME)
from simulation.params import (
    cable_chain_height,
    spool_axle_drop,
    cable_chain_length,
    cantilever_length,
    groove_height,
    joiner_width,
    motor_rail_length,
    platform_length,
    rail_height,
    rail_length,
    rail_thick,
    rail_width,
    z_base_height,
    z_joiner_spacing,
)
from simulation.place import fwd, left, place, right, translate, up, yrot, zrot
from simulation.spool import AXLE_Z, SpoolStand
from simulation.tower import ZTower
from simulation.wiring import Bundle
from simulation.x_axis import XAxis


#: Where the towers stand: on the ends of the X rail.
TOWER_X = motor_rail_length / 2 + rail_length

#: Where the bridge rests with Z at nought: the middle of the towers'
#: rails, less half a rail height, from ``z_tower_assembly_1``.
BRIDGE_Z = (rail_height + groove_height + z_base_height + rail_length
            - rail_height / 2)

#: Where the brace sits: on top of the towers' rails.
BRACE_Z = rail_height + groove_height + z_base_height + 2 * rail_length

#: Where the spool stand's foot lands on the right tower, in the
#: machine's frame: the tower is turned round, so the design's
#: ``left(platform_length) ... right(rail_height/2)`` reads the other way.
SPOOL_X = TOWER_X + platform_length - rail_height / 2
SPOOL_Z = BRACE_Z + rail_height

#: Where the spool's axis runs, and where the strand's own frame stands:
#: on top of the layer, at the near end of the hub, from which the layer
#: winds away along -y.
SPOOL_CENTRE = [SPOOL_X, 0, SPOOL_Z + AXLE_Z - spool_axle_drop]
STRAND_ORIGIN = [SPOOL_CENTRE[0], TRAVERSE / 2,
                 SPOOL_CENTRE[2] + STRAND_RADIUS]

#: Where the filament goes into the extruder: on the machine's axis,
#: at the top face of the idler arm's bar, with the bridge at Z nought.
INLET_Z = BRIDGE_Z + ARCH_OFFSET + INLET

#: Where the run goes through the brace: the hole down the middle of
#: ``bridge_brace_center()``, which stands ``rail_height -
#: joiner_width/2`` above the brace's foot and is ``joiner_width``
#: deep; and how far above it the run is already coming straight down.
HOLE_Z = BRACE_Z + rail_height - joiner_width / 2 - joiner_width / 2
ABOVE_HOLE = 40.0
HIGH_ABOVE_HOLE = 80.0

#: The two constant points above the brace's hole and the machine's own
#: axis at Z nought, each read in the strand's own frame: neither
#: depends on the bridge's height, so each stays a `connect()` of a
#: module constant rather than a relation.
HIGH_IN_STRAND = in_strand_frame([0, 0, HOLE_Z + HIGH_ABOVE_HOLE], STRAND_ORIGIN)
ABOVE_IN_STRAND = in_strand_frame([0, 0, HOLE_Z + ABOVE_HOLE], STRAND_ORIGIN)

#: Where the filament goes in, at Z nought, in the strand's own frame:
#: today's ``head`` expression with the `lift` term taken out, so
#: relation (7) can add `bridge.lift` back as its driver.
INLET_IN_STRAND = in_strand_frame([0, 0, INLET_Z], STRAND_ORIGIN)

#: Where the controller mount hangs off the back of the left tower.
RAMPS_X = TOWER_X + platform_length + 6

#: The Z cable chain, from ``final_assembly_5``: it climbs the front of
#: the left tower, in a frame turned to stand the design's chain up.
Z_CHAIN_X = TOWER_X + platform_length
Z_CHAIN_Y = z_joiner_spacing / 2 + joiner_width + 23.5
Z_CHAIN_Z = rail_height + groove_height + z_base_height + rail_length
Z_CHAIN_TOP = [-cable_chain_length / 2 - cable_chain_height / 4 - 1, 0,
               rail_height + groove_height / 2 + cantilever_length
               + cable_chain_height / 2 - 6]
Z_CHAIN_BOTTOM = [0, 0, 0]
Z_CHAIN_WIRES = 12
Z_CHAIN_OFFSET = -rail_height / 2


class SnappyReprap(AssemblyNode):
    """The complete Snappy RepRap 3.

    The three drivers are the design's own ``xslidepos``,
    ``yslidepos`` and ``zslidepos``: how far the X sled stands to the
    left of its rail's middle, how far the Y sled stands forward of
    its, and how high the bridge stands above the middle of the
    towers' rails.  Each ranges from where its limit switch stops it
    to where the firmware's travel ends.

    The instructions home each axis on its own: to its switch, at the
    firmware's own homing feedrate for that axis, which for Z is a
    screw's pace.  `Rest` is the pose the design draws.
    """

    x = Driver(default=0.0, unit='mm', range=(X_HOME, X_MAX))
    y = Driver(default=0.0, unit='mm', range=(Y_HOME, Y_MAX))
    z = Driver(default=0.0, unit='mm', range=(Z_HOME, Z_MAX),
               scale=z_screw.SCALE)

    instructions = {
        'HomeX': Instruction({'x': X_HOME}, duration=X_HOMING_TIME),
        'HomeY': Instruction({'y': Y_HOME}, duration=Y_HOMING_TIME),
        'HomeZ': Instruction({'z': Z_HOME}, duration=Z_HOMING_TIME),
        'Rest': Instruction({'x': 0.0, 'y': 0.0, 'z': 0.0},
                            duration=Z_HOMING_TIME),
    }

    x_axis = XAxis()
    left_tower = ZTower(chain_mount=True)
    right_tower = ZTower()
    bridge = Bridge()
    brace = TopBrace()
    spool_stand = SpoolStand()
    ramps_mount = RampsMount()
    z_chain = CableChain(top=Z_CHAIN_TOP, bottom=Z_CHAIN_BOTTOM,
                         least=Z_HOME + Z_CHAIN_OFFSET,
                         most=Z_MAX + Z_CHAIN_OFFSET, wires=Z_CHAIN_WIRES)
    filament = Filament()

    # The seven freedoms, driven by the three inputs.
    x.drives(x_axis.sled.travel)
    y.drives(x_axis.sled.y_axis.sled.travel)
    z.drives(left_tower.lifter.screw.spin, offset=z_screw.PHASE)
    z.drives(right_tower.lifter.screw.spin, offset=z_screw.PHASE)
    z.drives(bridge.lift, ratio=z_screw.SCALE)
    bridge.lift.drives(z_chain.offset, offset=Z_CHAIN_OFFSET)
    bridge.lift.drives(filament.head, offset=INLET_IN_STRAND[0])

    # ``final_assembly_2``: the towers' harnesses along the base rail.
    base_wires_a = Bundle(0)(path=[
        [-(TOWER_X + platform_length + 100), 0, rail_thick + 10],
        [-(TOWER_X + platform_length - 5), 0, rail_thick + 10],
        [-(TOWER_X + 15), 0, rail_thick + 5],
        [-motor_rail_length / 2, 0, rail_thick + 5],
    ], wires=4)
    base_wires_b = Bundle(0)(path=[
        [-(TOWER_X + platform_length + 100), 5, rail_thick + 5],
        [-(TOWER_X + platform_length - 5), 5, rail_thick + 5],
        [-(TOWER_X + 15), -rail_width / 3, rail_thick + 5],
        [-motor_rail_length / 2, -rail_width / 3, rail_thick + 5],
    ], wires=4)
    # ``final_assembly_4``: each top endstop's wires down its tower.
    left_tower_wires = Bundle(4)(path=[
        [rail_thick + 5.01, 0, BRACE_Z - 95],
        [rail_thick + 5, 0, rail_thick + 5],
        [-100, 0, rail_thick + 5],
    ], wires=2, fillet=9, wirenum=4)
    right_tower_wires = Bundle(4)(path=[
        [-(rail_thick + 5), 0, BRACE_Z - 95],
        [-(rail_thick + 5.01), 0, rail_thick + 5],
        [-100, 0, rail_thick + 5],
    ], wires=2, fillet=9, wirenum=4)
    # ``final_assembly_5`` also draws the bridge harness from the
    # chain's fixed end down the tower and its pigtail at the bridge
    # end; both are paths the design's ``wiring()`` cannot sweep under
    # OpenSCAD 2021.01 (see `wiring`), so neither is here.

    def render(self):
        place(self.left_tower, left(TOWER_X))
        place(self.right_tower, right(TOWER_X), zrot(180))
        place(self.bridge, up(BRIDGE_Z))
        place(self.brace, up(BRACE_Z))
        place(self.spool_stand, right(SPOOL_X), up(SPOOL_Z))
        place(self.ramps_mount, left(RAMPS_X), zrot(-90))
        place(self.left_tower_wires, left(TOWER_X + platform_length))
        place(self.right_tower_wires, right(TOWER_X + platform_length))

        chain = (up(Z_CHAIN_Z), left(Z_CHAIN_X), fwd(Z_CHAIN_Y))
        place(self.z_chain, *chain, yrot(90), up(cable_chain_height / 2))

        place(self.filament, translate(STRAND_ORIGIN), zrot(90), yrot(-90))

    def simulate(self):
        # Not transmissions: nothing drives these, they are constants of
        # the machine, each the strand-frame reading of a point on the
        # machine's own axis. `filament.head` is relation (7) instead.
        self.connect(HIGH_IN_STRAND[0], self.filament.high_x)
        self.connect(ABOVE_IN_STRAND[0], self.filament.above_x)
        self.connect(INLET_IN_STRAND[1], self.filament.axis_y)
        self.connect(INLET_IN_STRAND[2], self.filament.axis_z)
