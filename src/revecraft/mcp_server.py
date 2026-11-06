"""FastMCP server for ReveCraft."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from . import ghidra_extensions as _gx
from .cli import (
    calculate_entropy,
    create_snapshot,
    decode_dki,
    extract_strings as _extract_strings,
    parse_pe_info,
    run_capa,
    run_die,
)

mcp = FastMCP("ReveCraft", version="0.1.0")


@mcp.tool()
def extract_strings(file_path: str, min_len: int = 4) -> list[dict[str, Any]]:
    """Extract printable ASCII and UTF-16LE strings with byte offsets."""
    return _extract_strings(Path(file_path), min_len=min_len)


@mcp.tool()
def analyze_entropy(file_path: str, block_size: int = 256) -> dict[str, Any]:
    """Calculate Shannon entropy and identify compressed or encrypted sections."""
    return calculate_entropy(Path(file_path), block_size=block_size)


@mcp.tool()
def analyze_pe_file(file_path: str) -> dict[str, Any]:
    """Parse Windows PE headers, sections, machine architecture, and timestamps."""
    return parse_pe_info(Path(file_path))


@mcp.tool()
def decode_dki_file(file_path: str, output_path: str | None = None) -> dict[str, Any]:
    """Decompress Directmedia .DKI compressed text stream (zlib/gzip)."""
    out = Path(output_path) if output_path else None
    return decode_dki(Path(file_path), out_path=out)


@mcp.tool()
def research_snapshot(file_path: str, output_dir: str | None = None) -> dict[str, Any]:
    """Produce structured static triage snapshot before interactive reversing."""
    out = Path(output_dir) if output_dir else None
    return create_snapshot(Path(file_path), out_dir=out)


@mcp.tool()
def check_tools(file_path: str | None = None) -> dict[str, Any]:
    """Check availability of reversing engines (diec, capa, etc.)."""
    dummy = Path(file_path) if file_path else Path(__file__)
    return {
        "die": run_die(dummy),
        "capa": run_capa(dummy),
    }


@mcp.tool()
def ghidra_extensions(
    operation: str = "list",
    name: str | None = None,
    version: str | None = None,
    confirm: bool = False,
) -> dict[str, Any]:
    """Manage Ghidra community extensions (SNES/65816-first catalog).

    operation: list | catalog | install | remove | enable | disable.
    install takes a catalog name, owner/repo, or https .zip URL.
    remove needs confirm=True. Restart Ghidra after install/remove/enable.
    """
    op = (operation or "").lower()
    if op == "list":
        return _gx.list_installed()
    if op == "catalog":
        return _gx.catalog()
    if op == "install":
        if not name:
            return {"success": False, "error": "install requires name."}
        return _gx.install_extension(name, version=version)
    if op == "remove":
        if not name:
            return {"success": False, "error": "remove requires name."}
        return _gx.remove_extension(name, confirm=confirm)
    if op == "enable":
        if not name:
            return {"success": False, "error": "enable requires name."}
        return _gx.set_enabled(name, True)
    if op == "disable":
        if not name:
            return {"success": False, "error": "disable requires name."}
        return _gx.set_enabled(name, False)
    return {"success": False, "error": f"Unknown operation '{operation}'. Valid: list, catalog, install, remove, enable, disable."}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
