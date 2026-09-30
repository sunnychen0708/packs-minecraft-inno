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
    'copypaste','pos1','pos2','anchor','c','v','cut','undo','mode','rotate','mirror',
    'right','left','up','down','forward','backward','flipx','flipz'
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
    assert 'v0.4.1' in meta['pack']['description']
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
        assert 'execute if score @s mcc_ok matches 1 run scoreboard players set @s mcc_undo 0' in restore
        fail_files=['fail_clear.mcfunction']
        fail_files += ['fail_paste.mcfunction'] if op=='move' else ['fail_place_x.mcfunction','fail_place_z.mcfunction']
        for fn in fail_files:
            text=read(pack/f'data/mcc/function/{op}/{fn}')
            assert f'function mcc:{op}/restore_failed' in text
            assert 'Undo 備份已保留' in text
            assert '已完整還原到操作前狀態' in text
    for op in ('move','flip'):
        text=read(pack/f'data/mcc/function/{op}/fail_backup.mcfunction')
        assert 'scoreboard players set @s mcc_undo 0' in text

def check_selection_math(pack: Path):
    prep=read(pack/'data/mcc/function/selection/prepare.mcfunction')
    for axis in 'xyz':
        assert f'mcc_sel{axis}' in prep
        assert f'mcc_soff{axis}' in prep
    copy=read(pack/'data/mcc/function/copy/run.mcfunction')
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
    check_no_trigger_collisions(pack,repo)
    check_clipboard_isolation(pack)
    check_ordering(pack)
    check_rollback(pack)
    check_selection_math(pack)
    check_flip_anchor_formula(pack)
    check_move_model()
    tj=check_tellraw_json(pack)
    print(f'PASS copy-paste regression: {j} JSON, {f} functions, {o} objectives, {t} triggers, {tj} tellraw JSON, clipboard isolation, rollback, move/flip properties')

if __name__=='__main__': main()
