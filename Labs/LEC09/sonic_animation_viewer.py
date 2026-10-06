"""소닉 스프라이트 애니메이션 뷰어.

시트 조사 (좌상단 원점, 위에서 아래 순서):
  1행: 대기 9장, 웅크리기 2장
  2행: 걷기 12장
  3행: 달리기 6장
  4행: 회전 9장 / 5행: 회전 공 6장
  6행: 빠른 달리기 6장 / 7행: 전력 질주 6장
  8행: 방향 전환 6장, 피격 2장
  9행: 제동 8장
 10행: 낙하 2장, 균형 잡기 2장

실행: Python 3.10 이상 + pico2d 설치 후
  저장소 루트: python Labs/LEC09/sonic_animation_viewer.py
  이 폴더:     python sonic_animation_viewer.py
창 닫기 또는 ESC로 종료. 창 크기와 배율은 아래 상수에서 변경한다.
걷기·달리기·회전은 자동으로 좌우 이동하고, 제동은 서서히 감속한다.
화면 가장자리에서 방향을 바꾸며 동작 사이의 1초 정지에는 위치도 유지한다.

총 13동작, 76프레임. 이름은 포즈에 따른 뷰어용 분류다.
1행은 연속된 대기 포즈와 마지막의 낮은 포즈를 분리한다.
8·10행은 서로 다른 포즈 흐름을 각각 두 동작으로 분리한다.
제목, 크레딧, 하단의 노란색·갈색 별도 캐릭터는 제외한다.
"""

from dataclasses import dataclass
from pathlib import Path
from math import isfinite
from time import perf_counter

import pico2d

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800
SCALE = 8
GROUND_Y = WINDOW_HEIGHT / 2 - 140
EDGE_MARGIN = 32
REPEAT_COUNT = 5
PAUSE_SECONDS = 1.0
DEFAULT_FRAME_SECONDS = 0.1
TARGET_FPS = 60
PLAYING = 'PLAYING'
PAUSING = 'PAUSING'


@dataclass(frozen=True)
class Frame:
    # 이미지 좌상단 원점, 오른쪽으로 x 증가, 아래로 y 증가.
    x: int
    y: int
    width: int
    height: int
    anchor_x: float | None = None
    anchor_y: float | None = None

    @property
    def anchor(self):
        # 좌상단 기준. 기본은 발 중앙이며 필요한 포즈는 따로 보정한다.
        return (self.width / 2 if self.anchor_x is None else self.anchor_x,
                self.height if self.anchor_y is None else self.anchor_y)


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    frame_seconds: float = DEFAULT_FRAME_SECONDS
    move_speed: float = 0.0  # 화면 픽셀/초. 0이면 현재 위치에서 재생한다.
    decelerate: bool = False


