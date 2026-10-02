#!/usr/bin/env python3
"""Isolated vanilla 26.3 behavioral regression for Copy/Paste v1.0.

Uses a non-player armor stand test actor to exercise internal datapack functions.
This complements (not replaces) the opt-in real-player trigger/client harnesses.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
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

    with zipfile.ZipFile(packs/'copy-paste.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in PACK.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(PACK).as_posix())
    with zipfile.ZipFile(packs/'warehouse.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in WAREHOUSE.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(WAREHOUSE).as_posix())

    harness=packs/'regression'
    funcs=harness/'data/mcc_server_test/function'
    funcs.mkdir(parents=True)
    (harness/'pack.mcmeta').write_text(json.dumps({'pack':{'min_format':121,'max_format':121,'description':'CopyPaste v1.0 server regression'}}),encoding='utf-8')

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
    run_as('mcc:materials/build_start')
    for _ in range(4): run_as('mcc:materials/process_batch')
    check(f'if block 12 80 3 air if block 14 80 4 air if score {actor} mcc_matphase matches 0 if score {actor} mcc_bpactive matches 1','build_missing_all_or_nothing')
    check('if data block 8 80 8 Items[{id:"minecraft:gold_block",count:1}] if data block 8 80 8 Items[{id:"minecraft:diamond_block",count:1}]','build_missing_no_consume')
    lines.append('data modify block 8 80 8 Items append value {Slot:3b,id:"minecraft:iron_block",count:1}')
    run_as('mcc:materials/build_start')
    for _ in range(8): run_as('mcc:materials/process_batch')
    check(f'if block 12 80 3 gold_block if block 14 80 3 diamond_block if block 12 80 4 oak_stairs[facing=east] if block 14 80 4 iron_block if score {actor} mcc_bpactive matches 0','build_material_success')
    check('unless data block 8 80 8 Items[0]','build_materials_consumed')
    check('if data storage mcc:history u_p77_s1.materials.bom."minecraft:gold_block"{taken:1} if data storage mcc:history u_p77_s1.materials.bom."minecraft:diamond_block"{taken:1} if data storage mcc:history u_p77_s1.materials.bom."minecraft:oak_stairs"{taken:1} if data storage mcc:history u_p77_s1.materials.bom."minecraft:iron_block"{taken:1}','build_history_archives_taken')
    lines.append('setblock 12 80 3 emerald_block')
    run_as('mcc:undo/run')
    check(f'if block 12 80 3 emerald_block if score {actor} mcc_ucnt matches 1','build_undo_guard_refuses_modified_world')
    lines.append('setblock 12 80 3 gold_block')
    run_as('mcc:undo/run')
    check(f'if block 12 80 3 air if block 14 80 4 air if score {actor} mcc_rcnt matches 1','build_undo_world')
    check('if data storage warehouse:api result{operation:"refund_item",ok:1b,complete:1b}','build_undo_called_refund_api')
    check('unless data storage warehouse:api pending_refunds[0].item_id','build_undo_refund_not_pending')
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

    # 5. Direct Rotate90 modifies real blocks around Pos1 and is Undo/Redo reversible.
    fixture(3,80,17)
    run_as('mcc:rotate_edit/r90')
    check('if block 3 80 17 gold_block if block 3 80 19 diamond_block if block 2 80 17 oak_stairs[facing=south] if block 2 80 19 iron_block','rotate90_real')
    run_as('mcc:undo/run')
    check('if block 3 80 17 gold_block if block 5 80 17 diamond_block if block 3 80 18 oak_stairs[facing=east]','rotate90_undo')
    run_as('mcc:redo/run')
    check('if block 3 80 19 diamond_block if block 2 80 17 oak_stairs[facing=south]','rotate90_redo')

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
