"""Tests for Ghidra community extensions CRUD (no network)."""

from revecraft import ghidra_extensions as gx


def test_catalog_has_snes_first():
    cat = gx.catalog()
    assert cat["success"] is True
    names = [e["name"] for e in cat["entries"]]
    assert "ghidra-65816" in names
    assert "ghidra-snes-loader" in names
    # SNES processor entry comes before generic tooling
    assert names.index("ghidra-65816") < names.index("ghidra-findcrypt")


def test_catalog_entries_have_repos():
    cat = gx.catalog()
    for entry in cat["entries"]:
        assert entry["repo"] and "/" in entry["repo"]
        assert entry["install_kind"] in ("github_release", "manual")


def test_list_installed_never_raises():
    res = gx.list_installed()
    assert res["success"] is True
    assert isinstance(res["extensions"], list)


def test_remove_requires_confirm():
    res = gx.remove_extension("ghidra-65816", confirm=False)
    assert res["success"] is False
    assert res.get("needs_confirm") is True


def test_remove_rejects_odd_names():
    res = gx.remove_extension("../evil", confirm=True)
    assert res["success"] is False


def test_enable_rejects_odd_names():
    res = gx.set_enabled("a/b", True)
    assert res["success"] is False


def test_install_unknown_name_no_network():
    res = gx.install_extension("no-such-extension-xyz", version=None)
    assert res["success"] is False
    assert "Known" in res["error"]


def test_install_manual_refuses_honestly():
    res = gx.install_extension("Ghidrathon")
    assert res["success"] is False
    assert res.get("needs_manual") is True
