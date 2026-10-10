"""Short innotest shard: real bot /trigger pick in Nether, real Overworld Warehouse stock."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from innotest_harness import Suite

s = Suite("wpk", "WPK", {"a": "penguin0531"}, "Warehouse cross-dimension Pick live regression")
s.default_delay = 4
A = s.sel("a")
OUT = ROOT / "dist/warehouse-pick-nether-live-test"
X, Y, Z = -464, 240, 176
TX = X + 3
N = "in minecraft:the_nether"
ITEM = "minecraft:cobblestone"

s.step(
    "scoreboard players set #got htest 0",
    "scoreboard players set #restored htest 0",
    "scoreboard players set #forced htest 0",
    f"execute {N} store success score #forced htest run forceload query {X} {Z}",
    f"execute if score #forced htest matches 0 {N} run forceload add {X} {Z}",
    delay=40,
    realtime=True,
)
s.check("Nether fixture is empty", f"{N} if block {X} {Y-1} {Z} minecraft:air",
        f"{N} if block {TX} {Y} {Z} minecraft:air")
s.step(
    f"execute {N} if block {X} {Y-1} {Z} minecraft:air run setblock {X} {Y-1} {Z} minecraft:stone",
    f"execute {N} if block {TX} {Y} {Z} minecraft:air run setblock {TX} {Y} {Z} {ITEM}",
    f'function warehouse:api/count_item {{item_id:"{ITEM}"}}',
    "execute store result score #before htest run data get storage warehouse:api result.available",
    'execute store result score #inv0 htest run clear ' + A + f' {ITEM} 0',
)
s.check("Shared Warehouse source is complete", "data storage warehouse:api result{ok:1b,complete:1b}")
s.check("Shared Warehouse contains cobblestone", "score #before htest matches 1..")
s.tp("a", X + 0.5, Y, Z + 0.5, -90, 20.5, "the_nether")
s.check("Test bot is in Nether", f"as {A} at @s if dimension minecraft:the_nether")
s.bot("a", "cmd", "trigger", "pick", label="Nether player triggers Pick")
s.step(
    f'function warehouse:api/count_item {{item_id:"{ITEM}"}}',
    "execute store result score #after htest run data get storage warehouse:api result.available",
    f"execute store result score #inv1 htest run clear {A} {ITEM} 0",
    "scoreboard players operation #got htest = #inv1 htest",
    "scoreboard players operation #got htest -= #inv0 htest",
    "scoreboard players operation #taken htest = #before htest",
    "scoreboard players operation #taken htest -= #after htest",
    "scoreboard players set #want htest 64",
    "execute if score #before htest matches ..63 run scoreboard players operation #want htest = #before htest",
    delay=10,
)
s.check("Nether Pick gives expected stack", "score #got htest = #want htest")
s.check("Overworld warehouse loses exact amount", "score #taken htest = #got htest")
s.check("Nether target block is unchanged", f"{N} if block {TX} {Y} {Z} {ITEM}")
s.step("function wpk:restore", delay=30)
s.step(
    f'function warehouse:api/count_item {{item_id:"{ITEM}"}}',
    "execute store result score #returned htest run data get storage warehouse:api result.available",
)
s.check("All withdrawn items returned", "score #returned htest = #before htest")
s.check("No pending refund for test", "score #restored htest matches 1")

s.cleanup("function wpk:restore", 
          f"execute {N} if block {TX} {Y} {Z} {ITEM} run setblock {TX} {Y} {Z} minecraft:air",
          f"execute {N} if block {X} {Y-1} {Z} minecraft:stone run setblock {X} {Y-1} {Z} minecraft:air",
          f"execute if score #forced htest matches 0 {N} run forceload remove {X} {Z}")
s.write(OUT)
s.extra_function(OUT, "restore", [
    "execute if score #restored htest matches 1 run return 1",
    "scoreboard players set #restored htest 1",
    "scoreboard players set #removed htest 0",
    "execute if score #got htest matches 1.. run function wpk:remove_pick with storage wpk:arg",
    f"execute in minecraft:overworld run tp {A} -400.5 280 160.5",
    "return 1",
])
s.extra_function(OUT, "remove_pick", [
    "$execute store result score #removed htest run clear " + A + f" {ITEM} $(count)",
    "execute if score #removed htest matches 1.. store result storage wpk:arg count int 1 run scoreboard players get #removed htest",
    "execute if score #removed htest matches 1.. run function wpk:refund with storage wpk:arg",
])
s.extra_function(OUT, "refund", [
    f'$function warehouse:api/refund_item {{item_id:"{ITEM}",count:$(count)}}'
])
# Save a nonzero max count only after the successful withdrawal.
# The restore function uses this value to remove and refund exactly what the bot received.
p = OUT / "data/wpk/function/restore.mcfunction"
t = p.read_text(encoding="utf-8")
t = t.replace("execute if score #got htest matches 1.. run function wpk:remove_pick with storage wpk:arg", 
              "execute if score #got htest matches 1.. store result storage wpk:arg count int 1 run scoreboard players get #got htest\nexecute if score #got htest matches 1.. run function wpk:remove_pick with storage wpk:arg")
p.write_text(t, encoding="utf-8")
print("Built Nether Pick live shard with", len(s.steps), "steps")
