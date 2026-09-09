Behaviour-preserving throughout: the acceptance is that every leaf's world
matrix is unchanged at every pose, so evidence is captured before the first
motion edit and compared after the last. Run everything from the project
root with `PYTHONPATH=.` and the workspace venv
(`/home/asa/devel/libresolid-studio/.venv`). Never run two suites at once.
Never edit a test: if one blocks, stop and report the assertion and why.

## 0. The working state

- [x] 0.1 `git status`: the tree is clean at `18fd943` on `master`, so
      there is nothing to commit before the refactor. Confirm it; if
      anything has appeared since, commit it as
      `chore: commit the working state before the motion refactor`,
      leaving `*~`, `#*#`, screenshots and `.env` untracked.
      Confirmed: `git status --porcelain` showed only the untracked
      `openspec/changes/move-onto-motion/` proposal directory. No commit
      needed; stage 0 is a no-op as the proposal said.

## 1. Stage A — imports and baseline

- [x] 1.1 Import `TranslationalPort` and `RotationalPort` from
      `solid_node.motion.ports` in the seven modules that name them:
      `cable_chain.py`, `filament.py`, `x_axis.py`, `y_axis.py`,
      `motor_segment.py`, `tower.py`, `lifter.py`. Change nothing else.
      `simulation/test_snappy_reprap.py` imports no moved name and is not
      touched.
- [x] 1.2 Confirm the model imports:
      `PYTHONPATH=. .venv/bin/python -c "import simulation.snappy_reprap"`.
      Confirmed: imports cleanly.
- [x] 1.3 Run the whole suite and record each contract's result here:
      `PYTHONPATH=. .venv/bin/solid test --faceted simulation/snappy_reprap.py`.
      This is the baseline; it is not known to have been green on this
      framework tree, and whatever it is, it is what stage B must match.

      Baseline: **28 tests, 28 passed, 0 failed** (faceted kernel, volume
      epsilon 0 mm³, 40.31s). The proposal's "27 contracts" underestimates
      the suite by one; all 28 are green:
      test_a_whole_turn_of_the_rods_lifts_the_bridge_one_lead,
      test_driving_x_slides_the_sled_and_all_it_carries,
      test_driving_y_slides_the_bed_only,
      test_driving_z_lifts_the_bridge_and_nothing_else,
      test_driving_z_redraws_the_run_and_leaves_the_spool,
      test_each_axis_homes_onto_its_own_switch,
      test_each_chain_has_the_links_its_travel_needs,
      test_each_pinion_stands_in_its_racks_gaps_across_the_travel,
      test_each_pinion_turns_one_tooth_per_tooth_of_travel,
      test_each_travel_ends_on_its_hard_stop,
      test_each_z_sled_is_threaded_onto_its_rods,
      test_every_instruction_lands_on_the_position_it_names,
      test_homing_takes_the_firmwares_time,
      test_lifting_the_bridge_turns_the_rods_the_way_a_screw_turns,
      test_the_chains_end_links_stay_seated_in_their_anchors,
      test_the_design_phase_would_run_the_thread_through_the_sockets,
      test_the_flexible_parts_travel_into_the_viewer_as_shapes,
      test_the_layer_lies_on_the_spool_hub,
      test_the_links_follow_the_sled_one_pitch_apart,
      test_the_machine_rests_where_the_design_draws_it,
      test_the_rods_carry_the_bridge,
      test_the_run_goes_through_the_brace_into_the_extruder,
      test_the_sleds_stay_threaded_wherever_the_rods_are_turned,
      test_the_teeth_interleave_cleanly_at_any_one_height,
      test_the_wires_run_through_the_chains,
      test_the_x_sled_rides_the_x_rails,
      test_the_y_sled_rides_the_y_rails,
      test_the_z_sleds_ride_the_tower_rails.
- [x] 1.4 Capture poses:
      `PYTHONPATH=. .venv/bin/python <shop>/docs/motion-general-refactor/capture_poses.py capture simulation.snappy_reprap:SnappyReprap /tmp/snappy-before.json`,
      plus an `extra` pose file covering `HomeX`, `HomeY`, `HomeZ`, `Rest`
      and two intermediate poses (one with all three axes off nought).
      Extra pose file (native driver units: `x`/`y` in mm, `z` in the
      rods' own degrees via `z_screw.angle`, matching what `set_state`
      takes and what `drive()` in the test file does):
      `HomeX={x:-94.56}`, `HomeY={y:-94.76}`,
      `HomeZ={z: z_screw.angle(Z_HOME) = 4311.45}`,
      `Rest={x:0, y:0, z:-0.0}`,
      `mid1={x:-40, y:-40, z: z_screw.angle(40)=-1800.0}` (all three off
      nought), `mid2={x:60, y:20, z: z_screw.angle(70)=-3150.0}`.
      Captured 17 poses (11 default/range/time + 6 extra), 170 leaves,
      to `/tmp/snappy-before.json`.
