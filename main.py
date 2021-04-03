from ursina import *
from first_person_controller import FirstPersonController
import random
import configparser #콘피그파일 읽어드리는 모듈

#콘피그 읽기 설정
section_1 = "player_setting"
conf_file = "config.txt"

config = configparser.ConfigParser()
config.read(conf_file)

#콘피그 읽어들이기
m_lock = config.get(section_1, 'mouse_locked')

app = Ursina()

random_sc = 0

#프로그램 기본 설정
window.fps_counter.enabled = True
window.exit_button.enable = True
if m_lock == "False": mouse.locked = False#마우스 움직임 고정 여부 설정
elif m_lock == "True": mouse.locked = True

#콘피그파일 읽기 설정
section = "move_key"
conf_file = "config.txt"

config = configparser.ConfigParser()
config.read(conf_file)

f = config.get(section, 'front')

#펀치 소리
punch = Audio('assets/punch', autoplay=False)

#블럭 리스트 추가
blocks = [
    load_texture('assets/grass_block.png'), # 0
    load_texture('assets/grass_block.png'),
    load_texture('assets/stone.png'),
    load_texture('assets/gold_ore.png'),
    load_texture('assets/lava.png'),
    load_texture('assets/cobble_stone.png'),
    load_texture('assets/wood.png') # 6
]

block_id = 1
#번호키를 눌렀을때 블럭 바뀌게
def input(key):
    global block_id, hand
    if key.isdigit():
        block_id = int(int(key)-1)
        if block_id >= len(blocks):
            block_id = len(blocks) - 1
        hand.texture = blocks[block_id]
#하늘 추가
sky = Entity(
    parent=scene,
    model='sphere',
    texture=load_texture('assets/sky.jpg'),
    scale=500,
    double_sided=True
)
#블럭을 들고있는 손 추가
hand = Entity(
    parent=camera.ui,
    model='assets/block',
    texture=blocks[block_id],
    scale=0.2,
    rotation=Vec3(-10, -10, 10),
    position=Vec2(0.6, -0.6)
)
#블럭 부수거나 설치할때 소리와 손 위치
def update():
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.position = Vec2(0.4, -0.5)
    else:
        hand.position = Vec2(0.6, -0.6)
#블럭생성 클래스(함수)
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture='assets/grass_block.png'):
        super().__init__(
            parent=scene,
            position=position,
            model='assets/block',
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1.0)),
            scale=0.5
        )       
#블럭 부수기 설치하기
    def input(self, key):
        if self.hovered:
            if key == 'right mouse down' and self.position != camera.position:
                punch.play()
                Voxel(position=self.position + mouse.normal, texture=blocks[block_id])
            elif key == 'left mouse down':
                punch.play()
                destroy(self)
#월드 생성
for y in range(0,4):
    for z in range(-5,6):
        for x in range(-5,6):
            if y == 0:
                Voxel(position=(x, y, z), texture=blocks[2])
            else:
                random_sc = random.randint(0,1)
                if y == 0 and random_sc == 0:
                    Voxel(position=(x, y, z), texture=blocks[2])
                elif y == 1 or y == 2 or y == 3 and random_sc == 0:
                    Voxel(position=(x, y, z), texture=blocks[1])

player = FirstPersonController()
print(camera.position)

app.run()
