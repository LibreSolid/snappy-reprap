"""The controller mount on the back of the left tower."""

from simulation import colors
from simulation.part import ScadPart
from simulation.scad import ramps_mount


class RampsMount(ScadPart):
    color = colors.LIGHT_BLUE

    def render(self):
        return ramps_mount.ramps_mount()
