#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import subprocess
import os
import sys
import datetime

TS_JAR = "/home/pony2002/TunerStudioMS/TunerStudioMS.jar"
BACKGROUND_PATH = "/home/pony2002/mustang-shell/assets/mustang-splash-800x480.png"

class MustangShell(Gtk.Window):
    def __init__(self):
        super().__init__(title="Mustang Head Unit")

        # No window borders, full screen
        self.set_decorated(False)
        self.fullscreen()

        # === CSS styling ===
        self._init_css()

        # === Main overlay: background image + UI on top ===
        overlay = Gtk.Overlay()
        self.add(overlay)

        # Background image
        bg_image = Gtk.Image()
        if os.path.exists(BACKGROUND_PATH):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(BACKGROUND_PATH)
            # Simple scale-to-fit for 800x480 panels
            screen = self.get_screen()
            if screen:
                w = screen.get_width()
                h = screen.get_height()
                # Fallback if screen info isn't ready yet
                if w <= 0: w = 800
                if h <= 0: h = 480
                scaled = pixbuf.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR)
                bg_image.set_from_pixbuf(scaled)
            else:
                bg_image.set_from_pixbuf(pixbuf)
        overlay.add(bg_image)

        # Foreground layout (status bar + centered buttons)
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        overlay.add_overlay(main_vbox)

        # Make overlay box expand to cover whole window
        main_vbox.set_hexpand(True)
        main_vbox.set_vexpand(True)

        # === Status bar at top ===
        status_bar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )
        status_bar.set_name("statusbar")
        status_bar.set_margin_top(0)
        status_bar.set_margin_bottom(0)
        status_bar.set_margin_start(0)
        status_bar.set_margin_end(0)
        status_bar.set_hexpand(True)

        # Left side: app title
        title_label = Gtk.Label(label="MUSTANG")
        title_label.set_name("status-title")
        title_label.set_halign(Gtk.Align.START)

        # Middle: status text placeholder (e.g., "Ready")
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_name("status-text")
        self.status_label.set_halign(Gtk.Align.CENTER)

        # Right side: Wi-Fi + clock
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        right_box.set_halign(Gtk.Align.END)

        # Wi-Fi icon (using standard icon name; you can swap for a custom SVG later)
        wifi_icon = Gtk.Image.new_from_icon_name(
            "network-wireless-symbolic",
            Gtk.IconSize.DND
        )
        wifi_icon.set_name("status-wifi")

        self.clock_label = Gtk.Label(label="00:00")
        self.clock_label.set_name("status-clock")

        right_box.pack_start(wifi_icon, False, False, 0)
        right_box.pack_start(self.clock_label, False, False, 0)

        status_bar.pack_start(title_label, False, False, 16)
        status_bar.pack_start(self.status_label, True, True, 0)
        status_bar.pack_start(right_box, False, False, 16)

        main_vbox.pack_start(status_bar, False, False, 0)

        # === Centered button grid ===
        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        center_box.set_hexpand(True)
        center_box.set_vexpand(True)
        center_box.set_halign(Gtk.Align.CENTER)
        center_box.set_valign(Gtk.Align.CENTER)

        grid = Gtk.Grid(
            column_spacing=20,
            row_spacing=20
        )
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)

        btn_gauges = self._big_button("Gauges", self.launch_tunerstudio)
        btn_music  = self._big_button("Music", self.launch_music)
        btn_nav    = self._big_button("Navigation", self.launch_nav)
        btn_exit   = self._big_button("Quit", self.quit_shell)

        grid.attach(btn_gauges, 0, 0, 1, 1)
        grid.attach(btn_music,  1, 0, 1, 1)
        grid.attach(btn_nav,    0, 1, 1, 1)
        grid.attach(btn_exit,   1, 1, 1, 1)

        center_box.pack_start(grid, False, False, 0)
        main_vbox.pack_start(center_box, True, True, 0)

        # Update clock every second
        GLib.timeout_add_seconds(1, self._update_clock)

    def _init_css(self):
        css = b"""
        window {
            background-color: #05050D;
        }

        #statusbar {
            background-color: rgba(10, 10, 20, 0.88);
            padding: 8px 12px;
            border-bottom: 1px solid rgba(200, 200, 255, 0.18);
        }

        #status-title {
            font-size: 18px;
            font-weight: bold;
            color: #E0E4FF;
            letter-spacing: 2px;
        }

        #status-text {
            font-size: 14px;
            color: #C0C4E0;
        }

        #status-clock {
            font-size: 18px;
            color: #E0E4FF;
        }

        #status-wifi {
            /* icon inherits color from theme; this helps keep it visible */
        }

        .big-button {
            background: rgba(15, 15, 30, 0.82);
            color: #F5F7FF;
            border-radius: 18px;
            border: 1px solid rgba(180, 190, 255, 0.3);
            padding: 10px 20px;
        }

        .big-button:hover {
            background: rgba(25, 25, 45, 0.9);
            border-color: rgba(210, 220, 255, 0.6);
        }

        .big-button label {
            font-size: 18px;
        }
        """

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _big_button(self, label, callback):
        btn = Gtk.Button(label=label)
        btn.get_style_context().add_class("big-button")
        btn.set_size_request(200, 110)
        btn.connect("clicked", callback)
        return btn

    def _update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.set_text(now.strftime("%-I:%M %p"))  # e.g., "3:27 PM"
        return True  # keep the timeout running

    # ---------- Launchers ----------

    def launch_tunerstudio(self, _button):
        self.status_label.set_text("Launching gauges…")
        if os.path.exists(TS_JAR):
            subprocess.Popen(
                ["/usr/bin/java", "-jar", TS_JAR],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            msg = f"TunerStudio jar not found at: {TS_JAR}"
            print(msg, file=sys.stderr)
            self.status_label.set_text("TunerStudio not found")

    def _launch_chromium(self, url, label):
        self.status_label.set_text(f"Opening {label}…")
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
        self.status_label.set_text("Browser not found")

    def launch_music(self, _button):
        self._launch_chromium("https://music.apple.com", "Music")

    def launch_nav(self, _button):
        self._launch_chromium("https://www.google.com/maps", "Navigation")

    def quit_shell(self, _button):
        Gtk.main_quit()


if __name__ == "__main__":
    win = MustangShell()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()