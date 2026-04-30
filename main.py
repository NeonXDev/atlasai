"""
main.py
Atlas AI — Ghibli-style Kivy Android App
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
import threading

from commands import handle_command

# ── Try TTS ──────────────────────────────────────────────
try:
    from plyer import tts as plyer_tts
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

# ── Try STT ──────────────────────────────────────────────
try:
    from android.permissions import request_permissions, Permission
    from plyer import stt
    STT_AVAILABLE = True
except Exception:
    STT_AVAILABLE = False


# ── Colors ────────────────────────────────────────────────
SKY_TOP     = get_color_from_hex('#4ab3e8')
SKY_MID     = get_color_from_hex('#7fcfef')
SKY_BOT     = get_color_from_hex('#b8e4f5')
OCEAN       = get_color_from_hex('#1a7faa')
DECK        = get_color_from_hex('#c8955a')
DECK_DARK   = get_color_from_hex('#a0733f')
RAIL        = get_color_from_hex('#c8e6f5')
LEAF_GREEN  = get_color_from_hex('#5a9e3a')
FLOWER_RED  = get_color_from_hex('#e85555')
WHITE       = get_color_from_hex('#ffffff')
GLASS       = (1, 1, 1, 0.25)
BUBBLE_AI   = get_color_from_hex('#dcf5ff') + (0.88,)
BUBBLE_USER = get_color_from_hex('#ffffff') + (0.85,)
TEXT_DARK   = get_color_from_hex('#2c3e50')


class GhibliBackground(Widget):
    """Draws the animated ocean + sky + deck background."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._draw, pos=self._draw)
        self._wave_offset = 0
        Clock.schedule_interval(self._animate_waves, 1 / 30)

    def _draw(self, *args):
        self.canvas.before.clear()
        w, h = self.size
        x, y = self.pos
        with self.canvas.before:
            # Sky gradient (approximated with layers)
            Color(*SKY_TOP)
            Rectangle(pos=(x, y + h * 0.55), size=(w, h * 0.45))
            Color(*SKY_MID)
            Rectangle(pos=(x, y + h * 0.40), size=(w, h * 0.20))
            Color(*SKY_BOT)
            Rectangle(pos=(x, y + h * 0.35), size=(w, h * 0.10))

            # Ocean
            Color(*OCEAN)
            Rectangle(pos=(x, y + h * 0.18), size=(w, h * 0.22))

            # Wave highlight
            Color(0.36, 0.75, 0.87, 0.5)
            Rectangle(pos=(x, y + h * 0.33), size=(w, dp(12)))

            # Deck
            Color(*DECK)
            Rectangle(pos=(x, y), size=(w, h * 0.18))

            # Deck top line
            Color(*DECK_DARK)
            Rectangle(pos=(x, y + h * 0.18), size=(w, dp(3)))

            # Railing bar
            Color(*RAIL)
            Rectangle(pos=(x, y + h * 0.21), size=(w, dp(4)))

            # Rail posts
            for i in range(0, int(w), int(dp(22))):
                Color(*RAIL)
                Rectangle(pos=(x + i, y + h * 0.18), size=(dp(4), dp(28)))

    def _animate_waves(self, dt):
        self._wave_offset += dt * 40
        if self._wave_offset > dp(60):
            self._wave_offset = 0
        self._draw()


