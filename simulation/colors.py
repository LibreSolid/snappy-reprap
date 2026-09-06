"""Part colours, taken from the design's own ``color()`` calls.

Every printed part of Snappy is coloured by the module that draws it,
and the bought parts by ``vitamins.scad`` and ``NEMA.scad``.  A node's
colour is a property of the node rather than of the geometry it
renders, so the same palette is restated here as the hex colours the
viewer wants, one name per OpenSCAD colour, and each leaf carries the
colour of the module it calls.

A bought part the design draws in several colours -- a motor's grey
body and silver shaft, a bearing's silver races and dark grey shield --
is one leaf here and gets one colour: the colour of the most of it.
The design draws the glass with an alpha of one half; a node colour
carries no alpha, so the glass is opaque here.
"""

# OpenSCAD's named colours, as the design uses them.
SPRING_GREEN = '#00ff7f'
MEDIUM_SLATE_BLUE = '#7b68ee'
SIENNA = '#a0522d'
SALMON = '#fa8072'
STEEL_BLUE = '#4682b4'
LIGHT_PINK = '#ffb6c1'
CHOCOLATE = '#d2691e'
TAN = '#d2b48c'
DODGER_BLUE = '#1e90ff'
YELLOW_GREEN = '#9acd32'
LIGHT_BLUE = '#add8e6'
TURQUOISE = '#40e0d0'
VIOLET = '#ee82ee'
SANDY_BROWN = '#f4a460'
SILVER = '#c0c0c0'
DIM_GRAY = '#696969'
DARK_GRAY = '#a9a9a9'
GOLDENROD = '#daa520'
ORANGE = '#ffa500'

# The design's own RGB vectors.
RAIL = '#e6b3ff'          # [0.9, 0.7, 1.0]: rails, bases, bridge segments
JOINER = '#80b3ff'        # [0.5, 0.7, 1.0]: the YZ joiner
WHITE = '#ffffff'         # [1.0, 1.0, 1.0]: the cable chain mounts
MOTOR = '#666666'         # [0.4, 0.4, 0.4]: a stepper's body, a fan
SWITCH = '#4d4d4d'        # [0.3, 0.3, 0.3]: a microswitch, a hot end
SPOOL = '#808080'         # [0.5, 0.5, 0.5]
GLASS = '#bfffff'         # [0.75, 1.0, 1.0, 0.5], less its alpha

# What a module the design leaves unpainted renders in: OpenSCAD's
# default face colour, from its Cornfield scheme.  The lifter rods and
# couplers, the adjustment and compression screws and the bridge braces
# are drawn this way.
UNPAINTED = '#f9d72c'

# What the design draws no colour for, because it draws no filament:
# the strand is the colour of natural PLA, and the choice is this
# layer's.
FILAMENT = '#f5f0dc'

#: The seventeen wire colours of ``wiring.scad``, in its own order.
#: A bundle of `n` wires from offset `wirenum` takes colours
#: ``(i + wirenum) % 17`` for ``i`` in ``range(n)``.
WIRES = [
    '#333333', '#ff3333', '#00cc00', '#ffff33',
    '#4d4dff', '#ffffff', '#b38000', '#808080',
    '#33e6e6', '#cc00cc', '#009999', '#ffb3b3',
    '#ff80ff', '#809900', '#ffb300', '#b3ff80',
    '#9999ff',
]


def wire(index, wirenum=0):
    """The colour of wire `index` of a bundle starting at `wirenum`."""
    return WIRES[(index + wirenum) % len(WIRES)]
