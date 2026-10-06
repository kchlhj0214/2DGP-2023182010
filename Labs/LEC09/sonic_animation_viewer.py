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

총 13동작, 76프레임. 이름은 포즈에 따른 뷰어용 분류다.
1행은 연속된 대기 포즈와 마지막의 낮은 포즈를 분리한다.
8·10행은 서로 다른 포즈 흐름을 각각 두 동작으로 분리한다.
제목, 크레딧, 하단의 노란색·갈색 별도 캐릭터는 제외한다.
"""

from dataclasses import dataclass
from pathlib import Path

import pico2d

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800
SCALE = 6
REPEAT_COUNT = 5
PAUSE_SECONDS = 1.0
DEFAULT_FRAME_SECONDS = 0.1
TARGET_FPS = 60


@dataclass(frozen=True)
class Frame:
    # 이미지 좌상단 원점, 오른쪽으로 x 증가, 아래로 y 증가.
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    frame_seconds: float = DEFAULT_FRAME_SECONDS


ANIMATIONS = (
    Animation('idle', (
        Frame(1, 39, 29, 39), Frame(31, 40, 26, 38),
        Frame(58, 39, 29, 39), Frame(87, 40, 29, 38),
        Frame(118, 40, 30, 38), Frame(150, 40, 30, 38),
        Frame(182, 40, 31, 38), Frame(213, 39, 30, 38),
        Frame(243, 39, 26, 38),
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


def load_sheet():
    path = Path(__file__).resolve().with_name('sonic-sprite.png')
    if not path.is_file():
        raise FileNotFoundError(f'스프라이트 이미지가 없습니다: {path}')
    return pico2d.load_image(str(path))


def draw_frame(sheet, frame):
    bottom = sheet.h - frame.y - frame.height
    sheet.clip_draw(frame.x, bottom, frame.width, frame.height,
                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)


def handle_events():
    """창 닫기 요청이 없으면 실행을 계속한다."""
    return not any(event.type == pico2d.SDL_QUIT
                   for event in pico2d.get_events())


def main():
    """뷰어의 단일 실행 진입점."""
    pico2d.open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)
    sheet = load_sheet()
    pico2d.clear_canvas()
    draw_frame(sheet, ANIMATIONS[0].frames[0])
    pico2d.update_canvas()
    while handle_events():
        pico2d.delay(1 / TARGET_FPS)
    pico2d.close_canvas()


if __name__ == '__main__':
    main()
