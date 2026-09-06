## ADDED Requirements

### Requirement: The three axes are drivers on the machine root
The root SHALL declare drivers `x`, `y` and `z`, read and set in
millimetres in the design's own slide coordinates -- how far the X sled
stands to the left of its rail's middle, how far the Y sled stands forward
of its, how high the bridge stands above the middle of the towers' rails --
each defaulting to nought, which is the pose `final_assembly_9` draws.
Each SHALL range from where its switch is first touched to where its
travel physically ends. `z` SHALL hold the lifter rods' angle in degrees
and declare the scale that makes it millimetres: negative, one 8 mm acme
lead per turn.

#### Scenario: The machine opens at rest
- **WHEN** the model is built with no driver touched
- **THEN** a simulation's state is `x`, `y` and `z` all at 0.0

#### Scenario: A maker reads the ranges
- **WHEN** the drivers are inspected
- **THEN** `x` ranges -94.56 to 100.5 mm, `y` -94.76 to 100.5 mm, and `z`
  -95.81 to 111.0 mm, and `z` carries scale `-8/360` mm per degree

### Requirement: Each driver carries its load and nothing else
Driving X SHALL slide the X sled, the whole Y axis standing on it and the
bed along the X rail, by the driven distance along -x. Driving Y SHALL
slide the Y sled and the glass along the Y rail, by the driven distance
along -y, and nothing else. Driving Z SHALL lift the bridge with its
extruder, both Z sleds and the chain anchor, and nothing else. The rails,
the towers, the brace and the motors SHALL NOT move.

#### Scenario: X moves the sled and what it carries
- **WHEN** `x` is driven to 37.5 mm
- **THEN** a sled half, a joiner, the Y motor and the glass have moved by
  exactly -37.5 mm in x, and the X motor segment, an X rail, a tower base
  and the hot end have not moved

#### Scenario: Y moves the bed only
- **WHEN** `y` is driven to -41 mm
- **THEN** the Y sled's halves, endcaps, screws and glass have moved by
  +41 mm in y, and the Y motor segment, rails and endcaps and the X sled
  have not

#### Scenario: Z lifts the bridge only
- **WHEN** `z` is driven to 52 mm
- **THEN** the hot end, a bridge segment, a Z sled and the chain anchor
  have moved by +52 mm in z, and the tower rails, the brace, a lifter
  motor and the glass have not

### Requirement: Each axis homes to its own switch and stops on its own hard stop
Each home SHALL be the position at which the part that trips the switch
first touches the switch's lever: for X the hard-stop block of the left
joiner against the switch clipped beside the X motor, for Y the same block
of the near endcap against the Y switch, for Z the adjustment screw of each
Z sled against the switch at the top of its tower base. X and Y SHALL end
where the far joiner's or endcap's block meets the pinion; Z SHALL end
where the top of the Z sleds reaches the top of the tower rails,
`rail_length - rail_height/2`. The firmware's travels (198 mm, 198 mm,
220 mm) SHALL be recorded beside these and not used as ranges.

#### Scenario: Half a millimetre either side of home
- **WHEN** an axis stands 0.5 mm short of its home
- **THEN** the tripping part shares no volume with the switch
- **WHEN** it stands 0.5 mm past its home
- **THEN** the tripping part interferes with the switch

#### Scenario: Half a millimetre either side of the far end
- **WHEN** X or Y stands 0.5 mm short of its far end
- **THEN** the far block shares no volume with the pinion
- **WHEN** it stands 0.5 mm past it
- **THEN** the far block interferes with the pinion

#### Scenario: The top of Z
- **WHEN** `z` stands at 111.0 mm
- **THEN** the Z sled's top is at the top of the rails and the extruder
  motor clip clears the brace centre; 4 mm higher it interferes with it

### Requirement: Homing instructions run each axis to its switch at the firmware's rate
The root SHALL offer `HomeX`, `HomeY` and `HomeZ`, each moving only its own
axis to its home, and `Rest`, moving all three to nought. Each instruction
SHALL last its axis's whole declared travel at the firmware's homing
feedrate for that axis: 50 mm/s for X and Y, 4 mm/s for Z.

#### Scenario: An instruction lands where it says
- **WHEN** any instruction runs to completion in a simulation
- **THEN** each named axis stands at the instruction's target

#### Scenario: Homing proceeds at the feedrate
- **WHEN** `HomeX` has run for a third of its duration from rest
- **THEN** `x` stands a third of the way to its home
- **WHEN** `HomeZ` has run for a third of its duration from rest
- **THEN** the bridge stands a third of the way down, with the rods
  turning all the way
