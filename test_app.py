import importlib
import os
import types
import unittest
from unittest.mock import patch

import numpy as np

from airmouse.hand_tracker import HandTracker


class HeadlessQtStartupTests(unittest.TestCase):
    def test_main_window_defaults_to_offscreen_when_no_display_is_available(self):
        with patch.dict(
            os.environ,
            {"DISPLAY": "", "WAYLAND_DISPLAY": "", "QT_QPA_PLATFORM": "", "CI": "1"},
            clear=False,
        ):
            import airmouse.main_window as main_window

            importlib.reload(main_window)
            self.assertEqual(os.environ.get("QT_QPA_PLATFORM"), "offscreen")

    def test_pointer_and_click_helpers(self):
        hand = [
            types.SimpleNamespace(x=0.5, y=0.5),
            *[
                types.SimpleNamespace(x=0.5 + (i * 0.01), y=0.5 + (i * 0.01))
                for i in range(1, 21)
            ],
        ]
        hand[4] = types.SimpleNamespace(x=0.7, y=0.7)
        hand[8] = types.SimpleNamespace(x=0.75, y=0.75)

        pointer = HandTracker._pointer_from_hand(hand, 100, 100)
        self.assertEqual(pointer, (75, 75))
        self.assertTrue(HandTracker._is_pinching(hand))

    def test_open_hand_requires_all_fingers_extended(self):
        hand = [
            types.SimpleNamespace(x=0.0, y=0.0)
            for _ in range(21)
        ]
        for tip, joint, x in (
            (4, 3, 0.4),
            (8, 6, 0.5),
            (12, 10, 0.6),
            (16, 14, 0.7),
            (20, 18, 0.8),
        ):
            hand[joint] = types.SimpleNamespace(x=x / 2, y=0.0)
            hand[tip] = types.SimpleNamespace(x=x, y=0.0)

        self.assertTrue(HandTracker._is_open_hand(hand))

        hand[20] = types.SimpleNamespace(x=0.1, y=0.0)
        self.assertFalse(HandTracker._is_open_hand(hand))

    def test_four_finger_pose_requires_thumb_to_be_folded(self):
        hand = [
            types.SimpleNamespace(x=0.0, y=0.0)
            for _ in range(21)
        ]
        hand[3] = types.SimpleNamespace(x=0.2, y=0.0)
        hand[4] = types.SimpleNamespace(x=0.1, y=0.0)
        for tip, joint, x in (
            (8, 6, 0.5),
            (12, 10, 0.6),
            (16, 14, 0.7),
            (20, 18, 0.8),
        ):
            hand[joint] = types.SimpleNamespace(x=x / 2, y=0.0)
            hand[tip] = types.SimpleNamespace(x=x, y=0.0)

        self.assertTrue(HandTracker._is_four_finger_swipe_pose(hand))

        hand[4] = types.SimpleNamespace(x=0.4, y=0.0)
        self.assertFalse(HandTracker._is_four_finger_swipe_pose(hand))

    def test_four_finger_swipes_navigate_slides_once(self):
        tracker = HandTracker.__new__(HandTracker)
        tracker._swipe_positions = {}
        tracker._swipe_latched = set()

        def make_hand(index_mcp_x):
            hand = [
                types.SimpleNamespace(x=0.0, y=0.0)
                for _ in range(21)
            ]
            hand[3] = types.SimpleNamespace(x=0.2, y=0.0)
            hand[4] = types.SimpleNamespace(x=0.1, y=0.0)
            for tip, joint, x in (
                (8, 6, 0.5),
                (12, 10, 0.6),
                (16, 14, 0.7),
                (20, 18, 0.8),
            ):
                hand[joint] = types.SimpleNamespace(x=x / 2, y=0.0)
                hand[tip] = types.SimpleNamespace(x=x, y=0.0)
            hand[9] = types.SimpleNamespace(x=index_mcp_x, y=0.0)
            return hand

        with patch("airmouse.hand_tracker.pyautogui.press") as press:
            self.assertIsNone(
                tracker._update_slide_swipe(make_hand(0.7), "Right", 1.0)
            )
            self.assertEqual(
                tracker._update_slide_swipe(make_hand(0.45), "Right", 1.3),
                "right",
            )
            self.assertIsNone(
                tracker._update_slide_swipe(make_hand(0.2), "Right", 1.4)
            )

            self.assertIsNone(
                tracker._update_slide_swipe(make_hand(0.3), "Left", 2.0)
            )
            self.assertEqual(
                tracker._update_slide_swipe(make_hand(0.55), "Left", 2.3),
                "left",
            )

        self.assertEqual([call.args for call in press.call_args_list], [("right",), ("left",)])

    def test_open_hand_moves_pointer(self):
        hand = [
            types.SimpleNamespace(x=0.0, y=0.0)
            for _ in range(21)
        ]
        for tip, joint, x in (
            (4, 3, 0.4),
            (8, 6, 0.5),
            (12, 10, 0.6),
            (16, 14, 0.7),
            (20, 18, 0.8),
        ):
            hand[joint] = types.SimpleNamespace(x=x / 2, y=0.0)
            hand[tip] = types.SimpleNamespace(x=x, y=0.0)

        tracker = HandTracker.__new__(HandTracker)
        tracker._last_timestamp_ms = 0
        tracker._landmarker = types.SimpleNamespace(
            detect_for_video=lambda *_: types.SimpleNamespace(
                hand_landmarks=[hand],
                handedness=[[types.SimpleNamespace(category_name="Right")]],
            )
        )
        tracker._connections = ()
        tracker._last_click_time = 0.0
        tracker._smoothed_cursor = None
        tracker._zoom_anchor_span = None
        tracker._swipe_positions = {}
        tracker._swipe_latched = set()
        tracker._screen_width = 1920
        tracker._screen_height = 1080

        with patch("airmouse.hand_tracker.pyautogui.moveTo") as move_to:
            _, hand_detected, pointer = tracker.process(
                np.zeros((100, 100, 3), dtype=np.uint8)
            )

        self.assertTrue(hand_detected)
        self.assertEqual(pointer, (50, 0))
        move_to.assert_called_once()

    def test_two_hand_span_changes_zoom_in_and_out(self):
        tracker = HandTracker.__new__(HandTracker)
        tracker._zoom_anchor_span = 0.3

        def make_hand(wrist_x):
            return [
                types.SimpleNamespace(x=wrist_x, y=0.0)
                for _ in range(21)
            ]

        with (
            patch("airmouse.hand_tracker.pyautogui.keyDown") as key_down,
            patch("airmouse.hand_tracker.pyautogui.scroll") as scroll,
            patch("airmouse.hand_tracker.pyautogui.keyUp") as key_up,
        ):
            self.assertEqual(
                tracker._update_two_hand_zoom([make_hand(0), make_hand(0.35)]),
                1,
            )
            self.assertEqual(
                tracker._update_two_hand_zoom([make_hand(0), make_hand(0.28)]),
                -1,
            )

        self.assertEqual([call.args for call in scroll.call_args_list], [(1,), (-1,)])
        self.assertEqual(key_down.call_count, 2)
        self.assertEqual(key_up.call_count, 2)

    def test_cursor_move_handles_display_missing(self):
        tracker = HandTracker.__new__(HandTracker)
        tracker._screen_width = 1920
        tracker._screen_height = 1080
        tracker._smoothed_cursor = None

        with patch("airmouse.hand_tracker.pyautogui.moveTo"):
            tracker._move_cursor((100, 200), 400, 400)
            self.assertIsNotNone(tracker._smoothed_cursor)


if __name__ == "__main__":
    unittest.main()
