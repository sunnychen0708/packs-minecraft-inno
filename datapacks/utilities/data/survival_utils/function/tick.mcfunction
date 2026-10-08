execute as @a unless score @s su_init matches 1 run function survival_utils:player_init
scoreboard players enable @a treecap
scoreboard players enable @a veinmine
scoreboard players enable @a replant
execute as @a[scores={treecap=1..}] run function survival_utils:toggle/tree
execute as @a[scores={veinmine=1..}] run function survival_utils:toggle/vein
execute as @a[scores={replant=1..}] run function survival_utils:toggle/plant
scoreboard players set @a[scores={treecap=1..}] treecap 0
scoreboard players set @a[scores={veinmine=1..}] veinmine 0
scoreboard players set @a[scores={replant=1..}] replant 0

# Crop break events
execute as @a[scores={mc_wheat=1..}] run function survival_utils:crop/trigger/wheat
scoreboard players set @a[scores={mc_wheat=1..}] mc_wheat 0
execute as @a[scores={mc_carrot=1..}] run function survival_utils:crop/trigger/carrot
scoreboard players set @a[scores={mc_carrot=1..}] mc_carrot 0
execute as @a[scores={mc_potato=1..}] run function survival_utils:crop/trigger/potato
scoreboard players set @a[scores={mc_potato=1..}] mc_potato 0
execute as @a[scores={mc_beet=1..}] run function survival_utils:crop/trigger/beetroot
scoreboard players set @a[scores={mc_beet=1..}] mc_beet 0
execute as @a[scores={mc_wart=1..}] run function survival_utils:crop/trigger/wart
scoreboard players set @a[scores={mc_wart=1..}] mc_wart 0

# Replant attempts and timeout
execute as @a[scores={su_crop=1..,su_plant=1}] at @s run function survival_utils:crop/scan
scoreboard players remove @a[scores={su_ctime=1..}] su_ctime 1
scoreboard players set @a[scores={su_ctime=0}] su_crop 0

# Tree-felling events
execute as @a[scores={ml_oak=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_oak=1..}] ml_oak 0
execute as @a[scores={ml_spruce=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_spruce=1..}] ml_spruce 0
execute as @a[scores={ml_birch=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_birch=1..}] ml_birch 0
execute as @a[scores={ml_jungle=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_jungle=1..}] ml_jungle 0
execute as @a[scores={ml_acacia=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_acacia=1..}] ml_acacia 0
execute as @a[scores={ml_darkoak=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_darkoak=1..}] ml_darkoak 0
execute as @a[scores={ml_mangrove=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_mangrove=1..}] ml_mangrove 0
execute as @a[scores={ml_cherry=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_cherry=1..}] ml_cherry 0
execute as @a[scores={ml_paleoak=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_paleoak=1..}] ml_paleoak 0
execute as @a[scores={ml_poplar=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_poplar=1..}] ml_poplar 0
execute as @a[scores={ml_crimson=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_crimson=1..}] ml_crimson 0
execute as @a[scores={ml_warped=1..}] at @s run function survival_utils:tree/trigger
scoreboard players set @a[scores={ml_warped=1..}] ml_warped 0

# Vein-mining events
execute as @a[scores={mo_co1=1..}] at @s run function survival_utils:vein/coal/trigger
scoreboard players set @a[scores={mo_co1=1..}] mo_co1 0
execute as @a[scores={mo_co2=1..}] at @s run function survival_utils:vein/coal/trigger
scoreboard players set @a[scores={mo_co2=1..}] mo_co2 0
execute as @a[scores={mo_ir1=1..}] at @s run function survival_utils:vein/iron/trigger
scoreboard players set @a[scores={mo_ir1=1..}] mo_ir1 0
execute as @a[scores={mo_ir2=1..}] at @s run function survival_utils:vein/iron/trigger
scoreboard players set @a[scores={mo_ir2=1..}] mo_ir2 0
execute as @a[scores={mo_cu1=1..}] at @s run function survival_utils:vein/copper/trigger
scoreboard players set @a[scores={mo_cu1=1..}] mo_cu1 0
execute as @a[scores={mo_cu2=1..}] at @s run function survival_utils:vein/copper/trigger
scoreboard players set @a[scores={mo_cu2=1..}] mo_cu2 0
execute as @a[scores={mo_go1=1..}] at @s run function survival_utils:vein/gold/trigger
scoreboard players set @a[scores={mo_go1=1..}] mo_go1 0
execute as @a[scores={mo_go2=1..}] at @s run function survival_utils:vein/gold/trigger
scoreboard players set @a[scores={mo_go2=1..}] mo_go2 0
execute as @a[scores={mo_rs1=1..}] at @s run function survival_utils:vein/redstone/trigger
scoreboard players set @a[scores={mo_rs1=1..}] mo_rs1 0
execute as @a[scores={mo_rs2=1..}] at @s run function survival_utils:vein/redstone/trigger
scoreboard players set @a[scores={mo_rs2=1..}] mo_rs2 0
execute as @a[scores={mo_la1=1..}] at @s run function survival_utils:vein/lapis/trigger
scoreboard players set @a[scores={mo_la1=1..}] mo_la1 0
execute as @a[scores={mo_la2=1..}] at @s run function survival_utils:vein/lapis/trigger
scoreboard players set @a[scores={mo_la2=1..}] mo_la2 0
execute as @a[scores={mo_di1=1..}] at @s run function survival_utils:vein/diamond/trigger
scoreboard players set @a[scores={mo_di1=1..}] mo_di1 0
execute as @a[scores={mo_di2=1..}] at @s run function survival_utils:vein/diamond/trigger
scoreboard players set @a[scores={mo_di2=1..}] mo_di2 0
execute as @a[scores={mo_em1=1..}] at @s run function survival_utils:vein/emerald/trigger
scoreboard players set @a[scores={mo_em1=1..}] mo_em1 0
execute as @a[scores={mo_em2=1..}] at @s run function survival_utils:vein/emerald/trigger
scoreboard players set @a[scores={mo_em2=1..}] mo_em2 0
execute as @a[scores={mo_qu1=1..}] at @s run function survival_utils:vein/quartz/trigger
scoreboard players set @a[scores={mo_qu1=1..}] mo_qu1 0
execute as @a[scores={mo_ng1=1..}] at @s run function survival_utils:vein/nether_gold/trigger
scoreboard players set @a[scores={mo_ng1=1..}] mo_ng1 0
execute as @a[scores={mo_ad1=1..}] at @s run function survival_utils:vein/ancient/trigger
scoreboard players set @a[scores={mo_ad1=1..}] mo_ad1 0
