#!/usr/bin/env python3
"""Three independent <=240-second innotest-only live shards for Warehouse Issue #72."""
from __future__ import annotations
import io, json, os, subprocess, sys, time, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from exaroton_innotest import APIClient, pack_zip, level_name, Error

c=APIClient(os.environ["EXAROTON_API_TOKEN"])
P="penguin0531"; Q="geena0701"
stamp="BQA_"+str(int(time.time()))
site={
 "J":("minecraft:overworld",-31520,300,48640),
 "B":("minecraft:overworld",-31518,300,48640),
 "seedP":("minecraft:overworld",-31516,300,48640),
 "seedA":("minecraft:overworld",-31514,300,48640),
 "saveP":("minecraft:overworld",-31512,300,48640),
 "hotP":("minecraft:overworld",-31510,300,48640),
 "saveQ":("minecraft:overworld",-31508,300,48640),
 "hotQ":("minecraft:overworld",-31506,300,48640),
 "shared":("minecraft:overworld",-31504,300,48640),
 "sharedB":("minecraft:overworld",-31502,300,48640),
 "netA":("minecraft:the_nether",-31520,200,48640),
 "endB":("minecraft:the_end",-31520,200,48640)
}
def abc(name):
 d,x,y,z=site[name]
 return d,f"{x} {y} {z}"
def loc(name):
 return site[name][0]
def pp(name):
 return " ".join(map(str,site[name][1:]))
def cmd(s):
 c.command(s)
def fence(label,secs=50):
 token=stamp+"_"+label
 cmd("say "+token)
 expiry=time.monotonic()+secs
 while time.monotonic()<expiry:
  if token in c.log():return
  time.sleep(1)
 raise Error("No console fence "+label+"; last="+str(c.log().splitlines()[-12:]))
def wait_players(names,present=True,timeout=60):
 until=time.monotonic()+timeout
 while time.monotonic()<until:
  srv=c.target();online=set((srv.get("players") or {}).get("list") or [])
  if all((n in online)==present for n in names):return
  time.sleep(2)
 raise Error("Player precondition failed: "+str(names)+" online="+str(online))
def start_bot(name):
 env=dict(os.environ, MF26_HOST="innotest.exaroton.me",MF26_BOTS=name,MF26_DURATION_MS="0")
 f=open("/tmp/bqa_bot_"+name+".log","w")
 return subprocess.Popen(["node","scripts/mineflayer26/keepalive.js"],env=env,stdout=f,stderr=subprocess.STDOUT),f
def killbot(pair):
 if not pair:return
 p,f=pair
 if p.poll() is None:
  p.terminate()
  try:p.wait(timeout=4)
  except subprocess.TimeoutExpired:p.kill()
 f.close()
def slot_lines(items):
 # Direct 26.3 item-stack block NBT (including nested components).
 return "["+",".join("{Slot:"+str(i)+"b,id:\""+ident+"\",count:"+str(count)+(
  ",components:"+components if components else "")+"}" for i,ident,count,components in items)+"]"
pitems=[
 (0,"minecraft:diamond_pickaxe",1,'{"minecraft:damage":37,"minecraft:enchantments":{"minecraft:efficiency":5},"minecraft:custom_name":\'{"text":"BQA PICK"}\'}'),
 (1,"minecraft:purple_shulker_box",1,'{"minecraft:container":[{slot:0,item:{id:"minecraft:diamond",count:7}},{slot:10,item:{id:"minecraft:oak_log",count:13}}]}'),
 (2,"minecraft:potion",1,'{"minecraft:potion_contents":{potion:"minecraft:long_swiftness"}}'),
 (4,"minecraft:enchanted_book",1,'{"minecraft:stored_enchantments":{"minecraft:mending":1}}'),
 (5,"minecraft:stone",64,None),(6,"minecraft:diamond",9,None),
 (8,"minecraft:birch_log",11,None),(9,"minecraft:netherite_scrap",3,None),
 (10,"minecraft:emerald",17,None),(12,"minecraft:bread",4,None),
 (13,"minecraft:amethyst_shard",26,None),(15,"minecraft:iron_ingot",64,None),
 (17,"minecraft:gold_ingot",8,None),(18,"minecraft:oak_planks",48,None),
 (20,"minecraft:redstone",32,None),(21,"minecraft:lapis_lazuli",5,None),
 (23,"minecraft:quartz",37,None),(24,"minecraft:obsidian",4,None),
 (26,"minecraft:ender_pearl",16,None)]
