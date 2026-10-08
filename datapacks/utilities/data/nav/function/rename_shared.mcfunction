
# /function nav:rename_shared {slot:1,name:"中央村莊"}
$data modify storage sunny_nav:ctx slot set value $(slot)
$data modify storage sunny_nav:ctx name set value "$(name)"
function sunny_nav:command/shared_rename
