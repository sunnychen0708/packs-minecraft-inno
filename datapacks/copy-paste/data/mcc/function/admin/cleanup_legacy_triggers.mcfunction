# Optional migration helper for worlds upgraded from Copy/Paste v1.3 or older.
# Scoreboard objective names are global and have no owner metadata, so mcc:load must never
# delete these names automatically. Run this function only after confirming no other datapack
# currently uses rotate/mirror/rotate90/rotate270/flipx/flipz.
scoreboard objectives remove rotate
scoreboard objectives remove mirror
scoreboard objectives remove rotate90
scoreboard objectives remove rotate270
scoreboard objectives remove flipx
scoreboard objectives remove flipz
return 1
