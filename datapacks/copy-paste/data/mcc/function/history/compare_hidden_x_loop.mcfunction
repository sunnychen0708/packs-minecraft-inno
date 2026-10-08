scoreboard players operation @s mcc_mnx = #cmp_ex mcc_id
scoreboard players operation @s mcc_mnx += @s mcc_dx
scoreboard players operation @s mcc_mny = @s mcc_dy
scoreboard players operation @s mcc_mnz = #cmp_ez mcc_id
scoreboard players operation @s mcc_mnz += @s mcc_dz
scoreboard players operation @s mcc_mxx = @s mcc_dx
scoreboard players add @s mcc_mxx 31
scoreboard players operation @s mcc_tmp = @s mcc_fsx
scoreboard players remove @s mcc_tmp 1
execute if score @s mcc_mxx > @s mcc_tmp run scoreboard players operation @s mcc_mxx = @s mcc_tmp
scoreboard players operation @s mcc_mxx += #cmp_ex mcc_id
scoreboard players operation @s mcc_mxy = @s mcc_mny
scoreboard players operation @s mcc_mxz = @s mcc_mnz
scoreboard players operation @s mcc_dstx = #cmp_cx mcc_id
scoreboard players operation @s mcc_dstx += @s mcc_dx
scoreboard players operation @s mcc_dsty = @s mcc_dy
scoreboard players operation @s mcc_dstz = #cmp_cz mcc_id
scoreboard players operation @s mcc_dstz += @s mcc_dz
execute store result storage mcc:temp cmpq.sx1 int 1 run scoreboard players get @s mcc_mnx
execute store result storage mcc:temp cmpq.sy1 int 1 run scoreboard players get @s mcc_mny
execute store result storage mcc:temp cmpq.sz1 int 1 run scoreboard players get @s mcc_mnz
execute store result storage mcc:temp cmpq.sx2 int 1 run scoreboard players get @s mcc_mxx
execute store result storage mcc:temp cmpq.sy2 int 1 run scoreboard players get @s mcc_mxy
execute store result storage mcc:temp cmpq.sz2 int 1 run scoreboard players get @s mcc_mxz
execute store result storage mcc:temp cmpq.tx1 int 1 run scoreboard players get @s mcc_dstx
execute store result storage mcc:temp cmpq.ty1 int 1 run scoreboard players get @s mcc_dsty
execute store result storage mcc:temp cmpq.tz1 int 1 run scoreboard players get @s mcc_dstz
function mcc:history/compare_chunk with storage mcc:temp cmpq
execute unless score @s mcc_ok matches 1 run return fail
scoreboard players add @s mcc_dx 32
scoreboard players set @s mcc_tmp2 0
execute if score @s mcc_dx >= @s mcc_fsx run scoreboard players set @s mcc_tmp2 1
execute if score @s mcc_tmp2 matches 1 run scoreboard players set @s mcc_dx 0
execute if score @s mcc_tmp2 matches 1 run scoreboard players add @s mcc_dz 1
scoreboard players set @s mcc_amt 0
execute if score @s mcc_tmp2 matches 1 if score @s mcc_dz >= @s mcc_fsz run scoreboard players set @s mcc_amt 1
execute if score @s mcc_amt matches 1 run scoreboard players set @s mcc_dz 0
execute if score @s mcc_amt matches 1 run scoreboard players add @s mcc_dy 1
execute if score @s mcc_dy < @s mcc_sy run return run function mcc:history/compare_hidden_x_loop
return 1
