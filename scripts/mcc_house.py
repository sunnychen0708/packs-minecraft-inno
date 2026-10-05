"""Shared 3D test structure for the Copy/Paste regressions.

A 5x4x5 (x, y, z) house with the block kinds that break naive copy logic:
multi-block doors, double/top/bottom slabs, stairs in every facing and both
halves, log axes, glass panes with connection states, a wall torch and hanging
and standing lanterns that need support, and a directional chest.

Coordinates are relative to the house origin (its minimum corner). Blocks are
listed in placement order: supports first, attachments last, so setblock never
places a block whose support does not exist yet.
"""
from __future__ import annotations

SIZE = (5, 4, 5)

OAK_DOOR = 'minecraft:oak_door[facing=north,hinge=left,open=false,powered=false,half={half}]'
PANE_NS = 'minecraft:glass_pane[north=true,south=true,east=false,west=false,waterlogged=false]'


def _blocks() -> list[tuple[int, int, int, str]]:
    blocks: list[tuple[int, int, int, str]] = []
    # y0 floor: planks with one double slab.
    for x in range(5):
        for z in range(5):
            block = 'minecraft:oak_slab[type=double,waterlogged=false]' if (x, z) == (1, 1) else 'minecraft:oak_planks'
            blocks.append((x, 0, z, block))
    # y1/y2 walls: vertical log corners, stone bricks elsewhere, door opening on z=0, panes on x=0/4 at y2.
    for y in (1, 2):
        for x in range(5):
            for z in range(5):
                if x not in (0, 4) and z not in (0, 4):
                    continue
                if x in (0, 4) and z in (0, 4):
                    blocks.append((x, y, z, 'minecraft:oak_log[axis=y]'))
                elif (x, z) == (2, 0):
                    continue  # door, placed later
                elif y == 2 and z == 2:
                    continue  # pane, placed later
                else:
                    blocks.append((x, y, z, 'minecraft:stone_bricks'))
    # y3 roof: bottom stairs along z=0/z=4, bottom slabs on z=1/z=3, top stairs + planks + an x-axis log on z=2.
    for x in range(5):
        blocks.append((x, 3, 0, 'minecraft:oak_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]'))
        blocks.append((x, 3, 4, 'minecraft:oak_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]'))
        blocks.append((x, 3, 1, 'minecraft:oak_slab[type=bottom,waterlogged=false]'))
        blocks.append((x, 3, 3, 'minecraft:oak_slab[type=bottom,waterlogged=false]'))
    blocks.append((0, 3, 2, 'minecraft:oak_stairs[facing=east,half=top,shape=straight,waterlogged=false]'))
    blocks.append((4, 3, 2, 'minecraft:oak_stairs[facing=west,half=top,shape=straight,waterlogged=false]'))
    blocks.append((1, 3, 2, 'minecraft:oak_planks'))
    blocks.append((3, 3, 2, 'minecraft:oak_planks'))
    blocks.append((2, 3, 2, 'minecraft:oak_log[axis=x]'))
    # Attachments.
    blocks.append((2, 1, 0, OAK_DOOR.format(half='lower')))
    blocks.append((2, 2, 0, OAK_DOOR.format(half='upper')))
    blocks.append((0, 2, 2, PANE_NS))
    blocks.append((4, 2, 2, PANE_NS))
    blocks.append((1, 2, 1, 'minecraft:wall_torch[facing=east]'))
    blocks.append((2, 1, 2, 'minecraft:lantern[hanging=false,waterlogged=false]'))
    blocks.append((2, 2, 2, 'minecraft:lantern[hanging=true,waterlogged=false]'))
    blocks.append((3, 1, 3, 'minecraft:chest[facing=west,type=single,waterlogged=false]'))
    return blocks


BLOCKS = _blocks()

# Survival materials a Silk Touch break returns: the door's upper half drops
# nothing, a double slab drops two slabs, the wall torch drops a torch.
BOM = {
    'minecraft:oak_planks': 26,
    'minecraft:oak_slab': 12,
    'minecraft:stone_bricks': 20,
    'minecraft:oak_log': 9,
    'minecraft:oak_stairs': 12,
    'minecraft:oak_door': 1,
    'minecraft:glass_pane': 2,
    'minecraft:chest': 1,
    'minecraft:torch': 1,
    'minecraft:lantern': 2,
}

# Spot checks after a clockwise 90 degree Blueprint/Build with Pos1 (the origin)
# as pivot: (dx, dz) -> (-dz, dx) and every facing turns clockwise.
ROT90_EXPECT = [
    ((0, 1, 2), 'minecraft:oak_door[facing=east,half=lower]'),
    ((0, 2, 2), 'minecraft:oak_door[facing=east,half=upper]'),
    ((0, 3, 0), 'minecraft:oak_stairs[facing=west,half=bottom]'),
    ((-4, 3, 0), 'minecraft:oak_stairs[facing=east,half=bottom]'),
    ((-2, 3, 0), 'minecraft:oak_stairs[facing=south,half=top]'),
    ((-2, 3, 2), 'minecraft:oak_log[axis=z]'),
    ((-1, 2, 1), 'minecraft:wall_torch[facing=south]'),
    ((-3, 1, 3), 'minecraft:chest[facing=north]'),
    ((-2, 2, 0), 'minecraft:glass_pane[east=true,west=true,north=false,south=false]'),
    ((-1, 0, 1), 'minecraft:oak_slab[type=double]'),
    ((-2, 2, 2), 'minecraft:lantern[hanging=true]'),
]


def _check_bom() -> None:
    from collections import Counter
    counts: Counter[str] = Counter()
    for _, _, _, block in BLOCKS:
        bid = block.split('[', 1)[0]
        if bid == 'minecraft:oak_door' and 'half=upper' in block:
            continue
        if bid == 'minecraft:oak_slab' and 'type=double' in block:
            counts[bid] += 2
            continue
        counts['minecraft:torch' if bid == 'minecraft:wall_torch' else bid] += 1
    assert dict(counts) == BOM, (dict(counts), BOM)
    cells = {(x, y, z) for x, y, z, _ in BLOCKS}
    assert len(cells) == len(BLOCKS), 'duplicate house cell'
    assert all(0 <= x < SIZE[0] and 0 <= y < SIZE[1] and 0 <= z < SIZE[2] for x, y, z in cells)


_check_bom()


def place_commands(ox: int, oy: int, oz: int, dim: str | None = None) -> list[str]:
    """Commands that clear the house volume and build the house at an origin."""
    prefix = f'execute in minecraft:{dim} run ' if dim else ''
    sx, sy, sz = SIZE
    out = [f'{prefix}fill {ox} {oy} {oz} {ox+sx-1} {oy+sy-1} {oz+sz-1} air']
    out += [f'{prefix}setblock {ox+x} {oy+y} {oz+z} {block}' for x, y, z, block in BLOCKS]
    return out


def max_corner(ox: int, oy: int, oz: int) -> tuple[int, int, int]:
    return ox + SIZE[0] - 1, oy + SIZE[1] - 1, oz + SIZE[2] - 1


def stock_items(slot0: int = 0) -> list[str]:
    """SNBT item entries holding exactly the house BOM (one stack per id, <=64)."""
    items = []
    for i, (item, count) in enumerate(BOM.items()):
        assert count <= 64
        items.append(f'{{Slot:{slot0+i}b,id:"{item}",count:{count}}}')
    return items
