# /function nav:set_personal {slot:1,name:"沙漠村莊"}
$data modify storage sunny_nav:ctx slot set value $(slot)
$data modify storage sunny_nav:ctx name set value "$(name)"
function sunny_nav:command/personal_set
