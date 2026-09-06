"""Contracts the machine has to keep.

These ask the thing this layer is responsible for.  The geometry of
each part comes from the OpenSCAD design and was correct before this
package existed; what is new here is where every part is put and what
moves.  So the tests ask whether the sleds are on their rails, whether
the parts that move carry what they should and nothing else, whether
the pinions turn with their racks and the rods with the bridge, where
each axis meets its switch and its hard stop, and whether the chains
and the filament are drawn where the machine leaves them.

Two things about the design set the terms of several contracts, and
both are recorded where they are asked for rather than smoothed over.
The pinions are herringbone gears extruded with a twist against racks
skewed by an angle, and over the whole tooth the two do not quite
agree: at any one height they interleave cleanly, but the pair shares
some forty-five cubic millimetres at the best phase, and the contract
is that the phase stays the best one.  And the Z sleds' sockets clear
the lifter rods only for rods turned half a turn further than the
design's own phase constant turns them; the contracts hold the rods
at the phase that clears, at heights between pitches, where a wrong
phase shows.

The pair contracts -- clear, fouling, blocked, free -- are the
framework's own assertions.  OpenSCAD 2021.01 exports the design's
snap-together parts with edges that four faces share, where two
features of one part meet along an edge; trimesh calls those meshes
non-watertight, and the framework once refused them before the engine
saw them.  It now lets the engine judge, and Manifold builds every one
of them.  What is still asked of the engine directly, in `shared` and
the slab below, is a quantity the assertions do not report: the volume
a rack shares with a pinion summed over the racks, or over a slab of
the pair one millimetre thick, compared at the design's phase and a
fraction of a tooth off it.

The two whole-model contracts `solid new` scaffolds --
`assertNoDisconnectedSolids` and `assertNoSolidInterference` -- are
not asserted on the whole machine either.  The design nests its cable
chain links into each other by construction, seats a link inside each
anchor, passes wires through walls and set screws through gears and
couplers, and draws several bought parts as more than one body.
Neither contract could go green without changing the OpenSCAD design,
so each is asked instead of the pairs this layer moves: sleds against
rails, sockets against rods, links against the machine, strands
against links, filament against what it passes.
"""

import math

import numpy
import trimesh
from manifold3d import Manifold, Mesh
from scipy.spatial import cKDTree
from solid_node.core.serializer import (
    document_version, serialize_node, symbolic_document)
from solid_node.simulation import Sim
from solid_node.test import TestCase

from simulation import cable_chain as chain_module
from simulation import filament as filament_module
from simulation import pinion, z_screw
from simulation.homing import (
    X_HOME, X_MAX, Y_HOME, Y_MAX, Z_HOME, Z_MAX,
    X_HOMING_TIME, Z_HOMING_TIME, TICK)
from simulation.params import (
    cable_chain_height,
    cable_chain_pitch,
    filament_diam,
    lifter_rod_pitch,
    rack_tooth_size,
    spool_hub_diam,
)
from simulation.snappy_reprap import BRIDGE_Z, HOLE_Z, INLET_Z, TOWER_X
from simulation.tower import RAIL_X
from simulation.params import platform_length


def solid(node):
    """A part's world-placed mesh, on the engine."""
    mesh = node.mesh
    return Manifold(mesh=Mesh(
        vert_properties=numpy.asarray(mesh.vertices, numpy.float32),
        tri_verts=numpy.asarray(mesh.faces, numpy.uint32)))


def shared(node1, node2):
    """The volume two parts share, in mm^3."""
    result = solid(node1) ^ solid(node2)
    return 0.0 if result.is_empty() else result.volume()


def turned_about(node, before, axis_point):
    """How far `node` has turned about the vertical axis through
    `axis_point` since its vertices were `before`, in degrees."""
    after = node.mesh.vertices
    x0, y0 = axis_point[0], axis_point[1]
    a0 = numpy.arctan2(before[:, 1] - y0, before[:, 0] - x0)
    a1 = numpy.arctan2(after[:, 1] - y0, after[:, 0] - x0)
    turned = numpy.degrees(numpy.angle(numpy.exp(1j * (a1 - a0))))
    far = numpy.hypot(before[:, 0] - x0, before[:, 1] - y0) > 5
    return float(numpy.median(turned[far]))


def same_points(vertices, before):
    """The farthest any vertex stands from the nearest of `before`."""
    return float(cKDTree(before).query(vertices)[0].max())