- [x] 1.5 Commit as `refactor(simulation): import ports from solid_node.motion`,
      with the baseline in the message body.

## 2. Stage B — the joints

- [ ] 2.1 `XSled.travel = Prismatic(axis=(-1, 0, 0), unit='mm')` and
      `YSled.travel = Prismatic(axis=(0, -1, 0), unit='mm')`: the design's
      slide sign becomes the joint's axis. No `at`, no `range` (see the
      proposal's **Tests**).
- [ ] 2.2 `Bridge.lift = Prismatic(axis=(0, 0, 1), unit='mm')`.
- [ ] 2.3 `Pinion.spin = Revolute(axis=(0, 0, 1), unit='deg')` and
      `LifterScrew.spin = Revolute(axis=(0, 0, 1), unit='deg')`: each turns
      on its parent frame's own z axis, so the default anchor is the right
      line and neither declaration repeats a placement constant.
- [ ] 2.4 Delete `MotorSegment.simulate()` and `Lifter.simulate()`, with the
      imports they alone used (`pinion` and `Z` in `motor_segment.py`, `Z`
      in `lifter.py`).

## 3. Stage B — the relations

- [ ] 3.1 `pinion.py`: replace `angle()` with
      `DEGREES_PER_MM = SIGN * 360 / MM_PER_TURN`, keeping `SIGN`, `PHASE`,
      `MM_PER_TURN` and the module's account of the mesh untouched.
      `z_screw.angle()` and `z_screw.lift()` stay — the suite calls both.
- [ ] 3.2 `snappy_reprap.py`: add the module constants
      `HIGH_IN_STRAND`, `ABOVE_IN_STRAND`, `INLET_IN_STRAND`, each
      `in_strand_frame(<point on the machine's axis>, STRAND_ORIGIN)` with
      the `lift` term left out of the inlet.
- [ ] 3.3 State the root's seven relations in the class body, in the
      proposal's order: `x` and `y` to the two sleds' `travel` by path;
      `z` to each tower's `lifter.screw.spin` with `offset=z_screw.PHASE`;
      `z` to `bridge.lift` with `ratio=z_screw.SCALE`; `bridge.lift` to
      `z_chain.offset` with `offset=Z_CHAIN_OFFSET` and to `filament.head`
      with `offset=INLET_IN_STRAND[0]`.
- [ ] 3.4 State `sled.travel.drives(segment.pinion.spin,
      ratio=pinion.DEGREES_PER_MM, offset=pinion.PHASE)` on `XAxis` and on
      `YAxis`, and `sled.travel.drives(chain.offset)` on `XAxis`.
- [ ] 3.5 Delete the six forwarding ports — `XAxis.position`, `XAxis.bed`,
      `YAxis.position`, `MotorSegment.travel`, `ZTower.screw`,
      `Lifter.angle` — and the four `simulate()` methods that only carried
      them (`XAxis`, `YAxis`, `ZTower`, and the two above).
- [ ] 3.6 Shrink `SnappyReprap.simulate()` to the four constant filament
      bindings (`high_x`, `above_x`, `axis_y`, `axis_z`). `CableChain.simulate()`
      is unchanged: the nineteen link stations and the strands' molejo
      parameters stay as they are, for the reasons in **Known gaps**.

## 4. Evidence again

- [ ] 4.1 Re-capture poses to `/tmp/snappy-after.json` (same model, same
      extra poses) and run `capture_poses.py compare`. Expect either a
      maximum deviation of 0, or a deviation of order 1e-13 on the
      Z-carried leaves and the two gears — the one-ulp re-association the
      proposal measures. Anything larger is a real change and stops the
      work.
- [ ] 4.2 Run the suite again: the same contracts green as at 1.3, none
      newly red. Record the counts before and after.
- [ ] 4.3 Add one sentence to `README.md`'s simulation section saying the
      machine's freedoms are joints on the bodies that have them and its
      transmissions are relations, and that the cable chains' link
      stations are still placed by hand.
- [ ] 4.4 Commit as
      `refactor(simulation): move snappy-reprap onto solid-node joints and couplings`,
      with the pose comparison and the test result in the body.
- [ ] 4.5 Report: the two commit hashes, the pose comparison line, the test
      counts before and after, every deviation from this proposal, and every
      test you believe needs a change with the reason. Do not sync or
      archive this change; the orchestrator does that after review.