class AtlasOrb(Widget):
    """Animated glowing orb in the center."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = 'idle'
        self._angle = 0
        self._scale = 1.0
        self.bind(size=self._draw, pos=self._draw)
        Clock.schedule_interval(self._animate, 1 / 30)

    def set_state(self, state):
        self.state = state

    def _animate(self, dt):
        self._angle += dt * 40
        if self.state == 'thinking':
            self._scale = 0.95 + abs(__import__('math').sin(self._angle * 0.1)) * 0.1
        elif self.state == 'speaking':
            self._scale = 0.97 + abs(__import__('math').sin(self._angle * 0.2)) * 0.08
        else:
            self._scale = 1.0 + __import__('math').sin(self._angle * 0.05) * 0.02
        self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y
        r = min(self.width, self.height) / 2 * self._scale
        with self.canvas:
            # Outer rings
            Color(1, 1, 1, 0.15)
            Line(circle=(cx, cy, r + dp(14)), width=dp(1.5))
            Color(1, 1, 1, 0.25)
            Line(circle=(cx, cy, r + dp(7)), width=dp(1.5))
            # Glow
            if self.state == 'thinking':
                Color(0.1, 0.5, 0.8, 0.3)
            elif self.state == 'speaking':
                Color(0.2, 0.8, 0.4, 0.3)
            else:
                Color(1, 1, 1, 0.15)
            Ellipse(pos=(cx - r - dp(4), cy - r - dp(4)),
                    size=(r * 2 + dp(8), r * 2 + dp(8)))
            # Main orb
            Color(0.85, 0.95, 1.0, 1)
            Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))
            # Shine
            Color(1, 1, 1, 0.6)
            shine_r = r * 0.4
            Ellipse(pos=(cx - r * 0.55, cy + r * 0.15),
                    size=(shine_r, shine_r * 0.7))


class ToggleCard(Button):
    """A device toggle button card."""

    def __init__(self, icon, label, on_cmd, off_cmd, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.label_text = label
        self.on_cmd = on_cmd
        self.off_cmd = off_cmd
        self.is_on = False
        self.background_color = (0, 0, 0, 0)
        self.text = f"{icon}\n{label}"
        self.font_size = dp(11)
        self.color = (1, 1, 1, 0.9)
        self.halign = 'center'
        self.bind(on_press=self._toggle)
        self._draw_bg()

    def _toggle(self, *args):
        self.is_on = not self.is_on
        self._draw_bg()

    def _draw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_on:
                Color(1, 1, 1, 0.55)
            else:
                Color(1, 1, 1, 0.2)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )

    def get_command(self):
        return self.on_cmd if self.is_on else self.off_cmd


class ChatBubble(AnchorLayout):
    """A single chat message bubble."""

    def __init__(self, text, is_user=False, **kwargs):
        anchor = 'right' if is_user else 'left'
        super().__init__(anchor_x=anchor, size_hint_y=None, **kwargs)
        self.padding = [dp(8), dp(4)]

        lbl = Label(
            text=text,
            font_size=dp(13),
            color=TEXT_DARK,
            size_hint=(None, None),
            text_size=(Window.width * 0.68, None),
            halign='right' if is_user else 'left',
            valign='top',
            markup=True,
            padding=(dp(10), dp(8)),
        )
        lbl.bind(texture_size=lambda i, v: setattr(i, 'size', v))
        lbl.bind(size=lambda i, v: setattr(self, 'height', v[1] + dp(20)))

        with lbl.canvas.before:
            if is_user:
                Color(1, 1, 1, 0.88)
            else:
                Color(0.86, 0.96, 1.0, 0.9)
            lbl._rect = RoundedRectangle(
                pos=lbl.pos,
                size=lbl.size,
                radius=[dp(12)]
            )
        lbl.bind(pos=lambda i, v: setattr(i._rect, 'pos', v))
        lbl.bind(size=lambda i, v: setattr(i._rect, 'size', v))

        self.add_widget(lbl)


class AtlasApp(App):

    def build(self):
        Window.clearcolor = SKY_TOP
        self.title = 'Atlas AI'
        self._last_reply = ''
        self._is_speaking = False

        # Request permissions on Android
        try:
            request_permissions([
                Permission.INTERNET,
                Permission.RECORD_AUDIO,
                Permission.CHANGE_WIFI_STATE,
                Permission.ACCESS_WIFI_STATE,
                Permission.BLUETOOTH,
                Permission.BLUETOOTH_ADMIN,
                Permission.CAMERA,
                Permission.WRITE_SETTINGS,
                Permission.VIBRATE,
            ])
        except Exception:
            pass

        root = FloatLayout()

        # ── Background ──────────────────────────────────
        self.bg = GhibliBackground(size_hint=(1, 1), pos=(0, 0))
        root.add_widget(self.bg)

        # ── Main content ─────────────────────────────────
        self.main = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=[dp(12), dp(30), dp(12), dp(12)],
            spacing=dp(6),
        )
        root.add_widget(self.main)

        # Header
        self._build_header()

        # Orb
        self._build_orb()

        # Device toggles
        self._build_toggles()

        # Quick chips
        self._build_chips()

        # Chat area
        self._build_chat()

        # Input
        self._build_input()

        return root

    def _build_header(self):
        hdr = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )

        logo_lbl = Label(
            text='🌊  ATLAS',
            font_size=dp(16),
            bold=True,
            color=WHITE,
            size_hint_x=0.5,
            halign='left',
        )

        self.wake_btn = Button(
            text='🎙 Hey Atlas',
            font_size=dp(11),
            size_hint_x=0.3,
            background_color=(0, 0, 0, 0),
            color=WHITE,
        )
        with self.wake_btn.canvas.before:
            Color(1, 1, 1, 0.22)
            self._wake_rect = RoundedRectangle(
                pos=self.wake_btn.pos,
                size=self.wake_btn.size,
                radius=[dp(12)]
            )
        self.wake_btn.bind(
            pos=lambda i, v: setattr(self._wake_rect, 'pos', v),
            size=lambda i, v: setattr(self._wake_rect, 'size', v),
            on_press=self._toggle_wake
        )

        hdr.add_widget(logo_lbl)
        hdr.add_widget(Widget())
        hdr.add_widget(self.wake_btn)
        self.main.add_widget(hdr)

    def _build_orb(self):
        orb_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(110),
            spacing=dp(4),
        )

        self.orb = AtlasOrb(size_hint=(None, None), size=(dp(80), dp(80)))
        orb_anchor = AnchorLayout(anchor_x='center', size_hint_y=None, height=dp(90))
        orb_anchor.add_widget(self.orb)

        self.orb_label = Label(
            text='Ready to help you ✨',
            font_size=dp(11),
            color=(1, 1, 1, 0.9),
            size_hint_y=None,
            height=dp(18),
            halign='center',
        )

        orb_section.add_widget(orb_anchor)
        orb_section.add_widget(self.orb_label)
        self.main.add_widget(orb_section)

    def _build_toggles(self):
        grid = GridLayout(
            cols=4,
            size_hint_y=None,
            height=dp(90),
            spacing=dp(5),
        )

        self.toggles = [
            ToggleCard('📶', 'WiFi',      'turn on wifi',      'turn off wifi'),
            ToggleCard('🔵', 'Bluetooth', 'turn on bluetooth', 'turn off bluetooth'),
            ToggleCard('🔆', 'Bright',    'brightness 80',     'brightness 30'),
            ToggleCard('🔦', 'Torch',     'turn on flashlight','turn off flashlight'),
            ToggleCard('🔕', 'DND',       'turn on dnd',       'turn off dnd'),
            ToggleCard('🔄', 'Rotate',    'turn on auto rotate','turn off auto rotate'),
            ToggleCard('✈️', 'Airplane',  'turn on airplane mode','turn off airplane mode'),
            ToggleCard('🔔', 'Notif',     '',                  ''),
        ]

        for tog in self.toggles:
            tog.bind(on_press=lambda instance: self._handle_toggle(instance))
            grid.add_widget(tog)

        self.main.add_widget(grid)

    def _handle_toggle(self, tog):
        if tog.get_command():
            threading.Thread(
                target=self._process_command,
                args=(tog.get_command(),),
                daemon=True
            ).start()

    def _build_chips(self):
        chips_row = BoxLayout(
            size_hint_y=None,
            height=dp(30),
            spacing=dp(5),
        )

        chip_cmds = [
            ('▶ YouTube', 'open youtube'),
            ('🔍 Google',  'search google for'),
            ('🕐 Time',    'what time is it'),
            ('🔋 Battery', 'battery level'),
            ('💬 WhatsApp','open whatsapp'),
        ]

        for label, cmd in chip_cmds:
            btn = Button(
                text=label,
                font_size=dp(9),
                background_color=(0, 0, 0, 0),
                color=WHITE,
            )
            with btn.canvas.before:
                Color(1, 1, 1, 0.22)
                _r = RoundedRectangle(
                    pos=btn.pos,
                    size=btn.size,
                    radius=[dp(12)]
                )
            btn.bind(
                pos=lambda i, v, r=_r: setattr(r, 'pos', v),
                size=lambda i, v, r=_r: setattr(r, 'size', v),
            )
            btn.bind(on_press=lambda instance, c=cmd: self._quick_cmd(c))
            chips_row.add_widget(btn)

        self.main.add_widget(chips_row)

    def _build_chat(self):
        self.scroll = ScrollView(size_hint=(1, 1))
        self.chat_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(6),
            padding=[0, dp(4)],
        )
        self.chat_layout.bind(
            minimum_height=self.chat_layout.setter('height')
        )
        self.scroll.add_widget(self.chat_layout)
        self.main.add_widget(self.scroll)

        # Welcome message
        self._add_bubble("Hello! I'm Atlas 🌊 Ask me anything or tap a toggle!", is_user=False)

    def _build_input(self):
        inp_row = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(6),
        )

        with inp_row.canvas.before:
            Color(1, 1, 1, 0.88)
            self._inp_rect = RoundedRectangle(
                pos=inp_row.pos,
                size=inp_row.size,
                radius=[dp(25)]
            )
        inp_row.bind(
            pos=lambda i, v: setattr(self._inp_rect, 'pos', v),
            size=lambda i, v: setattr(self._inp_rect, 'size', v),
        )

        self.text_input = TextInput(
            hint_text='Ask Atlas anything...',
            hint_text_color=get_color_from_hex('#8aacbe'),
            multiline=False,
            font_size=dp(13),
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT_DARK,
            cursor_color=get_color_from_hex('#1a7faa'),
            padding=[dp(12), dp(12)],
        )
        self.text_input.bind(on_text_validate=self._on_send)

        # Wind spirit toggle button
        self.speak_btn = Button(
            text='🌬',
            font_size=dp(18),
            size_hint=(None, None),
            size=(dp(42), dp(42)),
            background_color=(0, 0, 0, 0),
        )
        with self.speak_btn.canvas.before:
            Color(0.91, 0.96, 1.0, 1)
            self._speak_rect = RoundedRectangle(
                pos=self.speak_btn.pos,
                size=self.speak_btn.size,
                radius=[dp(21)]
            )
        self.speak_btn.bind(
            pos=lambda i, v: setattr(self._speak_rect, 'pos', v),
            size=lambda i, v: setattr(self._speak_rect, 'size', v),
            on_press=self._toggle_speak,
        )

        mic_btn = Button(
            text='🎤',
            font_size=dp(18),
            size_hint=(None, None),
            size=(dp(42), dp(42)),
            background_color=(0, 0, 0, 0),
        )
        with mic_btn.canvas.before:
            Color(0.72, 0.89, 0.97, 1)
            self._mic_rect = RoundedRectangle(
                pos=mic_btn.pos,
                size=mic_btn.size,
                radius=[dp(21)]
            )
        mic_btn.bind(
            pos=lambda i, v: setattr(self._mic_rect, 'pos', v),
            size=lambda i, v: setattr(self._mic_rect, 'size', v),
            on_press=self._start_stt,
        )

        send_btn = Button(
            text='➤',
            font_size=dp(16),
            size_hint=(None, None),
            size=(dp(42), dp(42)),
            background_color=(0, 0, 0, 0),
            color=WHITE,
        )
        with send_btn.canvas.before:
            Color(0.29, 0.70, 0.91, 1)
            self._send_rect = RoundedRectangle(
                pos=send_btn.pos,
                size=send_btn.size,
                radius=[dp(21)]
            )
        send_btn.bind(
            pos=lambda i, v: setattr(self._send_rect, 'pos', v),
            size=lambda i, v: setattr(self._send_rect, 'size', v),
            on_press=self._on_send,
        )

        inp_row.add_widget(self.text_input)
        inp_row.add_widget(self.speak_btn)
        inp_row.add_widget(mic_btn)
        inp_row.add_widget(send_btn)
        self.main.add_widget(inp_row)

    # ── Chat helpers ──────────────────────────────────────
    def _add_bubble(self, text, is_user=False):
        bubble = ChatBubble(text=text, is_user=is_user)
        self.chat_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.15)

    def _set_orb(self, state, label):
        self.orb.set_state(state)
        self.orb_label.text = label

    # ── Command processing ────────────────────────────────
    def _on_send(self, *args):
        msg = self.text_input.text.strip()
        if not msg:
            return
        self.text_input.text = ''
        self._add_bubble(msg, is_user=True)
        self._set_orb('thinking', 'Thinking... 💭')
        threading.Thread(
            target=self._process_command,
            args=(msg,),
            daemon=True
        ).start()

    def _quick_cmd(self, cmd):
        self._add_bubble(cmd, is_user=True)
        self._set_orb('thinking', 'Thinking... 💭')
        threading.Thread(
            target=self._process_command,
            args=(cmd,),
            daemon=True
        ).start()

    def _process_command(self, command):
        reply = handle_command(command)
        self._last_reply = reply
        Clock.schedule_once(lambda dt: self._show_reply(reply), 0)

    def _show_reply(self, reply):
        self._add_bubble(reply, is_user=False)
        self._set_orb('idle', 'Ready to help you ✨')

    # ── TTS toggle ────────────────────────────────────────
    def _toggle_speak(self, *args):
        if not self._last_reply:
            self._set_orb('idle', 'Ask me something first! 🌸')
            return

        if self._is_speaking:
            # Stop speaking
            self._is_speaking = False
            self.speak_btn.text = '🌬'
            with self.speak_btn.canvas.before:
                Color(0.91, 0.96, 1.0, 1)
                RoundedRectangle(
                    pos=self.speak_btn.pos,
                    size=self.speak_btn.size,
                    radius=[dp(21)]
                )
            self._set_orb('idle', 'Ready to help you ✨')
            try:
                plyer_tts.speak('')
            except Exception:
                pass
        else:
            # Start speaking
            self._is_speaking = True
            self.speak_btn.text = '💚'
            with self.speak_btn.canvas.before:
                Color(0.38, 0.78, 0.5, 1)
                RoundedRectangle(
                    pos=self.speak_btn.pos,
                    size=self.speak_btn.size,
                    radius=[dp(21)]
                )
            self._set_orb('speaking', 'Speaking... 🔊')
            threading.Thread(target=self._speak_reply, daemon=True).start()

    def _speak_reply(self):
        clean = ''.join(c for c in self._last_reply if ord(c) < 10000)
        try:
            if TTS_AVAILABLE:
                plyer_tts.speak(clean)
        except Exception:
            pass
        Clock.schedule_once(lambda dt: self._done_speaking(), 0)

    def _done_speaking(self):
        self._is_speaking = False
        self.speak_btn.text = '🌬'
        self._set_orb('idle', 'Ready to help you ✨')

    # ── STT ───────────────────────────────────────────────
    def _start_stt(self, *args):
        if not STT_AVAILABLE:
            self._add_bubble("Voice input not available on this device", is_user=False)
            return
        self._set_orb('thinking', '🎤 Listening...')
        threading.Thread(target=self._do_stt, daemon=True).start()

    def _do_stt(self):
        try:
            stt.start()
            import time
            time.sleep(3)
            stt.stop()
            result = stt.last_result()
            if result:
                Clock.schedule_once(
                    lambda dt: self._on_stt_result(result), 0
                )
            else:
                Clock.schedule_once(
                    lambda dt: self._set_orb('idle', "Didn't catch that, try again"), 0
                )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self._set_orb('idle', f'STT error: {e}'), 0
            )

    def _on_stt_result(self, result):
        self._set_orb('idle', 'Ready to help you ✨')
        self._add_bubble(result, is_user=True)
        self._set_orb('thinking', 'Thinking... 💭')
        threading.Thread(
            target=self._process_command,
            args=(result,),
            daemon=True
        ).start()

    # ── Wake word toggle ──────────────────────────────────
    def _toggle_wake(self, *args):
        self._add_bubble(
            'Wake word feature coming soon! Use the mic button for now 🎤',
            is_user=False
        )


if __name__ == '__main__':
    AtlasApp().run()