class SnappyReprapTest(TestCase):

    # A driven part is placed by arithmetic on millimetres and its mesh
    # is only carried along by the transform, so it lands exactly where
    # it was sent.  A micron of slack allows for the float.
    PLACED = 0.001

    # How far past first contact a switch lever or a hard stop is asked
    # to foul, and how far short of it to be clear.
    TOUCH = 0.5

    # A tooth of rack, and the turn of pinion it is worth.
    TOOTH = rack_tooth_size
    TOOTH_TURN = 360 / pinion.MM_PER_TURN * rack_tooth_size

    # The most metal a pinion may share with its racks at the meshing
    # phase over the whole tooth: the design's own herringbone drift
    # (see `pinion`) is 45.6 mm^3, and it grows past 47 within a degree
    # of phase either way.  The Y sled's halves stand half a millimetre
    # apart where the X sled's touch, so its two racks are a quarter of
    # a millimetre out of pitch either way -- 2.7 degrees of pinion --
    # and the Y pinion, in phase with the pair, is that far out of
    # phase with each half alone: 48.3 mm^3 at the ends of its travel.
    MESHED = 46.0
    MESHED_Y = 49.0

    # A millimetre-thick slab of the pair, three millimetres below the
    # chevron's apex: clean at the phase, teeth on teeth a half tooth
    # off.
    SLAB_BELOW_APEX = 3.0
    SLAB_CLEAN = 0.2
    SLAB_CLEAN_Y = 1.0
    SLAB_FOULED = 3.0

    # The axial play of a Z sled's socket on its rod, and a push that
    # must meet the flank: the sockets clear the rods over 39 degrees
    # of turn, which is 0.87 mm of lead.
    Z_NUT_PLAY = 0.25
    Z_NUT_STOP = 0.7

    # Heights between pitches, where a rod that is not really threaded
    # through its socket shows.
    OFF_PITCH = (2.5, 33.3, -77.7)

    # A wire of the Z chain's outer ring stands 4 mm off the bundle's
    # centre and 1 mm thick, in a barrel whose chamfered cavity leaves
    # 4.9 mm: the design's own twelve wires graze the chamfer, by up to
    # six tenths of a cubic millimetre per link.
    GRAZE = 0.8

    # What two tessellated surfaces that only touch share, by rounding.
    TANGENT = 1e-6

    def drive(self, **positions):
        """Send the axes somewhere, in millimetres, Z included; an axis
        not named goes to nought.  Every test starts from rest this
        way, so none inherits where the last one left the machine."""
        state = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        state.update(positions)
        state['z'] = z_screw.angle(state['z'])
        self.node.set_state(**state)

    def bounds(self, node):
        return node.mesh.bounds.copy()

    def assertMovedBy(self, node, before, delta):
        after = node.mesh.bounds
        numpy.testing.assert_allclose(
            after - before, [delta, delta], atol=self.PLACED,
            err_msg=f'{node.name} did not move by {delta}')

    def assertStill(self, node, before):
        numpy.testing.assert_allclose(
            node.mesh.bounds, before, atol=self.PLACED,
            err_msg=f'{node.name} moved')

    def assertClear(self, node1, node2):
        self.assertNotIntersecting(node1, node2)

    def assertFouls(self, node1, node2, at_least=0.0):
        if at_least > 0.0:
            self.assertIntersectVolumeAbove(node1, node2, at_least)
        else:
            self.assertIntersecting(node1, node2)

    def assertNear(self, node1, node2, distance):
        """Some of `node1` stands within `distance` of `node2`."""
        nearest = trimesh.proximity.closest_point(
            node2.mesh, node1.mesh.vertices)[1].min()
        self.assertLessEqual(
            nearest, distance,
            f'{node1.name} is {nearest:.2f} mm from {node2.name}')

    def displaced(self, node, along, amounts):
        """The volume `node` shares with each of `along`'s parts when
        pushed by each of `amounts` along the given axis, both ways."""
        against, axis = along
        found = []
        for amount in amounts:
            for sign in (1, -1):
                node.save_checkpoint()
                node.translate([sign * amount * a for a in axis])
                found.append(max(shared(node, part) for part in against))
                node.restore_checkpoint()
        return found

    ########################################
    # The machine at rest

    def test_the_machine_rests_where_the_design_draws_it(self):
        """Untouched, all three slides stand at the design's nought."""
        self.drive()
        simulation = Sim(self.node, TICK)
        self.assertEqual(simulation.state, {'x': 0.0, 'y': 0.0, 'z': 0.0})

    def test_the_x_sled_rides_the_x_rails(self):
        """Both halves stand on both rails, and cut into neither."""
        self.drive()
        self.assertRides(self.node.x_axis)

    def test_the_y_sled_rides_the_y_rails(self):
        self.drive()
        self.assertRides(self.node.x_axis.sled.y_axis)

    def assertRides(self, axis):
        """Each half of the axis's sled cuts into no rail and stands on
        the one it is over: the motor segment in the middle, a plain
        segment at either end."""
        rails = list(axis.rails) + [axis.segment.segment]
        for half in axis.sled.halves:
            for rail in rails:
                self.assertClear(half, rail)
            self.assertNear(half, axis.segment.segment, 1.0)

    def test_the_z_sleds_ride_the_tower_rails(self):
        self.drive()
        for sled, tower in self.z_pairs():
            for rail in tower.rails:
                self.assertClear(sled, rail)
            self.assertNear(sled, tower.rails[0], 1.0)

    def z_pairs(self):
        """Each Z sled with the tower it rides: the sled at +x rides
        the right tower."""
        return list(zip(self.node.bridge.sleds,
                        (self.node.right_tower, self.node.left_tower)))

    ########################################
    # What each driver moves

    def test_driving_x_slides_the_sled_and_all_it_carries(self):
        """X moves the sled, the Y axis on it and the bed on that; not
        the rail it slides on."""
        self.drive()
        axis = self.node.x_axis
        carried = [axis.sled.halves[0], axis.sled.joiners[1],
                   axis.sled.y_axis.segment.motor,
                   axis.sled.y_axis.sled.glass]
        still = [axis.segment.segment, axis.rails[0],
                 self.node.left_tower.base, self.node.bridge.extruder.hotend]
        before = {part.name: self.bounds(part) for part in carried + still}
        self.drive(x=37.5)
        for part in carried:
            self.assertMovedBy(part, before[part.name], [-37.5, 0, 0])
        for part in still:
            self.assertStill(part, before[part.name])

    def test_driving_y_slides_the_bed_only(self):
        self.drive()
        axis = self.node.x_axis.sled.y_axis
        carried = [axis.sled.halves[1], axis.sled.glass,
                   axis.sled.corners[0].endcap, axis.sled.corners[1].screws[0]]
        still = [axis.segment.segment, axis.rails[1], axis.endcaps[0],
                 self.node.x_axis.sled.halves[0]]
        before = {part.name: self.bounds(part) for part in carried + still}
        self.drive(y=-41.0)
        for part in carried:
            self.assertMovedBy(part, before[part.name], [0, 41.0, 0])
        for part in still:
            self.assertStill(part, before[part.name])

    def test_driving_z_lifts_the_bridge_and_nothing_else(self):
        self.drive()
        bridge = self.node.bridge
        carried = [bridge.extruder.hotend, bridge.segments[0],
                   bridge.sleds[1], bridge.chain_anchor]
        still = [self.node.left_tower.rails[1], self.node.brace.centre,
                 self.node.left_tower.lifter.motor,
                 self.node.x_axis.sled.y_axis.sled.glass]
        before = {part.name: self.bounds(part) for part in carried + still}
        self.drive(z=52.0)
        for part in carried:
            self.assertMovedBy(part, before[part.name], [0, 0, 52.0])
        for part in still:
            self.assertStill(part, before[part.name])

    ########################################
    # The pinions, which turn with their racks

    def pinions(self):
        """Each pinion with the racks it drives."""
        x_axis = self.node.x_axis
        y_axis = x_axis.sled.y_axis
        return [('x', x_axis.segment.pinion, x_axis.sled.halves),
                ('y', y_axis.segment.pinion, y_axis.sled.halves)]

    def test_each_pinion_turns_one_tooth_per_tooth_of_travel(self):
        """A tooth of travel redraws the pinion exactly as it was, and
        half a tooth turns it half a tooth."""
        for axis, pinion_node, _ in self.pinions():
            gear = pinion_node.gear
            self.drive(x=0.0, y=0.0)
            at_rest = gear.mesh.vertices.copy()
            centre = gear.mesh.bounds.mean(axis=0)

            # The teeth only: the bore is D-shaped, the nut slot and the
            # screw's clearance cut through the base's rim, and the top
            # is bevelled on a polygon no tooth count divides, so the
            # whole gear comes back a tooth along only after a whole
            # turn.  The band between the base and the bevel does not.
            top = at_rest[:, 2].max()
            teeth = ((numpy.hypot(at_rest[:, 0] - centre[0],
                                  at_rest[:, 1] - centre[1]) > 11.5)
                     & (at_rest[:, 2] > top - 15.0 + 0.5)
                     & (at_rest[:, 2] < top - 1.5))
            self.drive(**{axis: self.TOOTH})
            self.assertLess(
                same_points(gear.mesh.vertices[teeth], at_rest[teeth]),
                self.PLACED,
                f'the {axis} pinion is drawn differently a tooth along')

            self.drive(**{axis: self.TOOTH / 2})
            turned = turned_about(gear, at_rest, centre)
            self.assertAlmostEqual(
                abs(turned), self.TOOTH_TURN / 2, delta=0.01,
                msg=f'half a tooth of {axis} turned the pinion {turned}')

    def test_each_pinion_stands_in_its_racks_gaps_across_the_travel(self):
        """The phase is the one that shares least metal, everywhere on
        the rack.

        The pair shares some metal at any phase -- see `pinion` -- and
        the least it shares is a number of the design.  A pinion that
        did not turn, or turned the wrong way, would be past that least
        within a millimetre of travel; a quarter tooth off, the pair
        shares more.
        """
        for axis, pinion_node, racks in self.pinions():
            most = self.MESHED if axis == 'x' else self.MESHED_Y
            for position in (-94.5, -30.0, 0.0, 1.0, 21.7, 60.0):
                self.drive(**{axis: position})
                meshed = sum(shared(rack, pinion_node.gear) for rack in racks)
                self.assertLess(
                    meshed, most,
                    f'the {axis} pinion at {position} shares {meshed:.1f}')
                if axis != 'x':
                    # The Y pinion is out of phase with each half alone
                    # by the halves' own misalignment, so a quarter
                    # tooth towards one half shares less with it.
                    continue
                pinion_node.save_checkpoint()
                pinion_node.rotate(self.TOOTH_TURN / 4, [0, 0, 1])
                off = sum(shared(rack, pinion_node.gear) for rack in racks)
                pinion_node.restore_checkpoint()
                self.assertGreater(
                    off, meshed,
                    f'the {axis} pinion at {position} shares less a '
                    f'quarter tooth off')

    def test_the_teeth_interleave_cleanly_at_any_one_height(self):
        """A slab of the pair a millimetre thick is clean at the phase
        and teeth-on-teeth a half tooth off, on both axes and along the
        travel."""
        for axis, pinion_node, racks in self.pinions():
            gear = pinion_node.gear
            for position in (-40.0, 45.0):
                self.drive(**{axis: position})
                apex = gear.mesh.bounds[1][2] - 7.5
                slab = Manifold.cube([80, 80, 1.0], True).translate(
                    [0, 0, apex - self.SLAB_BELOW_APEX])
                centre = gear.mesh.bounds.mean(axis=0)
                slab = slab.translate([centre[0], centre[1], 0])

                def slab_shared():
                    gear_slab = solid(gear) ^ slab
                    return sum(((solid(rack) ^ slab) ^ gear_slab).volume()
                               for rack in racks)

                clean = slab_shared()
                self.assertLess(
                    clean, self.SLAB_CLEAN if axis == 'x' else self.SLAB_CLEAN_Y,
                    f'{axis} at {position}: {clean:.3f}')
                pinion_node.save_checkpoint()
                pinion_node.rotate(self.TOOTH_TURN / 2, [0, 0, 1])
                fouled = slab_shared()
                pinion_node.restore_checkpoint()
                self.assertGreater(fouled, self.SLAB_FOULED,
                                   f'{axis} at {position}: {fouled:.3f}')

    ########################################
    # The lifter rods, which lift by turning

    def test_each_z_sled_is_threaded_onto_its_rods(self):
        """Both sockets are on their rods, and neither is in one."""
        self.drive()
        for sled, tower in self.z_pairs():
            for rod in tower.lifter.screw.rods:
                self.assertClear(sled, rod)
            self.assertNear(sled, tower.lifter.screw.rods[0], 1.5)

    def test_the_sleds_stay_threaded_wherever_the_rods_are_turned(self):
        """Clear at heights that are not whole pitches, and at both ends
        of the travel."""
        for height in self.OFF_PITCH + (Z_HOME, Z_MAX):
            self.drive(z=height)
            for sled, tower in self.z_pairs():
                for rod in tower.lifter.screw.rods:
                    self.assertClear(sled, rod)

    def test_the_design_phase_would_run_the_thread_through_the_sockets(self):
        """What the measured phase corrects: turned as the design's own
        constant turns them, the rods cut through both sockets."""
        self.drive()
        turn = z_screw.DESIGN_PHASE - z_screw.PHASE
        for sled, tower in self.z_pairs():
            screw = tower.lifter.screw
            screw.save_checkpoint()
            screw.rotate(turn, [0, 0, 1])
            fouled = sum(shared(sled, rod) for rod in screw.rods)
            screw.restore_checkpoint()
            self.assertGreater(fouled, 100.0)

    def test_the_rods_carry_the_bridge(self):
        """A socket cannot travel its rod unless the rod turns: free
        within its play, on the flank beyond it, both ways."""
        self.drive()
        for sled, tower in self.z_pairs():
            rods = tower.lifter.screw.rods
            for volume in self.displaced(sled, (rods, (0, 0, 1)),
                                         [self.Z_NUT_PLAY]):
                self.assertEqual(volume, 0.0, f'{sled.name} is not free')
            for volume in self.displaced(sled, (rods, (0, 0, 1)),
                                         [self.Z_NUT_STOP]):
                self.assertGreater(volume, 0.0, f'{sled.name} is not held')

    def test_a_whole_turn_of_the_rods_lifts_the_bridge_one_lead(self):
        self.drive()
        extruder = self.node.bridge.extruder.hotend
        at_rest = self.bounds(extruder)
        rods = [rod for _, tower in self.z_pairs()
                for rod in tower.lifter.screw.rods]
        rods_at_rest = [rod.mesh.vertices.copy() for rod in rods]

        self.drive(z=lifter_rod_pitch)

        for rod, before in zip(rods, rods_at_rest):
            self.assertLess(
                same_points(rod.mesh.vertices, before), self.PLACED,
                f'{rod.name} is drawn differently a lead along')
        self.assertMovedBy(extruder, at_rest, [0, 0, lifter_rod_pitch])

    def test_lifting_the_bridge_turns_the_rods_the_way_a_screw_turns(self):
        """A quarter lead of rise is a quarter turn clockwise, on both
        rods and the coupler under them, about the rod's own axis."""
        for side, (_, tower) in zip((1, -1), self.z_pairs()):
            screw = tower.lifter.screw
            parts = list(screw.rods) + [screw.coupler]
            self.drive(z=0.0)
            before = [part.mesh.vertices.copy() for part in parts]
            axis = [side * (TOWER_X + platform_length - RAIL_X), 0.0]
            self.drive(z=lifter_rod_pitch / 4)
            for part, vertices in zip(parts, before):
                turned = turned_about(part, vertices, axis)
                self.assertAlmostEqual(
                    turned, -90.0, delta=0.01,
                    msg=f'{part.name} turned {turned} for a quarter lead')

    ########################################
    # Homing and the ends of travel

    def test_each_axis_homes_onto_its_own_switch(self):
        """Half a millimetre short of home the tripping part is clear
        of the switch; half a millimetre past it, it presses the lever."""
        x_axis = self.node.x_axis
        y_axis = x_axis.sled.y_axis
        trips = [
            ('x', X_HOME, x_axis.sled.joiners[0], x_axis.segment.switch),
            ('y', Y_HOME, y_axis.sled.corners[0].endcap, y_axis.segment.switch),
            ('z', Z_HOME, self.node.bridge.screws[1],
             self.node.left_tower.switch),
            ('z', Z_HOME, self.node.bridge.screws[0],
             self.node.right_tower.switch),
        ]
        for axis, home, part, switch in trips:
            self.drive(**{axis: home + self.TOUCH})
            self.assertClear(part, switch)
            self.drive(**{axis: home - self.TOUCH})
            self.assertFouls(part, switch)
            self.drive(**{axis: 0.0})

    def test_each_travel_ends_on_its_hard_stop(self):
        """X and Y stop when the far joiner's block meets the pinion; Z
        stops with the sled's top at the top of the rails, and would
        meet the brace a few millimetres further."""
        x_axis = self.node.x_axis
        y_axis = x_axis.sled.y_axis
        stops = [('x', X_MAX, x_axis.sled.joiners[1], x_axis.segment.pinion.gear),
                 ('y', Y_MAX, y_axis.sled.corners[1].endcap,
                  y_axis.segment.pinion.gear)]
        for axis, end, part, against in stops:
            self.drive(**{axis: end - self.TOUCH})
            self.assertClear(part, against)
            self.drive(**{axis: end + self.TOUCH})
            self.assertFouls(part, against)
            self.drive(**{axis: 0.0})

        self.drive(z=Z_MAX)
        sled = self.node.bridge.sleds[1]
        self.assertAlmostEqual(
            sled.mesh.bounds[1][2], BRIDGE_Z + Z_MAX + 50.0, delta=self.PLACED)
        self.assertClear(self.node.bridge.extruder.motor_clip,
                         self.node.brace.centre)
        self.drive(z=Z_MAX + 4.0)
        self.assertFouls(self.node.bridge.extruder.motor_clip,
                         self.node.brace.centre)

    def test_every_instruction_lands_on_the_position_it_names(self):
        self.drive()
        for name, instruction in type(self.node).instructions.items():
            simulation = Sim(self.node, TICK)
            simulation.trigger(name)
            simulation.run(instruction.duration)
            for driver, target in instruction.targets.items():
                native = getattr(type(self.node), driver).native(target)
                self.assertAlmostEqual(
                    simulation.state[driver], native, delta=self.PLACED,
                    msg=f'{name} should leave {driver} at {target}')

    def test_homing_takes_the_firmwares_time(self):
        """X homes at 50 mm/s and Z at 4 mm/s, to the tick: a third of
        the way through each run the axis is a third of the way home,
        and no run is faster than the firmware."""
        self.drive()
        self.assertLessEqual((0 - X_HOME) / X_HOMING_TIME,
                             z_screw.XY_HOMING_RATE)
        self.assertLessEqual((0 - Z_HOME) / Z_HOMING_TIME,
                             z_screw.HOMING_RATE)
        self.assertGreater((X_MAX - X_HOME) / X_HOMING_TIME,
                           0.97 * z_screw.XY_HOMING_RATE)
        self.assertGreater((Z_MAX - Z_HOME) / Z_HOMING_TIME,
                           0.99 * z_screw.HOMING_RATE)

        simulation = Sim(self.node, TICK)
        simulation.trigger('HomeX')
        simulation.run(X_HOMING_TIME / 4)
        self.assertAlmostEqual(simulation.state['x'], X_HOME / 4,
                               delta=self.PLACED)

        simulation = Sim(self.node, TICK)
        simulation.trigger('HomeZ')
        simulation.run(Z_HOMING_TIME / 2)
        self.assertAlmostEqual(z_screw.lift(simulation.state['z']),
                               Z_HOME / 2, delta=self.PLACED)

    ########################################
    # The cable chains

    def chains(self):
        """Each chain with its axis, its anchors, three positions of the
        travel and the parts of the machine it passes."""
        x_axis = self.node.x_axis
        return [
            ('x', x_axis.chain, x_axis.chain_anchor, x_axis.sled.chain_mount,
             (X_HOME, 0.0, X_MAX),
             [x_axis.segment.segment, x_axis.rails[1], x_axis.segment.motor,
              x_axis.sled.halves[0], x_axis.sled.joiners[0]]),
            ('z', self.node.z_chain, self.node.left_tower.chain_anchor,
             self.node.bridge.chain_anchor, (Z_HOME, 0.0, Z_MAX),
             list(self.node.left_tower.rails)
             + [self.node.left_tower.base, self.node.brace.endcaps[1],
                self.node.bridge.segments[1]]),
        ]

    def links_of(self, chain):
        return [link for link in chain.links if not link._omitted]

    def test_each_chain_has_the_links_its_travel_needs(self):
        """As many links as the bend, the farthest reach and a straight
        link in each anchor take, from the anchors and the ends of the
        travel, and no more drawn; and at both ends of the travel the
        end links do lie straight."""
        for axis, chain, *_ in self.chains():
            radius = (chain.top_z - chain.bottom_z) / 2
            apart = chain.bottom_x - chain.top_x
            reach = max(abs(apart + chain.least), abs(apart + chain.most))
            wanted = math.ceil((math.pi * radius + reach)
                               / cable_chain_pitch) + 2
            links = self.links_of(chain)
            self.assertEqual(len(links), wanted)
            for position in (chain.least, chain.most):
                self.drive(**{axis: position - (0.0 if axis == 'x' else -25.0)})
                for link in (links[0], links[-1]):
                    height = link.mesh.bounds[1] - link.mesh.bounds[0]
                    self.assertAlmostEqual(
                        height[2 if axis == 'x' else 0], cable_chain_height,
                        delta=0.01, msg=f'{link.name} is not straight')
            self.drive(**{axis: 0.0})
        self.assertEqual(len(self.links_of(self.node.x_axis.chain)), 19)
        self.assertEqual(len(self.links_of(self.node.z_chain)), 19)

    def test_the_chains_end_links_stay_seated_in_their_anchors(self):
        """At both ends of the travel and in the middle, the first link
        nests in the fixed anchor and the last in the moving one, and no
        link touches the machine."""
        for axis, chain, fixed, moving, positions, machine in self.chains():
            for position in positions:
                self.drive(**{axis: position})
                links = self.links_of(chain)
                self.assertFouls(links[0], fixed)
                self.assertFouls(links[-1], moving)
                for link in links:
                    for part in machine:
                        self.assertClear(link, part)
            self.drive(**{axis: 0.0})

    def test_the_links_follow_the_sled_one_pitch_apart(self):
        """The chain moves as a chain: the moving end goes with the
        sled, the fixed end stays, and every link stands one pitch from
        the next on the runs and no further apart than the bend's
        outside allows in the bend."""
        for axis, chain, fixed, moving, *_ in self.chains():
            radius = (chain.top_z - chain.bottom_z) / 2
            widest = cable_chain_pitch * (radius + cable_chain_height) / radius
            self.drive(**{axis: 0.0})
            links = self.links_of(chain)
            first_before = self.bounds(links[0])
            last_before = self.bounds(links[-1])
            mount_before = self.bounds(moving)
            self.drive(**{axis: 33.0})
            self.assertStill(links[0], first_before)
            moved = moving.mesh.bounds - mount_before
            numpy.testing.assert_allclose(
                links[-1].mesh.bounds - last_before, moved, atol=0.6,
                err_msg=f'the {axis} chain\'s last link does not follow')
            centres = [link.mesh.centroid for link in links]
            for one, other in zip(centres, centres[1:]):
                apart = float(numpy.linalg.norm(other - one))
                self.assertLessEqual(apart, widest + 0.01)
                self.assertGreaterEqual(apart, 0.9 * cable_chain_pitch)
            self.drive(**{axis: 0.0})

    def test_the_wires_run_through_the_chains(self):
        """Each strand is a flexible leaf inside its chain: it touches
        no other strand, stays within the links' envelope along the
        whole travel, and shares with each link no more than the graze
        the design's own bundle makes on the barrel's chamfer."""
        for axis, chain, *_ in self.chains():
            strands = [strand for strand in chain.strands
                       if not strand._omitted]
            self.assertEqual(len(strands), chain.wires)
            for position in (-30.0, 0.0, 45.0):
                self.drive(**{axis: position})
                links = self.links_of(chain)
                envelope = numpy.array([
                    numpy.min([link.mesh.bounds[0] for link in links], axis=0),
                    numpy.max([link.mesh.bounds[1] for link in links], axis=0)])
                for strand in strands:
                    self.assertFalse(strand.rigid)
                    for link in links:
                        self.assertIntersectVolumeBelow(strand, link, self.GRAZE)
                    bounds = strand.mesh.bounds
                    self.assertTrue(
                        (bounds[0] >= envelope[0] - 1.0).all()
                        and (bounds[1] <= envelope[1] + 1.0).all(),
                        f'{strand.name} leaves its chain at {axis}={position}')
                # Neighbouring strands lie side by side and touch along
                # a line; a tessellated tangency shares a sliver of
                # rounding, not metal.
                for one, other in zip(strands, strands[1:]):
                    self.assertIntersectVolumeBelow(one, other, self.TANGENT)
            self.drive(**{axis: 0.0})

    ########################################
    # The filament

    def on_the_spool(self, vertices):
        """The vertices of the layer: molejo lays a path's rings out in
        path order, and the helix is the first element."""
        rings = filament_module.PATH_SAMPLES + 1
        return vertices[:rings * filament_module.PROFILE_SAMPLES]

    def test_the_layer_lies_on_the_spool_hub(self):
        """The turns on the spool run at the hub's radius plus half a
        stock, across the hub, and the stock's rings reach the hub."""
        self.drive()
        strand = self.node.filament
        spool = self.node.spool_stand.spool
        centre = spool.mesh.bounds.mean(axis=0)
        layer = self.on_the_spool(strand.mesh.vertices)
        radial = numpy.hypot(layer[:, 0] - centre[0], layer[:, 2] - centre[2])
        self.assertAlmostEqual(
            radial.min(), spool_hub_diam / 2, delta=0.05,
            msg='the layer does not lie on the hub')
        self.assertAlmostEqual(
            radial.max(), spool_hub_diam / 2 + filament_diam, delta=0.05)
        self.assertLess(abs(layer[:, 1] - centre[1]).max(),
                        filament_module.TRAVERSE / 2 + filament_diam)

    def test_the_run_goes_through_the_brace_into_the_extruder(self):
        """Down through the brace centre's hole and straight into the
        inlet on the machine's axis, clear of everything on the way,
        wherever the bridge stands."""
        strand = self.node.filament
        brace = self.node.brace
        extruder = self.node.bridge.extruder
        passed = [brace.centre] + list(brace.braces) + list(brace.endcaps) \
            + [extruder.idler, extruder.fan_shroud, extruder.fan_clip,
               extruder.fan, extruder.motor, extruder.compression_screw,
               self.node.spool_stand.holder, self.node.spool_stand.axle] \
            + list(self.node.right_tower.rails)
        for height in (Z_HOME, 0.0, Z_MAX):
            self.drive(z=height)
            vertices = strand.mesh.vertices
            in_hole = vertices[abs(vertices[:, 2] - HOLE_Z) < 1.0]
            self.assertGreater(len(in_hole), 0)
            self.assertLess(numpy.hypot(in_hole[:, 0], in_hole[:, 1]).max(),
                            5.0 - 0.1)
            self.assertAlmostEqual(vertices[:, 2].min(), INLET_Z + height,
                                   delta=0.05)
            tail = vertices[vertices[:, 2] < INLET_Z + height + 0.5]
            self.assertLess(numpy.hypot(tail[:, 0], tail[:, 1]).max(),
                            filament_diam / 2 + 0.05)
            for part in passed:
                self.assertClear(strand, part)

    def test_driving_z_redraws_the_run_and_leaves_the_spool(self):
        strand = self.node.filament
        self.drive(z=0.0)
        before = strand.mesh.vertices.copy()
        self.drive(z=64.0)
        after = strand.mesh.vertices
        self.assertEqual(len(after), len(before))
        numpy.testing.assert_allclose(
            self.on_the_spool(after), self.on_the_spool(before),
            atol=self.PLACED)
        self.assertAlmostEqual(after[:, 2].min() - before[:, 2].min(), 64.0,
                               delta=0.05)

    ########################################
    # What the viewer is handed

    def test_the_flexible_parts_travel_into_the_viewer_as_shapes(self):
        """The strands and the filament are published as shapes whose
        parameters name the machine's own drivers, beside the three
        drivers and the four instructions."""
        self.drive()
        with symbolic_document(self.node) as (declarations, instructions):
            root = serialize_node(self.node, lambda node: node.stl_file)
            self.assertEqual(document_version(root), 3)

            flexible = {}

            def walk(entry, path):
                if 'flexible' in entry:
                    flexible[path] = entry['flexible']
                for child in entry.get('children', []):
                    walk(child, f'{path}.{child["name"]}' if path
                         else child['name'])
            walk(root, '')

            strands = [path for path in flexible if '.strands-' in path]
            self.assertEqual(len(strands), 6 + 12)
            self.assertIn('filament', flexible)
            self.assertEqual(flexible['filament']['tech'], 'molejo')
            self.assertIn('z', flexible['filament']['params']['head'])
            self.assertIn('x', flexible['x_axis.chain.strands-0']['params']['bottom'])
            self.assertEqual(set(declarations), {'x', 'y', 'z'})
            self.assertEqual(set(instructions),
                             {'HomeX', 'HomeY', 'HomeZ', 'Rest'})
