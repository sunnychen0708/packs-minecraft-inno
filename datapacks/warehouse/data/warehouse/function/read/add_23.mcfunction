data modify storage warehouse:runtime read.name set from storage warehouse:boxnames c23
data modify storage warehouse:runtime read.action set value {label:{text:"23 ",extra:[]},width:190,action:{type:"run_command",command:"trigger wh_unreg set 23"}}
data modify storage warehouse:runtime read.action.label.extra append from storage warehouse:runtime read.name
data modify storage warehouse:runtime read.actions append from storage warehouse:runtime read.action
scoreboard players add @s wh_viewcnt 1