aitems=[
 (0,"minecraft:diamond_sword",1,'{"minecraft:damage":29,"minecraft:enchantments":{"minecraft:sharpness":4},"minecraft:custom_name":\'{"text":"BQA SWORD"}\'}'),
 (1,"minecraft:yellow_shulker_box",1,'{"minecraft:container":[{slot:3,item:{id:"minecraft:emerald",count:23}}]}'),
 (3,"minecraft:apple",31,None),(4,"minecraft:oak_log",64,None),(6,"minecraft:bone",4,None),
 (7,"minecraft:map",1,None),(10,"minecraft:blaze_rod",5,None),(11,"minecraft:diamond",1,None),
 (12,"minecraft:golden_carrot",64,None),(14,"minecraft:nether_star",1,None),
 (16,"minecraft:ender_eye",3,None),(18,"minecraft:slime_ball",17,None),
 (19,"minecraft:ancient_debris",2,None),(21,"minecraft:book",4,None),
 (22,"minecraft:stone",7,None),(23,"minecraft:glass",64,None),(25,"minecraft:coal",22,None)]
files={}
def fn(name,lines):
 files["data/bagqa/function/"+name+".mcfunction"]="\n".join(lines)+"\n"
def read_item(kind,who,idx):
 if kind=="player":return "entity "+who+" Inventory[{Slot:"+str(idx+9)+"b}]"
 d,xyz=abc(who)
 return "block "+xyz+" Items[{Slot:"+str(idx)+"b}]"
def cmd_read(dest,source):
 prefix=""
 if source.startswith("block "):
  # caller passes dimension separately
  pass
 return "data modify storage bagqa:state "+dest+" set from "+source
def capture(tag,kind,who):
 z=[]
 for i in range(27):
  key=tag+".s"+str(i)
  z.append("data modify storage bagqa:state "+key+" set value {}")
  src=read_item(kind,who,i)
  line=cmd_read(key,src)
  if kind=="box":line="execute in "+loc(who)+" run "+line
  z.append(line)
  z.append("data remove storage bagqa:state "+key+".Slot")
 return z
def compare(tag,kind,who,label):
 z=[]
 for i in range(27):
  src=read_item(kind,who,i)
  z.append("data modify storage bagqa:state actual set value {}")
  s=cmd_read("actual",src)
  if kind=="box":s="execute in "+loc(who)+" run "+s
  z.append(s)
  z.append("data remove storage bagqa:state actual.Slot")
  z.append("execute store success score #delta bqa run data modify storage bagqa:state actual set from storage bagqa:state "+tag+".s"+str(i))
  z.append("execute if score #delta bqa matches 1 run scoreboard players add #bad bqa 1")
  z.append("execute if score #delta bqa matches 1 run say "+stamp+"_DIFF_"+label+"_"+str(i))
 return z
def reg(part,name):
 d,x,y,z=site[name]
 return 'data modify storage warehouse:bags slots.p'+part+' set value {registered:1b,dimension:"'+d+'",x:'+str(x)+',y:'+str(y)+',z:'+str(z)+'}'
def stepresult(label):
 return [
 'execute if score #bad bqa matches 0 run say '+stamp+'_'+label+'_PASS',
 'execute unless score #bad bqa matches 0 run say '+stamp+'_'+label+'_FAIL'
 ]
