"""
notification_mgr.py
Controls per-app notification settings on Android.
"""

try:
    from jnius import autoclass, cast
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

# Map common app names to package names
APP_PACKAGES = {
    "whatsapp":    "com.whatsapp",
    "instagram":   "com.instagram.android",
    "facebook":    "com.facebook.katana",
    "youtube":     "com.google.android.youtube",
    "gmail":       "com.google.android.gm",
    "twitter":     "com.twitter.android",
    "x":           "com.twitter.android",
    "snapchat":    "com.snapchat.android",
    "telegram":    "org.telegram.messenger",
    "spotify":     "com.spotify.music",
    "netflix":     "com.netflix.mediaclient",
    "chrome":      "com.android.chrome",
    "maps":        "com.google.android.apps.maps",
    "tiktok":      "com.zhiliaoapp.musically",
    "zoom":        "us.zoom.videomeetings",
    "discord":     "com.discord",
    "reddit":      "com.reddit.frontpage",
    "linkedin":    "com.linkedin.android",
    "amazon":      "com.amazon.mShop.android.shopping",
    "uber":        "com.ubercab",
    "google":      "com.google.android.googlequicksearchbox",
    "clock":       "com.google.android.deskclock",
    "camera":      "com.android.camera2",
    "gallery":     "com.google.android.apps.photos",
    "calculator":  "com.google.android.calculator",
    "messages":    "com.google.android.apps.messaging",
    "phone":       "com.google.android.dialer",
    "contacts":    "com.google.android.contacts",
    "play store":  "com.android.vending",
    "settings":    "com.android.settings",
}


def _get_context():
    if not IS_ANDROID:
        return None
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    return PythonActivity.mActivity


def resolve_package(app_name: str) -> str:
    """Resolve common app name to package name."""
    name = app_name.lower().strip()
    for key, pkg in APP_PACKAGES.items():
        if key in name:
            return pkg
    return None


def set_app_notifications(app_name: str, enable: bool) -> str:
    """Enable or disable notifications for an app."""
    pkg = resolve_package(app_name)
    if not pkg:
        return f"I don't know the package for '{app_name}'. Try using the exact app name."

    if not IS_ANDROID:
        action = "enabled 🔔" if enable else "muted 🔕"
        return f"[SIM] {app_name.title()} notifications {action}"

    try:
        context = _get_context()
        NotificationManager = autoclass('android.app.NotificationManager')
        nm = context.getSystemService(context.NOTIFICATION_SERVICE)

        # Android 8+ — use notification channels
        channels = nm.getNotificationChannels()
        if channels and channels.size() > 0:
            for i in range(channels.size()):
                channel = channels.get(i)
                importance = (
                    NotificationManager.IMPORTANCE_DEFAULT
                    if enable else
                    NotificationManager.IMPORTANCE_NONE
                )
                channel.setImportance(importance)
                nm.createNotificationChannel(channel)

        action = "enabled 🔔" if enable else "muted 🔕"
        return f"{app_name.title()} notifications {action}"

    except Exception as e:
        # Fallback — open app notification settings for the user
        try:
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
            intent.putExtra(Settings.EXTRA_APP_PACKAGE, pkg)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
            return f"Opening {app_name.title()} notification settings for you ⚙️"
        except Exception as e2:
            return f"Notification error: {e2}"


def get_installed_apps() -> str:
    """Return a list of installed user apps."""
    if not IS_ANDROID:
        return "[SIM] Installed apps: WhatsApp, Instagram, YouTube, Gmail, Spotify"
    try:
        context = _get_context()
        pm = context.getPackageManager()
        Intent = autoclass('android.content.Intent')
        intent = Intent(Intent.ACTION_MAIN)
        intent.addCategory(Intent.CATEGORY_LAUNCHER)
        apps = pm.queryIntentActivities(intent, 0)
        names = []
        for i in range(min(apps.size(), 20)):
            info = apps.get(i)
            name = str(info.loadLabel(pm))
            names.append(name)
        return "Installed apps: " + ", ".join(sorted(names))
    except Exception as e:
        return f"App list error: {e}"


def open_notification_settings(app_name: str) -> str:
    """Open notification settings page for a specific app."""
    pkg = resolve_package(app_name)
    if not pkg:
        return f"Can't find settings for '{app_name}'"
    if not IS_ANDROID:
        return f"[SIM] Opening notification settings for {app_name}"
    try:
        context = _get_context()
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
        intent.putExtra(Settings.EXTRA_APP_PACKAGE, pkg)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
        return f"Opening {app_name.title()} notification settings ⚙️"
    except Exception as e:
        return f"Settings error: {e}"
