#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import subprocess
import os
import sys

TS_JAR = "/home/pony2002/TunerStudio/TunerStudioMS.jar"  # adjust if needed

class MustangShell(Gtk.Window):
    def __init__(self):
        super().__init__(title="Mustang Head Unit")

        # No window borders, full screen
        self.set_decorated(False)
        self.fullscreen()

        # Dark background
        self.override_background_color(
            Gtk.StateFlags.NORMAL,
            Gdk.RGBA(0.05, 0.05, 0.08, 1.0),
        )

        # Main grid
        grid = Gtk.Grid(
            column_spacing=20,
            row_spacing=20,
            margin_top=20,
            margin_bottom=20,
            margin_start=20,
            margin_end=20,
        )
        self.add(grid)

        btn_gauges = self._big_button("Gauges", self.launch_tunerstudio)
        btn_music  = self._big_button("Music", self.launch_music)
        btn_nav    = self._big_button("Navigation", self.launch_nav)
        btn_exit   = self._big_button("Quit", self.quit_shell)

        grid.attach(btn_gauges, 0, 0, 1, 1)
        grid.attach(btn_music,  1, 0, 1, 1)
        grid.attach(btn_nav,    0, 1, 1, 1)
        grid.attach(btn_exit,   1, 1, 1, 1)

    def _big_button(self, label, callback):
        btn = Gtk.Button(label=label)
        child = btn.get_child()
        if child:
            child.set_margin_top(10)
            child.set_margin_bottom(10)
            child.set_margin_start(10)
            child.set_margin_end(10)
        btn.set_size_request(180, 100)
        btn.connect("clicked", callback)
        return btn

    def launch_tunerstudio(self, _button):
        # Launch TunerStudio via Java
        if os.path.exists(TS_JAR):
            subprocess.Popen(
                ["/usr/bin/java", "-jar", TS_JAR],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            print(f"TunerStudio jar not found at: {TS_JAR}", file=sys.stderr)

    def _launch_chromium(self, url):
        # Try chromium-browser first, then chromium
        for cmd in ("chromium-browser", "chromium"):
            path = subprocess.run(
                ["which", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            ).stdout.strip()
            if path:
                subprocess.Popen(
                    [path, "--kiosk", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
        print("Chromium not found (chromium-browser or chromium)", file=sys.stderr)

    def launch_music(self, _button):
        self._launch_chromium("https://music.apple.com")

    def launch_nav(self, _button):
        self._launch_chromium("https://www.google.com/maps")

    def quit_shell(self, _button):
        Gtk.main_quit()


if __name__ == "__main__":
    win = MustangShell()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
