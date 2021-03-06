from ursina import *
import configparser

#변수
lock = 0

#콘피그파일 읽기 설정
section = "move_key"
section_1 = "player_setting"
conf_file = "config.txt"

config = configparser.ConfigParser()
config.read(conf_file)

#조작키 콘피그 읽어들이기 (section)
front_key = config.get(section, 'front')
east_key = config.get(section, 'east')
west_key = config.get(section, 'west')
behind_key = config.get(section, 'behind')
jump_key = config.get(section, 'jump')

#플레이어 기본설정 콘피그 읽어들이기 (section_1)
speed = config.get(section_1, 'speed')
x = config.get(section_1, 'x')
y = config.get(section_1, 'y')
z = config.get(section_1, 'z')
gravity = config.get(section_1, 'gravity')
fov = config.get(section_1, 'fov')
m_lock = config.get(section_1, 'mouse_locked')
j_height = config.get(section_1, 'jump_height')
j_dur = config.get(section_1, 'jump_duration')
m_sensitivity =  config.get(section_1, 'mouse_sensitivity')
print(m_lock)

class FirstPersonController(Entity):
    def __init__(self, **kwargs):
        super().__init__()#플레이어 셋팅 {
        self.speed = int(speed)
        self.origin_y = -.5
        self.camera_pivot = Entity(parent=self, y=2)
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)

        camera.parent = self.camera_pivot
        camera.position = (int(x),int(y),int(z)) #플레이어 좌표에 대한 화면 좌표 설정
        camera.rotation = (0,0,0) # 화면 회전 설정 
        camera.fov = int(fov)
        if m_lock == "False":
            lock = 0
            mouse.locked = False #마우스 움직임 고정 여부 설정
        elif m_lock == "True":
            lock = 1
            mouse.locked = True 
        self.mouse_sensitivity = Vec2(int(m_sensitivity), int(m_sensitivity)) #마우스 감도 설정

        self.gravity = 1
        self.grounded = False
        self.jump_height = int(j_height) # 점프 높이 설정
        self.jump_duration = int(j_dur)/10 # 점프할때 공중에 머무는 시간 설정
        self.jumping = False
        self.air_time = 0
        #}플레이어셋팅

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1] #카메라 회전 위아래

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0] #카메라 회전 좌우
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.forward * (held_keys[str(front_key)] - held_keys[str(west_key)]) #앞뒤 이동키
            + self.right * (held_keys[str(behind_key)] - held_keys[str(east_key)]) #좌우 이동키
            ).normalized()

        origin = self.world_position + (self.up*.5)
        hit_info = raycast(origin , self.direction, ignore=(self,), distance=.5, debug=False)
        if not hit_info.hit:
            self.position += self.direction * self.speed * time.dt


        if self.gravity:
            #중력 설정
            ray = raycast(self.world_position+(0,2,0), self.down, ignore=(self,))
            # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

            if ray.distance <= 2.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity


    def input(self, key): #키 입력
        if key == str(jump_key):
            self.jump()
        if key == 't':
            self.mouselock()

    def mouselock(self):
        global lock
        if lock == 0:
            mouse.locked = True #마우스 움직임 고정 여부 설정
            lock = 1
        elif lock == 1:
            mouse.locked = False
            lock = 0

    def jump(self): #점프 함수
        if not self.grounded:
            return

        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_duration, resolution=int(1//time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.jump_duration)


    def start_fall(self): #떨어짐 시작 함수
        self.y_animator.pause()
        self.jumping = False

    def land(self): #떨어질때 함수
        # print('land')
        self.air_time = 0
        self.grounded = True


if __name__ == '__main__':
    from first_person_controller import FirstPersonController
    # window.vsync = False
    app = Ursina()
    # Sky(color=color.gray)
    ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100), collider='box')
    e = Entity(model='cube', scale=(1,5,10), x=2, y=.01, rotation_y=45, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)
    e = Entity(model='cube', scale=(1,5,10), x=-2, y=.01, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)

    player = FirstPersonController(model='cube', y=1, origin_y=-.5)
    player.gun = None

    gun = Button(parent=scene, model='cube', color=color.blue, origin_y=-.5, position=(3,0,3), collider='box')
    gun.on_click = Sequence(Func(setattr, gun, 'parent', camera), Func(setattr, player, 'gun', gun))

    gun_2 = duplicate(gun, z=7, x=8)
    slope = Entity(model='cube', collider='box', position=(0,0,8), scale=6, rotation=(45,0,0), texture='brick', texture_scale=(8,8))
    slope = Entity(model='cube', collider='box', position=(5,0,10), scale=6, rotation=(80,0,0), texture='brick', texture_scale=(8,8))
    # hill = Entity(model='sphere', position=(20,-10,10), scale=(25,25,25), collider='sphere', color=color.green)
    # hill = Entity(model='sphere', position=(20,-0,10), scale=(25,25,25), collider='mesh', color=color.green)
    # from ursina.shaders import basic_lighting_shader
    # for e in scene.entities:
    #     e.shader = basic_lighting_shader

    def input(key):
        if key == 'left mouse down' and player.gun:
            gun.blink(color.orange)
            bullet = Entity(parent=gun, model='cube', scale=.1, color=color.black)
            bullet.world_parent = scene
            bullet.animate_position(bullet.position+(bullet.forward*80), curve=curve.linear, duration=1) #bullet.forwad * 80은 이동속도 조
            destroy(bullet, delay=1)

    # player.add_script(NoclipMode())
    app.run()
