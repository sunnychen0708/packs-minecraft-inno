data modify storage warehouse:runtime registered.l00 set value {"text":"未註冊 00 物品入口"}
execute if data storage warehouse:chests c00{registered:1b} run data modify storage warehouse:runtime registered.l00.text set value "已註冊 00 物品入口"
data modify storage warehouse:runtime registered.l10 set value {"text":"未註冊 10 ","extra":[]}
data modify storage warehouse:runtime registered.l10.extra append from storage warehouse:boxnames c10
execute if data storage warehouse:chests c10{registered:1b} run data modify storage warehouse:runtime registered.l10.text set value "已註冊 10 "
data modify storage warehouse:runtime registered.l20 set value {"text":"未註冊 20 ","extra":[]}
data modify storage warehouse:runtime registered.l20.extra append from storage warehouse:boxnames c20
execute if data storage warehouse:chests c20{registered:1b} run data modify storage warehouse:runtime registered.l20.text set value "已註冊 20 "
data modify storage warehouse:runtime registered.l30 set value {"text":"未註冊 30 ","extra":[]}
data modify storage warehouse:runtime registered.l30.extra append from storage warehouse:boxnames c30
execute if data storage warehouse:chests c30{registered:1b} run data modify storage warehouse:runtime registered.l30.text set value "已註冊 30 "
data modify storage warehouse:runtime registered.l40 set value {"text":"未註冊 40 ","extra":[]}
data modify storage warehouse:runtime registered.l40.extra append from storage warehouse:boxnames c40
execute if data storage warehouse:chests c40{registered:1b} run data modify storage warehouse:runtime registered.l40.text set value "已註冊 40 "
data modify storage warehouse:runtime registered.l50 set value {"text":"未註冊 50 ","extra":[]}
data modify storage warehouse:runtime registered.l50.extra append from storage warehouse:boxnames c50
execute if data storage warehouse:chests c50{registered:1b} run data modify storage warehouse:runtime registered.l50.text set value "已註冊 50 "
data modify storage warehouse:runtime registered.l60 set value {"text":"未註冊 60 ","extra":[]}
data modify storage warehouse:runtime registered.l60.extra append from storage warehouse:boxnames c60
execute if data storage warehouse:chests c60{registered:1b} run data modify storage warehouse:runtime registered.l60.text set value "已註冊 60 "
function warehouse:registered/special_render with storage warehouse:runtime registered
