import os


if (
    (os.name != "nt" and not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"))
    or (os.environ.get("CI") and not os.environ.get("QT_QPA_PLATFORM"))
) and not os.environ.get("QT_QPA_PLATFORM"):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

from airmouse.main_window import run


if __name__ == "__main__":
    raise SystemExit(run())
