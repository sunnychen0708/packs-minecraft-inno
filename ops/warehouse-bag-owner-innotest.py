#!/usr/bin/env python3
"""Fast, real-client-packet Warehouse bag registration regression. innotest ONLY."""
from __future__ import annotations
import json,os,subprocess,sys,time,zipfile,io,tempfile,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from exaroton_innotest import APIClient, pack_zip, level_name, Error
from innotest_harness import Suite

c=APIClient(os.environ["EXAROTON_API_TOKEN"])
shard_parser=argparse.ArgumentParser()
shard_parser.add_argument("--shard",choices=("01","05"),required=True)
shard=shard_parser.parse_args().shard
owners={"01":"SunnyChen","05":"SunnyChen"}
who=owners[shard]
other=["penguin0531","geena0701","Felicitypeng"]
names=[who]+other
aid=2*int(shard)-1
bid=aid+1
X,Y,Z=-31296,301,48768
tag="bagownerqa_return_"+shard
prefix="BUIOWNER_"+shard+"_"+str(int(time.time()))
bots=None
bf=None
original=None
world=""
wpath=""
testpath=""
deployed=False
testdeployed=False
setup=False
backup=False
begin=time.monotonic()
def out(s):print(s,flush=True)
def cmd(s):c.command(s)
def waittoken(tok,timeout=90):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  text=c.log()
  if tok in text:return text
  time.sleep(1)
 raise Error("Missing "+tok+" last-log="+repr(c.log().splitlines()[-12:]))
def online():
 return set((c.target().get("players") or {}).get("list") or [])
def wait_bots_absent(timeout=30):
 # After the Mineflayer process terminates, exaroton's online-player
 # snapshot may remain stale for several seconds. Never kick real players.
 deadline=time.monotonic()+timeout
 while time.monotonic()<deadline:
  seen=online().intersection(names)
  if not seen:return True
  time.sleep(1)
 return False