fn("seed",[
 "data modify block "+pp("seedP")+" Items set value "+slot_lines(pitems),
 "data modify block "+pp("seedA")+" Items set value "+slot_lines(aitems),
 "data modify block "+pp("shared")+" Items set value "+slot_lines(aitems)
])
fn("s1_prepare",[
 "scoreboard players set #bad bqa 0",
 "item override entity "+P+" inventory.* from block "+pp("seedP")+" container.*",
 "item override block "+pp("J")+" container.* from block "+pp("seedA")+" container.*",
 "data modify block "+pp("B")+" Items set value []",
 reg("02.a","J"),reg("02.b","B"),
 # Seed fidelity preflight checks.
 "execute unless items entity "+P+" inventory.0 minecraft:diamond_pickaxe run scoreboard players add #bad bqa 1",
 "execute unless items entity "+P+" inventory.1 minecraft:purple_shulker_box run scoreboard players add #bad bqa 1",
 "execute unless items block "+pp("J")+" container.0 minecraft:diamond_sword run scoreboard players add #bad bqa 1",
 "execute unless data entity "+P+" Inventory[{Slot:9b}].components.\"minecraft:damage\" run scoreboard players add #bad bqa 1",
 "execute unless data entity "+P+" Inventory[{Slot:10b}].components.\"minecraft:container\" run scoreboard players add #bad bqa 1",
 "execute unless data block "+pp("J")+" Items[{Slot:0b}].components.\"minecraft:enchantments\" run scoreboard players add #bad bqa 1",
 ]+capture("p1","player",P)+capture("a1","box","J")+
 ["execute if score #bad bqa matches 0 run say "+stamp+"_S1_PREPARE_PASS",
 "execute unless score #bad bqa matches 0 run say "+stamp+"_S1_PREPARE_FAIL"])
fn("s1_swap",[
 "scoreboard players set #bad bqa 0",
 "execute as "+P+" run function warehouse:bag/dispatch"
 ]+compare("a1","player",P,"S1_PLAYER")+compare("p1","box","J","S1_CHEST")+
 ["execute if items block "+pp("B")+" container.* * run scoreboard players add #bad bqa 1"]+
 stepresult("S1_SWAP"))
fn("s1_return",[
 "scoreboard players set #bad bqa 0",
 "execute as "+P+" run function warehouse:bag/dispatch"
 ]+compare("p1","player",P,"S1_RETURN_PLAYER")+compare("a1","box","J","S1_RETURN_CHEST")+
 stepresult("S1_RETURN"))
fn("s2_prepare",[
 "scoreboard players set #bad bqa 0",
 "item override entity "+P+" inventory.* from block "+pp("seedP")+" container.*",
 "data modify storage bagqa:stage crossItems set from block "+pp("seedA")+" Items",
 "execute in minecraft:the_nether run data modify block "+pp("netA")+" Items set from storage bagqa:stage crossItems",
 "execute in minecraft:the_nether unless items block "+pp("netA")+" container.0 minecraft:diamond_sword run scoreboard players add #bad bqa 1",
 "execute in minecraft:the_end run data modify block "+pp("endB")+" Items set value []",
 reg("02.a","netA"),reg("02.b","endB")
 ]+capture("p2","player",P)+capture("a2","box","netA")+
 stepresult("S2_PREPARE"))
fn("s2_swap",["scoreboard players set #bad bqa 0","execute as "+P+" run function warehouse:bag/dispatch"]+
 compare("a2","player",P,"S2_PLAYER")+compare("p2","box","netA","S2_CHEST")+
 ["execute in minecraft:the_end if items block "+pp("endB")+" container.* * run scoreboard players add #bad bqa 1"]+stepresult("S2_SWAP"))
fn("s2_return",["scoreboard players set #bad bqa 0","execute as "+P+" run function warehouse:bag/dispatch"]+
 compare("p2","player",P,"S2_RETURN_PLAYER")+compare("a2","box","netA","S2_RETURN_CHEST")+stepresult("S2_RETURN"))
fn("s2_buffer_guard",[
 "scoreboard players set #bad bqa 0",
 "execute in minecraft:the_end run data modify block "+pp("endB")+" Items set value [{Slot:13b,id:\"minecraft:diamond\",count:3}]",
 "execute as "+P+" run function warehouse:bag/dispatch"
 ]+compare("p2","player",P,"S2_GUARD_P")+compare("a2","box","netA","S2_GUARD_A")+
 ["execute in minecraft:the_end unless items block "+pp("endB")+" container.13 minecraft:diamond run scoreboard players add #bad bqa 1"]+stepresult("S2_BUFFER_GUARD"))
fn("s2_invalid_guard",[
 "scoreboard players set #bad bqa 0",
 "execute in minecraft:the_end run data modify block "+pp("endB")+" Items set value []",
 "data modify storage warehouse:bags slots.p02.a.x set value -31400",
 "execute as "+P+" run function warehouse:bag/dispatch"
 ]+compare("p2","player",P,"S2_INVALID_P")+
 ["data modify storage warehouse:bags slots.p02.a.x set value -31520"]+stepresult("S2_INVALID_GUARD"))
