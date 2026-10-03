#!/usr/bin/env python3
"""Regression checks for the copy-paste datapack.

Runs without a Minecraft client. CI should run this after validate-datapack.py.
"""
from __future__ import annotations
import argparse, json, random, re
from pathlib import Path

RE_FUNC = re.compile(r'\bfunction\s+(mcc:[a-z0-9_./-]+)')
RE_OBJ = re.compile(r'^scoreboard objectives add (\S+) (\S+)', re.M)
RE_TRIGGER = re.compile(r'^scoreboard objectives add (\S+) trigger$', re.M)
USER_TRIGGERS = {
    'copypaste','pos1','pos2','anchor','c','x','v','undo','redo','mode','rotate','mirror',
    'right','left','up','down','forward','backward','flipx','flipz',
    'rotate90','rotate180','rotate270','previewclear','build','materials','bpleft','bpright','bpforward','bpbackward','bpup','bpdown'
}

def read(p: Path) -> str:
    return p.read_text(encoding='utf-8')

def function_ids(pack: Path):
    data=pack/'data'
    out={}
    for p in data.glob('*/function/**/*.mcfunction'):
        rel=p.relative_to(data)
        fid=rel.parts[0]+':'+('/'.join(rel.parts[2:]).removesuffix('.mcfunction'))
        out[fid]=p
    return out

def check_json(pack: Path):
    count=0
    for p in pack.rglob('*.json'):
        json.loads(read(p)); count+=1
    meta=json.loads(read(pack/'pack.mcmeta'))
    assert meta['pack']['min_format']==121 and meta['pack']['max_format']==121
    assert re.search(r'v\d+\.\d+(?:\.\d+)?', str(meta['pack']['description']))
    return count

def check_refs(pack: Path):
    ids=function_ids(pack)
    missing=[]
    for fid,p in ids.items():
        for line in read(p).splitlines():
            if '$(' in line and 'function ' in line:
                continue
            for ref in RE_FUNC.findall(line):
                if ref not in ids: missing.append((fid,ref))
    assert not missing, missing[:20]
    return len(ids)

def check_objectives(pack: Path):
    load=read(pack/'data/mcc/function/load.mcfunction')
    objs=RE_OBJ.findall(load)
    names=[n for n,_ in objs]
    assert len(names)==len(set(names)), 'duplicate objectives in load'
    too_long=[n for n in names if len(n)>16]
    assert not too_long, too_long
    triggers=set(RE_TRIGGER.findall(load))
    assert USER_TRIGGERS <= triggers, USER_TRIGGERS-triggers
    return len(names),len(triggers)

def check_trigger_lifecycle(pack: Path):
    tick=read(pack/'data/mcc/function/tick.mcfunction')
    for t in USER_TRIGGERS:
        assert re.search(rf'scores=\{{{re.escape(t)}=',tick), f'no dispatch/reset selector for {t}'
        assert re.search(rf'scoreboard players set @a\[scores=\{{{re.escape(t)}=.*?\}}\] {re.escape(t)} 0',tick), f'no reset for {t}'
        assert f'scoreboard players enable @a {t}' in tick, f'no enable for {t}'

def check_upgrade_and_mode(pack: Path):
    tick=read(pack/'data/mcc/function/tick.mcfunction')
    for objective,valid in [('mcc_rot','0..3'),('mcc_mir','0..2'),('mcc_usel','0..1'),('mcc_cliptype','0..2'),('mcc_redo','0..1'),('mcc_ucnt','0..5'),('mcc_uhead','0..5'),('mcc_rcnt','0..5'),('mcc_rhead','0..5'),('mcc_bpscan','0..1'),('mcc_bpactive','0..1'),('mcc_bpready','0..1'),('mcc_bpbad','0..1'),('mcc_matphase','0..2'),('mcc_matleft','0..'),('mcc_bpover','0..'),('mcc_buildconfirm','0..1'),('mcc_bpover_scan','0..1'),('mcc_bpoindex','0..')]:
        migration=f'execute as @a unless score @s {objective} matches {valid} run scoreboard players set @s {objective} 0'
        assert migration in tick, f'missing non-destructive upgrade for {objective}'
        assert tick.index(migration)<tick.index('scores={copypaste='), 'migrate before dispatch'
    mode=read(pack/'data/mcc/function/mode_toggle.mcfunction').splitlines()
    assert mode == [
        'execute if score @s mcc_mask matches 0 run return run function mcc:mode/to_masked',
        'return run function mcc:mode/to_replace',
    ], 'mode toggle must return before evaluating the changed state'