def build():
 s=Suite("bagownerqa",prefix,{"a":who,"b":other[0]},"Warehouse single chest actual click / trigger / UI packet")
 s.default_delay=4
 s.trigger("a","wh_bag_reg",aid)
 s.wait("A_armed",[f"entity @a[name={who},tag=wh_bag_reg_pending]"],tries=50)
 s.tp("a",X+0.5,Y,Z+2.5,yaw=180,pitch=25)
 s.bot("a","use",X,Y,Z,tries=80,label="right click 02-A chest")
 s.bot("a","close",tries=60)
 s.check("A_registered",f'data storage warehouse:bags slots.p{shard}.a{{registered:1b,dimension:"minecraft:overworld",x:{X},y:{Y},z:{Z}}}')
 s.check("pending_cleared",f'entity @a[name={who},tag=!wh_bag_reg_pending]')
 s.check("item_untouched",f'in minecraft:overworld if items block {X} {Y} {Z} container.0 minecraft:diamond')
 # B must be an empty small chest and must not overwrite existing stacks.
 s.step(f"execute in minecraft:overworld run item replace block {X+3} {Y} {Z} container.3 with minecraft:stone 8")
 s.trigger("a","wh_bag_reg",bid)
 s.wait("B_armed",[f"entity @a[name={who},tag=wh_bag_reg_pending]"],tries=50)
 s.tp("a",X+3.5,Y,Z+2.5,yaw=180,pitch=25)
 s.bot("a","use",X+3,Y,Z,tries=80,label="right click nonempty B")
 s.bot("a","close",tries=60)
 s.check("B_nonempty_rejected",f'in minecraft:overworld unless data storage warehouse:bags slots.p{shard}.b{{registered:1b,x:{X+3},y:{Y},z:{Z}}}')
 s.check("B_stack_untouched",f'in minecraft:overworld if items block {X+3} {Y} {Z} container.3 minecraft:stone')
 s.step(f"execute in minecraft:overworld run data modify block {X+3} {Y} {Z} Items set value []")
 s.trigger("a","wh_bag_reg",bid)
 s.wait("B_rearmed",[f"entity @a[name={who},tag=wh_bag_reg_pending]"],tries=50)
 s.bot("a","use",X+3,Y,Z,tries=80,label="right click empty B")
 s.bot("a","close",tries=60)
 s.check("B_registered",f'data storage warehouse:bags slots.p{shard}.b{{registered:1b,x:{X+3},y:{Y},z:{Z}}}')
 if shard=="05":
  # While 05 is borrowed, even SunnyChen is denied registration or unregistration.
  # This only modifies the isolated innotest Warehouse storage, restored in finally.
  s.step('data modify storage warehouse:bags shared set value {active:1b,owner:2}')
  s.trigger("a","wh_bag_reg",aid)
  s.check("05_active_rebind_denied",f'entity @a[name={who},tag=!wh_bag_reg_pending]')
  s.check("05_active_A_retained",f'data storage warehouse:bags slots.p05.a{{registered:1b,x:{X},y:{Y},z:{Z}}}')
  s.trigger("a","wh_bag_unreg",bid)
  s.check("05_active_unregister_denied",f'data storage warehouse:bags slots.p05.b{{registered:1b,x:{X+3},y:{Y},z:{Z}}}')
  s.step('data remove storage warehouse:bags shared')
 # Rebind A without moving the old or new chest inventory.
 s.trigger("a","wh_bag_reg",aid)
 s.wait("A_rearmed",[f"entity @a[name={who},tag=wh_bag_reg_pending]"],tries=50)
 s.tp("a",X+6.5,Y,Z+2.5,yaw=180,pitch=25)
 s.bot("a","use",X+6,Y,Z,tries=80,label="rebind 02-A")
 s.bot("a","close",tries=60)
 s.check("A_rebound",f'data storage warehouse:bags slots.p{shard}.a{{registered:1b,x:{X+6},y:{Y},z:{Z}}}')
 s.check("old_A_unchanged",f'in minecraft:overworld if items block {X} {Y} {Z} container.0 minecraft:diamond')
 s.check("new_A_unchanged",f'in minecraft:overworld if items block {X+6} {Y} {Z} container.0 minecraft:emerald')
 # Other bot must be denied access.
 s.trigger("b","wh_bag_reg",aid)
 s.check("other_denied",f'entity @a[name={other[0]},tag=!wh_bag_reg_pending]')
 s.check("owner_binding_unchanged",f'data storage warehouse:bags slots.p{shard}.a{{registered:1b,x:{X+6},y:{Y},z:{Z}}}')
 # Remove A and B using owner-triggered commands.
 s.trigger("a","wh_bag_unreg",aid)
 s.check("A_unregistered",f'in minecraft:overworld unless data storage warehouse:bags slots.p{shard}.a{{registered:1b}}')
 s.trigger("a","wh_bag_unreg",bid)
 s.check("B_unregistered",f'in minecraft:overworld unless data storage warehouse:bags slots.p{shard}.b{{registered:1b}}')
 s.check("unregister_preserves_Q",f'in minecraft:overworld if items block {X+6} {Y} {Z} container.0 minecraft:emerald')
 # Test server G navigation -> actual show_dialog packet only; Mineflayer cannot press physical G key.
 s.dialog("a","trigger wh_nav set 2")
 p=Path(tempfile.mkdtemp(prefix="bagownerqa_"))
 s.write(p)
 fs=p/"data/bagownerqa/function"
 (fs/"ping.mcfunction").write_text(f"say {prefix}_PACK_READY\n",encoding="utf-8")
 (fs/"prepare.mcfunction").write_text("\n".join([
 *[f"execute unless block {X+dx} {Y+dy} {Z+dz} minecraft:air run say {prefix}_BLOCKED" for dx in (0,3,6) for dy,dz in ((0,0),(-1,0),(-1,2))],
 f"execute in minecraft:overworld run forceload add {X} {Z}",
 *[f"execute in minecraft:overworld run setblock {X+dx} {Y-1} {Z+dz} minecraft:barrier" for dx in (0,3,6) for dz in (0,2)],
 *[f"execute in minecraft:overworld run setblock {X+dx} {Y} {Z} minecraft:chest" for dx in (0,3,6)],
 f"execute in minecraft:overworld run item replace block {X} {Y} {Z} container.0 with minecraft:diamond 4",
 f"execute in minecraft:overworld run item replace block {X+6} {Y} {Z} container.0 with minecraft:emerald 7",
 "data modify storage bagownerqa:backup slots set from storage warehouse:bags slots",
 "data modify storage bagownerqa:backup shared set from storage warehouse:bags shared",
 "data modify storage bagownerqa:backup work set from storage warehouse:bags work",
 f'execute as {who} at @s run summon minecraft:marker ~ ~ ~ {{Tags:["{tag}"]}}',
 "scoreboard objectives add bagownerqa dummy",
 f"execute store result score #reg bagownerqa run scoreboard players get {who} wh_bag_reg",
 f"execute store result score #target bagownerqa run scoreboard players get {who} wh_bag_target",
 f"execute store result score #unreg bagownerqa run scoreboard players get {who} wh_bag_unreg",
 f"scoreboard players set #pending bagownerqa 0",
 f"execute if entity @a[name={who},tag=wh_bag_reg_pending] run scoreboard players set #pending bagownerqa 1",
 f"advancement revoke {who} only warehouse:register_chest",
 f"say {prefix}_PREPARED",
 ])+"\n",encoding="utf-8")
 (fs/"restore.mcfunction").write_text("\n".join([
 f"execute as {who} at @e[tag={tag},limit=1] run tp @s ~ ~ ~",
 f"execute in minecraft:overworld run kill @e[type=minecraft:marker,tag={tag}]",
 "data modify storage warehouse:bags slots set from storage bagownerqa:backup slots",
 "data remove storage warehouse:bags shared",
 "data modify storage warehouse:bags shared set from storage bagownerqa:backup shared",
 "data remove storage warehouse:bags work",
 "data modify storage warehouse:bags work set from storage bagownerqa:backup work",
 f"tag {who} remove wh_bag_reg_pending",
 f"scoreboard players set {who} wh_bag_reg 0",
 f"scoreboard players operation {who} wh_bag_target = #target bagownerqa",
 f"scoreboard players operation {who} wh_bag_reg = #reg bagownerqa",
 f"scoreboard players operation {who} wh_bag_unreg = #unreg bagownerqa",
 f"execute if score #pending bagownerqa matches 1 run tag {who} add wh_bag_reg_pending",
 "scoreboard objectives remove bagownerqa",
 "function warehouse:chunks/refresh",
 *[f"execute in minecraft:overworld run setblock {X+dx} {Y+dy} {Z+dz} minecraft:air" for dx in (0,3,6) for dy,dz in ((0,0),(-1,0),(-1,2))],
 f"execute in minecraft:overworld run forceload remove {X} {Z}",
 f"say {prefix}_RESTORED",
 ])+"\n",encoding="utf-8")
 z=io.BytesIO()
 with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as arc:
  for f in p.rglob("*"):
   if f.is_file():arc.write(f,f.relative_to(p).as_posix())
 return z.getvalue()

