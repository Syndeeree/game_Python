import math
import os
from re import A
import arcade.gui

import arcade
from time import time

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Platformer"

UPDATES_PER_FRAME = 5

TILE_SCALING = 0.5
CHARACTER_SCALING = TILE_SCALING * 2
COIN_SCALING = TILE_SCALING
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

SPRITE_SCALING_LASER = 0.8
SHOOT_SPEED = 15
BULLET_SPEED = 12
BULLET_DAMAGE = 25

PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1.5
PLAYER_JUMP_SPEED = 30

LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 5
PLAYER_START_Y = 5

RIGHT_FACING = 0
LEFT_FACING = 1

LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Enemies"
LAYER_NAME_BULLETS = "Bullets"



ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).replace("main.py", "")


def load_texture_pair(filename):

    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class Entity(arcade.Sprite):
    def __init__(self, name_folder, name_file):
        super().__init__()

        self.facing_direction = RIGHT_FACING

        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        main_path = f":resources:images/animated_characters/{name_folder}/{name_file}"

        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        self.texture = self.idle_texture_pair[0]

        self.set_hit_box(self.texture.hit_box_points)

class Entity01(arcade.Sprite):
    def __init__(self, name_folder, name_file):
        super().__init__()

        self.facing_direction = RIGHT_FACING

        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        main_path = f"Tiled/_PNG/{name_folder}/"

        self.idle_texture_pair = []
        for i in range(14):
            texture = load_texture_pair(f"{main_path}Idle/idle{i+1}.png")
            self.idle_texture_pair.append(texture)

        self.attack_texture_pair = []
        for i in range(7):
            texture = load_texture_pair(f"{main_path}Attack/attack{i+1}.png")
            self.attack_texture_pair.append(texture)


        self.jump_texture_pair = load_texture_pair(f"{main_path}Jump/jump2.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}Jump/jump6.png")

        self.walk_textures = []
        for i in range(7):
            texture = load_texture_pair(f"{main_path}Run/run{i+1}.png")
            self.walk_textures.append(texture)

        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}Climb/climb2.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}Climb/climb4.png")
        self.climbing_textures.append(texture)

        self.texture = self.idle_texture_pair[0][0]

        self.set_hit_box(self.texture.hit_box_points)


class Enemy(Entity):
    def __init__(self, name_folder, name_file):

        super().__init__(name_folder, name_file)

        self.should_update_walk = 0
        self.health = 0

    def update_animation(self, delta_time: float = 1 / 120):

        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return


        if self.should_update_walk == 3:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.facing_direction]
            self.should_update_walk = 0
            return

        self.should_update_walk += 1


class RobotEnemy(Enemy):
    def __init__(self):

        super().__init__("robot", "robot")

        self.health = 1000


class ZombieEnemy(Enemy):
    def __init__(self):

        super().__init__("zombie", "zombie")

        self.health = 50


