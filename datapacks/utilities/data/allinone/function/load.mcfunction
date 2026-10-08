# 依序載入三個子系統（維持原有計分板與儲存名稱，舊資料可直接沿用）
function survival_utils:load
function sunny_nav:load
function coords:load

# 統一說明指令 /trigger help
scoreboard objectives add help trigger
scoreboard players enable @a help

# 移除舊的說明 trigger（/trigger utility 與 /trigger navhelp 已整合進 /trigger help）
scoreboard objectives remove utility
scoreboard objectives remove navhelp
scoreboard objectives remove pdel
scoreboard objectives remove sdel
scoreboard objectives remove clearhome
scoreboard objectives remove clearmine
scoreboard objectives remove clearvillage
scoreboard objectives remove clearportal
scoreboard objectives remove cleartemp

data modify storage allinone:meta version set value "26.3-3.0"
