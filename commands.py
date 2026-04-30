"""
commands.py
Routes voice/text commands to the right handler.
"""

import datetime
import re
from ai_brain import ask_ai
from device_control import (
    set_wifi, set_bluetooth, set_flashlight,
    set_brightness, set_volume, set_auto_rotate,
    set_dnd, set_airplane_mode, get_battery,
    open_app, open_url
)
from notification_mgr import (
    set_app_notifications,
    get_installed_apps,
    open_notification_settings
)

# Common app package map for launching
LAUNCH_APPS = {
    "whatsapp":    ("com.whatsapp",                    "WhatsApp"),
    "instagram":   ("com.instagram.android",           "Instagram"),
    "facebook":    ("com.facebook.katana",             "Facebook"),
    "youtube":     ("com.google.android.youtube",      "YouTube"),
    "gmail":       ("com.google.android.gm",           "Gmail"),
    "twitter":     ("com.twitter.android",             "Twitter"),
    "x":           ("com.twitter.android",             "X"),
    "snapchat":    ("com.snapchat.android",            "Snapchat"),
    "telegram":    ("org.telegram.messenger",          "Telegram"),
    "spotify":     ("com.spotify.music",               "Spotify"),
    "netflix":     ("com.netflix.mediaclient",         "Netflix"),
    "chrome":      ("com.android.chrome",              "Chrome"),
    "maps":        ("com.google.android.apps.maps",    "Google Maps"),
    "tiktok":      ("com.zhiliaoapp.musically",        "TikTok"),
    "zoom":        ("us.zoom.videomeetings",           "Zoom"),
    "discord":     ("com.discord",                     "Discord"),
    "reddit":      ("com.reddit.frontpage",            "Reddit"),
    "calculator":  ("com.google.android.calculator",  "Calculator"),
    "camera":      ("com.android.camera2",             "Camera"),
    "settings":    ("com.android.settings",            "Settings"),
    "play store":  ("com.android.vending",             "Play Store"),
    "clock":       ("com.google.android.deskclock",    "Clock"),
    "contacts":    ("com.google.android.contacts",     "Contacts"),
    "photos":      ("com.google.android.apps.photos",  "Google Photos"),
    "messages":    ("com.google.android.apps.messaging","Messages"),
}


