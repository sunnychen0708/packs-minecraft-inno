"""Minimal read-only Anvil world reader: blocks (with properties), block entities, item entities."""
from __future__ import annotations
import gzip, io, struct, zlib, os
from pathlib import Path

# ---------- NBT ----------
def _read_nbt(buf: io.BytesIO, tag: int):
    r = buf.read
    if tag == 1: return struct.unpack('>b', r(1))[0]
    if tag == 2: return struct.unpack('>h', r(2))[0]
    if tag == 3: return struct.unpack('>i', r(4))[0]
    if tag == 4: return struct.unpack('>q', r(8))[0]
    if tag == 5: return struct.unpack('>f', r(4))[0]
    if tag == 6: return struct.unpack('>d', r(8))[0]
    if tag == 7:
        n = struct.unpack('>i', r(4))[0]; return r(n)
    if tag == 8:
        n = struct.unpack('>H', r(2))[0]; return r(n).decode('utf-8', 'replace')
    if tag == 9:
        t = r(1)[0]; n = struct.unpack('>i', r(4))[0]
        return [_read_nbt(buf, t) for _ in range(n)]
    if tag == 10:
        out = {}
        while True:
            t = r(1)[0]
            if t == 0: return out
            n = struct.unpack('>H', r(2))[0]; name = r(n).decode('utf-8', 'replace')
            out[name] = _read_nbt(buf, t)
    if tag == 11:
        n = struct.unpack('>i', r(4))[0]; return list(struct.unpack(f'>{n}i', r(4 * n)))
    if tag == 12:
        n = struct.unpack('>i', r(4))[0]; return list(struct.unpack(f'>{n}q', r(8 * n)))
    raise ValueError(f'bad tag {tag}')

def parse_nbt(data: bytes):
    buf = io.BytesIO(data)
    t = buf.read(1)[0]
    n = struct.unpack('>H', buf.read(2))[0]; buf.read(n)
    return _read_nbt(buf, t)

def _read_region_chunk(path: Path, cx: int, cz: int):
    if not path.exists(): return None
    with open(path, 'rb') as f:
        idx = 4 * ((cx & 31) + (cz & 31) * 32)
        f.seek(idx); loc = f.read(4)
        off = int.from_bytes(loc[:3], 'big'); cnt = loc[3]
        if off == 0 or cnt == 0: return None
        f.seek(off * 4096)
        length = int.from_bytes(f.read(4), 'big'); comp = f.read(1)[0]
        raw = f.read(length - 1)
    if comp & 0x80:
        ext = path.with_name(f'c.{cx}.{cz}.mcc'); raw = ext.read_bytes(); comp &= 0x7f
    if comp == 1: data = gzip.decompress(raw)
    elif comp == 2: data = zlib.decompress(raw)
    elif comp == 3: data = raw
    elif comp == 4:
        raise RuntimeError('LZ4 chunk compression not supported')
    else: raise RuntimeError(f'compression {comp}')
    return parse_nbt(data)

DIM_DIR = {'overworld': '', 'the_nether': 'DIM-1', 'the_end': 'DIM1'}

class World:
    def __init__(self, root: str | Path, dim: str = 'overworld'):
        self.root = Path(root)
        base = self.root / 'dimensions' / 'minecraft' / dim
        if not base.exists():  # legacy layout
            base = self.root / DIM_DIR[dim] if DIM_DIR[dim] else self.root
        self.base = base
        self._chunks = {}
        self._ent_chunks = {}

    def _chunk(self, cx, cz):
        k = (cx, cz)
        if k not in self._chunks:
            p = self.base / 'region' / f'r.{cx >> 5}.{cz >> 5}.mca'
            self._chunks[k] = _read_region_chunk(p, cx, cz)
        return self._chunks[k]

    def block(self, x, y, z) -> str:
        ch = self._chunk(x >> 4, z >> 4)
        if ch is None: return 'UNLOADED'
        secs = ch.get('sections') or ch.get('Level', {}).get('Sections') or []
        sy = y >> 4
        for s in secs:
            if s.get('Y') == sy:
                bs = s.get('block_states')
                if not bs: return 'minecraft:air'
                pal = bs['palette']
                if len(pal) == 1 or 'data' not in bs: return fmt(pal[0])
                bits = max(4, (len(pal) - 1).bit_length())
                per = 64 // bits
                i = ((y & 15) << 8) | ((z & 15) << 4) | (x & 15)
                v = bs['data'][i // per] & ((1 << 64) - 1)
                return fmt(pal[(v >> ((i % per) * bits)) & ((1 << bits) - 1)])
        return 'minecraft:air'

    def block_entity(self, x, y, z):
        ch = self._chunk(x >> 4, z >> 4)
        if ch is None: return None
        for be in ch.get('block_entities', []):
            if (be.get('x'), be.get('y'), be.get('z')) == (x, y, z): return be
        return None

    def entities_in(self, x1, y1, z1, x2, y2, z2):
        out = []
        for cx in range(min(x1, x2) >> 4, (max(x1, x2) >> 4) + 1):
            for cz in range(min(z1, z2) >> 4, (max(z1, z2) >> 4) + 1):
                p = self.base / 'entities' / f'r.{cx >> 5}.{cz >> 5}.mca'
                ch = _read_region_chunk(p, cx, cz)
                if not ch: continue
                for e in ch.get('Entities', []):
                    pos = e.get('Pos', [0, 0, 0])
                    if min(x1, x2) <= pos[0] <= max(x1, x2) + 1 and min(y1, y2) <= pos[1] <= max(y1, y2) + 1 and min(z1, z2) <= pos[2] <= max(z1, z2) + 1:
                        out.append(e)
        return out

import json as _json
_DEFAULTS = _json.load(open(Path(__file__).with_name('defaults.json'), encoding='utf-8'))

def fmt(p) -> str:
    if isinstance(p, str): name, props = p, None
    elif '' in p and len(p) == 1: name, props = p[''], None  # bare string in a mixed list
    else:
        name = p.get('Name') or p.get('id')
        props = p.get('Properties') or p.get('properties')
    full = dict(_DEFAULTS.get(name, {}))
    full.update(props or {})
    props = full
    if not props: return name
    return name + '[' + ','.join(f'{k}={v}' for k, v in sorted(props.items())) + ']'

def items_of(be) -> dict:
    out = {}
    for it in (be or {}).get('Items', []):
        out[it['id']] = out.get(it['id'], 0) + it.get('count', it.get('Count', 1))
    return out
