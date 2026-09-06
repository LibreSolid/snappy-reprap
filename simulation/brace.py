"""The brace across the top of the towers, with the rail endcaps that
snap it onto them.  ``top_brace_assembly_2`` of the design."""

from solid_node.node import AssemblyNode

from simulation import colors
from simulation.params import (
    joiner_width,
    motor_rail_length,
    platform_length,
    rail_height,
    rail_length,
)
from simulation.part import ScadPart
from simulation.place import place, right, up, yrot, zrot
from simulation.rails import RailZEndcap
from simulation.scad import bridge_brace, bridge_brace_center


#: Where the endcaps stand: over the towers' rails.
ENDCAP_X = motor_rail_length / 2 + rail_length + platform_length


class BridgeBrace(ScadPart):
    color = colors.UNPAINTED

    def render(self):
        return bridge_brace.bridge_brace()


class BridgeBraceCenter(ScadPart):
    color = colors.UNPAINTED

    def render(self):
        return bridge_brace_center.bridge_brace_center()


class TopBrace(AssemblyNode):
    centre = BridgeBraceCenter()
    braces = BridgeBrace().repeat(2)
    endcaps = RailZEndcap().repeat(2)

    def render(self):
        place(self.centre, up(rail_height - joiner_width / 2))
        for side, brace in zip((1, -1), self.braces):
            place(brace, up(rail_height - joiner_width / 2),
                  right(side * (rail_length + motor_rail_length) / 2))
        for side, endcap in zip((1, -1), self.endcaps):
            place(endcap, zrot(90 - 90 * side), right(ENDCAP_X), yrot(-90),
                  zrot(90))