class PlayerCharacter(Entity01):

    def __init__(self):

        super().__init__("Mage", "Mage")

        self.game = GameView()

        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.is_attack = False


    def update_animation(self, delta_time: float = 1 / 120):

        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.facing_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.facing_direction]
            return

        if self.is_attack:
            self.cur_texture += 1
            if self.cur_texture > 6*UPDATES_PER_FRAME:
                self.cur_texture = 0
                self.is_attack = False
            self.texture = self.attack_texture_pair[self.cur_texture//(UPDATES_PER_FRAME)][self.facing_direction]
            return


        if self.change_x == 0 and not self.is_attack:
            self.cur_texture += 1
            if self.cur_texture > 13*UPDATES_PER_FRAME*2:
                self.cur_texture = 0
            self.texture = self.idle_texture_pair[self.cur_texture//(UPDATES_PER_FRAME*2)][self.facing_direction]
            return

        self.cur_texture += 1
        if self.cur_texture > 6*UPDATES_PER_FRAME:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture//UPDATES_PER_FRAME][self.facing_direction]


class MainMenu(arcade.View):

    def on_show(self):

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        default_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 20,
            "font_color": arcade.color.BLACK,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.ALMOND,

            "bg_color_pressed": arcade.color.ALLOY_ORANGE,
            "border_color_pressed": arcade.color.BLACK,
            "font_color_pressed": arcade.color.BLACK,
        }
        red_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 20,
            "font_color": arcade.color.BLACK,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.REDWOOD,

            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.BLACK,
            "font_color_pressed": arcade.color.RED,
        }

        self.v_box = arcade.gui.UIBoxLayout(space_between = 50)

        self.start_button = arcade.gui.UIFlatButton(text="Играть", width=250, style=default_style)
        self.quit_button = arcade.gui.UIFlatButton(text="Выйти", width=250, style=red_style)

        self.v_box.add(self.start_button)
        self.v_box.add(self.quit_button)

        self.start_button.on_click = self.on_click_start
        self.quit_button.on_click = self.on_click_quit


        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child = self.v_box)
        )

        self.source = arcade.play_sound(arcade.load_sound("menu.mp3"), 1, 0, True)
        self.background = arcade.load_texture("fon.png")

    def on_draw(self):

        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        arcade.draw_text(
            "История о маленькой волшебнице Василии (Esc - меню)",
            SCREEN_WIDTH / 2,
            150,
            arcade.color.BLACK,
            font_size=30,
            anchor_x="center",
        )
        arcade.draw_text(
            "Остерегайтесь роботов, они почти бессмертны",
            SCREEN_WIDTH / 2,
            100,
            arcade.color.BLACK,
            font_size=30,
            anchor_x="center",
        )
        arcade.draw_text(
            "Нажмите <E>, чтобы создать заклинание",
            SCREEN_WIDTH / 2,
            50,
            arcade.color.BLACK,
            font_size=30,
            anchor_x="center",
        )
        self.manager.draw()


    def on_click_start(self, event):
        arcade.stop_sound(self.source)
        self.manager.disable()
        arcade.play_sound(arcade.load_sound("button_pressed.mp3"))
        """Use a mouse press to advance to the 'game' view."""
        game_view = GameView()
        self.window.show_view(game_view)

    def on_click_quit(self, event):
        arcade.exit()



