import time

import pyxel
from pyxel.constants import AUDIO_SOUND_COUNT, SOUND_MAX_LENGTH
from pyxel.ui import ImageButton, NumberPicker
from pyxel.ui.constants import WIDGET_HOLD_TIME, WIDGET_REPEAT_TIME

from .constants import EDITOR_IMAGE_X, EDITOR_IMAGE_Y
from .editor import Editor
from .octave_bar import OctaveBar
from .piano_keyboard import PianoKeyboard
from .piano_roll import PianoRoll
from .sound_input import SoundInput


class SoundEditor(Editor):
    class PlayInfo:
        is_playing = False
        is_looping = False
        start_time = 0
        speed = 0
        length = 0

    def __init__(self, parent):
        super().__init__(parent)

        self.cursor_x = 0
        self.cursor_y = 0
        self.octave = 2
        self._play_info = SoundEditor.PlayInfo()

        self._sound_picker = NumberPicker(self, 45, 17, 0, AUDIO_SOUND_COUNT - 1, 0)
        self._speed_picker = NumberPicker(self, 105, 17, 1, 99, pyxel.sound(0).speed)

        self._play_button = ImageButton(
            self, 185, 17, 3, EDITOR_IMAGE_X + 126, EDITOR_IMAGE_Y
        )
        self._stop_button = ImageButton(
            self, 195, 17, 3, EDITOR_IMAGE_X + 135, EDITOR_IMAGE_Y, is_enabled=False
        )
        self._loop_button = ImageButton(
            self, 205, 17, 3, EDITOR_IMAGE_X + 144, EDITOR_IMAGE_Y
        )

        self._piano_keyboard = PianoKeyboard(self)
        self._piano_roll = PianoRoll(self)
        self._sound_input = SoundInput(self)

        self._left_octave_bar = OctaveBar(self, 12, 25)
        self._right_octave_bar = OctaveBar(self, 224, 25)

        self.add_event_handler("update", self.__on_update)
        self.add_event_handler("draw", self.__on_draw)
        self._sound_picker.add_event_handler("change", self.__on_sound_change)
        self._speed_picker.add_event_handler("change", self.__on_speed_change)
        self._play_button.add_event_handler("press", self.__on_play_press)
        self._stop_button.add_event_handler("press", self.__on_stop_press)

    @property
    def sound(self):
        return self._sound_picker.value

    @property
    def speed(self):
        return self._speed_picker.value

    @property
    def sound_data(self):
        sound = pyxel.sound(self._sound_picker.value)

        if self.cursor_y == 0:
            data = sound.note
        elif self.cursor_y == 1:
            data = sound.tone
        elif self.cursor_y == 2:
            data = sound.volume
        elif self.cursor_y == 3:
            data = sound.effect

        return data

    @property
    def max_edit_x(self):
        return min(len(self.sound_data), SOUND_MAX_LENGTH - 1)

    @property
    def edit_x(self):
        return min(self.cursor_x, self.max_edit_x)

    @property
    def keyboard_note(self):
        return self._piano_keyboard.note

    @property
    def play_pos(self):
        play_info = self._play_info

        if not play_info.is_playing:
            return -1

        pos = int((time.time() - play_info.start_time) * 120 / play_info.speed)

        if play_info.is_looping:
            pos = pos % play_info.length
        elif pos >= play_info.length:
            pos = -1

        return pos

    def _play(self):
        pyxel.play(0, self._sound_picker.value)

        self._play_button.is_enabled = False
        self._stop_button.is_enabled = True
        self._loop_button.is_enabled = False

        sound = pyxel.sound(self._sound_picker.value)

        play_info = self._play_info
        play_info.is_playing = True
        play_info.is_looping = False
        play_info.start_time = time.time()
        play_info.speed = sound.speed
        play_info.length = len(sound.note)

    def _stop(self):
        pyxel.stop(0)

        self._play_button.is_enabled = True
        self._stop_button.is_enabled = False
        self._loop_button.is_enabled = True

        play_info = self._play_info
        play_info.is_playing = False

    def __on_update(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self._play_info.is_playing:
                self._stop_button.press()
            else:
                self._play_button.press()

        if self._play_info.is_playing and self.play_pos < 0:
            self._stop()

        if self._play_info.is_playing:
            return

        if self.cursor_x > 0 and pyxel.btnp(
            pyxel.KEY_LEFT, WIDGET_HOLD_TIME, WIDGET_REPEAT_TIME
        ):
            self.cursor_x = self.edit_x - 1

        if self.cursor_x < self.max_edit_x and pyxel.btnp(
            pyxel.KEY_RIGHT, WIDGET_HOLD_TIME, WIDGET_REPEAT_TIME
        ):
            self.cursor_x += 1

        if self.cursor_y > 0 and pyxel.btnp(
            pyxel.KEY_UP, WIDGET_HOLD_TIME, WIDGET_REPEAT_TIME
        ):
            self.cursor_y -= 1

        if self.cursor_y < 3 and pyxel.btnp(
            pyxel.KEY_DOWN, WIDGET_HOLD_TIME, WIDGET_REPEAT_TIME
        ):
            self.cursor_y += 1

    def __on_draw(self):
        self.draw_frame(11, 16, 218, 157)
        pyxel.text(23, 18, "SOUND", 6)
        pyxel.text(83, 18, "SPEED", 6)
        pyxel.text(17, 150, "TON", 6)
        pyxel.text(17, 158, "VOL", 6)
        pyxel.text(17, 166, "EFX", 6)

    def __on_sound_change(self, value):
        sound = pyxel.sound(value)
        self._speed_picker.value = sound.speed

    def __on_speed_change(self, value):
        sound = pyxel.sound(self._sound_picker.value)
        sound.speed = value

    def __on_play_press(self):
        self._play()

    def __on_stop_press(self):
        self._stop()
