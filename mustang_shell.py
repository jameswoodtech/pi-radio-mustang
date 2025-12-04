#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

import subprocess
import os
import sys

TS_JAR = "/home/pony2002/TunerStudioMS/TunerStudioMS.jar"  # adjust if needed
ASSETS_DIR = "/home/pony2002/mustang-shell/assets"
BG_IMAGE = os.path.join(ASSETS_DIR, "mustang-splash-800x480.png")  # export your splash to this


class MustangShell(Gtk.Window):
    def __init__(self):
        super().__init__(title="Mustang Head Unit")

        # No window borders, full screen
        self.set_decorated(False)
        self.fullscreen()

        # Set a dark fallback background
        self.override_background_color(
            Gtk.StateFlags.NORMAL,
            Gdk.RGBA(0.03, 0.03, 0.05, 1.0),
        )

        # Load CSS styling
        self._load_css()

        # Main overlay: background image + UI on top
        overlay = Gtk.Overlay()
        self.add(overlay)

        # Background image (scaled to window)
        if os.path.exists(BG_IMAGE):
            bg = self._background_image_widget(BG_IMAGE)
            overlay.add(bg)

        # Foreground content (button grid)
        fg_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        fg_box.set_halign(Gtk.Align.CENTER)
        fg_box.set_valign(Gtk.Align.CENTER)
        fg_box.set_spacing(20)

        # 2×2 grid of buttons
        grid = Gtk.Grid(
            column_spacing=20,
            row_spacing=20,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)

        btn_gauges = self._big_button("Gauges", self.launch_tunerstudio)
        btn_music  = self._big_button("Music", self.launch_music)
        btn_nav    = self._big_button("Navigation", self.launch_nav)
        btn_exit   = self._big_button("Exit", self.quit_shell)

        grid.attach(btn_gauges, 0, 0, 1, 1)
        grid.attach(btn_music,  1, 0, 1, 1)
        grid.attach(btn_nav,    0, 1, 1, 1)
        grid.attach(btn_exit,   1, 1, 1, 1)

        fg_box.pack_start(grid, False, False, 0)
        overlay.add_overlay(fg_box)

        # Ensure clicks go to foreground
        overlay.set_overlay_pass_through(fg_box, False)

    def _background_image_widget(self, path):
        """Return an image widget that scales to window size."""
        image = Gtk.Image.new_from_file(path)
        image.set_halign(Gtk.Align.FILL)
        image.set_valign(Gtk.Align.FILL)
        image.set_hexpand(True)
        image.set_vexpand(True)
        # Let GTK scale it; if you want pixel-perfect, we can manually rescale later
        return image

    def _load_css(self):
        css = b"""
        window {
            background-color: #05050a;
        }

        button.mustang-btn {
            background-image: none;
            background-color: #141824;
            border-radius: 16px;
            border-width: 2px;
            border-color: #2f5bff; /* Sonic-ish blue accent */
            color: #f0f0f0;
            padding: 12px 16px;
        }

        button.mustang-btn:hover {
            background-color: #1b2030;
        }

        button.mustang-btn label {
            font-size: 18px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _big_button(self, label, callback):
        btn = Gtk.Button(label=label)
        btn.set_name("mustang-btn")           # for CSS
        btn.get_style_context().add_class("mustang-btn")
        btn.set_size_request(220, 110)
        btn.connect("clicked", callback)
        return btn

    def launch_tunerstudio(self, _button):
        if os.path.exists(TS_JAR):
            subprocess.Popen(
                ["/usr/bin/java", "-jar", TS_JAR],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            print(f"TunerStudio jar not found at: {TS_JAR}", file=sys.stderr)

    def _launch_chromium(self, url):
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