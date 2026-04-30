"""
device_control.py
Controls Android device settings via jnius (Java bridge).
WiFi, Bluetooth, Brightness, Flashlight, DND, Airplane, Volume, Rotate.
"""

# Detect if running on Android
try:
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False
    print("[Device] Not on Android — using simulation mode")


def _get_context():
    if not IS_ANDROID:
        return None
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    return PythonActivity.mActivity


# ── WiFi ─────────────────────────────────────────────────
def set_wifi(enable: bool) -> str:
    if not IS_ANDROID:
        return f"[SIM] WiFi {'enabled' if enable else 'disabled'}"
    try:
        context = _get_context()
        WifiManager = autoclass('android.net.wifi.WifiManager')
        wifi = context.getSystemService(context.WIFI_SERVICE)
        wifi.setWifiEnabled(enable)
        return f"WiFi {'enabled 📶' if enable else 'disabled 📵'}"
    except Exception as e:
        return f"WiFi error: {e}"


# ── Bluetooth ─────────────────────────────────────────────
def set_bluetooth(enable: bool) -> str:
    if not IS_ANDROID:
        return f"[SIM] Bluetooth {'enabled' if enable else 'disabled'}"
    try:
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        adapter = BluetoothAdapter.getDefaultAdapter()
        if adapter is None:
            return "Bluetooth not available on this device"
        if enable:
            adapter.enable()
        else:
            adapter.disable()
        return f"Bluetooth {'enabled 🔵' if enable else 'disabled ⚫'}"
    except Exception as e:
        return f"Bluetooth error: {e}"


# ── Flashlight / Torch ────────────────────────────────────
def set_flashlight(enable: bool) -> str:
    if not IS_ANDROID:
        return f"[SIM] Flashlight {'on' if enable else 'off'}"
    try:
        context = _get_context()
        CameraManager = autoclass('android.hardware.camera2.CameraManager')
        cam_manager = context.getSystemService(context.CAMERA_SERVICE)
        camera_id = cam_manager.getCameraIdList()[0]
        cam_manager.setTorchMode(camera_id, enable)
        return f"Flashlight {'on 🔦' if enable else 'off'}"
    except Exception as e:
        return f"Flashlight error: {e}"


# ── Screen Brightness ─────────────────────────────────────
def set_brightness(level: int) -> str:
    """Set brightness 0-100."""
    if not IS_ANDROID:
        return f"[SIM] Brightness set to {level}%"
    try:
        context = _get_context()
        Settings = autoclass('android.provider.Settings')
        ContentResolver = autoclass('android.content.ContentResolver')
        resolver = context.getContentResolver()
        # Convert 0-100 to 0-255
        value = int((level / 100) * 255)
        Settings.System.putInt(
            resolver,
            Settings.System.SCREEN_BRIGHTNESS,
            value
        )
        window = context.getWindow()
        params = window.getAttributes()
        params.screenBrightness = level / 100.0
        window.setAttributes(params)
        return f"Brightness set to {level}% 🔆"
    except Exception as e:
        return f"Brightness error: {e}"


# ── Volume ────────────────────────────────────────────────
def set_volume(direction: str) -> str:
    """direction: 'up', 'down', or 'mute'"""
    if not IS_ANDROID:
        return f"[SIM] Volume {direction}"
    try:
        context = _get_context()
        AudioManager = autoclass('android.media.AudioManager')
        audio = context.getSystemService(context.AUDIO_SERVICE)
        if direction == 'up':
            audio.adjustStreamVolume(
                AudioManager.STREAM_MUSIC,
                AudioManager.ADJUST_RAISE,
                AudioManager.FLAG_SHOW_UI
            )
            return "Volume up 🔊"
        elif direction == 'down':
            audio.adjustStreamVolume(
                AudioManager.STREAM_MUSIC,
                AudioManager.ADJUST_LOWER,
                AudioManager.FLAG_SHOW_UI
            )
            return "Volume down 🔉"
        elif direction == 'mute':
            audio.adjustStreamVolume(
                AudioManager.STREAM_MUSIC,
                AudioManager.ADJUST_MUTE,
                AudioManager.FLAG_SHOW_UI
            )
            return "Muted 🔇"
    except Exception as e:
        return f"Volume error: {e}"


