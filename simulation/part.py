"""The shape every part of this layer takes.

Every leaf in the tree is one part of the machine and its geometry
comes from the OpenSCAD design, so every leaf shares one thing: it
depends on the whole .scad source set.  That lives here rather than
being repeated in every file.
"""

from solid_node.node import Solid2Node

from simulation.scad import scad_sources


class ScadPart(Solid2Node):
    """A part whose geometry is one OpenSCAD module of the design.

    The framework invalidates a node from the Python files it imports,
    which here decide only where a part goes, never what it is.  The
    .scad sources decide that, and no Python import mentions them, so
    each part adds them to its own source set.

    A subclass names its colour, which is the colour the design's own
    module paints it, and returns the module call from `render()`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()
