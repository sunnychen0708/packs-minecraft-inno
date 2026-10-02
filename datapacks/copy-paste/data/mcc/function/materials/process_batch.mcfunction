execute if score @s mcc_matleft matches 1.. run function mcc:materials/process_next
execute if score @s mcc_matleft matches 1.. run function mcc:materials/process_next
execute if score @s mcc_matleft matches 1.. run function mcc:materials/process_next
execute if score @s mcc_matleft matches 1.. run function mcc:materials/process_next
execute if score @s mcc_matphase matches 1 if score @s mcc_matleft matches 0 run function mcc:materials/count_done
execute if score @s mcc_matphase matches 2 if score @s mcc_matleft matches 0 run function mcc:materials/take_done
return 1
