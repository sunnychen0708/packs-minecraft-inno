$data modify storage warehouse:runtime migration_task set value {item_id:"$(item_id)",from:$(old_box),to:$(dest)}
data modify storage warehouse:migration queue append from storage warehouse:runtime migration_task
