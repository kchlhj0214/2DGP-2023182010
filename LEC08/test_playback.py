"""창을 열지 않고 실제 과제 데이터로 재생 경계를 검증한다."""
import unittest

from animation_data import load_animations
from playback import Player, PAUSE_SECONDS, REPEAT_COUNT


class PlaybackTests(unittest.TestCase):
    def setUp(self):
        self.animations = load_animations()[2]
        self.player = Player(self.animations)

    def test_every_frame_appears_exactly_five_times(self):
        for index, animation in enumerate(self.animations):
            visits = [0] * len(animation.frames)
            while not self.player.finished:
                visits[self.player.frame_index] += 1
                self.player.update(1 / animation.fps)
            self.assertEqual(visits, [5] * len(visits))
            self.assertEqual(self.player.completed_loops, 5)
            self.assertEqual(self.player.frame_index, len(visits) - 1)
            self.player.update(0.999)
            self.assertEqual(self.player.animation_index, index)
            self.assertTrue(self.player.finished)
            self.player.update(0.001)
            self.assertEqual(self.player.animation_index, (index + 1) % len(self.animations))
            self.assertEqual(self.player.frame_index, 0)
            self.assertFalse(self.player.finished)
        self.assertEqual(self.player.completed_cycles, 1)

    def test_last_frame_gets_its_full_duration(self):
        duration = 1 / self.player.animation.fps
        self.player.update(duration * (len(self.player.animation.frames) * 5 - 1))
        self.assertFalse(self.player.finished)
        self.player.update(duration - 0.0001)
        self.assertFalse(self.player.finished)
        self.player.update(0.0001)
        self.assertTrue(self.player.finished)

    def test_large_update_preserves_time_across_cycles(self):
        cycle = sum(len(a.frames) / a.fps * REPEAT_COUNT + PAUSE_SECONDS for a in self.animations)
        self.player.update(cycle * 3 + 0.125)
        self.assertEqual(self.player.completed_cycles, 3)
        self.assertEqual(self.player.animation_index, 0)
        self.assertEqual(self.player.frame_index, 0)
        self.assertAlmostEqual(self.player.elapsed, 0.125)

    def test_partitioned_updates_match_one_update(self):
        other = Player(self.animations)
        for _ in range(4000):
            self.player.update(0.017)
        other.update(68)
        for attr in ("animation_index", "frame_index", "completed_loops", "finished", "completed_cycles"):
            self.assertEqual(getattr(self.player, attr), getattr(other, attr))
        self.assertAlmostEqual(self.player.elapsed, other.elapsed)

    def test_invalid_time_and_empty_playlist(self):
        for dt in (-1, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                self.player.update(dt)
        with self.assertRaises(ValueError):
            Player(())


if __name__ == "__main__":
    unittest.main()
