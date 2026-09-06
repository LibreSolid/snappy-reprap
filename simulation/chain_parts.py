"""The printed parts of the two cable chains and their anchors."""

from simulation import colors
from simulation.part import ScadPart
from simulation.scad import cable_chain_link, cable_chain_mount


class CableChainLink(ScadPart):
    """One link: a barrel with a socket at one end and a pin at the
    other, so it nests in the next."""

    color = colors.SPRING_GREEN

    def render(self):
        return cable_chain_link.cable_chain_link()


class ChainJoinerMount(ScadPart):
    """The anchor that snaps onto a rail's side half-joiner."""

    color = colors.WHITE

    def render(self):
        return cable_chain_mount.cable_chain_joiner_mount()


class ChainJoinerVerticalMount(ScadPart):
    """The anchor on the bridge, for the chain that climbs the tower."""

    color = colors.WHITE

    def render(self):
        return cable_chain_mount.cable_chain_joiner_vertical_mount()