ANIMATIONS = (
    Animation('idle', (
        Frame(1, 39, 29, 39), Frame(31, 40, 26, 38),
        Frame(58, 39, 28, 39), Frame(86, 40, 30, 38),
        Frame(118, 40, 30, 38), Frame(150, 40, 30, 38),
        Frame(182, 40, 29, 38), Frame(211, 39, 29, 38),
        Frame(240, 39, 29, 38),
    )),
    Animation('crouch', (
        Frame(270, 45, 24, 32), Frame(302, 51, 29, 26),
    )),
    Animation('walk', (
        Frame(8, 80, 26, 37), Frame(37, 80, 27, 37),
        Frame(65, 80, 31, 38), Frame(97, 80, 37, 37),
        Frame(135, 80, 32, 35), Frame(170, 79, 32, 38),
        Frame(206, 79, 26, 38), Frame(238, 80, 24, 37),
        Frame(263, 80, 30, 37), Frame(295, 80, 36, 37),
        Frame(334, 80, 32, 36), Frame(370, 79, 29, 38),
    )),
    Animation('run', (
        Frame(1, 124, 33, 40), Frame(39, 124, 35, 39),
        Frame(89, 125, 35, 38), Frame(130, 121, 34, 42),
        Frame(181, 122, 34, 41), Frame(228, 122, 33, 40),
    )),
    Animation('roll', (
        Frame(1, 169, 29, 30), Frame(35, 167, 29, 31),
        Frame(67, 169, 30, 29), Frame(98, 169, 31, 29),
        Frame(131, 168, 29, 30), Frame(162, 168, 29, 31),
        Frame(193, 170, 30, 29), Frame(230, 170, 31, 29),
        Frame(268, 170, 30, 30),
    )),
    Animation('spin_ball', (
        Frame(1, 206, 30, 27), Frame(36, 206, 29, 27),
        Frame(70, 206, 29, 27), Frame(105, 206, 29, 27),
        Frame(139, 206, 29, 27), Frame(174, 206, 29, 27),
    )),
    Animation('fast_run', (
        Frame(1, 239, 29, 35), Frame(36, 239, 30, 35),
        Frame(74, 239, 31, 35), Frame(111, 238, 31, 36),
        Frame(149, 239, 30, 35), Frame(186, 238, 31, 36),
    )),
    Animation('dash', (
        Frame(1, 283, 29, 35), Frame(36, 283, 30, 35),
        Frame(72, 286, 39, 31), Frame(123, 285, 39, 32),
        Frame(172, 286, 39, 31), Frame(218, 285, 38, 32),
    )),
    Animation('turn', (
        Frame(1, 326, 24, 45), Frame(31, 327, 29, 44),
        Frame(65, 327, 20, 44), Frame(90, 327, 25, 43),
        Frame(119, 327, 25, 43), Frame(149, 327, 20, 44),
    )),
    Animation('hurt', (
        Frame(184, 341, 40, 28), Frame(232, 341, 39, 27),
    )),
    Animation('brake', (
        Frame(1, 379, 27, 38), Frame(31, 379, 31, 36),
        Frame(64, 379, 31, 36), Frame(99, 377, 33, 38),
        Frame(136, 379, 32, 36), Frame(176, 379, 33, 36),
        Frame(217, 379, 33, 36), Frame(254, 378, 33, 36),
    )),
    Animation('fall', (
        Frame(6, 429, 34, 40), Frame(49, 426, 34, 43),
    )),
    Animation('balance', (
        Frame(96, 427, 23, 39), Frame(125, 427, 23, 39),
    )),
)


def align_animations(animations):
    """동작별 기준선으로 프레임 기준점을 확정한다 (좌상단 기준)."""
    baselines = {'idle': 78, 'crouch': 78, 'walk': 118, 'run': 164,
                 'fast_run': 274, 'dash': 318, 'turn': 371,
                 'brake': 417, 'balance': 466}
    result = []
    frame_times = {'idle': 0.16, 'crouch': 0.18, 'walk': 0.10,
                   'run': 0.08, 'roll': 0.07, 'spin_ball': 0.07,
                   'fast_run': 0.08, 'dash': 0.07, 'turn': 0.12,
                   'hurt': 0.16, 'brake': 0.10, 'fall': 0.18, 'balance': 0.18}
    move_speeds = {'walk': 160, 'run': 320, 'roll': 240, 'spin_ball': 300,
                   'fast_run': 420, 'dash': 520, 'brake': 200}
    for animation in animations:
        frames = []
        for frame in animation.frames:
            # 공중 포즈는 중심 정렬, 지상 포즈는 시트의 공통 발 기준선 유지.
            anchor_y = (baselines[animation.name] - frame.y
                        if animation.name in baselines
                        else frame.height / 2 + (WINDOW_HEIGHT / 2 - GROUND_Y) / SCALE)
            frames.append(Frame(frame.x, frame.y, frame.width, frame.height,
                                frame.width / 2, anchor_y))
        result.append(Animation(animation.name, tuple(frames),
                                frame_times.get(animation.name, animation.frame_seconds),
                                move_speeds.get(animation.name, 0), animation.name == 'brake'))
    return tuple(result)


