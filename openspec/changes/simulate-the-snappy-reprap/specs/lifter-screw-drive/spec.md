## ADDED Requirements

### Requirement: The Z sleds are threaded on the lifter rods and stay so at every height
Each Z sled's acme socket SHALL be threaded on the two stacked lifter rods
of its tower: sharing no volume with either rod, its socket within 1.5 mm
of the rod, at rest and at heights that are not whole pitches (2.5, 33.3
and -77.7 mm) and at both ends of the travel. The rods SHALL be turned by
the design's own phase constant plus 193.5 degrees, the middle of the
window (174 to 213 degrees) in which the sockets clear the rods; turned
by the design's constant alone the rods SHALL be shown to run through both
sockets.

#### Scenario: Between pitches
- **WHEN** the bridge stands at 2.5 mm, 33.3 mm, -77.7 mm, its home and its
  top
- **THEN** neither socket shares volume with either of its rods

#### Scenario: The design's own phase
- **WHEN** the rods are turned back by 193.5 degrees
- **THEN** each socket shares over 100 mm^3 with its rods

### Requirement: The rods carry the bridge
A socket SHALL be free to move 0.25 mm along the rod's axis either way and
SHALL foul the rod's flank 0.7 mm either way: the thread is the load path.

#### Scenario: Pushed along the axis
- **WHEN** a Z sled is displaced 0.25 mm along z either way
- **THEN** it shares no volume with its rod
- **WHEN** it is displaced 0.7 mm either way
- **THEN** it interferes with its rod

### Requirement: The rods turn with the bridge at the acme lead, clockwise to lift
Both rods and the coupler under them SHALL turn together, one turn per
8 mm of bridge, clockwise seen from above to lift, while the lifter motors'
cases stand still.

#### Scenario: A whole turn is one lead
- **WHEN** the bridge is driven up one lead (8 mm)
- **THEN** every rod's vertices stand exactly where they stood, and the hot
  end has risen 8 mm

#### Scenario: A quarter lead is a quarter turn
- **WHEN** the bridge is driven up 2 mm
- **THEN** each rod and each coupler has turned -90 degrees about its axis
