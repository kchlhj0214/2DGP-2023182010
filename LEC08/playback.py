"""렌더링과 독립된 경과 시간 기반 애니메이션 재생 상태."""
import math

REPEAT_COUNT = 5
PAUSE_SECONDS = 1.0


class Player:
    def __init__(self, animations):
        if not animations:
            raise ValueError("재생할 애니메이션이 없습니다.")
        self.animations = animations
        self.animation_index = 0
        self.frame_index = 0
        self.elapsed = 0.0
        self.completed_loops = 0
        self.finished = False
        self.completed_cycles = 0

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
        while True:
            duration = PAUSE_SECONDS if self.finished else 1.0 / self.animation.fps
            if self.elapsed + 1e-12 < duration:
                break
            self.elapsed = max(0.0, self.elapsed - duration)
            if self.finished:
                self.animation_index = (self.animation_index + 1) % len(self.animations)
                if self.animation_index == 0:
                    self.completed_cycles += 1
                self.frame_index = 0
                self.completed_loops = 0
                self.finished = False
            elif self.frame_index + 1 < len(self.animation.frames):
                self.frame_index += 1
            else:
                self.completed_loops += 1
                if self.completed_loops == REPEAT_COUNT:
                    self.finished = True
                else:
                    self.frame_index = 0