fn("s3_prepare",[
 "scoreboard players set #bad bqa 0",
 "item override entity "+P+" inventory.* from block "+pp("seedP")+" container.*",
 "item override entity "+Q+" inventory.* from block "+pp("seedA")+" container.*",
 "item override block "+pp("shared")+" container.* from block "+pp("seedA")+" container.*",
 "data modify block "+pp("sharedB")+" Items set value []",
 reg("05.a","shared"),reg("05.b","sharedB"),
 "data remove storage warehouse:bags shared",
 ]+capture("p3","player",P)+capture("q3","player",Q)+capture("s3","box","shared")+
 ["say "+stamp+"_S3_PREPARE_PASS"])
fn("s3_compete",[
 "scoreboard players set #bad bqa 0",
 "scoreboard players set "+P+" sbag 1",
 "scoreboard players set "+Q+" sbag 1",
 "execute as "+P+" run function warehouse:bag/shared/dispatch",
 "execute as "+Q+" run function warehouse:bag/shared/dispatch",
 "execute unless data storage warehouse:bags shared{active:1b,owner:2} run scoreboard players add #bad bqa 1"
 ]+compare("s3","player",P,"S3_SHARED_P")+compare("p3","box","sharedB","S3_BUF")+
 compare("q3","player",Q,"S3_DENIED_Q")+
 ["execute as "+P+" run function warehouse:bag/dispatch"]+
 compare("s3","player",P,"S3_NO_PERSONAL_WHILE_SHARED")+stepresult("S3_COMPETE"))
fn("s3_while_offline",[
 "scoreboard players set #bad bqa 0",
 "execute as "+Q+" run function warehouse:bag/shared/dispatch",
 "execute unless data storage warehouse:bags shared{active:1b,owner:2} run scoreboard players add #bad bqa 1"
 ]+compare("q3","player",Q,"S3_OFFLINE_DENIED")+stepresult("S3_WHILE_OFFLINE"))
fn("s3_rejoin",[
 "scoreboard players set #bad bqa 0",
 "execute unless data storage warehouse:bags shared{active:1b,owner:2} run scoreboard players add #bad bqa 1",
 "execute as "+P+" run function warehouse:bag/shared/dispatch"
 ]+compare("p3","player",P,"S3_RESTORE_P")+compare("s3","box","shared","S3_RETURN_SHARED")+
 ["execute if data storage warehouse:bags shared{active:1b} run scoreboard players add #bad bqa 1",
 "execute as "+Q+" run function warehouse:bag/shared/dispatch",
 "execute unless data storage warehouse:bags shared{active:1b,owner:3} run scoreboard players add #bad bqa 1",
 "execute as "+Q+" run function warehouse:bag/shared/dispatch"
 ]+compare("q3","player",Q,"S3_RESTORE_Q")+compare("s3","box","shared","S3_SHARED_INTACT")+
 ["execute if data storage warehouse:bags shared{active:1b} run scoreboard players add #bad bqa 1"]+stepresult("S3_REJOIN"))
fn("s3_conflict1",[
 "scoreboard players set #bad bqa 0",
 "execute as "+P+" run function warehouse:bag/shared/dispatch",
 "execute unless data storage warehouse:bags shared{active:1b,owner:2} run scoreboard players add #bad bqa 1",
 "data modify block "+pp("shared")+" Items append value {Slot:26b,id:\"minecraft:coal\",count:9}",
 "execute as "+P+" run function warehouse:bag/shared/dispatch",
 "execute unless data storage warehouse:bags shared{active:1b,owner:2} run scoreboard players add #bad bqa 1",
 "execute unless items block "+pp("shared")+" container.26 minecraft:coal run scoreboard players add #bad bqa 1",
 "data modify block "+pp("shared")+" Items set value []",
 ]+compare("s3","player",P,"S3_CONFLICT_PLAYER")+stepresult("S3_CONFLICT1"))
fn("s3_conflict2",[
 "scoreboard players set #bad bqa 0",
 "execute as "+P+" run function warehouse:bag/shared/dispatch"
 ]+compare("p3","player",P,"S3_FINAL_P")+compare("s3","box","shared","S3_FINAL_S")+
 ["execute if data storage warehouse:bags shared{active:1b} run scoreboard players add #bad bqa 1"]+stepresult("S3_CONFLICT2"))
