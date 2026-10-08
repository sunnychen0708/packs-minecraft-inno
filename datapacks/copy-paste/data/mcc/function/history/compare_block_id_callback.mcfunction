data modify storage mcc:temp cmp_bid set from storage mcc:temp state.id
return run function mcc:history/compare_block_id with storage mcc:temp