ANIMATIONS = align_animations(ANIMATIONS)


def movement_bounds(animations=ANIMATIONS):
    """양 방향의 모든 프레임이 들어가는 공통 기준점 범위."""
    extent = max(max(frame.anchor[0], frame.width - frame.anchor[0]) * SCALE
                 for animation in animations for frame in animation.frames)
    left = EDGE_MARGIN + extent
    right = WINDOW_WIDTH - EDGE_MARGIN - extent
    if left >= right:
        raise ValueError('창 너비가 캐릭터의 이동 공간보다 작습니다.')
    return left, right


MOVE_LEFT, MOVE_RIGHT = movement_bounds()


@dataclass
class Playback:
    animation_index: int = 0
    frame_index: int = 0
    elapsed: float = 0.0
    completed: int = 0
    state: str = PLAYING
    x: float = WINDOW_WIDTH / 2
    direction: int = 1

    @property
    def animation(self):
        return ANIMATIONS[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def move(self, seconds):
        animation = self.animation
        distance = animation.move_speed * seconds
        if animation.decelerate:
            # 5회 재생 전체에 걸쳐 선형 감속. 시간 구간을 적분하므로
            # 긴 업데이트와 여러 짧은 업데이트의 이동 거리가 일치한다.
            duration = len(animation.frames) * animation.frame_seconds * REPEAT_COUNT
            played = ((self.completed * len(animation.frames) + self.frame_index)
                      * animation.frame_seconds + self.elapsed)
            distance *= max(0.0, 1 - (played + seconds / 2) / duration)
        if distance <= 0:
            return
        span = MOVE_RIGHT - MOVE_LEFT
        phase = self.x - MOVE_LEFT
        if self.direction < 0:
            phase = 2 * span - phase
        phase = (phase + distance) % (2 * span)
        # 경계의 미세한 누적 오차 때문에 반전이 한 프레임 늦어지지 않게 한다.
        if abs(phase - span) < 1e-9:
            phase = span
        elif phase < 1e-9 or 2 * span - phase < 1e-9:
            phase = 0.0
        if phase < span:
            self.x = MOVE_LEFT + phase
            self.direction = 1
        else:
            self.x = MOVE_RIGHT - (phase - span)
            self.direction = -1

    def update(self, seconds):
        if not isfinite(seconds) or seconds < 0:
            raise ValueError('경과 시간은 0 이상의 유한한 값이어야 합니다.')
        while True:
            duration = (PAUSE_SECONDS if self.state == PAUSING
                        else self.animation.frame_seconds)
            # 재생과 정지 구간을 분리해 재생한 시간만큼만 이동한다.
            step = min(seconds, max(0.0, duration - self.elapsed))
            if self.state == PLAYING:
                self.move(step)
            self.elapsed += step
            seconds = max(0.0, seconds - step)
            # 긴 경과 시간을 처리할 때의 누적 오차를 1ns 범위에서 보정한다.
            if self.elapsed + 1e-9 < duration:
                break
            self.elapsed = 0.0
            if self.state == PAUSING:
                self.next_animation()
                continue
            if self.frame_index < len(self.animation.frames) - 1:
                self.frame_index += 1
            else:
                self.completed += 1
                if self.completed < REPEAT_COUNT:
                    self.frame_index = 0
                else:
                    self.state = PAUSING

    def next_animation(self):
        self.animation_index = (self.animation_index + 1) % len(ANIMATIONS)
        self.frame_index = 0
        self.completed = 0
        self.elapsed = 0.0
        self.state = PLAYING


def validate_animations(sheet_width, sheet_height, animations=ANIMATIONS):
    if not animations:
        raise ValueError('동작 목록이 비어 있습니다.')
    names = set()
    for animation in animations:
        if not animation.name or animation.name in names:
            raise ValueError(f'동작 이름이 비었거나 중복됩니다: {animation.name}')
        names.add(animation.name)
        if not animation.frames:
            raise ValueError(f'{animation.name}: 프레임이 없습니다.')
        if not isfinite(animation.frame_seconds) or animation.frame_seconds <= 0:
            raise ValueError(f'{animation.name}: 프레임 시간은 양수여야 합니다.')
        if not isfinite(animation.move_speed) or animation.move_speed < 0:
            raise ValueError(f'{animation.name}: 이동 속도는 0 이상의 유한한 값이어야 합니다.')
        for index, frame in enumerate(animation.frames):
            if (frame.x < 0 or frame.y < 0 or frame.width <= 0 or frame.height <= 0
                    or frame.x + frame.width > sheet_width
                    or frame.y + frame.height > sheet_height):
                raise ValueError(f'{animation.name}[{index}]: 이미지 경계를 벗어납니다.')
            if not all(isfinite(value) for value in frame.anchor):
                raise ValueError(f'{animation.name}[{index}]: 기준점이 유효하지 않습니다.')
            x, y, width, height = frame_placement(frame)
            if (x - width / 2 < 0 or x + width / 2 > WINDOW_WIDTH
                    or y - height / 2 < 0 or y + height / 2 > WINDOW_HEIGHT):
                raise ValueError(f'{animation.name}[{index}]: 확대된 프레임이 창을 벗어납니다.')


def load_sheet():
    path = Path(__file__).resolve().with_name('sonic-sprite.png')
    if not path.is_file():
        raise FileNotFoundError(f'스프라이트 이미지가 없습니다: {path}')
    return pico2d.load_image(str(path))


def frame_placement(frame, x=WINDOW_WIDTH / 2, direction=1):
    anchor_x, anchor_y = frame.anchor
    # 지상 동작의 발을 화면 중앙보다 아래에 두어 몸통이 중앙에 보이게 한다.
    center_x = x + direction * (frame.width / 2 - anchor_x) * SCALE
    center_y = GROUND_Y + (anchor_y - frame.height / 2) * SCALE
    return center_x, center_y, frame.width * SCALE, frame.height * SCALE


def draw_frame(sheet, frame, x=WINDOW_WIDTH / 2, direction=1):
    bottom = sheet.h - frame.y - frame.height
    placement = frame_placement(frame, x, direction)
    if direction < 0:
        sheet.clip_composite_draw(frame.x, bottom, frame.width, frame.height,
                                  0, 'h', *placement)
    else:
        sheet.clip_draw(frame.x, bottom, frame.width, frame.height, *placement)


def handle_events():
    """재생·정지 상태와 무관하게 종료 입력을 처리한다."""
    for event in pico2d.get_events():
        if event.type == pico2d.SDL_QUIT:
            return False
        if event.type == pico2d.SDL_KEYDOWN and event.key == pico2d.SDLK_ESCAPE:
            return False
    return True


def main():
    """뷰어의 단일 실행 진입점."""
    pico2d.open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)
    sheet = None
    try:
        pico2d.hide_lattice()
        sheet = load_sheet()
        validate_animations(sheet.w, sheet.h)
        playback = Playback()
        previous_time = perf_counter()
        while handle_events():
            now = perf_counter()
            elapsed = now - previous_time
            previous_time = now
            playback.update(elapsed)
            pico2d.clear_canvas()
            draw_frame(sheet, playback.frame, playback.x, playback.direction)
            pico2d.update_canvas()
            pico2d.delay(max(0, 1 / TARGET_FPS - (perf_counter() - now)))
    finally:
        # SDL 렌더러가 살아 있을 때 이미지 텍스처부터 해제한다.
        del sheet
        pico2d.close_canvas()


if __name__ == '__main__':
    main()
