data modify storage warehouse:runtime registered.l51 set value {"text":"未註冊 51 ","extra":[]}
data modify storage warehouse:runtime registered.l51.extra append from storage warehouse:boxnames c51
execute if data storage warehouse:chests c51{registered:1b} run data modify storage warehouse:runtime registered.l51.text set value "已註冊 51 "
data modify storage warehouse:runtime registered.l52 set value {"text":"未註冊 52 ","extra":[]}
data modify storage warehouse:runtime registered.l52.extra append from storage warehouse:boxnames c52
execute if data storage warehouse:chests c52{registered:1b} run data modify storage warehouse:runtime registered.l52.text set value "已註冊 52 "
data modify storage warehouse:runtime registered.l53 set value {"text":"未註冊 53 ","extra":[]}
data modify storage warehouse:runtime registered.l53.extra append from storage warehouse:boxnames c53
execute if data storage warehouse:chests c53{registered:1b} run data modify storage warehouse:runtime registered.l53.text set value "已註冊 53 "
data modify storage warehouse:runtime registered.l54 set value {"text":"未註冊 54 ","extra":[]}
data modify storage warehouse:runtime registered.l54.extra append from storage warehouse:boxnames c54
execute if data storage warehouse:chests c54{registered:1b} run data modify storage warehouse:runtime registered.l54.text set value "已註冊 54 "
data modify storage warehouse:runtime registered.l55 set value {"text":"未註冊 55 ","extra":[]}
data modify storage warehouse:runtime registered.l55.extra append from storage warehouse:boxnames c55
execute if data storage warehouse:chests c55{registered:1b} run data modify storage warehouse:runtime registered.l55.text set value "已註冊 55 "
data modify storage warehouse:runtime registered.l56 set value {"text":"未註冊 56 ","extra":[]}
data modify storage warehouse:runtime registered.l56.extra append from storage warehouse:boxnames c56
execute if data storage warehouse:chests c56{registered:1b} run data modify storage warehouse:runtime registered.l56.text set value "已註冊 56 "
data modify storage warehouse:runtime registered.l57 set value {"text":"未註冊 57 ","extra":[]}
data modify storage warehouse:runtime registered.l57.extra append from storage warehouse:boxnames c57
execute if data storage warehouse:chests c57{registered:1b} run data modify storage warehouse:runtime registered.l57.text set value "已註冊 57 "
data modify storage warehouse:runtime registered.l58 set value {"text":"未註冊 58 ","extra":[]}
data modify storage warehouse:runtime registered.l58.extra append from storage warehouse:boxnames c58
execute if data storage warehouse:chests c58{registered:1b} run data modify storage warehouse:runtime registered.l58.text set value "已註冊 58 "
data modify storage warehouse:runtime registered.l59 set value {"text":"未註冊 59 ","extra":[]}
data modify storage warehouse:runtime registered.l59.extra append from storage warehouse:boxnames c59
execute if data storage warehouse:chests c59{registered:1b} run data modify storage warehouse:runtime registered.l59.text set value "已註冊 59 "
function warehouse:registered/region_5_render with storage warehouse:runtime registered
