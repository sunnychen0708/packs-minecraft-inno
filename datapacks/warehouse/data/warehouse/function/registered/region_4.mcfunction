data modify storage warehouse:runtime registered.l41 set value {"text":"未註冊 41 ","extra":[]}
data modify storage warehouse:runtime registered.l41.extra append from storage warehouse:boxnames c41
execute if data storage warehouse:chests c41{registered:1b} run data modify storage warehouse:runtime registered.l41.text set value "已註冊 41 "
data modify storage warehouse:runtime registered.l42 set value {"text":"未註冊 42 ","extra":[]}
data modify storage warehouse:runtime registered.l42.extra append from storage warehouse:boxnames c42
execute if data storage warehouse:chests c42{registered:1b} run data modify storage warehouse:runtime registered.l42.text set value "已註冊 42 "
data modify storage warehouse:runtime registered.l43 set value {"text":"未註冊 43 ","extra":[]}
data modify storage warehouse:runtime registered.l43.extra append from storage warehouse:boxnames c43
execute if data storage warehouse:chests c43{registered:1b} run data modify storage warehouse:runtime registered.l43.text set value "已註冊 43 "
data modify storage warehouse:runtime registered.l44 set value {"text":"未註冊 44 ","extra":[]}
data modify storage warehouse:runtime registered.l44.extra append from storage warehouse:boxnames c44
execute if data storage warehouse:chests c44{registered:1b} run data modify storage warehouse:runtime registered.l44.text set value "已註冊 44 "
data modify storage warehouse:runtime registered.l45 set value {"text":"未註冊 45 ","extra":[]}
data modify storage warehouse:runtime registered.l45.extra append from storage warehouse:boxnames c45
execute if data storage warehouse:chests c45{registered:1b} run data modify storage warehouse:runtime registered.l45.text set value "已註冊 45 "
data modify storage warehouse:runtime registered.l46 set value {"text":"未註冊 46 ","extra":[]}
data modify storage warehouse:runtime registered.l46.extra append from storage warehouse:boxnames c46
execute if data storage warehouse:chests c46{registered:1b} run data modify storage warehouse:runtime registered.l46.text set value "已註冊 46 "
data modify storage warehouse:runtime registered.l47 set value {"text":"未註冊 47 ","extra":[]}
data modify storage warehouse:runtime registered.l47.extra append from storage warehouse:boxnames c47
execute if data storage warehouse:chests c47{registered:1b} run data modify storage warehouse:runtime registered.l47.text set value "已註冊 47 "
data modify storage warehouse:runtime registered.l48 set value {"text":"未註冊 48 ","extra":[]}
data modify storage warehouse:runtime registered.l48.extra append from storage warehouse:boxnames c48
execute if data storage warehouse:chests c48{registered:1b} run data modify storage warehouse:runtime registered.l48.text set value "已註冊 48 "
data modify storage warehouse:runtime registered.l49 set value {"text":"未註冊 49 ","extra":[]}
data modify storage warehouse:runtime registered.l49.extra append from storage warehouse:boxnames c49
execute if data storage warehouse:chests c49{registered:1b} run data modify storage warehouse:runtime registered.l49.text set value "已註冊 49 "
function warehouse:registered/region_4_render with storage warehouse:runtime registered
