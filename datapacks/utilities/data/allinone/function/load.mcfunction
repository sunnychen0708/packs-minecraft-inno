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
tellraw @a [{"text":"[屁眼派對] ","color":"gold"},{"text":"已載入。輸入 ","color":"gray"},{"text":"/trigger help","color":"aqua","click_event":{"action":"run_command","command":"/trigger help"},"hover_event":{"action":"show_text","value":{"text":"點擊開啟功能總覽","color":"yellow"}}},{"text":" 查看全部功能與開關。","color":"gray"}]
