# ReveCraft

Binary and reverse-engineering craft workstation.

## Verbs
- `revecraft strings --file <path>`: Extract printable ASCII and UTF-16 strings
- `revecraft entropy --file <path>`: Calculate Shannon entropy and block mapping
- `revecraft pe-info --file <path>`: Parse Windows PE headers and architecture
- `revecraft die --file <path>`: Detect It Easy compiler/packer detection
- `revecraft capa --file <path>`: Mandiant capa capability detection
- `revecraft dki-decode --file <path>`: Decompress Directmedia .DKI files
- `revecraft snapshot --file <path>`: Generate full static analysis snapshot
- `revecraft extensions --action list|catalog|install|remove|enable|disable [--name ...]`: Manage Ghidra community extensions (SNES/65816-first catalog)
- `revecraft mcp`: FastMCP stdio server

## Status — does today / next week / non-goals

**Does today:** Python FastMCP workstation; 15 tests; strings/entropy/PE/
DiE/CAPA + DKI-decode + snapshot + Ghidra-extensions verbs.

**Next week:** engine-presence gates with `DOWN` receipts in tests; 3 recipes
(strings-entropy, die-capa-smoke, dki-decode); frida confirm-gate in code +
test.

**Non-goals:** frida never executes a target in default CI; Ghidra/ReVa
session lifecycle unproven yet.

## Lineage — the Storytold craft-app pattern

Storytold ArtCraft ([storytold/artcraft](https://github.com/storytold/artcraft) — "the IDE for artists") was the starting point. The 16 craft apps in the Storytold stable each ship one binary that is both the human CLI and the agent MCP server (stdio), headless-first, with `run.json` + report artifacts. That modus operandi and harness is what this repo implements; the code here is independent, the pattern is shared.