def make_pack():
 b=io.BytesIO()
 with zipfile.ZipFile(b,"w",zipfile.ZIP_DEFLATED) as z:
  z.writestr("pack.mcmeta",json.dumps({"pack":{"description":"Temporary innotest Warehouse QA","min_format":[121,0],"max_format":[121,0]}}))
  for p,txt in files.items():z.writestr(p,txt)
 return b.getvalue()
def stage(label):
 # Run an already loaded test function then wait for its reported result.
 t=time.monotonic()
 cmd("function bagqa:"+label)
 token=stamp+"_"+label.upper()
 deadline=time.monotonic()+135
 while time.monotonic()<deadline:
  log=c.log()
  if token+"_PASS" in log or token+"_FAIL" in log:
   actual="PASS" if token+"_PASS" in log else "FAIL"
   elapsed=time.monotonic()-t
   print("BQA_RESULT "+label+" "+actual+" "+str(round(elapsed,1)),flush=True)
   if actual=="FAIL":
    bits=[a for a in log.splitlines() if stamp+"_DIFF_" in a]
    print("BQA_DIFFS "+repr(bits[-20:]))
    raise Error(label+" failed")
   return
  time.sleep(.9)
 print("BQA_TIMEOUT_LOG "+repr(c.log().splitlines()[-80:]),flush=True)
 raise Error("Timeout waiting "+label)
def save_name(name):
 cmd("item override block "+pp("save"+name)+" container.* from entity "+(P if name=="P" else Q)+" inventory.*")
 cmd("item override block "+pp("hot"+name)+" container.* from entity "+(P if name=="P" else Q)+" hotbar.*")
def restore_name(name):
 player=P if name=="P" else Q
 cmd("item override entity "+player+" inventory.* from block "+pp("save"+name)+" container.*")
 cmd("item override entity "+player+" hotbar.* from block "+pp("hot"+name)+" container.*")