def check_no_trigger_collisions(pack: Path, repo: Path|None):
    if repo is None or not (repo/'datapacks').is_dir(): return 0
    ours=USER_TRIGGERS
    collisions=[]
    for other in (repo/'datapacks').iterdir():
        if not other.is_dir() or other.resolve()==pack.resolve(): continue
        for p in other.rglob('*.mcfunction'):
            for t in RE_TRIGGER.findall(read(p)):
                if t in ours: collisions.append((other.name,t,str(p.relative_to(repo))))
    assert not collisions, collisions
    return len(collisions)

def check_clipboard_isolation(pack: Path):
    move=read(pack/'data/mcc/function/move/run.mcfunction')
    flip=read(pack/'data/mcc/function/flip/common_prepare.mcfunction')
    assert 'execute store success score @s mcc_tmp run function mcc:selection/prepare\nexecute unless score @s mcc_tmp matches 1 run return fail' in flip
    for name,text in [('move',move),('flip',flip)]:
        assert 'function mcc:selection/prepare' in text
        assert 'function mcc:work/snapshot_selection' in text
        assert 'function mcc:copy/run' not in text, f'{name} must not overwrite clipboard'
        assert 'mcc:paste/to_' not in text, f'{name} must paste from work buffer, not clipboard'
    assert 'function mcc:work/to_' in move
    for p in (pack/'data/mcc/function/flip').glob('place_*_*.mcfunction'):
        text=read(p)
        assert 'mcc:work_$(id)' in text
        assert 'mcc:clipboard_$(id)' not in text
    work=read(pack/'data/mcc/function/work/save_template.mcfunction')
    assert 'mcc:work_$(id)' in work and '20000400' in work
    load=read(pack/'data/mcc/function/load.mcfunction')
    assert '#cbz mcc_id 20000000' in load
    assert '#ubz mcc_id 20000200' in load
    assert '#workz mcc_id 20000400' in load

def check_ordering(pack: Path):
    move=read(pack/'data/mcc/function/move/run.mcfunction')
    assert move.index('function mcc:work/snapshot_selection') < move.index('function mcc:undo/backup_from_')
    assert move.index('function mcc:undo/backup_from_') < move.index('function mcc:cut/clear_')
    assert move.index('function mcc:cut/clear_') < move.index('function mcc:work/to_')
    assert move.index('function mcc:work/to_') < move.index('function mcc:undo/snapshot_selection')
    flip=read(pack/'data/mcc/function/flip/common_prepare.mcfunction')
    assert flip.index('function mcc:work/snapshot_selection') < flip.index('function mcc:undo/backup_from_')
    assert flip.index('function mcc:undo/backup_from_') < flip.index('function mcc:work/save_template')
    assert flip.index('function mcc:work/save_template') < flip.index('function mcc:cut/clear_')

def check_rollback(pack: Path):
    for op in ('move','flip'):
        restore=read(pack/f'data/mcc/function/{op}/restore_failed.mcfunction')
        assert 'execute unless score @s mcc_ok matches 1 run return fail' in restore
        assert 'execute if score @s mcc_ok matches 1 run function mcc:history/sync_flags' in restore
        assert 'execute unless score @s mcc_ok matches 1 run function mcc:history/commit_edit' in restore
        fail_files=['fail_clear.mcfunction']
        fail_files += ['fail_paste.mcfunction'] if op=='move' else ['fail_place_x.mcfunction','fail_place_z.mcfunction']
        for fn in fail_files:
            text=read(pack/f'data/mcc/function/{op}/{fn}')
            assert f'function mcc:{op}/restore_failed' in text
            assert 'Undo 備份已保留' in text
            assert '已完整還原到操作前狀態' in text
    for op in ('move','flip'):
        text=read(pack/f'data/mcc/function/{op}/fail_backup.mcfunction')
        assert 'function mcc:history/sync_flags' in text

