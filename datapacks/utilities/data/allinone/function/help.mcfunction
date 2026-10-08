scoreboard players set @s help 0
tellraw @s {"text":"──────────────────────────────","color":"dark_gray"}
tellraw @s {"text":"─────── v3.8 功能總覽 ───────","color":"gold"}
tellraw @s {"text":"指令教學放在最上方；點指令只會自動填入聊天欄，不會直接執行。","color":"gray"}
tellraw @s {"text":" "}

# 指令教學：先顯示教學，再顯示操作按鈕
tellraw @s {"text":"────── 指令教學（點一下自動填入）──────","color":"gold"}
tellraw @s [{"text":"家: ","color":"white"},{"text":"/trigger sethome","color":"green","click_event":{"action":"suggest_command","command":"/trigger sethome"},"hover_event":{"action":"show_text","value":{"text":"設定目前位置為家","color":"yellow"}}},{"text":"  "},{"text":"/trigger home","color":"aqua","click_event":{"action":"suggest_command","command":"/trigger home"},"hover_event":{"action":"show_text","value":{"text":"傳送回家","color":"yellow"}}}]
tellraw @s [{"text":"礦坑: ","color":"white"},{"text":"/trigger setmine","color":"green","click_event":{"action":"suggest_command","command":"/trigger setmine"}},{"text":"  "},{"text":"/trigger mine","color":"aqua","click_event":{"action":"suggest_command","command":"/trigger mine"}}]
tellraw @s [{"text":"村莊: ","color":"white"},{"text":"/trigger setvillage","color":"green","click_event":{"action":"suggest_command","command":"/trigger setvillage"}},{"text":"  "},{"text":"/trigger village","color":"aqua","click_event":{"action":"suggest_command","command":"/trigger village"}}]
tellraw @s [{"text":"傳送門: ","color":"white"},{"text":"/trigger setportal","color":"green","click_event":{"action":"suggest_command","command":"/trigger setportal"}},{"text":"  "},{"text":"/trigger portal","color":"aqua","click_event":{"action":"suggest_command","command":"/trigger portal"}}]
tellraw @s [{"text":"臨時點: ","color":"white"},{"text":"/trigger settemp","color":"green","click_event":{"action":"suggest_command","command":"/trigger settemp"}},{"text":"  "},{"text":"/trigger temp","color":"aqua","click_event":{"action":"suggest_command","command":"/trigger temp"}}]
tellraw @s {"text":"固定據點只保留上方指令教學，不再另外顯示操作按鈕。","color":"gray"}
tellraw @s {"text":" "}
tellraw @s [{"text":"個人據點: ","color":"white"},{"text":"/trigger pset set 1","color":"green","click_event":{"action":"suggest_command","command":"/trigger pset set 1"}},{"text":"  "},{"text":"/trigger pgo set 1","color":"aqua","click_event":{"action":"suggest_command","command":"/trigger pgo set 1"}},{"text":"  "},{"text":"/trigger plist","color":"yellow","click_event":{"action":"suggest_command","command":"/trigger plist"}}]
tellraw @s [{"text":"共用據點: ","color":"white"},{"text":"/trigger sset set 1","color":"green","click_event":{"action":"suggest_command","command":"/trigger sset set 1"}},{"text":"  "},{"text":"/trigger sgo set 1","color":"aqua","click_event":{"action":"suggest_command","command":"/trigger sgo set 1"}},{"text":"  "},{"text":"/trigger slist","color":"yellow","click_event":{"action":"suggest_command","command":"/trigger slist"}}]
tellraw @s [{"text":"返回: ","color":"white"},{"text":"/trigger back","color":"light_purple","click_event":{"action":"suggest_command","command":"/trigger back"}},{"text":"  "},{"text":"死亡地點: ","color":"white"},{"text":"/trigger deathloc","color":"red","click_event":{"action":"suggest_command","command":"/trigger deathloc"}}]
tellraw @s {"text":" "}
tellraw @s [{"text":"設定位置＋名稱（個人）: ","color":"yellow"},{"text":"/function nav:set_personal {slot:1,name:\"名稱\"}","color":"green","click_event":{"action":"suggest_command","command":"/function nav:set_personal {slot:1,name:\"名稱\"}"}}]
tellraw @s [{"text":"設定位置＋名稱（共用）: ","color":"yellow"},{"text":"/function nav:set_shared {slot:1,name:\"名稱\"}","color":"aqua","click_event":{"action":"suggest_command","command":"/function nav:set_shared {slot:1,name:\"名稱\"}"}}]
tellraw @s {"text":" "}