origpack=None
world=""
testpack=""
backup={}
bots={}
placed=[]
loaded=[]
saved=[]
deployed=False
harness=False
try:
 server=c.target()
 if int(server.get("status",-1))!=1:
  if int(server.get("status",-1))==0:c.action("start")
  until=time.monotonic()+110
  while time.monotonic()<until:
   if int(c.target().get("status",-1))==1:break
   time.sleep(3)
  else:raise Error("innotest failed to reach ONLINE")
 # Preserve any current players; do not impersonate or kick a user already online.
 online=(c.target().get("players") or {}).get("list") or []
 if any(x in online for x in [P,Q]):raise Error("Refusing to take over already-online player(s): "+str(online))
 world=level_name(c.read_file("server.properties"))
 testpack=world+"/datapacks/warehouse-v4.7.zip"
 origpack=c.read_binary_file_optional(testpack)
 if origpack is None:raise Error("Expected warehouse-v4.7.zip before test; refusing version overwrite")
 cmd("say "+stamp+"_START");fence("START_ACK")
 # Force-load isolated test site chunks before inspecting them.
 for d,x,y,z in sorted({(v[0],v[1],v[2],v[3]) for v in site.values()}):
  chunk=(d,x//16,z//16)
  if chunk in loaded:continue
  cmd("execute in "+d+" run forceload add "+str(x)+" "+str(z))
  loaded.append(chunk)
 fence("CHUNKS_READY")
 for name in site:
  d,xyz=abc(name)
  cmd("execute in "+d+" unless block "+xyz+" minecraft:air run say "+stamp+"_NOT_AIR_"+name)
 fence("SITE_CHECKED")
 if stamp+"_NOT_AIR_" in c.log().split(stamp+"_START")[-1]:raise Error("Test site not empty; stopped before overwriting")
 for name in site:
  d,xyz=abc(name)
  cmd("execute in "+d+" run setblock "+xyz+" minecraft:chest")
  placed.append(name)
 fence("SITE_CREATED")
 # Upgrade only innotest to exact draft code, and add isolated temporary assertion pack.
 c.write_file(testpack,pack_zip("warehouse"));deployed=True
 c.write_file(world+"/datapacks/bagqa-temp.zip",make_pack());harness=True
 cmd("reload")
 fence("RELOAD_ISSUED")
 time.sleep(6)
 # Fail if parser errors occurred during this reload.
 seg=c.log().split(stamp+"_START")[-1]
 bad=[line for line in seg.splitlines() if ("/ERROR]:" in line or "Failed to load function bagqa" in line)]
 if bad:raise Error("Pack parser errors: "+" || ".join(bad[:8]))
 cmd("scoreboard objectives add bqa dummy")
 cmd("function bagqa:seed")
 fence("SEEDS_READY")
 # Snapshot preexisting Warehouse bag metadata for safe restoration.
 for path in ["slots.p02","slots.p03","slots.p05","shared","work"]:
  key=path.replace(".","_")
  cmd("data modify storage bagqa:backup "+key+" set from storage warehouse:bags "+path)
  backup[path]=key
 fence("STORAGE_BACKUP")
 # Spawn two isolated controlled bot processes (SunnyChen never used).
 for user in (P,Q):
  bots[user]=start_bot(user)
 wait_players([P,Q],True,70)
 for name in ["P","Q"]:
  save_name(name);saved.append(name)
 fence("INVENTORY_BACKUP")
 # Three distinct shards. Each START -> DONE measured separately, <= 240 seconds.
 for shard,tests in [(1,["s1_prepare","s1_swap","s1_return"]),
                     (2,["s2_prepare","s2_swap","s2_return","s2_buffer_guard","s2_invalid_guard"])]:
  begin=time.monotonic();print("BQA_SHARD_"+str(shard)+"_START",flush=True)
  for test in tests:stage(test)
  secs=time.monotonic()-begin
  if secs>240:raise Error("Shard "+str(shard)+" >240 seconds")
  print("BQA_SHARD_"+str(shard)+"_PASS seconds="+str(round(secs,2)),flush=True)
 # Shared competition + true disconnection / reconnection.
 begin=time.monotonic();print("BQA_SHARD_3_START",flush=True)
 for test in ["s3_prepare","s3_compete"]:stage(test)
 cmd("kick "+P+" BQA disconnect test")
 wait_players([P],False,25)
 stage("s3_while_offline")
 killbot(bots.pop(P,None))
 bots[P]=start_bot(P)
 wait_players([P],True,60)
 for test in ["s3_rejoin","s3_conflict1","s3_conflict2"]:stage(test)
 secs=time.monotonic()-begin
 if secs>240:raise Error("Shard 3 >240 seconds")
 print("BQA_SHARD_3_PASS seconds="+str(round(secs,2)),flush=True)
 print("BQA_OVERALL=PASS",flush=True)
finally:
 print("BQA_CLEANUP_START",flush=True)
 try:
  # Any p still offline after a failed reconnect is recovered via a fresh test bot.
  for user in (P,Q):
   if user not in [P if n=="P" else Q for n in saved]:continue
   current=(c.target().get("players") or {}).get("list") or []
   if user not in current:
    killbot(bots.pop(user,None));bots[user]=start_bot(user)
    try:wait_players([user],True,55)
    except Exception as exc:print("BQA_CLEANUP_RECONNECT_ERROR "+str(exc),flush=True)
  for n in saved:restore_name(n)
  # Persist backup of Warehouse storage registrations and shared owner.
  for path,key in backup.items():
   cmd("data remove storage warehouse:bags "+path)
   cmd("data modify storage warehouse:bags "+path+" set from storage bagqa:backup "+key)
  fence("RESTORE_COMMANDS",60)
  # Only delete the isolated test sites after restoration commands completed.
  for name in placed:
   d,xyz=abc(name)
   cmd("execute in "+d+" run setblock "+xyz+" minecraft:air")
  fence("BLOCKS_REMOVED",50)
  cmd("data remove storage bagqa:state p1") if False else None
  for d,cx,cz in loaded:
   cmd("execute in "+d+" run forceload remove "+str(cx*16)+" "+str(cz*16))
  fence("CHUNKS_RELEASED",40)
  if deployed:c.write_file(testpack,origpack)
  if harness:c.delete_file(world+"/datapacks/bagqa-temp.zip")
  if deployed or harness:
   cmd("reload")
   fence("RESTORE_RELOAD")
  print("BQA_CLEANUP=PASS; innotest kept ONLINE",flush=True)
 except Exception as exc:
  print("BQA_CLEANUP=FAIL "+repr(exc),flush=True)
  raise
 finally:
  for pair in bots.values():killbot(pair)