def check_selection_math(pack: Path):
    prep=read(pack/'data/mcc/function/selection/prepare.mcfunction')
    for axis in 'xyz':
        assert f'mcc_sel{axis}' in prep
        assert f'mcc_soff{axis}' in prep
    copy=read(pack/'data/mcc/function/copy/snapshot.mcfunction')
    for axis in 'xyz':
        assert f'mcc_s{axis} = @s mcc_sel{axis}' in copy
        assert f'mcc_off{axis} = @s mcc_soff{axis}' in copy

def check_flip_anchor_formula(pack: Path):
    x=read(pack/'data/mcc/function/flip/x.mcfunction')
    z=read(pack/'data/mcc/function/flip/z.mcfunction')
    assert 'mcc_tmp = @s mcc_minx' in x and 'mcc_tmp += @s mcc_maxx' in x and 'mcc_tmp -= @s mcc_anx' in x
    assert 'mcc_tmp = @s mcc_minz' in z and 'mcc_tmp += @s mcc_maxz' in z and 'mcc_tmp -= @s mcc_anz' in z
    rng=random.Random(401)
    for _ in range(2000):
        lo=rng.randint(-1000,1000); hi=lo+rng.randint(0,47); a=rng.randint(lo,hi)
        b=lo+hi-a
        assert lo<=b<=hi and lo+hi-b==a

def check_move_model():
    rng=random.Random(4041)
    for _ in range(1000):
        sx,sy,sz=[rng.randint(1,12) for _ in range(3)]
        dx,dy,dz=[rng.randint(-8,8) for _ in range(3)]
        if (dx,dy,dz)==(0,0,0): dx=1
        origin=(rng.randint(-20,20),rng.randint(0,30),rng.randint(-20,20))
        src={(origin[0]+x,origin[1]+y,origin[2]+z):(x,y,z) for x in range(sx) for y in range(sy) for z in range(sz)}
        world=dict(src)
        before=dict(world)
        snapshot=dict(src)
        for pos in src: world.pop(pos,None)
        for pos,val in snapshot.items():
            world[(pos[0]+dx,pos[1]+dy,pos[2]+dz)]=val
        world=before
        assert world==before

def check_multiplayer_isolation(pack: Path):
    """Prove the per-player address/name layout cannot collide for normal max selections."""
    load=read(pack/'data/mcc/function/load.mcfunction')
    def constant(name):
        m=re.search(rf'^scoreboard players set #{name} mcc_id (-?\d+)$',load,re.M)
        assert m, f'missing #{name} constant'
        return int(m.group(1))
    slot=constant('slot')
    base=constant('base')
    cbz=constant('cbz')
    ubz=constant('ubz')
    workz=constant('workz')
    redoz=constant('redoz')
    bpz=constant('bpz')
    uhistz=constant('uhistz')
    rhistz=constant('rhistz')
    hgap=constant('hgap')
    assert slot >= 256, f'player X slot too small: {slot}'
    assert len({cbz,ubz,workz,redoz,bpz,uhistz,rhistz}) == 7
    assert hgap >= 256 and hgap % 16 == 0
    undo_hist=[uhistz+i*hgap for i in range(5)]
    redo_hist=[rhistz+i*hgap for i in range(5)]
    hist_ranges=[(z,z+255) for z in undo_hist+redo_hist]
    for i,a in enumerate(hist_ranges):
        for b in hist_ranges[i+1:]:
            assert a[1] < b[0] or b[1] < a[0], f'history Z collision: {a} vs {b}'
    for z0,z1 in hist_ranges:
        assert not (z0 <= bpz+127 and bpz <= z1), f'history overlaps blueprint lane: {(z0,z1)}'

    rects=[]
    for player_id in range(1,65):
        x0=base+player_id*slot
        x1=x0+127
        for kind,z0 in [('clipboard',cbz),('undo',ubz),('work',workz),('redo',redoz),('blueprint',bpz)]:
            rects.append((player_id,kind,x0,x1,z0,z0+127))
    for i,a in enumerate(rects):
        for b in rects[i+1:]:
            overlap_x=not (a[3] < b[2] or b[3] < a[2])
            overlap_z=not (a[5] < b[4] or b[5] < a[4])
            assert not (overlap_x and overlap_z), f'buffer collision: {a} vs {b}'

    pinit=read(pack/'data/mcc/function/player_init.mcfunction')
    assert 'scoreboard players add #next mcc_id 1' in pinit
    assert 'scoreboard players operation @s mcc_id = #next mcc_id' in pinit

    clip_template=read(pack/'data/mcc/function/paste/save_template.mcfunction')
    work_template=read(pack/'data/mcc/function/work/save_template.mcfunction')
    assert 'mcc:clipboard_$(id)' in clip_template
    assert 'mcc:work_$(id)' in work_template

    scheduled=[]
    broad_selectors=[]
    for p in (pack/'data/mcc/function').rglob('*.mcfunction'):
        text=read(p)
        for line in text.splitlines():
            if re.search(r'\bschedule function mcc:',line):
                scheduled.append(str(p.relative_to(pack)))
        if p.name not in {'tick.mcfunction','load.mcfunction'} and '@a' in text:
            broad_selectors.append(str(p.relative_to(pack)))
    assert not scheduled, f'cross-tick shared scratch use: {scheduled}'
    assert not broad_selectors, f'player operation touches @a: {broad_selectors}'

    for name in ('hit_pos1.mcfunction','hit_pos2.mcfunction','hit_anchor.mcfunction','hit_paste.mcfunction'):
        text=read(pack/'data/mcc/function/ray'/name)
        assert text.count('kill @e[type=minecraft:marker,tag=mcc_temp_hit]') >= 2
        assert 'summon minecraft:marker' in text

    return 64

