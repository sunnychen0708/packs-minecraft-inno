$data modify storage warehouse:runtime viewer.line set value {text:"$(name) ×$(count)"}
data modify storage warehouse:runtime viewer.lines append from storage warehouse:runtime viewer.line
scoreboard players add @s wh_viewlines 1
