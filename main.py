#수정 要 사항: play 中 slider diable 할것, replay 시 slider 위치에서 play되게 할 것

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
from matplotlib import font_manager as fm

# 폰트 파일에서 직접 폰트 로드
font_path = './fonts/NotoSansKR-VariableFont_wght.ttf'  # 실제 폰트 파일 경로로 변경해야 합니다
font_prop = fm.FontProperties(fname=font_path)


# 폰트 매니저에 폰트 추가
fm.fontManager.addfont(font_path)

# 기본 폰트 설정
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# 사용자 입력으로 초기 속도, 각도, 시작 높이 설정
initial_velocity = float(input("초기 속도(m/s)를 입력하세요: "))
angle = float(input("발사 각도(도)를 입력하세요: "))
initial_height = float(input("시작 높이(m)를 입력하세요: "))
g = 9.81  # m/s^2 (중력가속도)

# 각도 변환
theta = np.radians(angle)

# 초기 속도 성분
vx = initial_velocity * np.cos(theta)
vy = initial_velocity * np.sin(theta)

# 시간 설정 (이차 방정식의 해를 이용해 최대 시간 계산)
t_flight = (vy + np.sqrt(vy ** 2 + 2 * g * initial_height)) / g
t = np.linspace(0, t_flight, 500)

# 포물선 운동의 위치 계산
x = vx * t
y = initial_height + vy * t - 0.5 * g * np.square(t)

# 속도 계산
v_x = np.full_like(t, vx)
v_y = vy - g * t
v = np.sqrt(v_x ** 2 + v_y ** 2)

# 지면에 닿는 지점 찾기
ground_index = np.where(y < 0)[0]
if len(ground_index) > 0:
    ground_index = ground_index[0]
    x = x[:ground_index]
    y = y[:ground_index]
    v = v[:ground_index]
    t = t[:ground_index]

fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(bottom=0.3)
line, = ax.plot([], [], 'bo', ms=10)
trajectory, = ax.plot([], [], 'r-', lw=2)

# 텍스트 객체 생성 - 위치 조정
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontproperties=font_prop)
speed_text = ax.text(0.02, 0.85, '', transform=ax.transAxes, fontproperties=font_prop)
pos_text = ax.text(0.02, 0.75, '', transform=ax.transAxes, fontproperties=font_prop)


def init():
    max_height = max(y)
    max_distance = max(x)
    ax.set_xlim(0, max_distance * 1.1)
    ax.set_ylim(0, max_height * 1.1)
    ax.set_aspect('equal', 'box')
    ax.set_xlabel('거리 (m)', fontproperties=font_prop)
    ax.set_ylabel('높이 (m)', fontproperties=font_prop)
    ax.set_title('포물선 운동 시뮬레이션', fontproperties=font_prop)
    return line, trajectory, time_text, speed_text, pos_text


# 슬라이더의 이벤트 핸들러를 일시적으로 비활성화하는 함수
def block_slider_event():
    frame_slider.eventson = False


# 슬라이더의 이벤트 핸들러를 다시 활성화하는 함수
def unblock_slider_event():
    frame_slider.eventson = True


def update(frame):
    block_slider_event()  # 이벤트 핸들러 비활성화
    line.set_data([x[frame]], [y[frame]])
    trajectory.set_data(x[:frame + 1], y[:frame + 1])

    time_text.set_text(f'시간: {t[frame]:.2f} 초')
    speed_text.set_text(f'속도: {v[frame]:.2f} m/s')
    pos_text.set_text(f'위치: ({x[frame]:.2f}, {y[frame]:.2f}) m')

    frame_slider.set_val(frame)  # 슬라이더 값을 업데이트
    unblock_slider_event()  # 이벤트 핸들러 다시 활성화

    return line, trajectory, time_text, speed_text, pos_text


# 애니메이션 객체 선언
ani = animation.FuncAnimation(fig, update, frames=range(len(t)), init_func=init, blit=False, interval=20, repeat=False)

# 재생/일시정지 상태를 저장할 변수
paused = True


def toggle_play(event):
    global paused
    if paused:
        ani.event_source.start()
        play_button.label.set_text('\u2161')  # 새로운 일시정지 아이콘 (U+2161)
    else:
        ani.event_source.stop()
        play_button.label.set_text('\u25B6')  # 재생 아이콘
    paused = not paused
    plt.draw()


def on_frame_change(val):
    global paused
    frame = int(val)
    ani.event_source.stop()
    ani._draw_frame(frame)
    if not paused:
        ani.event_source.start()


# 버튼 추가
play_ax = plt.axes([0.81, 0.05, 0.1, 0.075])
play_button = Button(play_ax, '\u25B6', color='lightgoldenrodyellow', hovercolor='0.975')
play_button.on_clicked(toggle_play)

# 슬라이더 추가
slider_ax = plt.axes([0.1, 0.1, 0.65, 0.03])
frame_slider = Slider(slider_ax, '프레임', 0, len(t) - 1, valinit=0, valstep=1)
frame_slider.on_changed(on_frame_change)

plt.show()