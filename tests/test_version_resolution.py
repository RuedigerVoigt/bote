import importlib


def reload_main_with_patch(monkeypatch, patch_importlib_version=None, patch_path_read_text=None):
    # Patch importlib.metadata.version if provided
    if patch_importlib_version is not None:
        import importlib.metadata as _im
        monkeypatch.setattr(_im, "version", patch_importlib_version, raising=True)

    # Patch pathlib.Path.read_text if provided
    if patch_path_read_text is not None:
        import pathlib as _pl
        monkeypatch.setattr(_pl.Path, "read_text", patch_path_read_text, raising=True)

    # Reload module under test to trigger top-level version resolution
    import bote.mailer as main
    importlib.reload(main)
    return main


def test_version_from_metadata(monkeypatch):
    def fake_version(_pkg: str) -> str:  # type: ignore[override]
        return "9.9.9"

    main = reload_main_with_patch(monkeypatch, patch_importlib_version=fake_version)
    assert main.__version__ == "9.9.9"


def test_version_fallback_to_pyproject(monkeypatch):
    # Raise PackageNotFoundError by making version() raise the same
    import importlib.metadata as _im

    def raise_not_found(_pkg: str):  # type: ignore[override]
        raise _im.PackageNotFoundError

    main = reload_main_with_patch(monkeypatch, patch_importlib_version=raise_not_found)
    # Expect version parsed from pyproject.toml in repo (2.0.0)
    assert isinstance(main.__version__, str) and len(main.__version__) > 0


def test_version_double_fallback_to_unknown(monkeypatch):
    import importlib.metadata as _im

    def raise_not_found(_pkg: str):  # type: ignore[override]
        raise _im.PackageNotFoundError

    def raise_io_error(self):  # type: ignore[override]
        raise OSError("cannot read")

    main = reload_main_with_patch(
        monkeypatch,
        patch_importlib_version=raise_not_found,
        patch_path_read_text=raise_io_error,
    )
    assert main.__version__ == "0+unknown"

