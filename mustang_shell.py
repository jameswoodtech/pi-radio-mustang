#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import subprocess
import os
import sys
import datetime

TS_JAR = "/home/pony2002/TunerStudioMS/TunerStudioMS.jar"
BACKGROUND_IMAGE = "/home/pony2002/mustang-shell/assets/mustang-splash-800x480.png"

class MustangShell(Gtk.Window):
    def __init__(self):
        super().__init__(title="Mustang Head Unit")

        # No window borders, full screen
        self.set_decorated(False)
        self.fullscreen()

        self._setup_css()

        # Overlay: background image + UI on top
        overlay = Gtk.Overlay()
        self.add(overlay)

        # Background image
        if os.path.exists(BACKGROUND_IMAGE):
            bg_image = Gtk.Image.new_from_file(BACKGROUND_IMAGE)
        else:
            # Fallback: solid dark background if image missing
            bg_image = Gtk.EventBox()
            bg_color = Gdk.RGBA(0.05, 0.05, 0.08, 1.0)
            bg_image.override_background_color(Gtk.StateFlags.NORMAL, bg_color)

        overlay.add(bg_image)

        # Foreground layout (status bar + buttons)
        vbox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)

        overlay.add_overlay(vbox)

        # === Top status bar ===
        status_bar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )
        status_bar.set_name("statusbar")
        vbox.pack_start(status_bar, False, False, 0)

        self.clock_label = Gtk.Label()
        self.clock_label.set_name("status-label")

        # Left: small "Mustang" label
        title_label = Gtk.Label(label="Mustang UI")
        title_label.set_name("status-label")

        # Right: placeholders for Wi-Fi + clock
        status_bar.pack_start(title_label, False, False, 10)
        status_bar.pack_end(self.clock_label, False, False, 10)

        self._update_clock()
        GLib.timeout_add_seconds(30, self._update_clock)

        # === Spacer + button grid ===
        # Expand to center the buttons roughly in the screen
        spacer_top = Gtk.Box()
        vbox.pack_start(spacer_top, True, True, 0)

        grid = Gtk.Grid(column_spacing=20, row_spacing=20)
        vbox.pack_start(grid, False, False, 0)

        spacer_bottom = Gtk.Box()
        vbox.pack_start(spacer_bottom, True, True, 0)

        btn_gauges = self._big_button("Gauges", self.launch_tunerstudio)
        btn_music  = self._big_button("Music", self.launch_music)
        btn_nav    = self._big_button("Navigation", self.launch_nav)
        btn_exit   = self._big_button("Quit", self.quit_shell)

        grid.attach(btn_gauges, 0, 0, 1, 1)
        grid.attach(btn_music,  1, 0, 1, 1)
        grid.attach(btn_nav,    0, 1, 1, 1)
        grid.attach(btn_exit,   1, 1, 1, 1)

    def _setup_css(self):
        css = b"""
        #statusbar {
            background-color: rgba(5, 5, 10, 0.85);
        }
        #status-label {
            color: #ffffff;
            font-size: 14px;
        }
        .big-button {
            background: rgba(0, 0, 0, 0.70);
            color: #f0f0f0;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            font-size: 18px;
        }
        .big-button:hover {
            background: rgba(20, 20, 30, 0.90);
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

    def _update_clock(self):
        now = datetime.datetime.now()
        # 12-hour or 24-hour, pick your poison:
        self.clock_label.set_text(now.strftime("%-I:%M %p"))
        return True  # keep the timeout active

    def _big_button(self, label, callback):
        btn = Gtk.Button(label=label)
        btn.set_size_request(200, 110)
        style = btn.get_style_context()
        style.add_class("big-button")

        child = btn.get_child()
        if child:
            child.set_margin_top(10)
            child.set_margin_bottom(10)
            child.set_margin_start(10)
            child.set_margin_end(10)

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