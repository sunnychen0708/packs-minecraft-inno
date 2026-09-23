data modify storage warehouse:runtime registered.l31 set value {"text":"未註冊 31 ","extra":[]}
data modify storage warehouse:runtime registered.l31.extra append from storage warehouse:boxnames c31
execute if data storage warehouse:chests c31{registered:1b} run data modify storage warehouse:runtime registered.l31.text set value "已註冊 31 "
data modify storage warehouse:runtime registered.l32 set value {"text":"未註冊 32 ","extra":[]}
data modify storage warehouse:runtime registered.l32.extra append from storage warehouse:boxnames c32
execute if data storage warehouse:chests c32{registered:1b} run data modify storage warehouse:runtime registered.l32.text set value "已註冊 32 "
data modify storage warehouse:runtime registered.l33 set value {"text":"未註冊 33 ","extra":[]}
data modify storage warehouse:runtime registered.l33.extra append from storage warehouse:boxnames c33
execute if data storage warehouse:chests c33{registered:1b} run data modify storage warehouse:runtime registered.l33.text set value "已註冊 33 "
data modify storage warehouse:runtime registered.l34 set value {"text":"未註冊 34 ","extra":[]}
data modify storage warehouse:runtime registered.l34.extra append from storage warehouse:boxnames c34
execute if data storage warehouse:chests c34{registered:1b} run data modify storage warehouse:runtime registered.l34.text set value "已註冊 34 "
data modify storage warehouse:runtime registered.l35 set value {"text":"未註冊 35 ","extra":[]}
data modify storage warehouse:runtime registered.l35.extra append from storage warehouse:boxnames c35
execute if data storage warehouse:chests c35{registered:1b} run data modify storage warehouse:runtime registered.l35.text set value "已註冊 35 "
data modify storage warehouse:runtime registered.l36 set value {"text":"未註冊 36 ","extra":[]}
data modify storage warehouse:runtime registered.l36.extra append from storage warehouse:boxnames c36
execute if data storage warehouse:chests c36{registered:1b} run data modify storage warehouse:runtime registered.l36.text set value "已註冊 36 "
data modify storage warehouse:runtime registered.l37 set value {"text":"未註冊 37 ","extra":[]}
data modify storage warehouse:runtime registered.l37.extra append from storage warehouse:boxnames c37
execute if data storage warehouse:chests c37{registered:1b} run data modify storage warehouse:runtime registered.l37.text set value "已註冊 37 "
data modify storage warehouse:runtime registered.l38 set value {"text":"未註冊 38 ","extra":[]}
data modify storage warehouse:runtime registered.l38.extra append from storage warehouse:boxnames c38
execute if data storage warehouse:chests c38{registered:1b} run data modify storage warehouse:runtime registered.l38.text set value "已註冊 38 "
data modify storage warehouse:runtime registered.l39 set value {"text":"未註冊 39 ","extra":[]}
data modify storage warehouse:runtime registered.l39.extra append from storage warehouse:boxnames c39
execute if data storage warehouse:chests c39{registered:1b} run data modify storage warehouse:runtime registered.l39.text set value "已註冊 39 "
function warehouse:registered/region_3_render with storage warehouse:runtime registered
