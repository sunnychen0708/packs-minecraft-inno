# Minecraft Vanilla Packs

A monorepo for Minecraft Java vanilla data packs and resource packs.

## Structure

- `datapacks/vanilla-utilities/` — utility pack, current version v3.2. Originally named **整合_v3.2**.
- `datapacks/warehouse/` — automatic warehouse sorting pack, current version v4.0 for Minecraft Java 26.3.
- `resourcepacks/` — reserved for current and future vanilla resource packs.
- `scripts/` — repository maintenance and release build scripts.

Each data pack is stored unpacked so individual files can be reviewed, edited, diffed, and versioned normally with Git. Release ZIPs are built with `pack.mcmeta` at the archive root so they can be placed directly in a world's `datapacks` folder.

## Release tags

Because multiple packs share this repository, tags include the pack name:

- `vanilla-utilities-v3.2`
- `warehouse-v4.0`
