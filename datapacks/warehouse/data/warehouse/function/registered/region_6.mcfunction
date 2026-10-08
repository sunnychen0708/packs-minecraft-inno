data modify storage warehouse:runtime registered.l61 set value {"text":"未註冊 61 ","extra":[]}
data modify storage warehouse:runtime registered.l61.extra append from storage warehouse:boxnames c61
execute if data storage warehouse:chests c61{registered:1b} run data modify storage warehouse:runtime registered.l61.text set value "已註冊 61 "
data modify storage warehouse:runtime registered.l62 set value {"text":"未註冊 62 ","extra":[]}
data modify storage warehouse:runtime registered.l62.extra append from storage warehouse:boxnames c62
execute if data storage warehouse:chests c62{registered:1b} run data modify storage warehouse:runtime registered.l62.text set value "已註冊 62 "
data modify storage warehouse:runtime registered.l63 set value {"text":"未註冊 63 ","extra":[]}
data modify storage warehouse:runtime registered.l63.extra append from storage warehouse:boxnames c63
execute if data storage warehouse:chests c63{registered:1b} run data modify storage warehouse:runtime registered.l63.text set value "已註冊 63 "
data modify storage warehouse:runtime registered.l64 set value {"text":"未註冊 64 ","extra":[]}
data modify storage warehouse:runtime registered.l64.extra append from storage warehouse:boxnames c64
execute if data storage warehouse:chests c64{registered:1b} run data modify storage warehouse:runtime registered.l64.text set value "已註冊 64 "
data modify storage warehouse:runtime registered.l65 set value {"text":"未註冊 65 ","extra":[]}
data modify storage warehouse:runtime registered.l65.extra append from storage warehouse:boxnames c65
execute if data storage warehouse:chests c65{registered:1b} run data modify storage warehouse:runtime registered.l65.text set value "已註冊 65 "
data modify storage warehouse:runtime registered.l66 set value {"text":"未註冊 66 ","extra":[]}
data modify storage warehouse:runtime registered.l66.extra append from storage warehouse:boxnames c66
execute if data storage warehouse:chests c66{registered:1b} run data modify storage warehouse:runtime registered.l66.text set value "已註冊 66 "
data modify storage warehouse:runtime registered.l67 set value {"text":"未註冊 67 ","extra":[]}
data modify storage warehouse:runtime registered.l67.extra append from storage warehouse:boxnames c67
execute if data storage warehouse:chests c67{registered:1b} run data modify storage warehouse:runtime registered.l67.text set value "已註冊 67 "
data modify storage warehouse:runtime registered.l68 set value {"text":"未註冊 68 ","extra":[]}
data modify storage warehouse:runtime registered.l68.extra append from storage warehouse:boxnames c68
execute if data storage warehouse:chests c68{registered:1b} run data modify storage warehouse:runtime registered.l68.text set value "已註冊 68 "
data modify storage warehouse:runtime registered.l69 set value {"text":"未註冊 69 ","extra":[]}
data modify storage warehouse:runtime registered.l69.extra append from storage warehouse:boxnames c69
execute if data storage warehouse:chests c69{registered:1b} run data modify storage warehouse:runtime registered.l69.text set value "已註冊 69 "
function warehouse:registered/region_6_render with storage warehouse:runtime registered
