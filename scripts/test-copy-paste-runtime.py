#!/usr/bin/env python3
"""Isolated vanilla 26.3 behavioral regression for Copy/Paste v1.7.

Uses a non-player armor stand test actor to exercise internal datapack functions.
This complements (not replaces) the opt-in real-player trigger/client harnesses.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'datapacks/copy-paste'
WAREHOUSE=ROOT/'datapacks/warehouse'
sys.path.insert(0,str(ROOT/'scripts'))
import mcc_house as house

# /forceload block ranges (x0, z0, x1, z1): every fixture chunk including the raycast stones at
# x/z=-4, the long-Z Move audit column (x=70, z=0..230) and the 3D house section (x=92..143, z=0..47).
FORCELOAD=[(-16,-16,47,31),(64,0,79,239),(92,0,143,47)]

def integration(java: Path, server: Path):
    work=ROOT/'dist'/('copy-paste-runtime-'+uuid.uuid4().hex[:8])
    work.mkdir(parents=True)
    packs=work/'world/datapacks'
    packs.mkdir(parents=True)

    # Build the innotest 3D-house harness into the same official-server world.
    # It is not executed headlessly, but every generated mcfunction is parsed by
    # vanilla 26.3 so stale/invalid harness commands fail CI before innotest.
    subprocess.run([sys.executable, str(ROOT/'scripts/build-copy-paste-multiplayer-test.py')], check=True)
    import shutil as _shutil
    _shutil.copytree(ROOT/'dist/mcc-multiplayer-test', packs/'mcc-multiplayer-test')

    with zipfile.ZipFile(packs/'copy-paste.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in PACK.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(PACK).as_posix())
    with zipfile.ZipFile(packs/'warehouse.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in WAREHOUSE.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(WAREHOUSE).as_posix())

    harness=packs/'regression'
    funcs=harness/'data/mcc_server_test/function'
    funcs.mkdir(parents=True)
    # The main UI is a macro Dialog; render it with sample values as a static dialog
    # so the official server's registry load rejects any schema error.
    import re as _re
    (harness/'data/mcc_server_test/dialog').mkdir(parents=True)
    for name in ('show','adjust','more_show','edit'):
        show=(PACK/f'data/mcc/function/ui/{name}.mcfunction').read_text(encoding='utf-8').strip().lstrip('$')
        assert show.startswith('dialog show @s '), name
        rendered=_re.sub(r'\$\(([a-z0-9_]+)\)',lambda m:f'sample {m.group(1)}',show[len('dialog show @s '):])
        (harness/f'data/mcc_server_test/dialog/ui_preview_{name}.json').write_text(rendered,encoding='utf-8')
    (harness/'pack.mcmeta').write_text(json.dumps({'pack':{'min_format':121,'max_format':121,'description':'CopyPaste server regression'}}),encoding='utf-8')

    actor='@e[type=minecraft:armor_stand,tag=mcc_server_actor,limit=1]'
    lines=[
        'scoreboard objectives add mccst dummy',
        'scoreboard players set #pass mccst 0',
        'scoreboard players set #fail mccst 0',
        'kill @e[type=minecraft:armor_stand,tag=mcc_server_actor]',
        'kill @e[type=minecraft:block_display,tag=mcc_blueprint]',
        'summon minecraft:armor_stand 0 80 0 {Tags:["mcc_server_actor"],NoGravity:1b,Invisible:1b}',
        f'scoreboard players set {actor} mcc_id 77',
        f'scoreboard players set {actor} mcc_mask 0',
        f'scoreboard players set {actor} mcc_rot 0',
        f'scoreboard players set {actor} mcc_mir 0',
        f'scoreboard players set {actor} mcc_hasa 0',
        f'scoreboard players set {actor} mcc_undo 0',
        f'scoreboard players set {actor} mcc_redo 0',
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_rhead 0',
        f'scoreboard players set {actor} mcc_matphase 0',
        f'scoreboard players set {actor} mcc_matjob 0',
        f'scoreboard players set {actor} mcc_buildconfirm 0',
        f'scoreboard players set {actor} mcc_bpover 0',
        f'scoreboard players set {actor} mcc_bpover_scan 0',
        'fill 0 78 0 40 90 30 air',
    ]
    assertions=[]

    def check(condition,label):
        assertions.append(label)
        lines.extend([
            'scoreboard players set #ok mccst 0',
            f'execute {condition} run scoreboard players set #ok mccst 1',
            'execute if score #ok mccst matches 1 run scoreboard players add #pass mccst 1',
            f'execute if score #ok mccst matches 1 run say MCCST_PASS_{label}',
            'execute unless score #ok mccst matches 1 run scoreboard players add #fail mccst 1',
            f'execute unless score #ok mccst matches 1 run say MCCST_FAIL_{label}',
        ])

    def fixture(x=3,y=80,z=3):
        lines.extend([
            f'fill {x} {y} {z} {x+3} {y+2} {z+3} air',
            f'setblock {x} {y} {z} gold_block',
            f'setblock {x+2} {y} {z} diamond_block',
            f'setblock {x} {y} {z+1} oak_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]',
            f'setblock {x+2} {y} {z+1} iron_block',
            f'scoreboard players set {actor} mcc_has1 1',
            f'scoreboard players set {actor} mcc_has2 1',
            f'scoreboard players set {actor} mcc_hasa 0',
            f'scoreboard players set {actor} mcc_p1x {x}',
            f'scoreboard players set {actor} mcc_p1y {y}',
            f'scoreboard players set {actor} mcc_p1z {z}',
            f'scoreboard players set {actor} mcc_p1d 1',
            f'scoreboard players set {actor} mcc_p2x {x+2}',
            f'scoreboard players set {actor} mcc_p2y {y}',
            f'scoreboard players set {actor} mcc_p2z {z+1}',
            f'scoreboard players set {actor} mcc_p2d 1',
        ])

    def target(x,y,z,dim=1):
        lines.extend([
            f'scoreboard players set {actor} mcc_dstx {x}',
            f'scoreboard players set {actor} mcc_dsty {y}',
            f'scoreboard players set {actor} mcc_dstz {z}',
            f'scoreboard players set {actor} mcc_dstd {dim}',
        ])

    def run_as(function):
        lines.append(f'execute as {actor} at @s run function {function}')

    def scan(n=4):
        for _ in range(n): run_as('mcc:blueprint/scan_batch')

    # -1. Exercise the real raycast entry points used by Pos1 / Pos2 / Anchor / V.
    lines.extend([
        'setblock 0 81 4 stone',
        'setblock -4 81 0 stone',
        'setblock 4 81 0 stone',
        'setblock 0 81 -4 stone',
        f'data merge entity {actor} {{Rotation:[0f,0f]}}',
    ])
    run_as('mcc:select/start_pos1')
    check(f'if score {actor} mcc_p1x matches 0 if score {actor} mcc_p1y matches 81 if score {actor} mcc_p1z matches 4 if score {actor} mcc_has1 matches 1','raycast_pos1_south')
    lines.append(f'data merge entity {actor} {{Rotation:[90f,0f]}}')
    run_as('mcc:select/start_pos2')
    check(f'if score {actor} mcc_p2x matches -4 if score {actor} mcc_p2y matches 81 if score {actor} mcc_p2z matches 0 if score {actor} mcc_has2 matches 1','raycast_pos2_west')
    lines.append(f'data merge entity {actor} {{Rotation:[-90f,0f]}}')
    run_as('mcc:select/start_anchor')
    check(f'if score {actor} mcc_anx matches 4 if score {actor} mcc_any matches 81 if score {actor} mcc_anz matches 0 if score {actor} mcc_hasa matches 1','raycast_anchor_east')
    lines.extend([
        f'scoreboard players set {actor} mcc_clip 0',
        f'data merge entity {actor} {{Rotation:[180f,0f]}}',
    ])
    check('if block 0 81 -4 stone if block 0 81 -3 air','raycast_v_fixture_placed')
    run_as('mcc:select/start_paste')
    check(f'if score {actor} mcc_dstx matches 0 if score {actor} mcc_dsty matches 81 if score {actor} mcc_dstz matches -3','raycast_v_adjacent_cell_north')
    lines.extend([
        'setblock 0 81 4 air',
        'setblock -4 81 0 air',
        'setblock 4 81 0 air',
        'setblock 0 81 -4 air',
        f'data merge entity {actor} {{Rotation:[0f,0f]}}',
    ])

    # -1. Reselecting either endpoint must discard a custom Anchor from the old selection.
    # This reproduces the player-visible failure where Copy/Cut kept rejecting a new
    # selection because mcc_hasa still pointed at an Anchor from a previous region.
    fixture()
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 99',
        f'scoreboard players set {actor} mcc_any 99',
        f'scoreboard players set {actor} mcc_anz 99',
        f'scoreboard players set {actor} mcc_and 1',
        f'execute as {actor} positioned 3 80 3 run function mcc:ray/hit_pos1',
    ])
    check(f'if score {actor} mcc_has1 matches 1 if score {actor} mcc_p1x matches 3 if score {actor} mcc_p1y matches 80 if score {actor} mcc_p1z matches 3 if score {actor} mcc_hasa matches 0','pos1_resets_stale_anchor')
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 99',
        f'scoreboard players set {actor} mcc_any 99',
        f'scoreboard players set {actor} mcc_anz 99',
        f'scoreboard players set {actor} mcc_and 1',
        f'execute as {actor} positioned 5 80 4 run function mcc:ray/hit_pos2',
    ])
    check(f'if score {actor} mcc_has2 matches 1 if score {actor} mcc_p2x matches 5 if score {actor} mcc_p2y matches 80 if score {actor} mcc_p2z matches 4 if score {actor} mcc_hasa matches 0','pos2_resets_stale_anchor')
    run_as('mcc:copy/run')
    check(f'if score {actor} mcc_clip matches 1 if score {actor} mcc_offx matches 0 if score {actor} mcc_offy matches 0 if score {actor} mcc_offz matches 0','reselection_copy_uses_pos1_default_anchor')

    # 0. Default Anchor regression: when no custom Anchor is set, Pos1 is the Anchor.
    # Make Pos1 the max-X/max-Z corner so this fails if Blueprint incorrectly treats
    # the aimed cell as the bounding minimum instead of the Pos1 destination.
    fixture()
    lines.extend([
        f'scoreboard players set {actor} mcc_p1x 5',
        f'scoreboard players set {actor} mcc_p1z 4',
        f'scoreboard players set {actor} mcc_p2x 3',
        f'scoreboard players set {actor} mcc_p2z 3',
    ])
    run_as('mcc:copy/run')
    target(12,80,12)
    run_as('mcc:paste/dispatch')
    scan()
    check(f'positioned 12.0 80.0 12.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={{block_state:"minecraft:iron_block"}},limit=1] if score {actor} mcc_bptx0 matches 10 if score {actor} mcc_bptz0 matches 11','default_anchor_pos1_blueprint_origin')
    check('positioned 10.0 80.0 11.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','default_anchor_pos1_blueprint_offset')

    # Default-anchor Blueprint Flip mirrors inside the current bounds, matching direct Flip.
    run_as('mcc:state/bp_flip_lr')
    scan()
    check(f'if score {actor} mcc_bptx0 matches 10 if score {actor} mcc_bptz0 matches 11 if score {actor} mcc_bpoffx matches -2','default_blueprint_flip_keeps_bounds')
    check('positioned 12.0 80.0 11.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1] positioned 10.0 80.0 12.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:iron_block"},limit=1]','default_blueprint_flip_mirrors_in_place')
    run_as('mcc:state/bp_flip_lr')
    scan()
    check(f'if score {actor} mcc_bptx0 matches 10 if score {actor} mcc_bptz0 matches 11 if score {actor} mcc_bpoffx matches 0','default_blueprint_flip_twice_restores_offset')
    check('positioned 10.0 80.0 11.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1] positioned 12.0 80.0 12.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:iron_block"},limit=1]','default_blueprint_flip_twice_restores_preview')
    run_as('mcc:blueprint/clear_internal')

    # 0a. Custom Anchor must land exactly on the V target, not merely near it.
    fixture()
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 5',
        f'scoreboard players set {actor} mcc_any 80',
        f'scoreboard players set {actor} mcc_anz 4',
        f'scoreboard players set {actor} mcc_and 1',
    ])
    run_as('mcc:copy/run')
    target(20,82,12)
    run_as('mcc:paste/dispatch')
    scan()
    check(f'positioned 20.0 82.0 12.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={{block_state:"minecraft:iron_block"}},limit=1] if score {actor} mcc_bptx0 matches 18 if score {actor} mcc_bpty0 matches 82 if score {actor} mcc_bptz0 matches 11','custom_anchor_direct_exact_target')
    check('positioned 18.0 82.0 11.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','custom_anchor_direct_source_offset')
    run_as('mcc:blueprint/clear_internal')

    # 0b. The same custom Anchor invariant must hold for every Rotate/Mirror combination.
    for rot in range(4):
        for mir in range(3):
            lines.append(f'scoreboard players set {actor} mcc_rot {rot}')
            lines.append(f'scoreboard players set {actor} mcc_mir {mir}')
            target(24,82,12)
            run_as('mcc:paste/dispatch')
            scan()
            check(f'positioned 24.0 82.0 12.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={{block_state:"minecraft:iron_block"}},limit=1]','custom_anchor_r%d_m%d_exact_target' % (rot,mir))
            run_as('mcc:blueprint/clear_internal')
    lines.append(f'scoreboard players set {actor} mcc_rot 0')
    lines.append(f'scoreboard players set {actor} mcc_mir 0')
    lines.append(f'scoreboard players set {actor} mcc_hasa 0')

    # 0c. External Anchor must also work for Blueprint placement, not only
    # direct real-block Rotate. Verify direct, rotated, and mirrored previews.
    fixture(10,80,10)
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 20',
        f'scoreboard players set {actor} mcc_any 80',
        f'scoreboard players set {actor} mcc_anz 20',
        f'scoreboard players set {actor} mcc_and 1',
    ])
    run_as('mcc:copy/run')
    target(40,80,40)
    run_as('mcc:paste/dispatch')
    scan()
    check(f'positioned 30.0 80.0 30.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={{block_state:"minecraft:gold_block"}},limit=1] if score {actor} mcc_bptx0 matches 30 if score {actor} mcc_bptz0 matches 30','external_anchor_blueprint_direct')
    run_as('mcc:blueprint/clear_internal')

    lines.append(f'scoreboard players set {actor} mcc_rot 1')
    target(40,80,40)
    run_as('mcc:paste/dispatch')
    scan()
    check('positioned 50.0 80.0 30.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','external_anchor_blueprint_rotate90_gold')
    check('positioned 50.0 80.0 32.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:diamond_block"},limit=1]','external_anchor_blueprint_rotate90_diamond')
    run_as('mcc:blueprint/clear_internal')

    lines.append(f'scoreboard players set {actor} mcc_rot 0')
    lines.append(f'scoreboard players set {actor} mcc_mir 1')
    target(40,80,40)
    run_as('mcc:paste/dispatch')
    scan()
    check('positioned 50.0 80.0 30.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','external_anchor_blueprint_mirrorx_gold')
    check('positioned 48.0 80.0 30.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:diamond_block"},limit=1]','external_anchor_blueprint_mirrorx_diamond')
    run_as('mcc:blueprint/clear_internal')
    lines.append(f'scoreboard players set {actor} mcc_mir 0')

    # 0c2. A very distant external Anchor must never move the hidden transformed
    # Blueprint outside this player's reserved buffer.
    fixture(10,80,10)
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 100000',
        f'scoreboard players set {actor} mcc_any 80',
        f'scoreboard players set {actor} mcc_anz 100000',
        f'scoreboard players set {actor} mcc_and 1',
        f'scoreboard players set {actor} mcc_rot 1',
        f'scoreboard players set {actor} mcc_mir 0',
    ])
    run_as('mcc:copy/run')
    target(40,80,40)
    run_as('mcc:paste/dispatch')
    check(f'if score {actor} mcc_bpsx0 matches 20019712 if score {actor} mcc_bpsx2 matches 20019713 if score {actor} mcc_bpsy0 matches 0 if score {actor} mcc_bpsz0 matches 20002000 if score {actor} mcc_bpsz2 matches 20002002','far_external_anchor_blueprint_hidden_buffer_isolated')
    run_as('mcc:blueprint/clear_internal')
    lines.extend([
        f'scoreboard players set {actor} mcc_rot 0',
        f'scoreboard players set {actor} mcc_mir 0',
        f'scoreboard players set {actor} mcc_hasa 0',
    ])

    # 0d. A custom Anchor may be outside the selection and must remain a usable
    # pivot after the first rotation moves the selection somewhere else.
    fixture(10,80,10)
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 20',
        f'scoreboard players set {actor} mcc_any 80',
        f'scoreboard players set {actor} mcc_anz 20',
        f'scoreboard players set {actor} mcc_and 1',
    ])
    run_as('mcc:rotate_edit/r90')
    check(f'if block 30 80 10 gold_block if block 30 80 12 diamond_block if block 29 80 10 oak_stairs[facing=south] if block 29 80 12 iron_block if score {actor} mcc_anx matches 20 if score {actor} mcc_anz matches 20 if score {actor} mcc_p1x matches 29 if score {actor} mcc_p2x matches 30 if score {actor} mcc_p1z matches 10 if score {actor} mcc_p2z matches 12','external_anchor_rotate90_first')
    run_as('mcc:rotate_edit/r90')
    check(f'if block 30 80 30 gold_block if block 28 80 30 diamond_block if block 30 80 29 oak_stairs[facing=west] if block 28 80 29 iron_block if score {actor} mcc_anx matches 20 if score {actor} mcc_anz matches 20 if score {actor} mcc_p1x matches 28 if score {actor} mcc_p2x matches 30 if score {actor} mcc_p1z matches 29 if score {actor} mcc_p2z matches 30','external_anchor_rotate90_second')
    run_as('mcc:undo/run')
    check('if block 30 80 10 gold_block if block 30 80 12 diamond_block','external_anchor_rotate_undo_once')
    run_as('mcc:undo/run')
    check('if block 10 80 10 gold_block if block 12 80 10 diamond_block','external_anchor_rotate_undo_twice')

    # 1. Copy -> Blueprint: source remains, destination remains air, exact-state displays exist.
    fixture()
    run_as('mcc:copy/run')
    check(f'if score {actor} mcc_cliptype matches 1 if score {actor} mcc_clip matches 1','copy_type')
    target(12,80,3)
    run_as('mcc:paste/dispatch')
    scan()
    check('if block 12 80 3 air if block 14 80 4 air','copy_v_no_real_blocks')
    check('positioned 12.0 80.0 3.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','blueprint_gold_state')
    check('positioned 12.0 80.0 4.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:{id:"minecraft:oak_stairs",properties:{facing:"east",half:"bottom",shape:"straight",waterlogged:"false"}}},limit=1]','blueprint_stair_state')
    check('if block 3 80 3 gold_block if block 5 80 4 iron_block','copy_source_unchanged')

    # 1a. Phase 3 Blueprint micro-adjust moves displays without rebuilding the BOM.
    lines.append(f'scoreboard players set {actor} bpright 1')
    run_as('mcc:blueprint/nudge/right')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 11.0 80.0 3.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bptx0 matches 11 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_right')
    lines.append(f'scoreboard players set {actor} bpleft 1')
    run_as('mcc:blueprint/nudge/left')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12.0 80.0 3.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bptx0 matches 12 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_left_restore')
    lines.append(f'scoreboard players set {actor} bpforward 1')
    run_as('mcc:blueprint/nudge/forward')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12.0 80.0 4.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bptz0 matches 4 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_forward')
    lines.append(f'scoreboard players set {actor} bpbackward 1')
    run_as('mcc:blueprint/nudge/backward')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12.0 80.0 3.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bptz0 matches 3 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_backward_restore')
    lines.append(f'scoreboard players set {actor} bpup 1')
    run_as('mcc:blueprint/nudge/up')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12.0 81.0 3.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bpty0 matches 81 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_up')
    lines.append(f'scoreboard players set {actor} bpdown 1')
    run_as('mcc:blueprint/nudge/down')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12.0 80.0 3.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bpty0 matches 80 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_down_restore')

    # Phase 3 overwrite guard: recount target blocks and require a second Build confirmation.
    lines.append('setblock 12 80 3 stone')
    run_as('mcc:blueprint/recount_start')
    run_as('mcc:blueprint/recount_batch')
    check(f'if score {actor} mcc_bpover matches 1 if score {actor} mcc_bpover_scan matches 0','phase3_overlap_recount')
    run_as('mcc:materials/build_start')
    check(f'if block 12 80 3 stone if score {actor} mcc_buildconfirm matches 1 if score {actor} mcc_matphase matches 0','phase3_overlap_first_build_warns')
    lines.append('setblock 12 80 3 air')
    run_as('mcc:blueprint/recount_start')
    run_as('mcc:blueprint/recount_batch')
    check(f'if score {actor} mcc_bpover matches 0 if score {actor} mcc_buildconfirm matches 0','phase3_overlap_recount_resets_confirmation')

    # 1b. v1.0 material-backed Build: missing materials do nothing; complete stock consumes then builds.
    lines.extend([
        'setblock 6 80 8 chest',
        'setblock 7 80 8 chest',
        'setblock 8 80 8 chest',
        'setblock 9 80 8 chest',
        'data modify block 8 80 8 Items set value [{Slot:0b,id:"minecraft:gold_block",count:1},{Slot:1b,id:"minecraft:diamond_block",count:1},{Slot:2b,id:"minecraft:oak_stairs",count:1}]',
        'data modify storage warehouse:chests c00 set value {registered:1b,valid:1b,dimension:"minecraft:overworld",a_x:6,a_y:80,a_z:8,b_x:7,b_y:80,b_z:8}',
        'data modify storage warehouse:chests c11 set value {registered:1b,valid:1b,dimension:"minecraft:overworld",a_x:8,a_y:80,a_z:8,b_x:9,b_y:80,b_z:8}',
    ])
    # Phase 3 material report is read-only even when Warehouse is missing stock.
    run_as('mcc:materials/check_start')
    for _ in range(4): run_as('mcc:materials/process_batch')
    check(f'if score {actor} mcc_matphase matches 0 if score {actor} mcc_matjob matches 0 if score {actor} mcc_matkind matches 1 if score {actor} mcc_mattotal matches 1','phase3_material_report_missing_summary')
    check('if data block 8 80 8 Items[{id:"minecraft:gold_block",count:1}] if data block 8 80 8 Items[{id:"minecraft:diamond_block",count:1}] if data block 8 80 8 Items[{id:"minecraft:oak_stairs",count:1}]','phase3_material_report_no_consume')

    run_as('mcc:materials/build_start')
    for _ in range(4): run_as('mcc:materials/process_batch')
    check(f'if block 12 80 3 air if block 14 80 4 air if score {actor} mcc_matphase matches 0 if score {actor} mcc_bpactive matches 1','build_missing_all_or_nothing')
    check('if data block 8 80 8 Items[{id:"minecraft:gold_block",count:1}] if data block 8 80 8 Items[{id:"minecraft:diamond_block",count:1}]','build_missing_no_consume')
    lines.append('data modify block 8 80 8 Items append value {Slot:3b,id:"minecraft:iron_block",count:1}')
    # With complete stock a material check must still only report: no take, no build.
    run_as('mcc:materials/check_start')
    for _ in range(8): run_as('mcc:materials/process_batch')
    check(f'if block 12 80 3 air if block 14 80 4 air if score {actor} mcc_matphase matches 0 if score {actor} mcc_matjob matches 0 if score {actor} mcc_bpactive matches 1','material_check_full_stock_does_not_build')
    check('if data block 8 80 8 Items[{id:"minecraft:gold_block",count:1}] if data block 8 80 8 Items[{id:"minecraft:iron_block",count:1}]','material_check_full_stock_no_consume')
    run_as('mcc:materials/build_start')
    for _ in range(8): run_as('mcc:materials/process_batch')
    check(f'if block 12 80 3 gold_block if block 14 80 3 diamond_block if block 12 80 4 oak_stairs[facing=east] if block 14 80 4 iron_block if score {actor} mcc_bpactive matches 0','build_material_success')
    check('unless data block 8 80 8 Items[0]','build_materials_consumed')
    check('if data storage mcc:history u_p77_s1.materials.bom."minecraft:gold_block"{taken:1} if data storage mcc:history u_p77_s1.materials.bom."minecraft:diamond_block"{taken:1} if data storage mcc:history u_p77_s1.materials.bom."minecraft:oak_stairs"{taken:1} if data storage mcc:history u_p77_s1.materials.bom."minecraft:iron_block"{taken:1} if data storage mcc:history u_p77_s1.materials.items[{id:"minecraft:gold_block",taken:1}] if data storage mcc:history u_p77_s1.materials.items[{id:"minecraft:iron_block",taken:1}]','build_history_archives_taken')
    lines.append('setblock 12 80 3 emerald_block')
    run_as('mcc:undo/run')
    check(f'if block 12 80 3 emerald_block if score {actor} mcc_ucnt matches 1','build_undo_guard_refuses_modified_world')
    lines.append('setblock 12 80 3 gold_block')
    run_as('mcc:undo/run')
    check(f'if block 12 80 3 air if block 14 80 4 air if score {actor} mcc_rcnt matches 1','build_undo_world')
    check(f'if score {actor} mcc_umat matches 1','build_undo_material_flag_preserved')
    check('if data storage mcc:temp txctx{id:77,slot:1}','build_undo_refund_loop_entered')
    check('unless data storage mcc:temp txwork[0]','build_undo_refund_loop_drained')
    check('if data storage mcc:temp refund{count:1}','build_undo_refund_request_built')
    check('if data storage warehouse:api result{operation:"refund_item",ok:1b,complete:1b}','build_undo_called_refund_api')
    check('unless data storage warehouse:api pending_refunds[0]','build_undo_refund_not_pending')
    check('if data block 6 80 8 Items[{id:"minecraft:gold_block",count:1}] if data block 6 80 8 Items[{id:"minecraft:diamond_block",count:1}] if data block 6 80 8 Items[{id:"minecraft:oak_stairs",count:1}] if data block 6 80 8 Items[{id:"minecraft:iron_block",count:1}]','build_undo_refunds_to_warehouse_entry')
    check('if block 8 80 8 #warehouse:storage_chests if block 9 80 8 #warehouse:storage_chests','warehouse_source_blocks_before_redo')
    check('if data storage warehouse:chests c11{registered:1b,valid:1b,dimension:"minecraft:overworld",a_x:8,a_y:80,a_z:8,b_x:9,b_y:80,b_z:8}','warehouse_source_registration_before_redo')
    lines.append(f'execute as {actor} run function warehouse:api/count_item {{item_id:"minecraft:iron_block"}}')
    check('if data storage warehouse:api result{ok:1b,complete:1b,available:1,stale_sources:0}','warehouse_source_api_before_redo')
    run_as('mcc:redo/run')
    for _ in range(8): run_as('mcc:materials/process_batch')
    check(f'if block 12 80 3 gold_block if block 14 80 4 iron_block if score {actor} mcc_ucnt matches 1 if score {actor} mcc_rcnt matches 0','build_redo_material_success')
    check('unless data block 6 80 8 Items[0] if block 8 80 8 #warehouse:storage_chests','build_redo_materials_consumed_from_warehouse')
    run_as('mcc:undo/run')
    check('if block 12 80 3 air if block 14 80 4 air','build_second_undo_world')
    check('if data block 6 80 8 Items[{id:"minecraft:iron_block",count:1}]','build_second_undo_refunds_to_warehouse')
    run_as('mcc:blueprint/clear_internal')
    check('unless entity @e[type=minecraft:block_display,tag=mcc_blueprint]','blueprint_clear')

    # 1c. Build must preserve custom-Anchor placement exactly, not only preview it correctly.
    fixture(3,80,21)
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 5',
        f'scoreboard players set {actor} mcc_any 80',
        f'scoreboard players set {actor} mcc_anz 22',
        f'scoreboard players set {actor} mcc_and 1',
        'data modify block 8 80 8 Items set value [{Slot:0b,id:"minecraft:gold_block",count:1},{Slot:1b,id:"minecraft:diamond_block",count:1},{Slot:2b,id:"minecraft:oak_stairs",count:1},{Slot:3b,id:"minecraft:iron_block",count:1}]',
    ])
    run_as('mcc:copy/run')
    target(20,82,21)
    run_as('mcc:paste/dispatch')
    scan()
    check('positioned 20.0 82.0 21.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:iron_block"},limit=1]','custom_anchor_build_preview_exact')
    run_as('mcc:materials/build_start')
    for _ in range(8): run_as('mcc:materials/process_batch')
    check(f'if block 20 82 21 iron_block if block 18 82 20 gold_block if score {actor} mcc_bpactive matches 0','custom_anchor_build_world_exact')
    run_as('mcc:undo/run')
    check('if block 20 82 21 air if block 18 82 20 air','custom_anchor_build_undo')

    # 1d. Cut + V uses the same Anchor contract and consumes the clipboard.
    fixture(3,80,25)
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 5',
        f'scoreboard players set {actor} mcc_any 80',
        f'scoreboard players set {actor} mcc_anz 26',
        f'scoreboard players set {actor} mcc_and 1',
    ])
    run_as('mcc:cut/run')
    target(20,80,25)
    run_as('mcc:paste/dispatch')
    check(f'if block 20 80 25 iron_block if block 18 80 24 gold_block if score {actor} mcc_clip matches 0 if score {actor} mcc_cliptype matches 0','custom_anchor_cut_v_exact')
    run_as('mcc:undo/run')
    check('if block 20 80 25 air if block 18 80 24 air','custom_anchor_cut_v_undo')

    # Restore the original basic fixture for the existing Cut/Undo/Redo sequence.
    fixture()

    # 2. X -> real cut, Undo/Redo, then X+V consumes clipboard.
    run_as('mcc:cut/run')
    check(f'if block 3 80 3 air if block 5 80 4 air if score {actor} mcc_cliptype matches 2','x_real_cut')
    run_as('mcc:undo/run')
    check(f'if block 3 80 3 gold_block if block 5 80 4 iron_block if score {actor} mcc_redo matches 1 if score {actor} mcc_clip matches 0 if score {actor} mcc_cliptype matches 0','x_undo_clears_cut_clipboard')
    run_as('mcc:redo/run')
    check(f'if block 3 80 3 air if block 5 80 4 air if score {actor} mcc_undo matches 1 if score {actor} mcc_clip matches 1 if score {actor} mcc_cliptype matches 2','x_redo_rebuilds_cut_clipboard')
    check('if block 20019712 0 20000000 gold_block if block 20019714 0 20000001 iron_block','x_redo_clipboard_exact')
    run_as('mcc:undo/run')
    run_as('mcc:cut/run')
    target(12,80,3)
    run_as('mcc:paste/dispatch')
    check(f'if block 12 80 3 gold_block if block 14 80 4 iron_block if score {actor} mcc_clip matches 0 if score {actor} mcc_cliptype matches 0','x_v_real_and_consumed')
    target(20,80,3)
    run_as('mcc:paste/dispatch')
    check('if block 20 80 3 air if block 22 80 4 air','x_no_second_paste')

    # 3. Undo <-> Redo toggles the latest real paste (the X+V above). Keep this
    # directly after it: later sections reset the actor history counters.
    run_as('mcc:undo/run')
    check(f'if block 12 80 3 air if score {actor} mcc_redo matches 1','paste_undo')
    run_as('mcc:redo/run')
    check(f'if block 12 80 3 gold_block if score {actor} mcc_undo matches 1','paste_redo')
    run_as('mcc:undo/run')

    # 2a. Cut -> Undo must restore a container but invalidate the live Cut clipboard.
    lines.extend([
        'fill 34 80 4 38 80 6 air',
        'setblock 35 80 5 chest',
        'data modify block 35 80 5 Items set value [{Slot:0b,id:"minecraft:diamond",count:5}]',
        f'scoreboard players set {actor} mcc_has1 1',
        f'scoreboard players set {actor} mcc_has2 1',
        f'scoreboard players set {actor} mcc_hasa 0',
        f'scoreboard players set {actor} mcc_p1x 35',
        f'scoreboard players set {actor} mcc_p1y 80',
        f'scoreboard players set {actor} mcc_p1z 5',
        f'scoreboard players set {actor} mcc_p1d 1',
        f'scoreboard players set {actor} mcc_p2x 35',
        f'scoreboard players set {actor} mcc_p2y 80',
        f'scoreboard players set {actor} mcc_p2z 5',
        f'scoreboard players set {actor} mcc_p2d 1',
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_rhead 0',
    ])
    run_as('mcc:cut/run')
    run_as('mcc:undo/run')
    check(f'if block 35 80 5 chest if data block 35 80 5 Items[{{id:"minecraft:diamond",count:5}}] if score {actor} mcc_clip matches 0 if score {actor} mcc_cliptype matches 0','cut_undo_container_restored_clipboard_invalidated')
    target(37,80,5)
    run_as('mcc:paste/dispatch')
    check('if block 37 80 5 air','cut_undo_cannot_second_paste_container')

    # Copying something else after Undo must not destroy the archived Cut Redo
    # clipboard. Redo restores the original Cut clipboard, not the intervening Copy.
    lines.extend([
        'fill 32 80 9 39 80 10 air',
        'setblock 33 80 9 redstone_block',
        'setblock 38 80 9 lapis_block',
        f'scoreboard players set {actor} mcc_p1x 33',
        f'scoreboard players set {actor} mcc_p1y 80',
        f'scoreboard players set {actor} mcc_p1z 9',
        f'scoreboard players set {actor} mcc_p2x 33',
        f'scoreboard players set {actor} mcc_p2y 80',
        f'scoreboard players set {actor} mcc_p2z 9',
        f'scoreboard players set {actor} mcc_p1d 1',
        f'scoreboard players set {actor} mcc_p2d 1',
        f'scoreboard players set {actor} mcc_hasa 0',
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_rhead 0',
    ])
    run_as('mcc:cut/run')
    run_as('mcc:undo/run')
    lines.extend([
        f'scoreboard players set {actor} mcc_p1x 38',
        f'scoreboard players set {actor} mcc_p2x 38',
    ])
    run_as('mcc:copy/run')
    check(f'if score {actor} mcc_cliptype matches 1','cut_redo_intervening_copy_exists')
    run_as('mcc:redo/run')
    check(f'if block 33 80 9 air if block 38 80 9 lapis_block if score {actor} mcc_clip matches 1 if score {actor} mcc_cliptype matches 2','cut_redo_replaces_intervening_copy_with_original_cut')
    target(35,80,9)
    run_as('mcc:paste/dispatch')
    check('if block 35 80 9 redstone_block if block 38 80 9 lapis_block','cut_redo_original_clipboard_pastes_exact_source')

    # 2b. Rotated Cut + Masked must preserve target blocks where transformed source is air.
    lines.extend([
        'fill 40 80 0 46 80 2 air',
        'setblock 40 80 0 gold_block',
        f'scoreboard players set {actor} mcc_has1 1',
        f'scoreboard players set {actor} mcc_has2 1',
        f'scoreboard players set {actor} mcc_hasa 0',
        f'scoreboard players set {actor} mcc_p1x 40',
        f'scoreboard players set {actor} mcc_p1y 80',
        f'scoreboard players set {actor} mcc_p1z 0',
        f'scoreboard players set {actor} mcc_p1d 1',
        f'scoreboard players set {actor} mcc_p2x 41',
        f'scoreboard players set {actor} mcc_p2y 80',
        f'scoreboard players set {actor} mcc_p2z 0',
        f'scoreboard players set {actor} mcc_p2d 1',
        f'scoreboard players set {actor} mcc_mask 1',
        f'scoreboard players set {actor} mcc_rot 1',
        f'scoreboard players set {actor} mcc_mir 0',
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_rhead 0',
    ])
    run_as('mcc:cut/run')
    lines.append('setblock 45 80 1 stone')
    target(45,80,0)
    run_as('mcc:paste/dispatch')
    check('if block 45 80 0 gold_block if block 45 80 1 stone','transformed_cut_masked_preserves_target_under_source_air')
    lines.extend([
        f'scoreboard players set {actor} mcc_mask 0',
        f'scoreboard players set {actor} mcc_rot 0',
        f'scoreboard players set {actor} mcc_mir 0',
    ])


    # 4. Move remains real and is Undo/Redo reversible.
    fixture(3,80,10)
    lines.extend([
        f'scoreboard players set {actor} mcc_dx 1',
        f'scoreboard players set {actor} mcc_dy 0',
        f'scoreboard players set {actor} mcc_dz 0',
    ])
    run_as('mcc:move/run')
    check('if block 4 80 10 gold_block if block 3 80 10 air','move_real')
    run_as('mcc:undo/run')
    check('if block 3 80 10 gold_block if block 4 80 10 air','move_undo')
    run_as('mcc:redo/run')
    check('if block 4 80 10 gold_block if block 3 80 10 air','move_redo')
    run_as('mcc:undo/run')

    # 4b. A Move whose source+destination Z span exceeds 200 blocks fills the Undo
    # scratch lane (#ubz) up to 256 deep. It must not overlap the Work lane, or the
    # first moved Z rows are overwritten before the Work snapshot is pasted.
    lines.extend([
        'fill 70 80 0 70 80 230 air',
        'setblock 70 80 0 gold_block',
        'setblock 70 80 127 iron_block',
        f'scoreboard players set {actor} mcc_has1 1',
        f'scoreboard players set {actor} mcc_has2 1',
        f'scoreboard players set {actor} mcc_hasa 0',
        f'scoreboard players set {actor} mcc_p1x 70',
        f'scoreboard players set {actor} mcc_p1y 80',
        f'scoreboard players set {actor} mcc_p1z 0',
        f'scoreboard players set {actor} mcc_p1d 1',
        f'scoreboard players set {actor} mcc_p2x 70',
        f'scoreboard players set {actor} mcc_p2y 80',
        f'scoreboard players set {actor} mcc_p2z 127',
        f'scoreboard players set {actor} mcc_p2d 1',
        f'scoreboard players set {actor} mcc_dx 0',
        f'scoreboard players set {actor} mcc_dy 0',
        f'scoreboard players set {actor} mcc_dz 100',
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_rhead 0',
    ])
    run_as('mcc:move/run')
    check('if block 70 80 100 gold_block if block 70 80 227 iron_block if block 70 80 0 air if block 70 80 127 air','long_z_move_keeps_every_row')
    run_as('mcc:undo/run')
    check('if block 70 80 0 gold_block if block 70 80 127 iron_block if block 70 80 100 air if block 70 80 227 air','long_z_move_undo')
    lines.append('fill 70 80 0 70 80 230 air')

    # 4a. Generic Undo guard must include block-entity NBT, not only block states.
    lines.extend([
        'fill 29 80 4 32 80 6 air',
        'setblock 30 80 5 chest',
        'data modify block 30 80 5 Items set value [{Slot:0b,id:"minecraft:diamond",count:7}]',
        f'scoreboard players set {actor} mcc_has1 1',
        f'scoreboard players set {actor} mcc_has2 1',
        f'scoreboard players set {actor} mcc_hasa 0',
        f'scoreboard players set {actor} mcc_p1x 30',
        f'scoreboard players set {actor} mcc_p1y 80',
        f'scoreboard players set {actor} mcc_p1z 5',
        f'scoreboard players set {actor} mcc_p1d 1',
        f'scoreboard players set {actor} mcc_p2x 30',
        f'scoreboard players set {actor} mcc_p2y 80',
        f'scoreboard players set {actor} mcc_p2z 5',
        f'scoreboard players set {actor} mcc_p2d 1',
        f'scoreboard players set {actor} mcc_dx 1',
        f'scoreboard players set {actor} mcc_dy 0',
        f'scoreboard players set {actor} mcc_dz 0',
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_rhead 0',
    ])
    run_as('mcc:move/run')
    lines.append('data remove block 31 80 5 Items')
    run_as('mcc:undo/run')
    check(f'if block 30 80 5 air if block 31 80 5 chest unless data block 31 80 5 Items[0] if score {actor} mcc_ucnt matches 1 if score {actor} mcc_rcnt matches 0','move_undo_guard_detects_container_nbt_change')

    # 4b. Redo also requires the exact post-Undo world to remain untouched.
    lines.extend([
        'fill 29 80 4 32 80 6 air',
        'setblock 30 80 5 emerald_block',
        f'scoreboard players set {actor} mcc_p1x 30',
        f'scoreboard players set {actor} mcc_p1y 80',
        f'scoreboard players set {actor} mcc_p1z 5',
        f'scoreboard players set {actor} mcc_p2x 30',
        f'scoreboard players set {actor} mcc_p2y 80',
        f'scoreboard players set {actor} mcc_p2z 5',
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_rhead 0',
    ])
    run_as('mcc:move/run')
    run_as('mcc:undo/run')
    lines.append('setblock 30 80 5 diamond_block')
    run_as('mcc:redo/run')
    check(f'if block 30 80 5 diamond_block if block 31 80 5 air if score {actor} mcc_rcnt matches 1 if score {actor} mcc_ucnt matches 0','move_redo_guard_refuses_modified_post_undo_world')

    # Reset guard-test history before direction wrappers.
    lines.extend([
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_rhead 0',
        f'scoreboard players set {actor} mcc_undo 0',
        f'scoreboard players set {actor} mcc_redo 0',
        'fill 29 80 4 32 80 6 air',
    ])

    # 4c. Player-facing Move wrappers at yaw 0 must map to the expected world directions.
    lines.extend([
        'setblock 30 80 5 emerald_block',
        f'scoreboard players set {actor} mcc_has1 1',
        f'scoreboard players set {actor} mcc_has2 1',
        f'scoreboard players set {actor} mcc_hasa 0',
        f'scoreboard players set {actor} mcc_p1x 30',
        f'scoreboard players set {actor} mcc_p1y 80',
        f'scoreboard players set {actor} mcc_p1z 5',
        f'scoreboard players set {actor} mcc_p1d 1',
        f'scoreboard players set {actor} mcc_p2x 30',
        f'scoreboard players set {actor} mcc_p2y 80',
        f'scoreboard players set {actor} mcc_p2z 5',
        f'scoreboard players set {actor} mcc_p2d 1',
        f'data merge entity {actor} {{Rotation:[0f,0f]}}',
    ])
    for objective,function,condition,label in [
        ('right','mcc:move/right','if block 29 80 5 emerald_block if block 30 80 5 air','move_right_yaw0'),
        ('left','mcc:move/left','if block 31 80 5 emerald_block if block 30 80 5 air','move_left_yaw0'),
        ('forward','mcc:move/forward','if block 30 80 6 emerald_block if block 30 80 5 air','move_forward_yaw0'),
        ('backward','mcc:move/backward','if block 30 80 4 emerald_block if block 30 80 5 air','move_backward_yaw0'),
        ('up','mcc:move/up','if block 30 81 5 emerald_block if block 30 80 5 air','move_up'),
        ('down','mcc:move/down','if block 30 79 5 emerald_block if block 30 80 5 air','move_down'),
    ]:
        lines.append(f'scoreboard players set {actor} {objective} 1')
        run_as(function)
        check(condition,label)
        run_as('mcc:undo/run')
        check('if block 30 80 5 emerald_block',label+'_undo')

    # 4b. Flip X/Z must actually mirror the selected blocks, not only report success.
    fixture(3,80,10)
    run_as('mcc:flip/x')
    check('if block 5 80 10 gold_block if block 3 80 10 diamond_block if block 3 80 11 iron_block','flip_x_real_positions')
    run_as('mcc:undo/run')
    check('if block 3 80 10 gold_block if block 5 80 10 diamond_block if block 5 80 11 iron_block','flip_x_undo')
    run_as('mcc:flip/z')
    check('if block 3 80 11 gold_block if block 5 80 11 diamond_block if block 5 80 10 iron_block','flip_z_real_positions')
    run_as('mcc:undo/run')
    check('if block 3 80 10 gold_block if block 5 80 10 diamond_block if block 5 80 11 iron_block','flip_z_undo')

    # 4d. With a custom external Anchor, Flip keeps the Anchor fixed and moves
    # the selected structure around that pivot.
    fixture(10,80,25)
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 20',
        f'scoreboard players set {actor} mcc_any 80',
        f'scoreboard players set {actor} mcc_anz 25',
        f'scoreboard players set {actor} mcc_and 1',
    ])
    run_as('mcc:flip/x')
    check(f'if block 30 80 25 gold_block if block 28 80 25 diamond_block if block 28 80 26 iron_block if score {actor} mcc_anx matches 20 if score {actor} mcc_anz matches 25 if score {actor} mcc_p1x matches 28 if score {actor} mcc_p2x matches 30','external_anchor_flip_x_fixed_pivot')
    run_as('mcc:undo/run')
    check('if block 10 80 25 gold_block if block 12 80 25 diamond_block if block 12 80 26 iron_block','external_anchor_flip_x_undo')

    fixture(10,80,25)
    lines.extend([
        f'scoreboard players set {actor} mcc_hasa 1',
        f'scoreboard players set {actor} mcc_anx 10',
        f'scoreboard players set {actor} mcc_any 80',
        f'scoreboard players set {actor} mcc_anz 35',
        f'scoreboard players set {actor} mcc_and 1',
    ])
    run_as('mcc:flip/z')
    check(f'if block 10 80 45 gold_block if block 12 80 45 diamond_block if block 12 80 44 iron_block if score {actor} mcc_anx matches 10 if score {actor} mcc_anz matches 35 if score {actor} mcc_p1z matches 44 if score {actor} mcc_p2z matches 45','external_anchor_flip_z_fixed_pivot')
    run_as('mcc:undo/run')
    check('if block 10 80 25 gold_block if block 12 80 25 diamond_block if block 12 80 26 iron_block','external_anchor_flip_z_undo')
    lines.append(f'scoreboard players set {actor} mcc_hasa 0')

    # 5. Direct Rotate90 modifies real blocks around Pos1 and is Undo/Redo reversible.
    fixture(3,80,17)
    run_as('mcc:rotate_edit/r90')
    check('if block 3 80 17 gold_block if block 3 80 19 diamond_block if block 2 80 17 oak_stairs[facing=south] if block 2 80 19 iron_block','rotate90_real')
    run_as('mcc:undo/run')
    check('if block 3 80 17 gold_block if block 5 80 17 diamond_block if block 3 80 18 oak_stairs[facing=east]','rotate90_undo')
    run_as('mcc:redo/run')
    check('if block 3 80 19 diamond_block if block 2 80 17 oak_stairs[facing=south]','rotate90_redo')

    # 5a. Rotate180 and Rotate270 must also place the asymmetric fixture correctly.
    run_as('mcc:undo/run')
    fixture(3,80,17)
    run_as('mcc:rotate_edit/r180')
    check('if block 3 80 17 gold_block if block 1 80 17 diamond_block if block 1 80 16 iron_block','rotate180_real')
    run_as('mcc:undo/run')
    check('if block 3 80 17 gold_block if block 5 80 17 diamond_block if block 5 80 18 iron_block','rotate180_undo')
    run_as('mcc:rotate_edit/r270')
    check('if block 3 80 17 gold_block if block 3 80 15 diamond_block if block 4 80 15 iron_block','rotate270_real')
    run_as('mcc:undo/run')
    check('if block 3 80 17 gold_block if block 5 80 17 diamond_block if block 5 80 18 iron_block','rotate270_undo')

    # 6. Rotated Copy -> Blueprint still creates displays only.
    run_as('mcc:undo/run')
    run_as('mcc:copy/run')
    lines.append(f'scoreboard players set {actor} mcc_rot 1')
    target(20,80,17)
    run_as('mcc:paste/dispatch')
    scan()
    check('if block 20 80 17 air if block 20 80 19 air if block 19 80 17 air','rotated_blueprint_no_blocks')
    check('positioned 20.0 80.0 17.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..4,limit=1]','rotated_blueprint_display')
    run_as('mcc:blueprint/clear_internal')
    lines.append(f'scoreboard players set {actor} mcc_rot 0')

    # 6a. Unguarded legacy history must never execute world restores.
    lines.extend([
        'setblock 38 80 25 emerald_block',
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_undo 1',
        f'scoreboard players set {actor} mcc_redo 0',
        f'scoreboard players set {actor} mcc_ux 38',
        f'scoreboard players set {actor} mcc_uy 80',
        f'scoreboard players set {actor} mcc_uz 25',
        f'scoreboard players set {actor} mcc_ux2 38',
        f'scoreboard players set {actor} mcc_uy2 80',
        f'scoreboard players set {actor} mcc_uz2 25',
        f'scoreboard players set {actor} mcc_udim 1',
    ])
    run_as('mcc:undo/run')
    check(f'if block 38 80 25 emerald_block if score {actor} mcc_undo matches 0 if score {actor} mcc_redo matches 0','legacy_undo_is_discarded_without_restore')
    lines.extend([
        f'scoreboard players set {actor} mcc_redo 1',
        f'scoreboard players set {actor} mcc_undo 0',
        f'scoreboard players set {actor} mcc_rx 38',
        f'scoreboard players set {actor} mcc_ry 80',
        f'scoreboard players set {actor} mcc_rz 25',
        f'scoreboard players set {actor} mcc_rx2 38',
        f'scoreboard players set {actor} mcc_ry2 80',
        f'scoreboard players set {actor} mcc_rz2 25',
        f'scoreboard players set {actor} mcc_rdim 1',
    ])
    run_as('mcc:redo/run')
    check(f'if block 38 80 25 emerald_block if score {actor} mcc_undo matches 0 if score {actor} mcc_redo matches 0','legacy_redo_is_discarded_without_restore')

    # 7. Five real edits can be undone and redone in order.
    lines.extend([
        f'scoreboard players set {actor} mcc_ucnt 0',
        f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0',
        f'scoreboard players set {actor} mcc_rhead 0',
        f'scoreboard players set {actor} mcc_undo 0',
        f'scoreboard players set {actor} mcc_redo 0',
        'setblock 30 80 25 emerald_block',
        f'scoreboard players set {actor} mcc_has1 1',
        f'scoreboard players set {actor} mcc_has2 1',
        f'scoreboard players set {actor} mcc_hasa 0',
        f'scoreboard players set {actor} mcc_p1x 30',
        f'scoreboard players set {actor} mcc_p1y 80',
        f'scoreboard players set {actor} mcc_p1z 25',
        f'scoreboard players set {actor} mcc_p1d 1',
        f'scoreboard players set {actor} mcc_p2x 30',
        f'scoreboard players set {actor} mcc_p2y 80',
        f'scoreboard players set {actor} mcc_p2z 25',
        f'scoreboard players set {actor} mcc_p2d 1',
        f'scoreboard players set {actor} mcc_dx 1',
        f'scoreboard players set {actor} mcc_dy 0',
        f'scoreboard players set {actor} mcc_dz 0',
    ])
    for _ in range(5): run_as('mcc:move/run')
    check(f'if block 35 80 25 emerald_block if score {actor} mcc_ucnt matches 5','history_five_edits')
    for _ in range(5): run_as('mcc:undo/run')
    check(f'if block 30 80 25 emerald_block if score {actor} mcc_ucnt matches 0 if score {actor} mcc_rcnt matches 5','history_five_undo')
    for _ in range(5): run_as('mcc:redo/run')
    check(f'if block 35 80 25 emerald_block if score {actor} mcc_ucnt matches 5 if score {actor} mcc_rcnt matches 0','history_five_redo')

    # 5. Realistic 3D house: Copy -> Blueprint -> Build with exact Warehouse materials,
    # Undo refunds / Redo re-consumes, rotated Build, and Cut / Move / Flip / Rotate
    # on a multi-layer structure with doors, slabs, stairs, logs, panes, torches,
    # lanterns and a chest. No item entities may drop at any point.
    HS=(100,80,4); HR=(100,80,20); HT=(112,80,4); HT2=(130,80,4); HA=(100,80,36)
    def hbox(o): return f'{o[0]} {o[1]} {o[2]} {o[0]+4} {o[1]+3} {o[2]+4}'
    def hat(o): return f'{o[0]} {o[1]} {o[2]}'
    C00A,C00B,C11A,C11B='100 80 44','101 80 44','103 80 44','104 80 44'
    def hsel():
        lines.extend([
            f'scoreboard players set {actor} mcc_has1 1',
            f'scoreboard players set {actor} mcc_has2 1',
            f'scoreboard players set {actor} mcc_hasa 0',
            f'scoreboard players set {actor} mcc_p1x {HS[0]}',
            f'scoreboard players set {actor} mcc_p1y {HS[1]}',
            f'scoreboard players set {actor} mcc_p1z {HS[2]}',
            f'scoreboard players set {actor} mcc_p1d 1',
            f'scoreboard players set {actor} mcc_p2x {HS[0]+4}',
            f'scoreboard players set {actor} mcc_p2y {HS[1]+3}',
            f'scoreboard players set {actor} mcc_p2z {HS[2]+4}',
            f'scoreboard players set {actor} mcc_p2d 1',
        ])
    def hjobs():
        for _ in range(40): lines.append(f'execute as {actor} at @s if score @s mcc_bpscan matches 1.. run function mcc:blueprint/scan_batch')
        for _ in range(20): lines.append(f'execute as {actor} at @s if score @s mcc_bpover_scan matches 1 run function mcc:blueprint/recount_batch')
    def hmat():
        for _ in range(120): lines.append(f'execute as {actor} at @s if score @s mcc_matphase matches 1..2 run function mcc:materials/process_batch')
    no_items='unless entity @e[type=minecraft:item]'
    def hdrops(tag):
        # Report every dropped item (its name appears in the say prefix), then clear them
        # so each step is judged on its own drops.
        lines.append(f'execute as @e[type=minecraft:item] at @s run say MCCST_DIAG_DROP_{tag}')
    def hclear_drops(): lines.append('kill @e[type=minecraft:item]')
    def hdiff(tag, origin, rot90=False):
        for x,y,z,block in house.BLOCKS:
            dx,dz=(-z,x) if rot90 else (x,z)
            lines.append(f'execute unless block {origin[0]+dx} {origin[1]+y} {origin[2]+dz} {block.split("[")[0]} run say MCCST_DIAG_DIFF_{tag} rel {x} {y} {z} expected {block.split("[")[0]}')
    def hbpdiag(tag):
        for obj in ('mcc_bpactive','mcc_bpready','mcc_bpbad','mcc_bpscan','mcc_bpover_scan','mcc_matphase','mcc_clip','mcc_cliptype'):
            for v in (0,1,2):
                lines.append(f'execute if score {actor} {obj} matches {v} run say MCCST_DIAG_{tag} {obj}={v}')
    sources_empty=f'unless data block {C00A} Items[0] unless data block {C00B} Items[0] unless data block {C11A} Items[0] unless data block {C11B} Items[0]'
    lines.extend([
        'kill @e[type=minecraft:item]',
        f'fill 92 79 0 143 86 47 air',
        f'fill 92 78 0 143 78 47 stone',
    ])
    lines.extend(house.place_commands(*HS))
    lines.append(f'clone {hbox(HS)} {hat(HR)}')
    check(f'if blocks {hbox(HS)} {hat(HR)} all if block {HS[0]+2} {HS[1]+2} {HS[2]} minecraft:oak_door[half=upper] if block {HS[0]+2} {HS[1]+2} {HS[2]+2} minecraft:lantern[hanging=true] if block {HS[0]+1} {HS[1]+2} {HS[2]+1} minecraft:wall_torch','house_fixture_ready')
    check(no_items,'house_fixture_no_item_drops')
    lines.extend([
        f'setblock {C00A} chest', f'setblock {C00B} chest', f'setblock {C11A} chest', f'setblock {C11B} chest',
        'data modify storage warehouse:chests c00 set value {registered:1b,valid:1b,dimension:"minecraft:overworld",a_x:100,a_y:80,a_z:44,b_x:101,b_y:80,b_z:44}',
        'data modify storage warehouse:chests c11 set value {registered:1b,valid:1b,dimension:"minecraft:overworld",a_x:103,a_y:80,a_z:44,b_x:104,b_y:80,b_z:44}',
        f'data modify block {C11A} Items set value [{",".join(house.stock_items())}]',
        f'data modify block {C11A} Items[{{id:"minecraft:oak_planks"}}].count set value {house.BOM["minecraft:oak_planks"]-1}',
        f'scoreboard players set {actor} mcc_rot 0', f'scoreboard players set {actor} mcc_mir 0', f'scoreboard players set {actor} mcc_mask 0',
        f'scoreboard players set {actor} mcc_ucnt 0', f'scoreboard players set {actor} mcc_uhead 0',
        f'scoreboard players set {actor} mcc_rcnt 0', f'scoreboard players set {actor} mcc_rhead 0',
        f'scoreboard players set {actor} mcc_buildconfirm 0',
    ])
    run_as('mcc:blueprint/clear_internal')
    hsel()
    run_as('mcc:copy/run')
    target(*HT)
    run_as('mcc:paste/dispatch')
    hjobs()
    hbpdiag('BP')
    hdrops('BLUEPRINT'); hclear_drops()
    check(f'if score {actor} mcc_bpactive matches 1 if score {actor} mcc_bpready matches 1 if score {actor} mcc_bpbad matches 0 if blocks {hbox(HT)} {hat(HA)} all','house_blueprint_ready_no_real_blocks')
    run_as('mcc:materials/build_start')
    hmat()
    check(f'if blocks {hbox(HT)} {hat(HA)} all if score {actor} mcc_bpactive matches 1','house_build_short_one_plank_builds_nothing')
    check(f'if data block {C11A} Items[{{id:"minecraft:oak_planks",count:{house.BOM["minecraft:oak_planks"]-1}}}] if data block {C11A} Items[{{id:"minecraft:oak_door",count:1}}] if data block {C11A} Items[{{id:"minecraft:stone_bricks",count:20}}]','house_build_short_one_plank_consumes_nothing')
    lines.append(f'data modify block {C11A} Items[{{id:"minecraft:oak_planks"}}].count set value {house.BOM["minecraft:oak_planks"]}')
    run_as('mcc:materials/build_start')
    hmat()
    hbpdiag('AFTERBUILD'); hdiff('BUILD',HT); hdrops('BUILD')
    check(f'if blocks {hbox(HS)} {hat(HT)} all','house_build_exact_3d_copy')
    check(sources_empty,'house_build_consumes_exact_bom')
    check(f'{no_items} if score {actor} mcc_bpactive matches 0','house_build_no_item_drops')
    hclear_drops()
    run_as('mcc:undo/run')
    check(f'if blocks {hbox(HT)} {hat(HA)} all {no_items}','house_build_undo_world')
    for item,count in house.BOM.items():
        lines.append(f'execute as {actor} run function warehouse:api/count_item {{item_id:"{item}"}}')
        check(f'if data storage warehouse:api result{{ok:1b,complete:1b,available:{count}}}',f'house_undo_refunds_{item.split(":")[1]}')
    run_as('mcc:redo/run')
    hmat()
    check(f'if blocks {hbox(HS)} {hat(HT)} all {no_items}','house_redo_rebuilds_exact')
    check(sources_empty,'house_redo_reconsumes_exact_bom')
    run_as('mcc:undo/run')
    check(f'if blocks {hbox(HT)} {hat(HA)} all {no_items}','house_second_undo_world')

    # Rotated (clockwise 90) Blueprint/Build of the same clipboard, materials from the refunded stock.
    lines.append(f'scoreboard players set {actor} mcc_rot 1')
    target(*HT2)
    run_as('mcc:paste/dispatch')
    hjobs()
    run_as('mcc:materials/build_start')
    hmat()
    for i,((dx,dy,dz),state) in enumerate(house.ROT90_EXPECT):
        check(f'if block {HT2[0]+dx} {HT2[1]+dy} {HT2[2]+dz} {state}',f'house_rot90_state_{i}')
    check(f'{sources_empty} {no_items}','house_rot90_consumes_exact_bom')
    run_as('mcc:undo/run')
    check(f'if blocks {HT2[0]-4} {HT2[1]} {HT2[2]} {HT2[0]} {HT2[1]+3} {HT2[2]+4} {hat(HA)} all {no_items}','house_rot90_undo_world')
    lines.append(f'scoreboard players set {actor} mcc_rot 0')
    run_as('mcc:blueprint/clear_internal')

    # Cut + V moves the real 3D house; Undo twice restores the source without drops.
    hsel()
    run_as('mcc:cut/run')
    check(f'if blocks {hbox(HS)} {hat(HA)} all','house_cut_clears_source')
    hdrops('CUT')
    check(no_items,'house_cut_no_item_drops')
    hclear_drops()
    target(*HT)
    run_as('mcc:paste/dispatch')
    hdiff('CUTPASTE',HT); hdrops('CUTPASTE')
    check(f'if blocks {hbox(HR)} {hat(HT)} all {no_items}','house_cut_paste_exact')
    hclear_drops()
    run_as('mcc:undo/run')
    run_as('mcc:undo/run')
    hdiff('CUTUNDO',HS); hdrops('CUTUNDO')
    check(f'if blocks {hbox(HR)} {hat(HS)} all if blocks {hbox(HT)} {hat(HA)} all {no_items}','house_cut_undo_restores_source')
    hclear_drops()

    # Move by +7 on X.
    hsel()
    lines.extend([f'scoreboard players set {actor} mcc_dx 7', f'scoreboard players set {actor} mcc_dy 0', f'scoreboard players set {actor} mcc_dz 0'])
    run_as('mcc:move/run')
    check(f'if blocks {hbox(HR)} {HS[0]+7} {HS[1]} {HS[2]} all if blocks {HS[0]} {HS[1]} {HS[2]} {HS[0]+6} {HS[1]+3} {HS[2]+4} {HA[0]} {HA[1]} {HA[2]} all','house_move_exact')
    hdrops('MOVE')
    check(no_items,'house_move_no_item_drops')
    hclear_drops()
    run_as('mcc:undo/run')
    hdiff('MOVEUNDO',HS); hdrops('MOVEUNDO')
    check(f'if blocks {hbox(HR)} {hat(HS)} all {no_items}','house_move_undo_exact')
    hclear_drops()

    # Flip X mirrors on the X axis: torch and chest swap sides and face the other way, door hinge flips.
    hsel()
    run_as('mcc:flip/x')
    check(f'if block {HS[0]+3} {HS[1]+2} {HS[2]+1} minecraft:wall_torch[facing=west] if block {HS[0]+1} {HS[1]+1} {HS[2]+3} minecraft:chest[facing=east] if block {HS[0]+2} {HS[1]+1} {HS[2]} minecraft:oak_door[facing=north,hinge=right,half=lower]','house_flipx_mirrors_states')
    hdrops('FLIP')
    check(no_items,'house_flipx_no_item_drops')
    hclear_drops()
    run_as('mcc:undo/run')
    hdiff('FLIPUNDO',HS); hdrops('FLIPUNDO')
    check(f'if blocks {hbox(HR)} {hat(HS)} all {no_items}','house_flipx_undo_exact')
    hclear_drops()

    # Direct Rotate 90 around Pos1, four times, returns to the original house.
    hsel()
    run_as('mcc:rotate_edit/r90')
    check(f'if block {HS[0]-1} {HS[1]+2} {HS[2]+1} minecraft:wall_torch[facing=south] if block {HS[0]} {HS[1]+1} {HS[2]+2} minecraft:oak_door[facing=east,half=lower]','house_rotate90_states')
    hdrops('ROT90')
    check(no_items,'house_rotate90_no_item_drops')
    hclear_drops()
    for k in (2,3,4):
        run_as('mcc:rotate_edit/r90')
        lines.append(f'execute as @e[type=minecraft:item] at @s if entity @s[x=90,y=70,z=-10,dx=60,dy=20,dz=60] run say MCCST_DIAG_DROP_ROT{k}_IN_WORLD')
        lines.append(f'execute as @e[type=minecraft:item] at @s unless entity @s[x=90,y=70,z=-10,dx=60,dy=20,dz=60] run say MCCST_DIAG_DROP_ROT{k}_ELSEWHERE')
        hclear_drops()
    for x,y,z,block in house.BLOCKS:
        lines.append(f'execute unless block {HS[0]+x} {HS[1]+y} {HS[2]+z} {block} run say MCCST_DIAG_STATE_ROT90X4 rel {x} {y} {z} expected {block}')
    hdiff('ROT90X4',HS); hdrops('ROT90X4')
    check(f'if blocks {hbox(HR)} {hat(HS)} all {no_items}','house_rotate90_x4_returns_original')
    lines.append(f'fill 92 79 0 143 86 47 air')

    # Main UI toggle labels are built from the player's real state.
    hsel()
    run_as('mcc:ui/more')
    check('if data storage mcc:ui mode if data storage mcc:ui modetip','ui_paste_mode_label')
    check('if data storage mcc:names key{"minecraft:oak_door":"block.minecraft.oak_door","minecraft:redstone":"item.minecraft.redstone"}','item_name_table_loaded')
    # Materials come from the carrier's own stacks first: the take really removes them
    # (a modifier that fails to parse must not be recorded as taken, or Undo would duplicate).
    lines.extend([
        f'item replace entity {actor} weapon.offhand with minecraft:oak_planks 5',
        'data modify storage mcc:materials p991 set value {bom:{"minecraft:oak_planks":{need:3,have:0,remain:3,missing:0,taken:0,inv:0,invhave:0}},items:[{id:"minecraft:oak_planks"}]}',
        'data modify storage mcc:temp mat set value {id:"minecraft:oak_planks",pid:991}',
        f'execute as {actor} run function mcc:materials/inv_take_one with storage mcc:temp mat',
    ])
    check(f'if data entity {actor} equipment.offhand{{id:"minecraft:oak_planks",count:2}} if data storage mcc:materials p991.bom."minecraft:oak_planks"{{remain:0,inv:3}} if data storage mcc:materials p991.items[{{id:"minecraft:oak_planks",inv:3}}]','inventory_take_removes_from_offhand')
    lines.extend([
        'data modify storage mcc:temp mat set value {id:"minecraft:oak_planks",pid:991}',
        f'execute as {actor} run function mcc:materials/inv_count_one with storage mcc:temp mat',
    ])
    check('if data storage mcc:materials p991.bom."minecraft:oak_planks"{invhave:2,have:2}','inventory_count_sees_offhand')
    lines.extend([f'item replace entity {actor} weapon.offhand with minecraft:air', 'data remove storage mcc:materials p991'])

    # Clearing or rebuilding a Blueprint must cancel a pending overlap recount and
    # release its forceload. A 17-wide row puts the actor's buffer (x=20019712,
    # chunk-aligned) across two X chunks; turned 90° it spans two Z chunks instead,
    # so the second X chunk is only released if the recount itself is cancelled.
    def forced(name,x,z):
        lines.append(f'execute in minecraft:overworld store success score #{name} mccst run forceload query {x} {z}')
    run_as('mcc:blueprint/clear_internal')
    lines.extend([
        'fill 0 88 26 16 88 26 stone',
        f'scoreboard players set {actor} mcc_rot 0',
        f'scoreboard players set {actor} mcc_mir 0',
        f'scoreboard players set {actor} mcc_hasa 0',
        f'scoreboard players set {actor} mcc_has1 1',
        f'scoreboard players set {actor} mcc_has2 1',
        f'scoreboard players set {actor} mcc_p1x 0',
        f'scoreboard players set {actor} mcc_p1y 88',
        f'scoreboard players set {actor} mcc_p1z 26',
        f'scoreboard players set {actor} mcc_p1d 1',
        f'scoreboard players set {actor} mcc_p2x 16',
        f'scoreboard players set {actor} mcc_p2y 88',
        f'scoreboard players set {actor} mcc_p2z 26',
        f'scoreboard players set {actor} mcc_p2d 1',
        f'data merge entity {actor} {{Rotation:[0f,0f]}}',
    ])
    run_as('mcc:copy/run')
    for path in ('clear','rebuild'):
        target(0,88,28)
        run_as('mcc:paste/dispatch')
        scan()
        lines.append(f'scoreboard players set {actor} bpright 1')
        run_as('mcc:blueprint/nudge/right')
        forced('fla',20019712,20002000); forced('flb',20019728,20002000)
        check(f'if score {actor} mcc_bpover_scan matches 1 if score #fla mccst matches 1 if score #flb mccst matches 1','recount_pending_before_'+path)
        if path=='clear':
            # Checked before any recount_batch: a stale job would otherwise finish and hide the leak.
            run_as('mcc:blueprint/clear_internal')
            forced('fla',20019712,20002000); forced('flb',20019728,20002000)
            check(f'if score {actor} mcc_bpover_scan matches 0 if score {actor} mcc_bpactive matches 0 if score #fla mccst matches 0 if score #flb mccst matches 0 unless entity @e[type=minecraft:block_display,tag=mcc_blueprint]','clear_cancels_pending_recount')
        else:
            run_as('mcc:state/bp_turn_right')
            scan(4)
            forced('fla',20019712,20002000); forced('flb',20019728,20002000); forced('flc',20019712,20002016)
            check(f'if score {actor} mcc_bpover_scan matches 0 if score {actor} mcc_bpready matches 1 if score {actor} mcc_rot matches 1 if score {actor} mcc_bpsx2 matches 20019712 if score {actor} mcc_bpsz2 matches 20002016 if score #fla mccst matches 0 if score #flb mccst matches 0 if score #flc mccst matches 0','rebuild_cancels_pending_recount_forceload')
    run_as('mcc:blueprint/clear_internal')
    lines.extend([
        'fill 0 88 26 16 88 26 air',
        f'scoreboard players set {actor} mcc_rot 0',
    ])

    # A gated trigger pressed while a material job runs is reported, not silently dropped.
    lines.extend([
        f'scoreboard players set {actor} mcc_tmp 0',
        f'scoreboard players set {actor} undo 1',
    ])
    run_as('mcc:materials/busy_notice')
    check(f'if score {actor} mcc_tmp matches 1','busy_notice_detects_gated_trigger')
    # Earlier sections call nudge functions directly with bp* scores set, and no
    # tick resets them for the armor-stand actor, so clear every gated trigger.
    lines.extend(f'scoreboard players set {actor} {t} 0' for t in (
        'c','x','v','undo','redo','right','left','up','down','forward','backward',
        'flip','flipfb','turnright','rotate180','turnleft',
        'bpleft','bpright','bpforward','bpbackward','bpup','bpdown'))
    lines.append(f'scoreboard players set {actor} mcc_tmp 1')
    run_as('mcc:materials/busy_notice')
    check(f'if score {actor} mcc_tmp matches 0','busy_notice_quiet_without_trigger')

    # Legacy objective names are global. Reloading must preserve them because another datapack
    # may own the same names; only the explicit admin migration may remove them.
    legacy=('rotate','mirror','rotate90','rotate270','flipx','flipz')
    lines.extend(f'scoreboard objectives add {t} trigger' for t in legacy)
    lines.append('function mcc:load')
    for t in legacy+('rotate180','bpturnright'):
        lines.append(f'execute store success score #has_{t} mccst run scoreboard players set #probe {t} 0')
    check(' '.join(f'if score #has_{t} mccst matches 1' for t in legacy)+' if score #has_rotate180 mccst matches 1 if score #has_bpturnright mccst matches 1','legacy_trigger_objectives_preserved_on_load')
    lines.append('function mcc:admin/cleanup_legacy_triggers')
    for t in legacy+('rotate180','bpturnright'):
        lines.append(f'execute store success score #after_{t} mccst run scoreboard players set #probe {t} 0')
    check(' '.join(f'if score #after_{t} mccst matches 0' for t in legacy)+' if score #after_rotate180 mccst matches 1 if score #after_bpturnright mccst matches 1','legacy_trigger_objectives_removed_by_explicit_cleanup')

    # Issue #49: every exact 26.3 block state, placed without block updates, must make the generated
    # matcher write exactly {id, properties} and reach summon (run as the server, so summon itself
    # creates nothing). Repeats cover a state that is already in storage; air must still fail.
    blocks=json.loads((ROOT/'scripts/data/blocks-26.3.json').read_text(encoding='utf-8'))
    states=[]
    for block,spec in blocks.items():
        props=spec.get('properties',{})
        for combo in itertools.product(*props.values()):
            states.append((block,dict(zip(props,combo))))
    states+=[s for s in states if s[0] in ('minecraft:stone','minecraft:oak_planks')]
    states+=[('minecraft:oak_stairs',blocks['minecraft:oak_stairs']['default'])]*2
    bp_lines=['scoreboard players set #bpstates mccst 0','scoreboard players set #bpfail mccst 0',
              'data merge storage mcc:temp {tx:0,ty:0,tz:0,id:0}']
    for block,props in states:
        pred=block+('['+','.join(f'{k}={v}' for k,v in props.items())+']' if props else '')
        snbt='{id:"%s"%s}'%(block,(',properties:{'+','.join(f'{k}:"{v}"' for k,v in props.items())+'}') if props else '')
        bp_lines+=[f'setblock -8 100 -8 {pred} strict',
                   f'data modify storage mcc_server_test:bp want set value {snbt}',
                   'function mcc_server_test:bp_check']
    bp_lines+=['setblock -8 100 -8 minecraft:air strict','data remove storage mcc:temp state',
               'execute store result score #bpair mccst positioned -8 100 -8 run function mcc:blueprint/generated/root']
    (funcs/'bp_states.mcfunction').write_text('\n'.join(bp_lines)+'\n',encoding='utf-8')
    (funcs/'bp_check.mcfunction').write_text('\n'.join([
        'scoreboard players add #bpstates mccst 1',
        'data remove storage mcc:temp state',
        'execute store result score #bpret mccst positioned -8 100 -8 run function mcc:blueprint/generated/root',
        'execute unless score #bpret mccst matches 1 run return run function mcc_server_test:bp_fail with storage mcc_server_test:bp',
        'execute unless data storage mcc:temp state run return run function mcc_server_test:bp_fail with storage mcc_server_test:bp',
        'data modify storage mcc_server_test:bp cmp set from storage mcc_server_test:bp want',
        'execute store success score #bpchg mccst run data modify storage mcc_server_test:bp cmp set from storage mcc:temp state',
        'execute unless score #bpchg mccst matches 0 run return run function mcc_server_test:bp_fail with storage mcc_server_test:bp',
    ])+'\n',encoding='utf-8')
    (funcs/'bp_fail.mcfunction').write_text('scoreboard players add #bpfail mccst 1\n$say MCCST_DIAG_BP_STATE_FAIL $(want)\n',encoding='utf-8')
    lines.append('function mcc_server_test:bp_states')
    check(f'if score #bpstates mccst matches {len(states)} if score #bpfail mccst matches 0 if score #bpair mccst matches 0 unless data storage mcc:temp state','blueprint_matcher_all_exact_states')

    lines.extend([
        f'execute if score #pass mccst matches {len(assertions)} if score #fail mccst matches 0 run say MCCST_REGRESSION_SUCCESS',
        'say MCCST_REGRESSION_DONE',
    ])
    (funcs/'run.mcfunction').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # The run must not start until every fixture chunk is loaded: on a slow runner the console
    # commands queue up, and a fixed sleep once let the run start with the raycast stone's
    # chunk (0,-1) unloaded, failing raycast_v_adjacent_cell_north.
    ready_lines=[f'execute unless loaded {x} 0 {z} run return run say MCCST_CHUNKS_PENDING'
                 for x0,z0,x1,z1 in FORCELOAD for x in range(x0>>4<<4,x1+1,16) for z in range(z0>>4<<4,z1+1,16)]
    (funcs/'chunks_ready.mcfunction').write_text('\n'.join(ready_lines+['say MCCST_CHUNKS_READY'])+'\n',encoding='utf-8')

    (work/'eula.txt').write_text('eula=true\n',encoding='utf-8')
    (work/'server.properties').write_text(
        'server-ip=127.0.0.1\nserver-port=0\nonline-mode=false\nwhite-list=true\n'
        'view-distance=2\nsimulation-distance=2\nlevel-type=minecraft:flat\nmax-tick-time=-1\n'
        'generator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n',
        encoding='utf-8'
    )

    ready=threading.Event(); chunks_ready=threading.Event(); done=threading.Event(); output=[]
    proc=subprocess.Popen([str(java),'-Xms256M','-Xmx2048M','-jar',str(server),'--nogui'],cwd=work,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    def reader():
        assert proc.stdout is not None
        for line in proc.stdout:
            output.append(line)
            if 'Done (' in line: ready.set()
            if 'MCCST_CHUNKS_READY' in line: chunks_ready.set()
            if 'MCCST_REGRESSION_DONE' in line: done.set()
    thread=threading.Thread(target=reader,daemon=True); thread.start()
    try:
        assert ready.wait(90),'Server did not become ready'
        assert proc.stdin is not None
        for x0,z0,x1,z1 in FORCELOAD:
            proc.stdin.write(f'forceload add {x0} {z0} {x1} {z1}\n'); proc.stdin.flush()
        proc.stdin.write('gamerule minecraft:max_command_sequence_length 20000000\n'); proc.stdin.flush()
        deadline=time.monotonic()+120
        while not chunks_ready.is_set():
            assert time.monotonic()<deadline,'Forceloaded fixture chunks did not load'
            proc.stdin.write('function mcc_server_test:chunks_ready\n'); proc.stdin.flush()
            chunks_ready.wait(1)
        proc.stdin.write('function mcc_server_test:run\n'); proc.stdin.flush()
        completed=done.wait(300)
    finally:
        if proc.poll() is None:
            assert proc.stdin is not None
            proc.stdin.write('stop\n'); proc.stdin.flush()
            try: proc.wait(timeout=30)
            except subprocess.TimeoutExpired: proc.terminate()
        thread.join(timeout=5)

    report=''.join(output)
    (work/'console.log').write_text(report,encoding='utf-8')
    failures=[label for label in assertions if f'MCCST_PASS_{label}' not in report]
    parse_errors=[line.strip() for line in output if any(x in line.lower() for x in ('failed to load function','failed to parse','whilst instantiating','invalid macro','missing argument','unknown function'))]
    limit_hits=[line.strip() for line in output if 'limit' in line.lower() and 'command' in line.lower()]
    assert completed, f'Runtime regression did not complete; failed/missing so far: {failures[:40]}; limit messages: {limit_hits[:5]}'
    diag=[line.strip().split(']: ',1)[-1] for line in output if 'MCCST_DIAG_' in line]
    if diag: print('DIAGNOSTICS:\n'+'\n'.join(diag[:400]),flush=True)
    assert not failures, f'Runtime assertion failures: {failures}'
    assert not parse_errors, f'Runtime parser/macro errors: {parse_errors[:20]}'
    assert 'MCCST_REGRESSION_SUCCESS' in report
    print(f'PASS Copy/Paste vanilla 26.3 behavioral regression: {len(assertions)} assertions; evidence: {work}',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--java',type=Path,required=True)
    ap.add_argument('--server-jar',type=Path,required=True)
    ap.add_argument('--accept-eula',action='store_true',required=True)
    args=ap.parse_args()
    (ROOT/'dist').mkdir(exist_ok=True)
    integration(args.java.resolve(),args.server_jar.resolve())