# 按鈕區：固定據點不放按鈕
tellraw @s {"text":"────── 操作按鈕 ──────","color":"gold"}
tellraw @s [{"text":"座標顯示 ","color":"yellow"},{"text":"X / Y / Z","color":"white"}]
execute if score @s c26_show matches 1 run tellraw @s [{"text":"目前：開啟  ","color":"green"},{"text":"[關閉]","color":"red","click_event":{"action":"run_command","command":"/trigger coords"}}]
execute unless score @s c26_show matches 1 run tellraw @s [{"text":"目前：關閉  ","color":"red"},{"text":"[開啟]","color":"green","click_event":{"action":"run_command","command":"/trigger coords"}}]
tellraw @s [{"text":"自動補種 ","color":"yellow"}]
execute if score @s su_plant matches 1 run tellraw @s [{"text":"目前：開啟  ","color":"green"},{"text":"[關閉]","color":"red","click_event":{"action":"run_command","command":"/trigger replant"}}]
execute unless score @s su_plant matches 1 run tellraw @s [{"text":"目前：關閉  ","color":"red"},{"text":"[開啟]","color":"green","click_event":{"action":"run_command","command":"/trigger replant"}}]
tellraw @s [{"text":"連鎖砍樹 ","color":"yellow"}]
execute if score @s su_tree matches 1 run tellraw @s [{"text":"目前：開啟  ","color":"green"},{"text":"[關閉]","color":"red","click_event":{"action":"run_command","command":"/trigger treecap"}}]
execute unless score @s su_tree matches 1 run tellraw @s [{"text":"目前：關閉  ","color":"red"},{"text":"[開啟]","color":"green","click_event":{"action":"run_command","command":"/trigger treecap"}}]
tellraw @s [{"text":"礦脈挖掘 ","color":"yellow"}]
execute if score @s su_vein matches 1 run tellraw @s [{"text":"目前：開啟  ","color":"green"},{"text":"[關閉]","color":"red","click_event":{"action":"run_command","command":"/trigger veinmine"}}]
execute unless score @s su_vein matches 1 run tellraw @s [{"text":"目前：關閉  ","color":"red"},{"text":"[開啟]","color":"green","click_event":{"action":"run_command","command":"/trigger veinmine"}}]
tellraw @s {"text":" "}
tellraw @s [{"text":"[返回上次位置]","color":"light_purple","click_event":{"action":"run_command","command":"/trigger back"},"hover_event":{"action":"show_text","value":{"text":"回到上一次使用本資料包傳送前的位置；可來回切換","color":"yellow"}}},{"text":"  "},{"text":"[返回死亡地點]","color":"red","click_event":{"action":"run_command","command":"/trigger deathloc"},"hover_event":{"action":"show_text","value":{"text":"傳送到最近一次死亡位置","color":"yellow"}}}]
tellraw @s {"text":" "}
tellraw @s [{"text":"個人據點 ","color":"yellow"},{"text":"8 格  ","color":"gray"},{"text":"[開啟清單]","color":"green","click_event":{"action":"run_command","command":"/trigger plist"}}]
tellraw @s [{"text":"共用據點 ","color":"yellow"},{"text":"8 格  ","color":"gray"},{"text":"[開啟清單]","color":"aqua","click_event":{"action":"run_command","command":"/trigger slist"}}]
tellraw @s {"text":"未設定格按 [設定]：輸入名稱後才儲存位置；按 Esc／取消會直接返回且不儲存。已設定格的 [覆蓋] 只更新位置並保留名稱。","color":"gray"}
tellraw @s {"text":"──────────────────────────────","color":"dark_gray"}
tellraw @s [{"text":"隨時輸入 ","color":"gray"},{"text":"/trigger help","color":"aqua","click_event":{"action":"suggest_command","command":"/trigger help"}},{"text":" 重新開啟本選單","color":"gray"}]