def handle_command(command: str) -> str:
    """Main command router. Returns reply string."""
    cmd = command.lower().strip()

    # ── WiFi ──────────────────────────────────────────────
    if "wifi" in cmd or "wi-fi" in cmd:
        if any(w in cmd for w in ["on", "enable", "turn on", "connect"]):
            return set_wifi(True)
        elif any(w in cmd for w in ["off", "disable", "turn off", "disconnect"]):
            return set_wifi(False)

    # ── Bluetooth ─────────────────────────────────────────
    elif "bluetooth" in cmd or "bluet" in cmd:
        if any(w in cmd for w in ["on", "enable", "turn on"]):
            return set_bluetooth(True)
        elif any(w in cmd for w in ["off", "disable", "turn off"]):
            return set_bluetooth(False)

    # ── Flashlight / Torch ────────────────────────────────
    elif any(w in cmd for w in ["flashlight", "torch", "flash"]):
        if any(w in cmd for w in ["on", "enable", "turn on"]):
            return set_flashlight(True)
        elif any(w in cmd for w in ["off", "disable", "turn off"]):
            return set_flashlight(False)

    # ── Brightness ────────────────────────────────────────
    elif "brightness" in cmd or "bright" in cmd:
        nums = re.findall(r'\d+', cmd)
        level = int(nums[0]) if nums else 50
        level = max(0, min(100, level))
        return set_brightness(level)

    # ── Volume ────────────────────────────────────────────
    elif "volume" in cmd or "sound" in cmd:
        if any(w in cmd for w in ["up", "increase", "louder", "raise"]):
            return set_volume("up")
        elif any(w in cmd for w in ["down", "decrease", "lower", "quieter"]):
            return set_volume("down")
        elif any(w in cmd for w in ["mute", "silent", "silence"]):
            return set_volume("mute")

    # ── Auto Rotate ───────────────────────────────────────
    elif "rotate" in cmd or "rotation" in cmd or "auto rotate" in cmd:
        if any(w in cmd for w in ["on", "enable", "turn on"]):
            return set_auto_rotate(True)
        elif any(w in cmd for w in ["off", "disable", "turn off"]):
            return set_auto_rotate(False)

    # ── Do Not Disturb ────────────────────────────────────
    elif any(w in cmd for w in ["do not disturb", "dnd", "silent mode", "quiet mode"]):
        if any(w in cmd for w in ["on", "enable", "turn on", "activate"]):
            return set_dnd(True)
        elif any(w in cmd for w in ["off", "disable", "turn off", "deactivate"]):
            return set_dnd(False)

    # ── Airplane Mode ─────────────────────────────────────
    elif "airplane" in cmd or "flight mode" in cmd or "aeroplane" in cmd:
        if any(w in cmd for w in ["on", "enable", "turn on"]):
            return set_airplane_mode(True)
        elif any(w in cmd for w in ["off", "disable", "turn off"]):
            return set_airplane_mode(False)

    # ── Battery ───────────────────────────────────────────
    elif "battery" in cmd or "charge" in cmd or "power" in cmd:
        return get_battery()

    # ── Notifications: mute/enable specific app ───────────
    elif any(w in cmd for w in ["mute", "unmute", "notification", "notifications"]):
        enable = any(w in cmd for w in ["unmute", "enable", "turn on", "on"])
        # Extract app name
        app_name = cmd
        for word in ["mute", "unmute", "notification", "notifications", "for",
                     "enable", "disable", "turn on", "turn off", "on", "off"]:
            app_name = app_name.replace(word, "").strip()
        if app_name:
            return set_app_notifications(app_name, enable)
        return "Which app's notifications would you like to control?"

    # ── List installed apps ───────────────────────────────
    elif "installed apps" in cmd or "list apps" in cmd or "what apps" in cmd:
        return get_installed_apps()

    # ── Open app notification settings ───────────────────
    elif "notification settings" in cmd:
        app_name = cmd.replace("notification settings", "").replace("open", "").replace("for", "").strip()
        if app_name:
            return open_notification_settings(app_name)
        return "Which app's notification settings do you want to open?"

    # ── Time ─────────────────────────────────────────────
    elif "time" in cmd and any(w in cmd for w in ["what", "current", "now", "tell"]):
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"It's {now} 🕐"

    # ── Date ─────────────────────────────────────────────
    elif "date" in cmd and any(w in cmd for w in ["what", "today", "current"]):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today} 📅"

    # ── YouTube search ────────────────────────────────────
    elif "youtube" in cmd and any(w in cmd for w in ["search", "play", "find", "watch"]):
        query = cmd
        for w in ["search youtube for", "search on youtube", "play on youtube",
                  "find on youtube", "youtube search", "youtube", "search", "play", "watch"]:
            query = query.replace(w, "").strip()
        return open_url(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")

    # ── Google search ─────────────────────────────────────
    elif "google" in cmd or "search for" in cmd or "search" in cmd:
        query = cmd
        for w in ["search google for", "google search", "search for", "google", "search"]:
            query = query.replace(w, "").strip()
        if query:
            return open_url(f"https://www.google.com/search?q={query.replace(' ', '+')}")

    # ── Open apps ─────────────────────────────────────────
    elif "open" in cmd or "launch" in cmd or "start" in cmd:
        app_name = cmd
        for w in ["open", "launch", "start", "the", "app"]:
            app_name = app_name.replace(w, "").strip()
        for key, (pkg, display) in LAUNCH_APPS.items():
            if key in app_name:
                return open_app(pkg, display)
        # Try opening as URL if it looks like a website
        if "." in app_name:
            return open_url(f"https://{app_name}")
        return ask_ai(command)

    # ── Fallback → Groq AI ────────────────────────────────
    else:
        return ask_ai(command)
