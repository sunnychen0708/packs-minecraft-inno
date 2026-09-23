# 三個子系統的每刻邏輯
function survival_utils:tick
function sunny_nav:tick
function coords:tick

# 統一說明指令
scoreboard players enable @a help
execute as @a[scores={help=1..}] run function allinone:help
