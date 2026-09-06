# Design Reading Specification

## Purpose

What the simulation layer reads from the OpenSCAD design and how: a leaf per module in the design's colours, every dimension from config.scad, the design's sources as every leaf's rebuild dependency, and what the design cannot draw left out by name.

## Requirements

### Requirement: Every part is one module of the design, coloured as the design paints it
Every printed and bought part of the machine SHALL be one leaf whose
geometry is one module of the OpenSCAD design called as the design calls
it, and whose colour is the hex value of the `color()` that module paints
itself with. A module the design leaves unpainted SHALL carry OpenSCAD's
default face colour (`#f9d72c`); a bought part the design draws in several
colours SHALL carry the colour of the most of it; a wiring bundle SHALL
carry the design's colour for its first wire. The design's own sources
SHALL NOT be edited by the layer.

#### Scenario: A leaf is rebuilt when its module changes
- **WHEN** any `.scad` file of the design is edited
- **THEN** every leaf reports itself stale, because each carries the whole
  `.scad` source set in its own source set

#### Scenario: The published document names the design's colours
- **WHEN** the model is built
- **THEN** every rigid leaf's `color` in `viewer.json` is one of the
  design's colours, and the two Z sleds and the four sled halves are
  `MediumSlateBlue`

### Requirement: Every dimension is read from config.scad
Every dimension the layer places a part by SHALL be a top-level name of
`config.scad`, evaluated by OpenSCAD once at import, under that name. A
value the design writes inside a module body SHALL be restated once, in
`params.py`, annotated with the module it belongs to.

#### Scenario: A derived name is what the design derives
- **WHEN** `simulation.params` is imported
- **THEN** `platform_z` is `rail_height + groove_height + rail_offset`
  (76.5 mm) and `cantilever_length` is 44.0 mm, as `config.scad` derives
  them

### Requirement: What the design cannot draw is left out and named
A harness run whose `wiring()` sweep produces no geometry under OpenSCAD
2021.01 SHALL NOT be a leaf; the layer SHALL name each such run where it
would have stood. Four runs qualify: the extruder motor's wires, the
harness down the bridge's left span, and the bridge harness down the left
tower with its pigtail.

#### Scenario: No leaf is empty
- **WHEN** the model is built
- **THEN** every piece in `viewer.json` has a size and a positive volume