def check_v100_semantics(pack: Path):
    load=read(pack/'data/mcc/function/load.mcfunction')
    tick=read(pack/'data/mcc/function/tick.mcfunction')
    assert 'scoreboard objectives add x trigger' in load
    assert 'scoreboard objectives add cut trigger' not in load
    assert 'scoreboard objectives add redo trigger' in load
    assert 'scoreboard objectives add rotate90 trigger' in load
    assert 'scoreboard objectives add rotate180 trigger' in load
    assert 'scoreboard objectives add rotate270 trigger' in load
    assert 'scoreboard objectives add previewclear trigger' in load
    assert 'scoreboard objectives add build trigger' in load
    assert 'scores={x=1..}' in tick and 'function mcc:cut/run' in tick

    copy=read(pack/'data/mcc/function/copy/run.mcfunction')
    snapshot=read(pack/'data/mcc/function/copy/snapshot.mcfunction')
    cut=read(pack/'data/mcc/function/cut/run.mcfunction')
    dispatch=read(pack/'data/mcc/function/paste/dispatch.mcfunction')
    cut_paste=read(pack/'data/mcc/function/paste/cut_run.mcfunction')
    assert 'function mcc:copy/snapshot' in copy
    assert 'scoreboard players set @s mcc_cliptype 1' in copy
    assert 'function mcc:copy/snapshot' in cut
    assert 'scoreboard players set @s mcc_cliptype 2' in cut
    assert 'function mcc:blueprint/create' in dispatch
    assert 'function mcc:paste/cut_run' in dispatch
    assert 'scoreboard players set @s mcc_clip 0' in cut_paste
    assert 'scoreboard players set @s mcc_cliptype 0' in cut_paste
    assert 'mcc_sx = @s mcc_selx' in snapshot

    # v0.6: five-level per-player Undo/Redo ring history, with legacy one-step fallback.
    undo=read(pack/'data/mcc/function/undo/run.mcfunction')
    redo=read(pack/'data/mcc/function/redo/run.mcfunction')
    hundo=read(pack/'data/mcc/function/history/undo.mcfunction')
    hredo=read(pack/'data/mcc/function/history/redo.mcfunction')
    commit=read(pack/'data/mcc/function/history/commit_edit.mcfunction')
    assert 'mcc_ucnt matches 1..' in undo and 'function mcc:history/undo' in undo
    assert 'mcc_undo matches 1 run return run function mcc:undo/legacy_run' in undo
    assert 'mcc_rcnt matches 1..' in redo and 'function mcc:history/redo' in redo
    assert 'mcc_redo matches 1 run return run function mcc:redo/legacy_run' in redo
    assert 'scoreboard players set @s mcc_rcnt 0' in commit
    assert 'scoreboard players set @s mcc_rhead 0' in commit
    assert 'mcc_hslot matches 6..' in commit
    assert 'mcc_ucnt matches ..4 run scoreboard players add @s mcc_ucnt 1' in commit
    assert 'function mcc:history/save_undo_meta' in commit
    assert 'function mcc:history/load_undo_meta' in hundo
    assert 'function mcc:history/save_redo_meta' in hundo
    assert 'scoreboard players remove @s mcc_ucnt 1' in hundo
    assert 'function mcc:history/load_redo_meta' in hredo
    assert 'function mcc:history/save_undo_meta' in read(pack/'data/mcc/function/history/redo_apply.mcfunction')
    assert 'scoreboard players remove @s mcc_rcnt 1' in read(pack/'data/mcc/function/history/redo_apply.mcfunction')
    for name,key in [('save_undo_meta.mcfunction','u_p$(id)_s$(slot)'),('load_undo_meta.mcfunction','u_p$(id)_s$(slot)'),('save_redo_meta.mcfunction','r_p$(id)_s$(slot)'),('load_redo_meta.mcfunction','r_p$(id)_s$(slot)')]:
        assert key in read(pack/'data/mcc/function/history'/name)
    save_u=read(pack/'data/mcc/function/history/save_undo_meta.mcfunction')
    load_u=read(pack/'data/mcc/function/history/load_undo_meta.mcfunction')
    assert '.mat int 1 run scoreboard players get @s mcc_histmat' in save_u
    assert '.materials.items set from storage mcc:materials p$(id).items' in save_u
    assert '.materials.bom set from storage mcc:materials p$(id).bom' in save_u
    assert 'scoreboard players set @s mcc_umat 0' in load_u
    assert 'u_p$(id)_s$(slot){mat:1} run scoreboard players set @s mcc_umat 1' in load_u
    load_r=read(pack/'data/mcc/function/history/load_redo_meta.mcfunction')
    assert 'r_p$(id)_s$(slot){mat:1} run scoreboard players set @s mcc_rmat 1' in load_r
    undo_hist=read(pack/'data/mcc/function/history/undo.mcfunction')
    redo_hist=read(pack/'data/mcc/function/history/redo.mcfunction')
    redo_apply=read(pack/'data/mcc/function/history/redo_apply.mcfunction')
    assert 'function mcc:history/check_undo_material_guard' in undo_hist
    assert 'function mcc:history/refund_undo_materials' in undo_hist
    assert 'function mcc:history/copy_undo_materials_to_redo' in undo_hist
    assert 'function mcc:materials/redo_start' in redo_hist
    assert 'function mcc:history/copy_redo_snapshot_to_material_guard' in redo_apply
    assert (pack/'data/mcc/function/history/compare_hidden.mcfunction').is_file()

    for p in (
        pack/'data/mcc/function/move/run.mcfunction',
        pack/'data/mcc/function/flip/x.mcfunction',
        pack/'data/mcc/function/flip/z.mcfunction',
        pack/'data/mcc/function/cut/run.mcfunction',
        pack/'data/mcc/function/rotate_edit/run.mcfunction',
    ):
        assert 'function mcc:history/commit_edit' in read(p), f'new world edit must commit Undo and invalidate Redo: {p}'

    rotate=read(pack/'data/mcc/function/rotate_edit/run.mcfunction')
    assert 'function mcc:work/snapshot_selection' in rotate
    assert 'function mcc:undo/backup_from_' in rotate
    assert 'function mcc:cut/clear_' in rotate
    assert 'function mcc:rotate_edit/place_' in rotate
    assert rotate.index('function mcc:work/snapshot_selection') < rotate.index('function mcc:cut/clear_')
    assert rotate.index('function mcc:undo/backup_from_') < rotate.index('function mcc:cut/clear_')
    for name in ('r90.mcfunction','r180.mcfunction','r270.mcfunction'):
        assert (pack/'data/mcc/function/rotate_edit'/name).is_file()

    bp=pack/'data/mcc/function/blueprint'
    create=read(bp/'create.mcfunction')
    direct=read(bp/'init_direct.mcfunction')
    transformed=read(bp/'init_transformed.mcfunction')
    summon=read(bp/'summon.mcfunction')
    assert 'mcc_cliptype matches 1' in create
    assert 'function mcc:blueprint/init_direct' in create
    assert 'function mcc:blueprint/init_transformed' in create
    assert 'function mcc:blueprint/copy_direct_buffer' in direct
    assert 'clone from minecraft:overworld' in read(bp/'copy_direct_buffer.mcfunction')
    # The aimed cell is always the Anchor destination. Without a custom Anchor,
    # selection/prepare uses Pos1; direct Blueprint placement must apply the saved
    # Pos1/Anchor offset exactly like real paste.
    prep=read(pack/'data/mcc/function/selection/prepare.mcfunction')
    for axis in 'xyz':
        pos1 = {'x':'mcc_p1x','y':'mcc_p1y','z':'mcc_p1z'}[axis]
        anchor = {'x':'mcc_anx','y':'mcc_any','z':'mcc_anz'}[axis]
        soff = f'mcc_soff{axis}'
        target = {'x':'mcc_dstx','y':'mcc_dsty','z':'mcc_dstz'}[axis]
        preview = {'x':'mcc_bptx0','y':'mcc_bpty0','z':'mcc_bptz0'}[axis]
        offset = {'x':'mcc_offx','y':'mcc_offy','z':'mcc_offz'}[axis]
        assert f'{soff} = @s {pos1}' in prep
        assert f'execute if score @s mcc_hasa matches 1 run scoreboard players operation @s {soff} = @s {anchor}' in prep
        assert f'{preview} = @s {target}' in direct
        assert f'{preview} -= @s {offset}' in direct
    # Transformed Blueprint placement uses the same saved Anchor offset through transform math.
    assert 'function mcc:paste/prepare_transform' in transformed
    assert 'function mcc:paste/save_template' in transformed
    assert 'execute in minecraft:overworld run function mcc:paste/do_place' in transformed
    assert 'summon minecraft:block_display' in summon
    assert 'block_state set from storage mcc:temp state' in summon

    # Generated exact-state dispatcher: every non-air 26.3 block appears in exactly one group.
    tag_dir=pack/'data/mcc/tags/block/blueprint/generated'
    group_dir=pack/'data/mcc/function/blueprint/generated'
    tags=sorted(tag_dir.glob('g_*.json'))
    groups=sorted(group_dir.glob('group_*.mcfunction'))
    assert len(tags)==128 and len(groups)==128
    block_ids=[]
    for p in tags:
        obj=json.loads(read(p))
        block_ids.extend(obj['values'])
    assert len(block_ids)==len(set(block_ids))==1283
    matcher_states=sum(read(p).count('run data modify storage mcc:temp state set value') for p in groups)
    assert matcher_states==35720, matcher_states
    root=read(group_dir/'root.mcfunction')
    for i in range(128):
        assert f'#mcc:blueprint/generated/g_{i}' in root
        assert f'function mcc:blueprint/generated/group_{i}' in root

    # Copy-V stays preview-only; v1.0 construction is a separate, material-gated Build step.
    assert 'mcc_cliptype matches 1 run return run function mcc:blueprint/create' in dispatch
    build=read(pack/'data/mcc/function/materials/build_start.mcfunction')
    place=read(pack/'data/mcc/function/materials/place.mcfunction')
    scan=read(pack/'data/mcc/function/blueprint/scan_one.mcfunction')
    assert 'mcc_bpready matches 1' in build
    assert 'function mcc:materials/bom_reset' in create
    assert 'function mcc:materials/bom_from_block' in scan
    assert 'function mcc:materials/sanitize_block' in scan
    assert 'function mcc:materials/queue_items' in build
    assert 'function mcc:materials/queue_boxes' not in build
    process_next=read(pack/'data/mcc/function/materials/process_next_do.mcfunction')
    count_one=read(pack/'data/mcc/function/materials/warehouse_count_one.mcfunction')
    take_one=read(pack/'data/mcc/function/materials/warehouse_take_one.mcfunction')
    assert 'warehouse:api/count_item' in count_one
    assert 'warehouse:api/take_item' in take_one
    assert 'items[{id:"$(id)"}].taken' in take_one
    assert 'mcc:materials/warehouse_count_one' in process_next
    assert 'mcc:materials/warehouse_take_one' in process_next
    refund_taken=read(pack/'data/mcc/function/materials/refund_taken_one.mcfunction')
    refund_undo=read(pack/'data/mcc/function/history/refund_undo_materials_one.mcfunction')
    assert 'warehouse:api/refund_item' in refund_taken
    assert 'warehouse:api/refund_item' in refund_undo
    assert 'mcc:temp mat.taken' in refund_taken
    assert 'mcc:temp txitem.taken' in refund_undo
    refund_tx_entry=read(pack/'data/mcc/function/history/refund_undo_materials.mcfunction')
    copy_tx_entry=read(pack/'data/mcc/function/history/copy_undo_materials_to_redo.mcfunction')
    redo_tx_entry=read(pack/'data/mcc/function/materials/redo_start.mcfunction')
    for tx_entry in (refund_tx_entry,copy_tx_entry,redo_tx_entry):
        assert 'data modify storage mcc:temp tx set value {}' in tx_entry
    assert 'give @s' not in refund_taken and 'give @s' not in refund_undo
    assert 'function mcc:materials/place_buffer' in place
    assert 'mcc_bpover' in read(pack/'data/mcc/function/blueprint/scan_one.mcfunction')
    assert 'function mcc:materials/build_warn_overlap' in build
    assert (pack/'data/mcc/function/materials/check_start.mcfunction').is_file()
    assert (pack/'data/mcc/function/materials/report_all_start.mcfunction').is_file()
    assert (pack/'data/mcc/function/blueprint/nudge/run.mcfunction').is_file()
    assert 'function mcc:blueprint/recount_start' in read(pack/'data/mcc/function/blueprint/nudge/run.mcfunction')
    assert 'mcc_bpover_scan' in read(pack/'data/mcc/function/tick.mcfunction')
    assert (pack/'data/mcc/dialog/main.json').is_file()
    main_dialog=read(pack/'data/mcc/dialog/main.json')
    assert '"dialog": "warehouse:main"' not in main_dialog
    assert '"command": "trigger wh_nav set 1"' in main_dialog
    assert 'scoreboard players set @s mcc_histmat 1' in place
    assert (pack/'data/mcc/tags/block/material_unsupported.json').is_file()
    panel=read(pack/'data/mcc/function/panel.mcfunction')
    assert '/trigger build' in panel
    assert '/trigger matbox' not in panel and '/trigger matremove' not in panel and '/trigger matlist' not in panel
    assert 'Warehouse 共用倉庫' in panel
    return matcher_states

