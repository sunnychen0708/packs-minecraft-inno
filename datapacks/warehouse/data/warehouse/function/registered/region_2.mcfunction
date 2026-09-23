data modify storage warehouse:runtime registered.l21 set value {"text":"未註冊 21 ","extra":[]}
data modify storage warehouse:runtime registered.l21.extra append from storage warehouse:boxnames c21
execute if data storage warehouse:chests c21{registered:1b} run data modify storage warehouse:runtime registered.l21.text set value "已註冊 21 "
data modify storage warehouse:runtime registered.l22 set value {"text":"未註冊 22 ","extra":[]}
data modify storage warehouse:runtime registered.l22.extra append from storage warehouse:boxnames c22
execute if data storage warehouse:chests c22{registered:1b} run data modify storage warehouse:runtime registered.l22.text set value "已註冊 22 "
data modify storage warehouse:runtime registered.l23 set value {"text":"未註冊 23 ","extra":[]}
data modify storage warehouse:runtime registered.l23.extra append from storage warehouse:boxnames c23
execute if data storage warehouse:chests c23{registered:1b} run data modify storage warehouse:runtime registered.l23.text set value "已註冊 23 "
data modify storage warehouse:runtime registered.l24 set value {"text":"未註冊 24 ","extra":[]}
data modify storage warehouse:runtime registered.l24.extra append from storage warehouse:boxnames c24
execute if data storage warehouse:chests c24{registered:1b} run data modify storage warehouse:runtime registered.l24.text set value "已註冊 24 "
data modify storage warehouse:runtime registered.l25 set value {"text":"未註冊 25 ","extra":[]}
data modify storage warehouse:runtime registered.l25.extra append from storage warehouse:boxnames c25
execute if data storage warehouse:chests c25{registered:1b} run data modify storage warehouse:runtime registered.l25.text set value "已註冊 25 "
data modify storage warehouse:runtime registered.l26 set value {"text":"未註冊 26 ","extra":[]}
data modify storage warehouse:runtime registered.l26.extra append from storage warehouse:boxnames c26
execute if data storage warehouse:chests c26{registered:1b} run data modify storage warehouse:runtime registered.l26.text set value "已註冊 26 "
data modify storage warehouse:runtime registered.l27 set value {"text":"未註冊 27 ","extra":[]}
data modify storage warehouse:runtime registered.l27.extra append from storage warehouse:boxnames c27
execute if data storage warehouse:chests c27{registered:1b} run data modify storage warehouse:runtime registered.l27.text set value "已註冊 27 "
data modify storage warehouse:runtime registered.l28 set value {"text":"未註冊 28 ","extra":[]}
data modify storage warehouse:runtime registered.l28.extra append from storage warehouse:boxnames c28
execute if data storage warehouse:chests c28{registered:1b} run data modify storage warehouse:runtime registered.l28.text set value "已註冊 28 "
data modify storage warehouse:runtime registered.l29 set value {"text":"未註冊 29 ","extra":[]}
data modify storage warehouse:runtime registered.l29.extra append from storage warehouse:boxnames c29
execute if data storage warehouse:chests c29{registered:1b} run data modify storage warehouse:runtime registered.l29.text set value "已註冊 29 "
function warehouse:registered/region_2_render with storage warehouse:runtime registered
