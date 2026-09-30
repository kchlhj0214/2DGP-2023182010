"""렌더링과 독립된 경과 시간 기반 애니메이션 재생 상태."""
import math


class Player:
    def __init__(self, animations):
        if not animations:
            raise ValueError("재생할 애니메이션이 없습니다.")
        self.animations = animations
        self.animation_index = 0
        self.frame_index = 0
        self.elapsed = 0.0

    @property
    def animation(self):
        return self.animations[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, dt):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("경과 시간은 유한한 0 이상의 값이어야 합니다.")
        self.elapsed += dt
        duration = 1.0 / self.animation.fps
        while self.elapsed + 1e-12 >= duration:
            self.elapsed = max(0.0, self.elapsed - duration)
            self.frame_index = (self.frame_index + 1) % len(self.animation.frames)