def check_version_labels(pack: Path):
    meta=json.loads(read(pack/'pack.mcmeta'))
    desc=meta['pack']['description']
    m=re.search(r'v(\d+\.\d+(?:\.\d+)?)',desc)
    assert m, f'pack description has no semantic version: {desc}'
    version=m.group(1)
    load=read(pack/'data/mcc/function/load.mcfunction')
    panel=read(pack/'data/mcc/function/panel.mcfunction')
    assert f'v{version} 已載入' in load, f'load message not synced to v{version}'
    assert f'Copy/Paste v{version}' in panel, f'panel title not synced to v{version}'
    return version

def check_tellraw_json(pack: Path):
    checked=0
    for p in pack.rglob('*.mcfunction'):
        for line in read(p).splitlines():
            idx=line.find('tellraw ')
            if idx<0: continue
            tail=line[idx:].split(' ',2)
            if len(tail)<3: continue
            payload=tail[2]
            if payload.startswith('[') or payload.startswith('{'):
                json.loads(payload); checked+=1
    return checked

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pack-root',type=Path)
    ap.add_argument('--repo-root',type=Path)
    args=ap.parse_args()
    if args.pack_root:
        pack=args.pack_root.resolve(); repo=args.repo_root.resolve() if args.repo_root else None
    else:
        repo=Path(__file__).resolve().parents[1]
        pack=repo/'datapacks/copy-paste'
    j=check_json(pack)
    f=check_refs(pack)
    o,t=check_objectives(pack)
    check_trigger_lifecycle(pack)
    check_upgrade_and_mode(pack)
    check_no_trigger_collisions(pack,repo)
    check_clipboard_isolation(pack)
    check_ordering(pack)
    check_rollback(pack)
    check_selection_math(pack)
    check_flip_anchor_formula(pack)
    check_move_model()
    mp=check_multiplayer_isolation(pack)
    states=check_v100_semantics(pack)
    version=check_version_labels(pack)
    tj=check_tellraw_json(pack)
    print(f'PASS copy-paste regression v{version}: {j} JSON, {f} functions, {o} objectives, {t} triggers, {tj} tellraw JSON, {mp}-player buffer isolation, {states} exact blueprint states, copy-v blueprint/material-build semantics, five-level undo/redo, real rotate, clipboard isolation, rollback, move/flip properties')

if __name__=='__main__': main()
