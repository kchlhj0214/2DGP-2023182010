"""시트 잘림, 가변 프레임, 화면 밖 출력 및 데이터 오류를 검사한다."""
from dataclasses import replace
import unittest

from PIL import Image

from animation_data import ASSETS, load_animations, validate
from animation_viewer import WIDTH, HEIGHT, frame_destination
from build_atlas import SPECS


class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.path, self.size, self.animations = load_animations()

    def test_all_pixels_preserved_from_original(self):
        with Image.open(self.path) as atlas:
            self.assertEqual(atlas.size, self.size)
            for animation, spec in zip(self.animations, SPECS):
                with Image.open(ASSETS / "source" / f"{animation.name}.png") as image:
                    source = image.convert("RGBA")
                for frame, region in zip(animation.frames, spec[3]):
                    original = source.crop(region)
                    x, y, w, h = frame.rect
                    actual = atlas.crop((x, y, x + w, y + h))
                    expected = original.crop(original.getbbox())
                    self.assertEqual(actual.size, expected.size)
                    self.assertEqual(actual.tobytes(), expected.tobytes())

    def test_bonus_conditions_and_sword_overflow(self):
        self.assertEqual([len(a.frames) for a in self.animations], [2, 8, 4, 5])
        sizes = {f.rect[2:] for a in self.animations for f in a.frames}
        self.assertGreater(len(sizes), 4)
        # 공격 두 번째 칸의 칼 이펙트가 원본 64px 폭을 넘는 부분까지 보존된다.
        self.assertGreater(self.animations[3].frames[1].rect[2], 64)

    def test_every_frame_is_large_and_inside_stage(self):
        for animation in self.animations:
            for frame in animation.frames:
                x, y, w, h = frame_destination(frame)
                self.assertGreaterEqual(h, HEIGHT / 2)
                self.assertGreaterEqual(x - w / 2, 0)
                self.assertLessEqual(x + w / 2, WIDTH)
                self.assertGreaterEqual(y - h / 2, 120)
                self.assertLessEqual(y + h / 2, 515)

    def test_reject_out_of_bounds_empty_and_invalid_fps(self):
        animation = self.animations[0]
        bad_frame = replace(animation.frames[0], rect=(0, 0, 999, 999))
        for bad in (replace(animation, frames=(bad_frame,)),
                    replace(animation, frames=()), replace(animation, fps=0)):
            with self.assertRaises(ValueError):
                validate(self.size, (bad,))


if __name__ == "__main__":
    unittest.main()