# ── Auto Rotate ───────────────────────────────────────────
def set_auto_rotate(enable: bool) -> str:
    if not IS_ANDROID:
        return f"[SIM] Auto-rotate {'on' if enable else 'off'}"
    try:
        context = _get_context()
        Settings = autoclass('android.provider.Settings')
        Settings.System.putInt(
            context.getContentResolver(),
            Settings.System.ACCELEROMETER_ROTATION,
            1 if enable else 0
        )
        return f"Auto-rotate {'enabled 🔄' if enable else 'disabled'}"
    except Exception as e:
        return f"Auto-rotate error: {e}"


# ── Do Not Disturb ────────────────────────────────────────
def set_dnd(enable: bool) -> str:
    if not IS_ANDROID:
        return f"[SIM] DND {'on' if enable else 'off'}"
    try:
        context = _get_context()
        NotificationManager = autoclass('android.app.NotificationManager')
        nm = context.getSystemService(context.NOTIFICATION_SERVICE)
        if enable:
            nm.setInterruptionFilter(
                NotificationManager.INTERRUPTION_FILTER_NONE
            )
            return "Do Not Disturb enabled 🔕"
        else:
            nm.setInterruptionFilter(
                NotificationManager.INTERRUPTION_FILTER_ALL
            )
            return "Do Not Disturb disabled 🔔"
    except Exception as e:
        return f"DND error: {e}"


# ── Airplane Mode ─────────────────────────────────────────
def set_airplane_mode(enable: bool) -> str:
    if not IS_ANDROID:
        return f"[SIM] Airplane mode {'on' if enable else 'off'}"
    try:
        context = _get_context()
        Settings = autoclass('android.provider.Settings')
        Settings.Global.putInt(
            context.getContentResolver(),
            Settings.Global.AIRPLANE_MODE_ON,
            1 if enable else 0
        )
        Intent = autoclass('android.content.Intent')
        intent = Intent(Intent.ACTION_AIRPLANE_MODE_CHANGED)
        intent.putExtra("state", enable)
        context.sendBroadcast(intent)
        return f"Airplane mode {'on ✈️' if enable else 'off'}"
    except Exception as e:
        return f"Airplane mode error: {e}"


# ── Battery Info ──────────────────────────────────────────
def get_battery() -> str:
    if not IS_ANDROID:
        return "[SIM] Battery: 87%"
    try:
        context = _get_context()
        Intent = autoclass('android.content.Intent')
        IntentFilter = autoclass('android.content.IntentFilter')
        BatteryManager = autoclass('android.os.BatteryManager')
        ifilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        battery_status = context.registerReceiver(None, ifilter)
        level = battery_status.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        scale = battery_status.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
        pct = int((level / scale) * 100)
        return f"Battery is at {pct}% 🔋"
    except Exception as e:
        return f"Battery error: {e}"


# ── Open App by package name ──────────────────────────────
def open_app(package_name: str, display_name: str) -> str:
    if not IS_ANDROID:
        return f"[SIM] Opening {display_name}"
    try:
        context = _get_context()
        pm = context.getPackageManager()
        intent = pm.getLaunchIntentForPackage(package_name)
        if intent:
            context.startActivity(intent)
            return f"Opening {display_name}! 🚀"
        else:
            return f"{display_name} is not installed"
    except Exception as e:
        return f"Open app error: {e}"


# ── Open URL in browser ───────────────────────────────────
def open_url(url: str) -> str:
    if not IS_ANDROID:
        return f"[SIM] Opening {url}"
    try:
        context = _get_context()
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
        return f"Opening {url} 🌐"
    except Exception as e:
        return f"URL error: {e}"
