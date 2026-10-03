scoreboard players enable @a wh_register
scoreboard players enable @a wh_action
scoreboard players enable @a wh_nav
scoreboard players enable @a wh_view
scoreboard players enable @a wh_rule
scoreboard players enable @a wh_rule_dest
scoreboard players enable @a wh_rename_target
scoreboard players enable @a wh_unreg_do
scoreboard players enable @a wh_unreg
scoreboard players enable @a wh_search_pick
scoreboard players enable @a wh_viewpage
scoreboard players enable @a wh_highlight
scoreboard players enable @a pick
scoreboard players enable @a pick
execute as @a[scores={wh_nav=1..}] run function warehouse:ui/nav
execute as @a[scores={wh_register=100}] run function warehouse:ui/select_00
execute as @a[scores={wh_register=10..19}] run function warehouse:ui/select_code
execute as @a[scores={wh_register=20..29}] run function warehouse:ui/select_code
execute as @a[scores={wh_register=30..39}] run function warehouse:ui/select_code
execute as @a[scores={wh_register=40..49}] run function warehouse:ui/select_code
execute as @a[scores={wh_register=50..59}] run function warehouse:ui/select_code
execute as @a[scores={wh_register=60..69}] run function warehouse:ui/select_code
execute as @a[scores={wh_register=1..9}] run scoreboard players set @s wh_register 0
execute as @a[scores={wh_register=70..}] run scoreboard players set @s wh_register 0
execute as @a[scores={wh_action=1}] run scoreboard players set @s wh_action 0
execute as @a[scores={wh_action=2}] run dialog show @s warehouse:manage
execute as @a[scores={wh_action=2}] run scoreboard players set @s wh_action 0
execute as @a[scores={wh_action=3}] run function warehouse:ui/status
execute as @a[scores={wh_action=4}] run function warehouse:ui/retry
execute as @a[scores={wh_action=6}] run dialog show @s warehouse:help
execute as @a[scores={wh_action=6}] run scoreboard players set @s wh_action 0
execute as @a[scores={wh_action=7}] run dialog show @s warehouse:view/index
execute as @a[scores={wh_action=7}] run scoreboard players set @s wh_action 0
execute as @a[scores={wh_action=8}] run scoreboard players set @s wh_action 0
execute as @a[scores={wh_action=10..}] run scoreboard players set @s wh_action 0
execute as @a[scores={wh_action=5}] run scoreboard players set @s wh_action 0
execute as @a[scores={wh_view=1..}] run function warehouse:view/dispatch
execute as @a[scores={wh_viewpage=1..7}] run function warehouse:view/page/dispatch
execute as @a[scores={wh_search_pick=1..1544}] run function warehouse:rule/select_search
execute as @a[scores={wh_highlight=1..}] run function warehouse:highlight/from_rule
execute as @a[scores={pick=1..}] at @s run function warehouse:pick/start
execute as @a[scores={pick=1..}] run scoreboard players set @s pick 0
execute as @a[scores={wh_highlight=1..}] run scoreboard players set @s wh_highlight 0
execute as @a[scores={wh_rule=1}] run function warehouse:rule/show_current
execute as @a[scores={wh_rule=2}] run function warehouse:rule/remove_current
execute as @a[scores={wh_rule=3}] run scoreboard players set @s wh_rule 0
execute as @a[scores={wh_rule=4}] run function warehouse:rule/show_selected_or_home
execute as @a[scores={wh_rule=5..}] run scoreboard players set @s wh_rule 0
execute as @a[scores={wh_rule_dest=11..19}] run function warehouse:rule/apply_destination
execute as @a[scores={wh_rule_dest=21..29}] run function warehouse:rule/apply_destination
execute as @a[scores={wh_rule_dest=31..39}] run function warehouse:rule/apply_destination
execute as @a[scores={wh_rule_dest=41..49}] run function warehouse:rule/apply_destination
execute as @a[scores={wh_rule_dest=51..59}] run function warehouse:rule/apply_destination
execute as @a[scores={wh_rule_dest=61..69}] run function warehouse:rule/apply_destination
execute as @a[scores={wh_rule_dest=1..10}] run scoreboard players set @s wh_rule_dest 0
execute as @a[scores={wh_rule_dest=20}] run scoreboard players set @s wh_rule_dest 0
execute as @a[scores={wh_rule_dest=30}] run scoreboard players set @s wh_rule_dest 0
execute as @a[scores={wh_rule_dest=40}] run scoreboard players set @s wh_rule_dest 0
execute as @a[scores={wh_rule_dest=50}] run scoreboard players set @s wh_rule_dest 0
execute as @a[scores={wh_rule_dest=60}] run scoreboard players set @s wh_rule_dest 0
execute as @a[scores={wh_rule_dest=70..}] run scoreboard players set @s wh_rule_dest 0
execute if score #enabled wh_sys matches 1 if data storage warehouse:chests c00{registered:1b,valid:1b} run function warehouse:sort/tick
function warehouse:api/pending_refunds/tick
execute as @a[scores={wh_unreg=10..69}] run function warehouse:unregister/prepare
execute as @a[scores={wh_unreg=100}] run function warehouse:unregister/prepare
execute as @a[scores={wh_unreg_do=1}] run function warehouse:unregister/do
execute as @a[scores={wh_rename_target=10..69}] run function warehouse:boxname/select
execute as @a[scores={wh_rename_target=100}] run function warehouse:boxname/select
execute as @a[scores={wh_rename=1}] run function warehouse:boxname/apply
execute as @a[scores={wh_rename=2}] run function warehouse:boxname/reset
execute if score #enabled wh_sys matches 1 run function warehouse:compact/tick
execute if score #enabled wh_sys matches 1 run function warehouse:migration/tick
