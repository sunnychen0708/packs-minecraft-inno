# Internal helper for warehouse:api/material_sources/refresh.
# The same physical large chest may be registered under multiple Warehouse codes.
# Export it only once so inventory totals cannot be double-counted.
$data modify storage warehouse:api work.candidate_source set from storage warehouse:chests c$(code)
function warehouse:api/material_sources/append_unique with storage warehouse:api work.candidate_source
return 1
