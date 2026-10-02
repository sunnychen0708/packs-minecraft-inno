execute as @a unless score @s mcc_id matches 1.. run function mcc:player_init
# Initialize newly introduced state for existing players without resetting their clipboard.
execute as @a unless score @s mcc_rot matches 0..3 run scoreboard players set @s mcc_rot 0
execute as @a unless score @s mcc_mir matches 0..2 run scoreboard players set @s mcc_mir 0
execute as @a unless score @s mcc_usel matches 0..1 run scoreboard players set @s mcc_usel 0
execute as @a unless score @s mcc_cliptype matches 0..2 run scoreboard players set @s mcc_cliptype 0
execute as @a unless score @s mcc_redo matches 0..1 run scoreboard players set @s mcc_redo 0
execute as @a unless score @s mcc_ucnt matches 0..5 run scoreboard players set @s mcc_ucnt 0
execute as @a unless score @s mcc_uhead matches 0..5 run scoreboard players set @s mcc_uhead 0
execute as @a unless score @s mcc_rcnt matches 0..5 run scoreboard players set @s mcc_rcnt 0
execute as @a unless score @s mcc_rhead matches 0..5 run scoreboard players set @s mcc_rhead 0
execute as @a unless score @s mcc_bpscan matches 0..1 run scoreboard players set @s mcc_bpscan 0
execute as @a unless score @s mcc_bpactive matches 0..1 run scoreboard players set @s mcc_bpactive 0
execute as @a unless score @s mcc_bpready matches 0..1 run scoreboard players set @s mcc_bpready 0
execute as @a unless score @s mcc_bpbad matches 0..1 run scoreboard players set @s mcc_bpbad 0
execute as @a unless score @s mcc_matphase matches 0..2 run scoreboard players set @s mcc_matphase 0
execute as @a unless score @s mcc_matleft matches 0.. run scoreboard players set @s mcc_matleft 0
execute as @a unless score @s mcc_histmat matches 0..1 run scoreboard players set @s mcc_histmat 0
execute as @a unless score @s mcc_umat matches 0..1 run scoreboard players set @s mcc_umat 0
execute as @a unless score @s mcc_rmat matches 0..1 run scoreboard players set @s mcc_rmat 0
execute as @a unless score @s mcc_matjob matches 0..1 run scoreboard players set @s mcc_matjob 0
execute as @a unless score @s mcc_txslot matches 0..5 run scoreboard players set @s mcc_txslot 0
execute as @a[scores={copypaste=1..}] run function mcc:panel

execute as @a[scores={pos1=1..}] at @s run function mcc:select/start_pos1
execute as @a[scores={pos2=1..}] at @s run function mcc:select/start_pos2
execute as @a[scores={anchor=1}] at @s run function mcc:select/start_anchor
execute as @a[scores={anchor=2..}] run function mcc:anchor_clear
execute as @a[scores={c=1..,mcc_matphase=0}] run function mcc:copy/run
execute as @a[scores={x=1..,mcc_matphase=0}] run function mcc:cut/run
execute as @a[scores={v=1..,mcc_matphase=0}] at @s run function mcc:select/start_paste
execute as @a[scores={undo=1..,mcc_matphase=0}] run function mcc:undo/run
execute as @a[scores={redo=1..,mcc_matphase=0}] run function mcc:redo/run
execute as @a[scores={mode=1..}] run function mcc:mode_toggle
execute as @a[scores={rotate=1}] run function mcc:state/rot_cycle
execute as @a[scores={rotate=10}] run function mcc:state/rot_0
execute as @a[scores={rotate=20}] run function mcc:state/rot_90
execute as @a[scores={rotate=30}] run function mcc:state/rot_180
execute as @a[scores={rotate=40}] run function mcc:state/rot_270
execute as @a[scores={mirror=1}] run function mcc:state/mir_cycle
execute as @a[scores={mirror=10}] run function mcc:state/mir_none
execute as @a[scores={mirror=20}] run function mcc:state/mir_x
execute as @a[scores={mirror=30}] run function mcc:state/mir_z
execute as @a[scores={right=1..,mcc_matphase=0}] at @s run function mcc:move/right
execute as @a[scores={left=1..,mcc_matphase=0}] at @s run function mcc:move/left
execute as @a[scores={up=1..,mcc_matphase=0}] at @s run function mcc:move/up
execute as @a[scores={down=1..,mcc_matphase=0}] at @s run function mcc:move/down
execute as @a[scores={forward=1..,mcc_matphase=0}] at @s run function mcc:move/forward
execute as @a[scores={backward=1..,mcc_matphase=0}] at @s run function mcc:move/backward
execute as @a[scores={flipx=1..,mcc_matphase=0}] run function mcc:flip/x
execute as @a[scores={flipz=1..,mcc_matphase=0}] run function mcc:flip/z
execute as @a[scores={rotate90=1..,mcc_matphase=0}] run function mcc:rotate_edit/r90
execute as @a[scores={rotate180=1..,mcc_matphase=0}] run function mcc:rotate_edit/r180
execute as @a[scores={rotate270=1..,mcc_matphase=0}] run function mcc:rotate_edit/r270
execute as @a[scores={previewclear=1..}] run function mcc:blueprint/clear
execute as @a[scores={build=1..}] run function mcc:materials/build_start
execute as @a[scores={matbox=1..}] at @s run function mcc:select/start_matbox
execute as @a[scores={matremove=1..}] at @s run function mcc:select/start_matremove
execute as @a[scores={matlist=1..}] run function mcc:materials/list
execute as @a[scores={mcc_bpscan=1..}] run function mcc:blueprint/scan_batch
execute as @a[scores={mcc_matphase=1..2}] run function mcc:materials/process_batch

