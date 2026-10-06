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

from pathlib import Path

import pico2d

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800
SCALE = 6
REPEAT_COUNT = 5
PAUSE_SECONDS = 1.0
DEFAULT_FRAME_SECONDS = 0.1
TARGET_FPS = 60


def load_sheet():
    path = Path(__file__).resolve().with_name('sonic-sprite.png')
    if not path.is_file():
        raise FileNotFoundError(f'스프라이트 이미지가 없습니다: {path}')
    return pico2d.load_image(str(path))


def handle_events():
    """창 닫기 요청이 없으면 실행을 계속한다."""
    return not any(event.type == pico2d.SDL_QUIT
                   for event in pico2d.get_events())


def main():
    """뷰어의 단일 실행 진입점."""
    pico2d.open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)
    sheet = load_sheet()
    while handle_events():
        pico2d.delay(1 / TARGET_FPS)
    pico2d.close_canvas()


if __name__ == '__main__':
    main()
