data modify storage warehouse:runtime viewer.queue set value []
data modify storage warehouse:runtime viewer.totals set value []
data modify storage warehouse:runtime viewer.lines set value []
scoreboard players set @s wh_viewcnt 0
scoreboard players set @s wh_viewlines 0
$execute in $(dimension) if loaded $(a_x) $(a_y) $(a_z) if block $(a_x) $(a_y) $(a_z) #warehouse:storage_chests run scoreboard players add @s wh_viewcnt 1
$execute in $(dimension) if loaded $(b_x) $(b_y) $(b_z) if block $(b_x) $(b_y) $(b_z) #warehouse:storage_chests run scoreboard players add @s wh_viewcnt 1
execute unless score @s wh_viewcnt matches 2 run dialog show @s warehouse:view/error_inaccessible
execute unless score @s wh_viewcnt matches 2 run return 0
data modify storage warehouse:runtime viewer.queue set value []
$execute in $(dimension) run data modify storage warehouse:runtime viewer.queue set from block $(a_x) $(a_y) $(a_z) Items
execute if data storage warehouse:runtime viewer.queue[0] run function warehouse:view/aggregate_loop
data modify storage warehouse:runtime viewer.queue set value []
$execute in $(dimension) run data modify storage warehouse:runtime viewer.queue set from block $(b_x) $(b_y) $(b_z) Items
execute if data storage warehouse:runtime viewer.queue[0] run function warehouse:view/aggregate_loop
execute if data storage warehouse:runtime viewer.totals[0] run function warehouse:view/line_loop
data modify storage warehouse:runtime viewer.render set value {title:"",l01:"",l02:"",l03:"",l04:"",l05:"",l06:"",l07:"",l08:"",l09:"",l10:"",l11:"",l12:"",l13:"",l14:"",l15:"",l16:"",l17:"",l18:"",l19:"",l20:"",l21:"",l22:"",l23:"",l24:"",l25:"",l26:"",l27:"",l28:"",l29:"",l30:"",l31:"",l32:"",l33:"",l34:"",l35:"",l36:"",l37:"",l38:"",l39:"",l40:"",l41:"",l42:"",l43:"",l44:"",l45:"",l46:"",l47:"",l48:"",l49:"",l50:"",l51:"",l52:"",l53:"",l54:""}
data modify storage warehouse:runtime viewer.render.title set from storage warehouse:runtime viewer.title
execute if data storage warehouse:runtime viewer.lines[0].text run data modify storage warehouse:runtime viewer.render.l01 set from storage warehouse:runtime viewer.lines[0].text
execute if data storage warehouse:runtime viewer.lines[1].text run data modify storage warehouse:runtime viewer.render.l02 set from storage warehouse:runtime viewer.lines[1].text
execute if data storage warehouse:runtime viewer.lines[2].text run data modify storage warehouse:runtime viewer.render.l03 set from storage warehouse:runtime viewer.lines[2].text
execute if data storage warehouse:runtime viewer.lines[3].text run data modify storage warehouse:runtime viewer.render.l04 set from storage warehouse:runtime viewer.lines[3].text
execute if data storage warehouse:runtime viewer.lines[4].text run data modify storage warehouse:runtime viewer.render.l05 set from storage warehouse:runtime viewer.lines[4].text
execute if data storage warehouse:runtime viewer.lines[5].text run data modify storage warehouse:runtime viewer.render.l06 set from storage warehouse:runtime viewer.lines[5].text
execute if data storage warehouse:runtime viewer.lines[6].text run data modify storage warehouse:runtime viewer.render.l07 set from storage warehouse:runtime viewer.lines[6].text
execute if data storage warehouse:runtime viewer.lines[7].text run data modify storage warehouse:runtime viewer.render.l08 set from storage warehouse:runtime viewer.lines[7].text
execute if data storage warehouse:runtime viewer.lines[8].text run data modify storage warehouse:runtime viewer.render.l09 set from storage warehouse:runtime viewer.lines[8].text
execute if data storage warehouse:runtime viewer.lines[9].text run data modify storage warehouse:runtime viewer.render.l10 set from storage warehouse:runtime viewer.lines[9].text
execute if data storage warehouse:runtime viewer.lines[10].text run data modify storage warehouse:runtime viewer.render.l11 set from storage warehouse:runtime viewer.lines[10].text
execute if data storage warehouse:runtime viewer.lines[11].text run data modify storage warehouse:runtime viewer.render.l12 set from storage warehouse:runtime viewer.lines[11].text
execute if data storage warehouse:runtime viewer.lines[12].text run data modify storage warehouse:runtime viewer.render.l13 set from storage warehouse:runtime viewer.lines[12].text
execute if data storage warehouse:runtime viewer.lines[13].text run data modify storage warehouse:runtime viewer.render.l14 set from storage warehouse:runtime viewer.lines[13].text
execute if data storage warehouse:runtime viewer.lines[14].text run data modify storage warehouse:runtime viewer.render.l15 set from storage warehouse:runtime viewer.lines[14].text
execute if data storage warehouse:runtime viewer.lines[15].text run data modify storage warehouse:runtime viewer.render.l16 set from storage warehouse:runtime viewer.lines[15].text
execute if data storage warehouse:runtime viewer.lines[16].text run data modify storage warehouse:runtime viewer.render.l17 set from storage warehouse:runtime viewer.lines[16].text
execute if data storage warehouse:runtime viewer.lines[17].text run data modify storage warehouse:runtime viewer.render.l18 set from storage warehouse:runtime viewer.lines[17].text
execute if data storage warehouse:runtime viewer.lines[18].text run data modify storage warehouse:runtime viewer.render.l19 set from storage warehouse:runtime viewer.lines[18].text
execute if data storage warehouse:runtime viewer.lines[19].text run data modify storage warehouse:runtime viewer.render.l20 set from storage warehouse:runtime viewer.lines[19].text
execute if data storage warehouse:runtime viewer.lines[20].text run data modify storage warehouse:runtime viewer.render.l21 set from storage warehouse:runtime viewer.lines[20].text
execute if data storage warehouse:runtime viewer.lines[21].text run data modify storage warehouse:runtime viewer.render.l22 set from storage warehouse:runtime viewer.lines[21].text
execute if data storage warehouse:runtime viewer.lines[22].text run data modify storage warehouse:runtime viewer.render.l23 set from storage warehouse:runtime viewer.lines[22].text
execute if data storage warehouse:runtime viewer.lines[23].text run data modify storage warehouse:runtime viewer.render.l24 set from storage warehouse:runtime viewer.lines[23].text
execute if data storage warehouse:runtime viewer.lines[24].text run data modify storage warehouse:runtime viewer.render.l25 set from storage warehouse:runtime viewer.lines[24].text
execute if data storage warehouse:runtime viewer.lines[25].text run data modify storage warehouse:runtime viewer.render.l26 set from storage warehouse:runtime viewer.lines[25].text
execute if data storage warehouse:runtime viewer.lines[26].text run data modify storage warehouse:runtime viewer.render.l27 set from storage warehouse:runtime viewer.lines[26].text
execute if data storage warehouse:runtime viewer.lines[27].text run data modify storage warehouse:runtime viewer.render.l28 set from storage warehouse:runtime viewer.lines[27].text
execute if data storage warehouse:runtime viewer.lines[28].text run data modify storage warehouse:runtime viewer.render.l29 set from storage warehouse:runtime viewer.lines[28].text
execute if data storage warehouse:runtime viewer.lines[29].text run data modify storage warehouse:runtime viewer.render.l30 set from storage warehouse:runtime viewer.lines[29].text
execute if data storage warehouse:runtime viewer.lines[30].text run data modify storage warehouse:runtime viewer.render.l31 set from storage warehouse:runtime viewer.lines[30].text
execute if data storage warehouse:runtime viewer.lines[31].text run data modify storage warehouse:runtime viewer.render.l32 set from storage warehouse:runtime viewer.lines[31].text
execute if data storage warehouse:runtime viewer.lines[32].text run data modify storage warehouse:runtime viewer.render.l33 set from storage warehouse:runtime viewer.lines[32].text
execute if data storage warehouse:runtime viewer.lines[33].text run data modify storage warehouse:runtime viewer.render.l34 set from storage warehouse:runtime viewer.lines[33].text
execute if data storage warehouse:runtime viewer.lines[34].text run data modify storage warehouse:runtime viewer.render.l35 set from storage warehouse:runtime viewer.lines[34].text
execute if data storage warehouse:runtime viewer.lines[35].text run data modify storage warehouse:runtime viewer.render.l36 set from storage warehouse:runtime viewer.lines[35].text
execute if data storage warehouse:runtime viewer.lines[36].text run data modify storage warehouse:runtime viewer.render.l37 set from storage warehouse:runtime viewer.lines[36].text
execute if data storage warehouse:runtime viewer.lines[37].text run data modify storage warehouse:runtime viewer.render.l38 set from storage warehouse:runtime viewer.lines[37].text
execute if data storage warehouse:runtime viewer.lines[38].text run data modify storage warehouse:runtime viewer.render.l39 set from storage warehouse:runtime viewer.lines[38].text
execute if data storage warehouse:runtime viewer.lines[39].text run data modify storage warehouse:runtime viewer.render.l40 set from storage warehouse:runtime viewer.lines[39].text
execute if data storage warehouse:runtime viewer.lines[40].text run data modify storage warehouse:runtime viewer.render.l41 set from storage warehouse:runtime viewer.lines[40].text
execute if data storage warehouse:runtime viewer.lines[41].text run data modify storage warehouse:runtime viewer.render.l42 set from storage warehouse:runtime viewer.lines[41].text
execute if data storage warehouse:runtime viewer.lines[42].text run data modify storage warehouse:runtime viewer.render.l43 set from storage warehouse:runtime viewer.lines[42].text
execute if data storage warehouse:runtime viewer.lines[43].text run data modify storage warehouse:runtime viewer.render.l44 set from storage warehouse:runtime viewer.lines[43].text
execute if data storage warehouse:runtime viewer.lines[44].text run data modify storage warehouse:runtime viewer.render.l45 set from storage warehouse:runtime viewer.lines[44].text
execute if data storage warehouse:runtime viewer.lines[45].text run data modify storage warehouse:runtime viewer.render.l46 set from storage warehouse:runtime viewer.lines[45].text
execute if data storage warehouse:runtime viewer.lines[46].text run data modify storage warehouse:runtime viewer.render.l47 set from storage warehouse:runtime viewer.lines[46].text
execute if data storage warehouse:runtime viewer.lines[47].text run data modify storage warehouse:runtime viewer.render.l48 set from storage warehouse:runtime viewer.lines[47].text
execute if data storage warehouse:runtime viewer.lines[48].text run data modify storage warehouse:runtime viewer.render.l49 set from storage warehouse:runtime viewer.lines[48].text
execute if data storage warehouse:runtime viewer.lines[49].text run data modify storage warehouse:runtime viewer.render.l50 set from storage warehouse:runtime viewer.lines[49].text
execute if data storage warehouse:runtime viewer.lines[50].text run data modify storage warehouse:runtime viewer.render.l51 set from storage warehouse:runtime viewer.lines[50].text
execute if data storage warehouse:runtime viewer.lines[51].text run data modify storage warehouse:runtime viewer.render.l52 set from storage warehouse:runtime viewer.lines[51].text
execute if data storage warehouse:runtime viewer.lines[52].text run data modify storage warehouse:runtime viewer.render.l53 set from storage warehouse:runtime viewer.lines[52].text
execute if data storage warehouse:runtime viewer.lines[53].text run data modify storage warehouse:runtime viewer.render.l54 set from storage warehouse:runtime viewer.lines[53].text
execute store result storage warehouse:runtime viewer.render.count int 1 run scoreboard players get @s wh_viewlines
function warehouse:view/page/show_1