scoreboard players set @a[scores={copypaste=1..}] copypaste 0
scoreboard players set @a[scores={pos1=1..}] pos1 0
scoreboard players set @a[scores={pos2=1..}] pos2 0
scoreboard players set @a[scores={anchor=1..}] anchor 0
scoreboard players set @a[scores={c=1..}] c 0
scoreboard players set @a[scores={x=1..}] x 0
scoreboard players set @a[scores={v=1..}] v 0
scoreboard players set @a[scores={undo=1..}] undo 0
scoreboard players set @a[scores={redo=1..}] redo 0
scoreboard players set @a[scores={mode=1..}] mode 0
scoreboard players set @a[scores={rotate=1..}] rotate 0
scoreboard players set @a[scores={mirror=1..}] mirror 0
scoreboard players set @a[scores={right=1..}] right 0
scoreboard players set @a[scores={left=1..}] left 0
scoreboard players set @a[scores={up=1..}] up 0
scoreboard players set @a[scores={down=1..}] down 0
scoreboard players set @a[scores={forward=1..}] forward 0
scoreboard players set @a[scores={backward=1..}] backward 0
scoreboard players set @a[scores={flipx=1..}] flipx 0
scoreboard players set @a[scores={flipz=1..}] flipz 0
scoreboard players set @a[scores={rotate90=1..}] rotate90 0
scoreboard players set @a[scores={rotate180=1..}] rotate180 0
scoreboard players set @a[scores={rotate270=1..}] rotate270 0
scoreboard players set @a[scores={previewclear=1..}] previewclear 0
scoreboard players set @a[scores={build=1..}] build 0
scoreboard players set @a[scores={matbox=1..}] matbox 0
scoreboard players set @a[scores={matremove=1..}] matremove 0
scoreboard players set @a[scores={matlist=1..}] matlist 0

scoreboard players enable @a copypaste
scoreboard players enable @a pos1
scoreboard players enable @a pos2
scoreboard players enable @a anchor
scoreboard players enable @a c
scoreboard players enable @a x
scoreboard players enable @a v
scoreboard players enable @a undo
scoreboard players enable @a redo
scoreboard players enable @a mode
scoreboard players enable @a rotate
scoreboard players enable @a mirror
scoreboard players enable @a right
scoreboard players enable @a left
scoreboard players enable @a up
scoreboard players enable @a down
scoreboard players enable @a forward
scoreboard players enable @a backward
scoreboard players enable @a flipx
scoreboard players enable @a flipz
scoreboard players enable @a rotate90
scoreboard players enable @a rotate180
scoreboard players enable @a rotate270
scoreboard players enable @a previewclear
scoreboard players enable @a build
scoreboard players enable @a matbox
scoreboard players enable @a matremove
scoreboard players enable @a matlist