class GameView(arcade.View):

    def __init__(self):

        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout()

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        self.background = None

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shoot_pressed = False
        self.jump_needs_reset = False

        self.tile_map = None

        self.scene = None

        self.player_sprite = None

        self.physics_engine = None

        self.camera = None

        self.gui_camera = None

        self.end_of_map = 0

        self.score = 0
        self.key = 0

        self.can_shoot = False
        self.shoot_timer = 0

        self.background_music = arcade.load_sound("back.mp3")
        self.collect_coin_sound = arcade.load_sound("money.mp3")
        self.sound_koko = arcade.load_sound("chicken.mp3")
        self.jump_sound = arcade.load_sound("jump.mp3")
        self.game_over = arcade.load_sound("Death.mp3")
        self.shoot_sound = arcade.load_sound("fire.mp3")
        self.hit_sound = arcade.load_sound("hert.mp3")
        self.enemy_death = arcade.load_sound("Zombie_death.mp3")
        self.win_sound = arcade.load_sound("win.mp3")
        self.need_more = arcade.load_sound("needmore.mp3")



    def setup(self):

        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)

        map_name = f"{ROOT_DIR}\Tiled\map.json"

        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_PLATFORMS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.score = 0

        self.can_shoot = True
        self.shoot_timer = 0

        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = (
            self.tile_map.tile_width * TILE_SCALING * PLAYER_START_X
        )
        self.player_sprite.center_y = (
            self.tile_map.tile_height * TILE_SCALING * PLAYER_START_Y
        )

        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        enemies_layer = self.tile_map.object_lists[LAYER_NAME_ENEMIES]

        for my_object in enemies_layer:
            cartesian = self.tile_map.get_cartesian(
                my_object.shape[0], my_object.shape[1]
            )
            enemy_type = my_object.properties["type"]
            if enemy_type == "robot":
                enemy = RobotEnemy()
            elif enemy_type == "zombie":
                enemy = ZombieEnemy()
            enemy.center_x = math.floor(
                cartesian[0] * TILE_SCALING * self.tile_map.tile_width
            )
            enemy.center_y = math.floor(
                (cartesian[1] + 1) * (self.tile_map.tile_height * TILE_SCALING)
            )
            if "boundary_left" in my_object.properties:
                enemy.boundary_left = my_object.properties["boundary_left"]
            if "boundary_right" in my_object.properties:
                enemy.boundary_right = my_object.properties["boundary_right"]
            if "change_x" in my_object.properties:
                enemy.change_x = my_object.properties["change_x"]
            self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)


        self.scene.add_sprite_list(LAYER_NAME_BULLETS)

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms = self.scene[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            ladders = self.scene[LAYER_NAME_LADDERS],
            walls = self.scene[LAYER_NAME_PLATFORMS]
        )

    def on_show(self):
        self.setup()
        self.time_start = time()
        self.audiosource = arcade.play_sound(self.background_music, 0.5, 0, True)

    def on_draw(self):

        self.clear()

        self.camera.use()

        self.scene.draw()

        self.gui_camera.use()
        self.manager.draw()

        score_text = f"Монеты (снаряды): {self.score}"
        arcade.draw_text(
            score_text,
            10,
            40,
            arcade.csscolor.WHITE,
            18,
        )
        a =  float("{0:.2f}".format(time()-self.time_start))
        time_text = f"Время: {a}"
        arcade.draw_text(
            time_text,
            10,
            10,
            arcade.csscolor.WHITE,
            18,
        )


    def process_keychange(self):

        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif (
                self.physics_engine.can_jump(y_distance=10)
                and not self.jump_needs_reset
            ):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):

        if key == arcade.key.UP or key == arcade.key.SPACE or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        if key == arcade.key.E:
            self.shoot_pressed = True

        if key == arcade.key.ESCAPE:
            arcade.stop_sound(self.audiosource)
            game_view = MainMenu()
            self.window.show_view(game_view)

        self.process_keychange()

    def on_key_release(self, key, modifiers):

        if key == arcade.key.UP or key == arcade.key.SPACE or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        if key == arcade.key.E:
            self.shoot_pressed = False


        self.process_keychange()


    def center_camera_to_player(self, speed=0.2):
        screen_center_x = self.camera.scale * (self.player_sprite.center_x - (self.camera.viewport_width / 2))
        screen_center_y = self.camera.scale * (self.player_sprite.center_y - (self.camera.viewport_height / 2))
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = (screen_center_x, screen_center_y)

        self.camera.move_to(player_centered, speed)

    def koko(self, button_text):
        arcade.play_sound(self.sound_koko, 10)

    def on_update(self, delta_time):

        self.physics_engine.update()

        if self.key > 0:
            self.player_sprite.center_x = (
                self.tile_map.tile_width * TILE_SCALING * PLAYER_START_X
            )
            self.player_sprite.center_y = (
                self.tile_map.tile_height * TILE_SCALING * (PLAYER_START_Y+24)
            )

            arcade.play_sound(self.win_sound, 15)

            a = float("{0:.2f}".format(time()-self.time_start))
            try:
                with open('record') as fin:
                    i = float(fin.read())
            except IOError:
                i = 9999999

            if a<i:
                x = a
                with open('record','w') as fout:
                    fout.write(str(a))
            else:
                x = i

            message_box = arcade.gui.UIMessageBox(

            width=300,

            height=200,

            message_text=(

                "Вы нашли ключ от древней сокровищницы! \n"

                f"Время прохождения: {a} sec \n"
                f"Лучшее время: {x} sec \n"

                "Для того чтобы выйти нажите Esc \n"

            ),

            callback = self.koko,

            buttons=["Ok"]

            )
            self.manager.add(message_box)

            self.key = 0

        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        if self.can_shoot:
            if self.shoot_pressed and self.score>0:
                self.player_sprite.is_attack = True
                self.score -= 1
                arcade.play_sound(self.shoot_sound, 0.5)

                bullet = arcade.Sprite(
                    f"{ROOT_DIR}\Tiled/fire.png",
                    SPRITE_SCALING_LASER,
                )

                if self.player_sprite.facing_direction == RIGHT_FACING:
                    bullet.change_x = BULLET_SPEED
                else:
                    bullet.change_x = -BULLET_SPEED

                bullet.center_x = self.player_sprite.center_x
                bullet.center_y = self.player_sprite.center_y

                self.scene.add_sprite(LAYER_NAME_BULLETS, bullet)

                self.can_shoot = False
            elif self.shoot_pressed and self.score <= 0:
                try:
                    arcade.stop_sound(self.needsource)
                except AttributeError:
                    print("Ик")
                self.needsource = arcade.play_sound(self.need_more)

        else:
            self.shoot_timer += 1
            if self.shoot_timer == SHOOT_SPEED:
                self.can_shoot = True
                self.shoot_timer = 0

        self.scene.update_animation(
            delta_time,
            [
                LAYER_NAME_COINS,
                LAYER_NAME_BACKGROUND,
                LAYER_NAME_PLAYER,
                LAYER_NAME_ENEMIES,
            ],
        )

        self.scene.update(
            [LAYER_NAME_MOVING_PLATFORMS, LAYER_NAME_ENEMIES, LAYER_NAME_BULLETS]
        )

        for enemy in self.scene[LAYER_NAME_ENEMIES]:
            if (
                enemy.boundary_right
                and enemy.right > enemy.boundary_right
                and enemy.change_x > 0
            ):
                enemy.change_x *= -1

            if (
                enemy.boundary_left
                and enemy.left < enemy.boundary_left
                and enemy.change_x < 0
            ):
                enemy.change_x *= -1

        for bullet in self.scene[LAYER_NAME_BULLETS]:
            hit_list = arcade.check_for_collision_with_lists(
                bullet,
                [
                    self.scene[LAYER_NAME_ENEMIES],
                    self.scene[LAYER_NAME_PLATFORMS],
                    self.scene[LAYER_NAME_MOVING_PLATFORMS],
                ],
            )

            if hit_list:
                bullet.remove_from_sprite_lists()

                for collision in hit_list:
                    if (
                        self.scene[LAYER_NAME_ENEMIES]
                        in collision.sprite_lists
                    ):
                        collision.health -= BULLET_DAMAGE

                        if collision.health <= 0:
                            arcade.play_sound(self.enemy_death)
                            collision.remove_from_sprite_lists()
                            self.score += 20
                        else:
                            arcade.play_sound(self.hit_sound)

                return

            if (bullet.right < 0) or (
                bullet.left
                > (self.tile_map.width * self.tile_map.tile_width) * TILE_SCALING
            ):
                bullet.remove_from_sprite_lists()

        player_collision_list = arcade.check_for_collision_with_lists(
            self.player_sprite,
            [
                self.scene[LAYER_NAME_COINS],
                self.scene[LAYER_NAME_ENEMIES],
            ],
        )

        for collision in player_collision_list:

            if self.scene[LAYER_NAME_ENEMIES] in collision.sprite_lists:
                arcade.stop_sound(self.audiosource)
                arcade.play_sound(self.game_over)
                game_over = GameOverView()
                self.window.show_view(game_over)
                return
            else:

                if "Points" not in collision.properties:
                    print("Warning, collected a coin without a Points property.")
                else:
                    points = int(collision.properties["Points"])
                    self.score += points

                if "Key" not in collision.properties:
                    print("Warning, collected a coin without a key property.")
                else:
                    key = int(collision.properties["Key"])
                    self.key += key

                collision.remove_from_sprite_lists()
                arcade.play_sound(self.collect_coin_sound)

        self.center_camera_to_player()

        


class GameOverView(arcade.View):

    def on_show(self):

        arcade.set_background_color(arcade.color.BLACK)
        self.sound = arcade.play_sound(arcade.load_sound("darksous.mp3"))
        self.voskres = arcade.load_sound("voskres.mp3")
        
    def on_draw(self):

        self.clear()
        arcade.draw_text(
            "Вы погибли!",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 50,
            arcade.color.RED,
            30,
            anchor_x="center",
        )
        arcade.draw_text(
            "Тык на пробел для возрождения!",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.RED,
            20,
            anchor_x="center",
        )
    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            arcade.stop_sound(self.sound)
            game_view = GameView()
            self.window.show_view(game_view)
            arcade.play_sound(self.voskres)


def main():

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MainMenu()
    window.show_view(menu_view)
    arcade.run()
    

if __name__ == "__main__":
    main()