try:
 srv=c.target()
 if int(srv.get("status",-1))!=1:
  if int(srv.get("status",-1))==0:c.action("start")
  lim=time.monotonic()+100
  while time.monotonic()<lim:
   if int(c.target().get("status",-1))==1:break
   time.sleep(3)
  else:raise Error("innotest not ready")
 if online().intersection(names):
  # Prior shard bots can linger briefly in the player list after their
  # runner exits. Give disconnect propagation time, but never take over.
  out("BUI_PREFLIGHT waiting for prior bot disconnection")
  if not wait_bots_absent(30):
   raise Error("Refusing to take over online player(s): "+str(sorted(online().intersection(names))))
 world=level_name(c.read_file("server.properties"))
 wpath=f"{world}/datapacks/warehouse-v4.7.zip"
 testpath=f"{world}/datapacks/bagownerqa-test.zip"
 original=c.read_binary_file_optional(wpath)
 if original is None:raise Error("Warehouse file absent")
 if c.read_binary_file_optional(testpath) is not None:
  raise Error("Prior test harness remains; refusing to overwrite")
 # Check air before any modifications.
 cmd(f"execute in minecraft:overworld run forceload add {X} {Z}")
 for dx in (0,3,6):
  for dy,dz in ((0,0),(-1,0),(-1,2)):
   cmd(f"execute in minecraft:overworld unless block {X+dx} {Y+dy} {Z+dz} minecraft:air run say {prefix}_BLOCKED")
 cmd(f"say {prefix}_SITE_CHECKED")
 log=waittoken(prefix+"_SITE_CHECKED",55)
 if prefix+"_BLOCKED" in log:raise Error("Test fixture site contains blocks")
 c.write_file(wpath,pack_zip("warehouse"));deployed=True
 pack_bytes=build()
 with zipfile.ZipFile(io.BytesIO(pack_bytes)) as testzip:
  filenames=testzip.namelist()
  assert "data/bagownerqa/function/prepare.mcfunction" in filenames, "Missing prepare function in generated ZIP"
  assert "data/bagownerqa/function/ping.mcfunction" in filenames, "Missing ping function in generated ZIP"
  out("BUI_PACK_MANIFEST="+str(len(filenames))+" files; prepare and ping present")
 c.write_file(testpath,pack_bytes);testdeployed=True
 cmd("reload");cmd(f"say {prefix}_RELOAD")
 waittoken(prefix+"_RELOAD",65)
 time.sleep(6)
 cmd("datapack list enabled")
 cmd("function bagownerqa:ping")
 try:
  waittoken(prefix+"_PACK_READY",25)
 except Error:
  log=c.log()
  out("BUI_DATAPACK_DIAGNOSTICS="+repr(log.splitlines()[-75:]))
  raise
 env=dict(os.environ,MF26_HOST="innotest.exaroton.me",MF26_BOTS=",".join(names),MF26_DURATION_MS="0")
 bf=open("/tmp/bagownerqa-bots.log","w")
 bots=subprocess.Popen(["node","scripts/mineflayer26/keepalive.js"],env=env,stdout=bf,stderr=subprocess.STDOUT)
 limit=time.monotonic()+65
 while time.monotonic()<limit:
  if set(names).issubset(online()):break
  time.sleep(2)
 else:raise Error("3 bot players did not connect")
 cmd(f"execute if data storage warehouse:bags shared{{active:1b}} run say {prefix}_SHARED_ALREADY_ACTIVE")
 cmd(f"say {prefix}_SHARED_GUARD")
 guardlog=waittoken(prefix+"_SHARED_GUARD",40)
 if prefix+"_SHARED_ALREADY_ACTIVE" in guardlog:
  raise Error("existing shared checkout; refusing to test while bag 05 is borrowed")
 cmd("function bagownerqa:prepare");setup=True
 waittoken(prefix+"_PREPARED",65);backup=True
 run_start=time.monotonic()
 cmd("function bagownerqa:start")
 log=waittoken(prefix+"_RESULT ",145)
 tests=[line for line in log.splitlines() if prefix+"_CHECK " in line]
 for line in tests:out("BUI_ASSERT "+line[-210:])
 outcome="PASS" if prefix+"_RESULT PASS" in log else "FAIL"
 elapsed=time.monotonic()-run_start
 out(f"BUI_FAST_RESULT={outcome} elapsed={elapsed:.1f} shard={shard}")
 if elapsed>240:raise Error("shard >240 seconds")
 if outcome!="PASS":raise Error("innotest bag click or dialog test failed")
finally:
 out("BUI_FAST_CLEANUP=START")
 try:
  if testdeployed:
   cmd("function bagownerqa:cleanup")
  if backup:
   cmd("function bagownerqa:restore")
   waittoken(prefix+"_RESTORED",55)
  if testdeployed:
   c.delete_file(testpath)
  if deployed and original is not None:
   c.write_file(wpath,original)
   cmd("reload")
   cmd(f"say {prefix}_BACK_TO_PREVIOUS_PACK")
   waittoken(prefix+"_BACK_TO_PREVIOUS_PACK",55)
  out("BUI_FAST_CLEANUP=PASS; innotest left ONLINE")
 finally:
  if bots is not None and bots.poll() is None:
   bots.terminate()
   try:bots.wait(timeout=5)
   except subprocess.TimeoutExpired:bots.kill()
  if bots is not None:
   if not wait_bots_absent(30):
    raise Error("Bot processes exited but players still ONLINE: "+str(sorted(online().intersection(names))))
   out("BUI_FAST_BOTS_DISCONNECTED=PASS")
  if bf is not None:bf.close()
  try:out("BUI_FAST_BOT_TAIL="+repr(Path("/tmp/bagownerqa-bots.log").read_text().splitlines()[-50:]))
  except Exception:pass
