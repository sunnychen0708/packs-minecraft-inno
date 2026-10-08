#!/usr/bin/env python3
"""Isolated vanilla 26.3 behavioral regression for Copy/Paste v1.2.1.

Uses a non-player armor stand test actor to exercise internal datapack functions.
This complements (not replaces) the opt-in real-player trigger/client harnesses.
"""
from __future__ import annotations
import argparse
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

def integration(java: Path, server: Path):
    work=ROOT/'dist'/('copy-paste-runtime-'+uuid.uuid4().hex[:8])
    work.mkdir(parents=True)
    packs=work/'world/datapacks'
    packs.mkdir(parents=True)

    # Build the current real-player harness into the same official-server world.
    # It is not executed headlessly, but every generated mcfunction is parsed by
    # vanilla 26.3 so stale/invalid Trigger harness commands fail CI.
    subprocess.run([
        sys.executable,
        str(ROOT/'scripts/build-copy-paste-live-test.py'),
        '--output', str(packs/'mcc-live-test'),
    ], check=True)

    with zipfile.ZipFile(packs/'copy-paste.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in PACK.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(PACK).as_posix())
    with zipfile.ZipFile(packs/'warehouse.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in WAREHOUSE.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(WAREHOUSE).as_posix())

    harness=packs/'regression'
    funcs=harness/'data/mcc_server_test/function'
    funcs.mkdir(parents=True)
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
    check(f'positioned 12 80 12 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={{block_state:"minecraft:iron_block"}},limit=1] if score {actor} mcc_bptx0 matches 10 if score {actor} mcc_bptz0 matches 11','default_anchor_pos1_blueprint_origin')
    check('positioned 10 80 11 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','default_anchor_pos1_blueprint_offset')
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
    check(f'positioned 20 82 12 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={{block_state:"minecraft:iron_block"}},limit=1] if score {actor} mcc_bptx0 matches 18 if score {actor} mcc_bpty0 matches 82 if score {actor} mcc_bptz0 matches 11','custom_anchor_direct_exact_target')
    check('positioned 18 82 11 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','custom_anchor_direct_source_offset')
    run_as('mcc:blueprint/clear_internal')

    # 0b. The same custom Anchor invariant must hold for every Rotate/Mirror combination.
    for rot in range(4):
        for mir in range(3):
            lines.append(f'scoreboard players set {actor} mcc_rot {rot}')
            lines.append(f'scoreboard players set {actor} mcc_mir {mir}')
            target(24,82,12)
            run_as('mcc:paste/dispatch')
            scan()
            check(f'positioned 24 82 12 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={{block_state:"minecraft:iron_block"}},limit=1]','custom_anchor_r%d_m%d_exact_target' % (rot,mir))
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
    check(f'positioned 30 80 30 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={{block_state:"minecraft:gold_block"}},limit=1] if score {actor} mcc_bptx0 matches 30 if score {actor} mcc_bptz0 matches 30','external_anchor_blueprint_direct')
    run_as('mcc:blueprint/clear_internal')

    lines.append(f'scoreboard players set {actor} mcc_rot 1')
    target(40,80,40)
    run_as('mcc:paste/dispatch')
    scan()
    check('positioned 50 80 30 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','external_anchor_blueprint_rotate90_gold')
    check('positioned 50 80 32 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:diamond_block"},limit=1]','external_anchor_blueprint_rotate90_diamond')
    run_as('mcc:blueprint/clear_internal')

    lines.append(f'scoreboard players set {actor} mcc_rot 0')
    lines.append(f'scoreboard players set {actor} mcc_mir 1')
    target(40,80,40)
    run_as('mcc:paste/dispatch')
    scan()
    check('positioned 50 80 30 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','external_anchor_blueprint_mirrorx_gold')
    check('positioned 48 80 30 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:diamond_block"},limit=1]','external_anchor_blueprint_mirrorx_diamond')
    run_as('mcc:blueprint/clear_internal')
    lines.append(f'scoreboard players set {actor} mcc_mir 0')

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
    check('positioned 12 80 3 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]','blueprint_gold_state')
    check('positioned 12 80 4 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:{id:"minecraft:oak_stairs",properties:{facing:"east",half:"bottom",shape:"straight",waterlogged:"false"}}},limit=1]','blueprint_stair_state')
    check('if block 3 80 3 gold_block if block 5 80 4 iron_block','copy_source_unchanged')

    # 1a. Phase 3 Blueprint micro-adjust moves displays without rebuilding the BOM.
    lines.append(f'scoreboard players set {actor} bpright 1')
    run_as('mcc:blueprint/nudge/right')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 11 80 3 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bptx0 matches 11 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_right')
    lines.append(f'scoreboard players set {actor} bpleft 1')
    run_as('mcc:blueprint/nudge/left')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12 80 3 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bptx0 matches 12 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_left_restore')
    lines.append(f'scoreboard players set {actor} bpforward 1')
    run_as('mcc:blueprint/nudge/forward')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12 80 4 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bptz0 matches 4 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_forward')
    lines.append(f'scoreboard players set {actor} bpbackward 1')
    run_as('mcc:blueprint/nudge/backward')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12 80 3 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bptz0 matches 3 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_backward_restore')
    lines.append(f'scoreboard players set {actor} bpup 1')
    run_as('mcc:blueprint/nudge/up')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12 81 3 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bpty0 matches 81 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_up')
    lines.append(f'scoreboard players set {actor} bpdown 1')
    run_as('mcc:blueprint/nudge/down')
    run_as('mcc:blueprint/recount_batch')
    check(f'positioned 12 80 3 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,limit=1] if score {actor} mcc_bpty0 matches 80 if score {actor} mcc_bpover_scan matches 0','phase3_blueprint_nudge_down_restore')

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
    check('positioned 20 82 21 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:iron_block"},limit=1]','custom_anchor_build_preview_exact')
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
    check(f'if block 3 80 3 gold_block if block 5 80 4 iron_block if score {actor} mcc_redo matches 1','x_undo')
    run_as('mcc:redo/run')
    check(f'if block 3 80 3 air if block 5 80 4 air if score {actor} mcc_undo matches 1','x_redo')
    run_as('mcc:undo/run')
    run_as('mcc:cut/run')
    target(12,80,3)
    run_as('mcc:paste/dispatch')
    check(f'if block 12 80 3 gold_block if block 14 80 4 iron_block if score {actor} mcc_clip matches 0 if score {actor} mcc_cliptype matches 0','x_v_real_and_consumed')
    target(20,80,3)
    run_as('mcc:paste/dispatch')
    check('if block 20 80 3 air if block 22 80 4 air','x_no_second_paste')

    # 3. Undo <-> Redo toggles latest real paste.
    run_as('mcc:undo/run')
    check(f'if block 12 80 3 air if score {actor} mcc_redo matches 1','paste_undo')
    run_as('mcc:redo/run')
    check(f'if block 12 80 3 gold_block if score {actor} mcc_undo matches 1','paste_redo')
    run_as('mcc:undo/run')

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

    # 4a. Player-facing Move wrappers at yaw 0 must map to the expected world directions.
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
    check('positioned 20 80 17 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..4,limit=1]','rotated_blueprint_display')
    run_as('mcc:blueprint/clear_internal')
    lines.append(f'scoreboard players set {actor} mcc_rot 0')

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

    lines.extend([
        f'execute if score #pass mccst matches {len(assertions)} if score #fail mccst matches 0 run say MCCST_REGRESSION_SUCCESS',
        'say MCCST_REGRESSION_DONE',
    ])
    (funcs/'run.mcfunction').write_text('\n'.join(lines)+'\n',encoding='utf-8')

    (work/'eula.txt').write_text('eula=true\n',encoding='utf-8')
    (work/'server.properties').write_text(
        'server-ip=127.0.0.1\nserver-port=0\nonline-mode=false\nwhite-list=true\n'
        'view-distance=2\nsimulation-distance=2\nlevel-type=minecraft:flat\n'
        'generator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n',
        encoding='utf-8'
    )

    ready=threading.Event(); done=threading.Event(); output=[]
    proc=subprocess.Popen([str(java),'-Xms256M','-Xmx1024M','-jar',str(server),'--nogui'],cwd=work,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    def reader():
        assert proc.stdout is not None
        for line in proc.stdout:
            output.append(line)
            if 'Done (' in line: ready.set()
            if 'MCCST_REGRESSION_DONE' in line: done.set()
    thread=threading.Thread(target=reader,daemon=True); thread.start()
    try:
        assert ready.wait(90),'Server did not become ready'
        assert proc.stdin is not None
        # /forceload takes block coordinates, not chunk indices. Cover every visible fixture chunk (x=0..2, z=0..1).
        proc.stdin.write('forceload add 0 0 47 31\n'); proc.stdin.flush()
        proc.stdin.write('gamerule minecraft:max_command_sequence_length 250000\n'); proc.stdin.flush()
        time.sleep(2)
        proc.stdin.write('function mcc_server_test:run\n'); proc.stdin.flush()
        assert done.wait(90),'Runtime regression did not complete'
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
