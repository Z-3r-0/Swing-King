from src.scene import Scene, SceneType

import src.utils.level_export as export
from src.hud.level_creator_hud import *
from src.hud.level_creator_hud import obstacle_selection_buttons

class LevelCreator(Scene):

    def __init__(self, screen, scene_from: SceneType = None):
        super().__init__(screen, SceneType.LEVEL_CREATOR, "Level Creator")

        info = pygame.display.Info()
        get_user_width, get_user_height = info.current_w, info.current_h

        self.width, self.height, self.max_width, self.max_height = round(get_user_width), round(get_user_height), 10000, 2000
        self.min_width, self.min_height = -500, -500  # Must be negative

        self.list_polygons = [Polygon(terrain_type="fairway")]
        self.cooldown = 0
        self.last_point = pygame.Vector2(0, 0)

        action_bar_height = self.height * 0.16
        action_bar_pos = pygame.Vector2(0, self.height - action_bar_height)
        self.action_bar_background = pygame.Rect(action_bar_pos.x, action_bar_pos.y, self.width, action_bar_height)

        self.interacted = False

        self.action_buttons = action_buttons(self.width, self.height, action_bar_pos)
        self.camera_buttons = camera_movement_buttons(self.width, self.height, action_bar_pos)
        self.terrain_selection_buttons = terrain_selection_buttons(self.width, self.height, action_bar_pos)
        self.obstacle_type_buttons = obstacle_type_buttons(self.width, self.height, action_bar_pos)
        self.obstacle_selection_buttons = obstacle_selection_buttons(self.width, self.height, action_bar_pos)
        self.obstacle_switching_buttons = obstacle_switching_buttons(self.width, self.height, action_bar_pos)
        self.props_selection_buttons = environment_selection_buttons(self.width, self.height, action_bar_pos)

        self.elements_buttons = self.props_selection_buttons + self.obstacle_selection_buttons
        
        self.background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
        self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))

        # Define camera
        self.camera = pygame.Vector2(0, 0)
        self.camera_movement = pygame.Vector2(0, 0)
        
        # region Terrain type control
        self.current_terrain_type = "fairway"

        self.selection_keys = {
            pygame.K_g: "green",
            pygame.K_f: "fairway",
            pygame.K_b: "bunker",
            pygame.K_l: "lake"
        }

        self.action_keys = {
            pygame.K_SPACE: "detach polygon",
            pygame.K_ESCAPE: "compensating polygon",
            pygame.K_DELETE: "delete props and decors",
            pygame.K_r: "rotate left",
            pygame.K_t: "rotate right",
        }

        self.switch_index = 0
        
        # obstacles handling
        self.generated_obstacles = []
        self.selected_obstacle = None
        self.placing_obstacle = None
        self.resizing_obstacle = None
        self.moving_obstacle = None
        
        # For existing obstacles translation
        self.drag_offset = pygame.Vector2(0, 0)
        
        # Characteristics of special buttons
        self.chara_but_spe = [
            "start",
            "end",
            "coins",
        ]
        
        # List all .png files in the folder
        folder_path = "assets/images/props/"
        self.obstacles_image_list = [f for f in os.listdir(folder_path+"obstacles/") if f.endswith(".png")]
        self.environment_image_list = [f for f in os.listdir(folder_path+"environment/") if f.endswith(".png")]
        self.specials_image_list = [f for f in os.listdir(folder_path+"specials/") if f.endswith(".png")]

        self.grid_size = 15
        self.camera_speed = pygame.Vector2(self.grid_size*10, self.grid_size*2)
        self.has_been_interacted = False

        self.button_to_action = {
            self.action_buttons[0]: (lambda: self.action_buttons[0].toggle()),
            self.action_buttons[1]: (lambda: self.clear_list_polygons()),
            self.action_buttons[2]: (lambda: self.restart_level()),
            self.action_buttons[3]: (lambda: rewind(self.list_polygons)),
            self.action_buttons[4]: (lambda: restore(self.list_polygons)),
            self.action_buttons[5]: (lambda: self.action_buttons[5].toggle()),
            self.action_buttons[7]: (lambda: export(self.list_polygons, self.generated_obstacles)),
            self.action_buttons[8]: (lambda: self.quit_level_creator()),

            self.camera_buttons[0]: (lambda: self.move_camera_left()),
            self.camera_buttons[1]: (lambda: self.move_camera_right()),
            self.camera_buttons[2]: (lambda: self.move_camera_up()),
            self.camera_buttons[3]: (lambda: self.move_camera_down()),

            self.terrain_selection_buttons[0]: (lambda: self.start_polygon_of_type("fairway")),
            self.terrain_selection_buttons[1]: (lambda: self.start_polygon_of_type("green")),
            self.terrain_selection_buttons[2]: (lambda: self.start_polygon_of_type("bunker")),
            self.terrain_selection_buttons[3]: (lambda: self.start_polygon_of_type("lake")),
            self.terrain_selection_buttons[4]: (lambda: self.start_polygon_of_type("rocks")),
            self.terrain_selection_buttons[5]: (lambda: self.start_polygon_of_type("dirt")),
            self.terrain_selection_buttons[6]: (lambda: self.start_polygon_of_type("darkgreen")),
            self.terrain_selection_buttons[7]: (lambda: self.start_polygon_of_type("darkrocks")),
            self.terrain_selection_buttons[8]: (lambda: self.start_polygon_of_type("darkdirt")),

            self.obstacle_switching_buttons[0]: (lambda: self.switch_obstacles_left_()),
            self.obstacle_switching_buttons[1]: (lambda: self.switch_obstacles_right_()),
        }
        
    def draw(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        # draw the background
        self.screen.blit(self.background, (0, 0))
    
        # Draw the grid if toggled
        if self.action_buttons[5].toggled:  # action_buttons[5] is the grid button
            self.draw_grid(self.screen, self.camera, self.grid_size, self.width, self.height)
    
        for poly in self.list_polygons:
            poly.update(self.screen, self.camera_movement)
    
        # Draw the action bar
        pygame.draw.rect(self.screen, (115, 115, 115), self.action_bar_background)
    
        for button in self.action_buttons:
            button.draw(self.screen)
    
        for button in self.camera_buttons:
            button.draw(self.screen)
    
        for button in self.obstacle_switching_buttons:
            button.draw(self.screen)

        self.obstacle_type_buttons[self.switch_index].draw(self.screen)
    
        # Handle obstacle movement and resizing
        if self.placing_obstacle is not None and self.placing_obstacle.moving:
            self.placing_obstacle.position = mouse_pos
    
        if self.resizing_obstacle is not None:
            self.resizing_obstacle.change_size(mouse_pos)
    
        if self.moving_obstacle is not None:
            self.moving_obstacle.position = mouse_pos + self.drag_offset
    
        # Draw all props
        for obs in self.generated_obstacles:
            obs.update_obstacle(self.screen, self.camera_movement)
            if obs.is_colliding:
                obs.draw_points(self.screen)
    
            # Highlight selected obstacle
            if obs == self.selected_obstacle:
                obs.draw_bounding_box(self.screen, (0, 255, 0))
    
                # Draw the red dot for resizing
                red_dot_rect = pygame.Rect(obs.position.x, obs.position.y, 15, 15)
                pygame.draw.rect(self.screen, (255, 0, 0), red_dot_rect)
    
        if self.obstacle_type_buttons[self.switch_index].toggled:
            for button in self.obstacle_selection_buttons[self.switch_index]:
                button.draw(self.screen)
    
        if self.action_buttons[6].toggled:
            for button in self.props_selection_buttons:
                button.draw(self.screen)
    
        if self.action_buttons[0].toggled:
            for button in self.terrain_selection_buttons:
                button.draw(self.screen)
                if button.text.lower() == self.current_terrain_type:
                    button.contour(self.screen)
    
        # Draw the camera movement
        self.camera_movement = pygame.Vector2(0, 0)


    def clear_list_polygons(self):
        self.list_polygons, self.current_terrain_type= clear(self.list_polygons, self.current_terrain_type)

    def restart_level(self):
        self.list_polygons, self.current_terrain_type = restart()
    
    def quit_level_creator(self):
        self.restart_level()
        self.generated_obstacles = []
        self.switch_scene(self.scene_from)
    
    def move_camera_left(self):
        self.camera, self.camera_movement = camera_left(self.camera, self.camera_speed, self.camera_movement, self.min_width)
    
    def move_camera_right(self):
        self.camera, self.camera_movement = camera_right(self.camera, self.camera_speed, self.camera_movement, self.max_width, self.width)
    
    def move_camera_up(self):
        self.camera, self.camera_movement = camera_up(self.camera, self.camera_speed, self.camera_movement, self.min_height)
    
    def move_camera_down(self):
        self.camera, self.camera_movement = camera_down(self.camera, self.camera_speed, self.camera_movement, self.max_height, self.height)
    
    def start_polygon_of_type(self, new_terrain_type):
        self.list_polygons, self.current_terrain_type = add_polygon_of_type(self.list_polygons, self.current_terrain_type, new_terrain_type)
        if len(self.list_polygons) == 2 and self.list_polygons[0].points == []:
            self.list_polygons.pop(0)
    
    def switch_obstacles_left_(self):
        self.switch_index = switch_obstacles_left(self.obstacle_type_buttons[self.switch_index], self.obstacle_type_buttons)
    
    def switch_obstacles_right_(self):
        self.switch_index = switch_obstacles_right(self.obstacle_type_buttons[self.switch_index], self.obstacle_type_buttons)
    
    
    def generate_obstacle(self, path, colliding:bool, characteristics:str = None):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        if colliding:
            self.obstacle_type_buttons[0].toggled = False
            self.placing_obstacle = Obstacle(mouse_pos, path, 100, colliding, 150)
        elif characteristics is not None:
            self.obstacle_type_buttons[1].toggled = False
            self.placing_obstacle = Obstacle(mouse_pos, path, 100, colliding, 150, characteristic=characteristics)
        else:
            self.action_buttons[6].toggled = False
            self.placing_obstacle = Obstacle(mouse_pos, path, 100, colliding, 150)
        self.placing_obstacle.moving = True
        self.generated_obstacles.append(self.placing_obstacle)
        self.selected_obstacle = self.placing_obstacle
        self.resizing_obstacle = None
        self.moving_obstacle = None
        self.interacted = True

    def snap_to_grid(self, point_actu: pygame.Vector2, grid_size: int):
        return pygame.Vector2(round(point_actu.x / grid_size) * grid_size, round(point_actu.y / grid_size) * grid_size)

    def draw_grid(self, screen, camera, grid_size, width, height, color=(200, 200, 200)):
        # Convert camera coordinates to integers to avoid float rounding issues.
        cam_x = int(camera.x)
        cam_y = int(camera.y)
    
        # Assuming that world-to-screen conversion is:
        # screen_x = world_x - camera.x
        # screen_y = world_y - camera.y
        #
        # We want to draw grid lines at world positions that are multiples of grid_size.
        # Find the first grid line (in world coordinates) that is <= camera position.
        first_x = cam_x - (cam_x % grid_size)
        first_y = cam_y - (cam_y % grid_size)
    
        # Draw vertical grid lines.
        x = first_x
        while x < cam_x + width:
            screen_x = int(x - cam_x)
            pygame.draw.line(screen, color, (screen_x, 0), (screen_x, height))
            x += grid_size
    
        # Draw horizontal grid lines.
        y = first_y
        while y < cam_y + height:
            screen_y = int(y - cam_y)
            pygame.draw.line(screen, color, (0, screen_y), (width, screen_y))
            y += grid_size
            
    def run(self):
        while self.running:
            self.interacted = False
            clicked_control_point = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
        
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.moving_obstacle = None
        
                elif event.type == pygame.KEYDOWN and event.key in self.action_keys.keys():
                    match event.key:
                        case pygame.K_SPACE:
                            last_poly = self.list_polygons[-1]
        
                            while last_poly.points == []:
                                self.list_polygons.pop()
                                last_poly = self.list_polygons[-1]

                            new_poly = Polygon(terrain_type=last_poly.terrain_type, compensates=True)
                            self.list_polygons.append(new_poly)
        
                        case pygame.K_ESCAPE:
                            last_poly = self.list_polygons[-1]
        
                            while last_poly.points == []:
                                self.list_polygons.pop()
                                last_poly = self.list_polygons[-1]
        
                            new_poly = Polygon(terrain_type=last_poly.terrain_type, compensates=False)
                            self.list_polygons.append(new_poly)
        
        
                        case pygame.K_DELETE:
                            if self.selected_obstacle:
                                if self.selected_obstacle in self.generated_obstacles:
                                    self.generated_obstacles.remove(self.selected_obstacle)
                                self.selected_obstacle = self.resizing_obstacle = self.moving_obstacle = None
                        case pygame.K_r:
                            if self.selected_obstacle:
                                self.selected_obstacle.rotate(self.selected_obstacle.angle - 10)  # Rotate -10 degrees
                        case pygame.K_t:
                            if self.selected_obstacle:
                                self.selected_obstacle.rotate(self.selected_obstacle.angle + 10)  # Rotate 10 degrees
        
        
        
                elif event.type == pygame.KEYDOWN and event.key in self.selection_keys.keys() and self.selection_keys[event.key] != self.current_terrain_type:
                    self.list_polygons, self.current_terrain_type = add_polygon_of_type(self.list_polygons, self.current_terrain_type, self.selection_keys[event.key])
        
                # Detect a mouse button press
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.cooldown <= 0:
                    self.last_point = pygame.Vector2(event.pos[0], event.pos[1])
            
                    for button in self.button_to_action.keys():
                        if button.rect.collidepoint(self.last_point) and self.cooldown <= 0:
                            # To avoid triggering the terrain selection buttons when the terrain button is not toggled
                            if button in self.terrain_selection_buttons and not self.action_buttons[0].toggled:
                                continue
    
                            self.button_to_action[button]()
                            self.cooldown = 60
                            self.interacted = True
            
                    # region obstacles Interactions
            
                    # Check if clicking on a button that generate obstacles:
                    if self.obstacle_type_buttons[0].toggled and not self.selected_obstacle and self.switch_index==0:
                        for png_obstacles in range(len(self.obstacle_selection_buttons[self.switch_index])):
                            if self.obstacle_selection_buttons[self.switch_index][png_obstacles].rect.collidepoint(self.last_point) :
                                self.generate_obstacle("assets/images/props/obstacles/" + str(self.obstacles_image_list[png_obstacles]), True)
                                self.has_been_interacted = True
            
            
                    # Check if clicking on a button that generate specials objects:
                    if self.obstacle_type_buttons[1].toggled and not self.selected_obstacle and self.switch_index == 1:
                        for png_specials in range(len(self.obstacle_selection_buttons[self.switch_index])):
                            if self.obstacle_selection_buttons[self.switch_index][png_specials].rect.collidepoint(self.last_point):
                                self.generate_obstacle("assets/images/props/specials/" + str(self.specials_image_list[png_specials]), False, characteristics=self.chara_but_spe[png_specials])
                                self.has_been_interacted = True
            
                    # Check if clicking on a button that generate environment objects:
                    if self.action_buttons[6].toggled and not self.selected_obstacle:
                        for png_environment in range(len(self.props_selection_buttons)):
                            if self.props_selection_buttons[png_environment].rect.collidepoint(self.last_point):
                                self.generate_obstacle("assets/images/props/environment/" + str(self.environment_image_list[png_environment]), False)
                                self.has_been_interacted = True
            
                    if self.interacted:
                        self.interacted = False
            
                    elif self.obstacle_type_buttons[self.switch_index].rect.collidepoint(self.last_point):
                        self.obstacle_type_buttons[self.switch_index].toggle()
            
                    elif self.action_buttons[6].rect.collidepoint(self.last_point):
                        self.action_buttons[6].toggle()
                    # Handle obstacle-specific interactions
                    elif self.action_bar_background.collidepoint(self.last_point):
                        continue
            
            
                    elif self.placing_obstacle is not None and self.placing_obstacle.moving:
                        self.placing_obstacle.place_obstacle(pygame.mouse.get_pos(), pygame.Vector2(0, 0))
                        self.placing_obstacle.moving = False
                        self.placing_obstacle = None
                        self.selected_obstacle = None
                        continue
                    # endregion
            
            
                    # Check if clicking on existing props
                    elif not self.action_bar_background.collidepoint(self.last_point):
                        # Check if clicking on the red dot (for resizing)
                        obstacle_interaction_occurred = False
                        for obs in self.generated_obstacles:
                            red_dot_rect = pygame.Rect(obs.position.x, obs.position.y, 15, 15)
                            if red_dot_rect.collidepoint(self.last_point):
                                self.selected_obstacle = obs
                                # Toggle resize mode
                                if self.resizing_obstacle == obs:
                                    self.resizing_obstacle = None
                                else:
                                    self.resizing_obstacle = obs
                                    self.moving_obstacle = None
                                clicked_control_point = True
                                obstacle_interaction_occurred = True
                                self.interacted = True
                                break
            
                        if not clicked_control_point:
                            # Check if clicking on an obstacle (for moving)
                            for obs in self.generated_obstacles:
                                obstacle_rect = pygame.Rect(
                                    obs.position.x,
                                    obs.position.y,
                                    obs.image.get_width(),
                                    obs.image.get_height()
                                )
                                if obstacle_rect.collidepoint(self.last_point):
                                    self.selected_obstacle = obs
                                    self.moving_obstacle = obs
                                    self.resizing_obstacle = None
                                    self.drag_offset = obs.position - self.last_point
                                    obstacle_interaction_occurred = True
                                    break
            
                        # Only add point to polygon if no obstacle interaction occurred
                        if not obstacle_interaction_occurred:
                            if self.resizing_obstacle is not None:
                                self.interacted = True
            
                            if self.selected_obstacle is not None or self.resizing_obstacle is not None or self.moving_obstacle is not None:
                                # If an obstacle is selected, do not add a point to the polygon
                                self.interacted = True
                            self.selected_obstacle = None
                            self.resizing_obstacle = None
                            self.moving_obstacle = None
            
                            if not self.interacted:
                                if self.list_polygons:
                                    last_poly = self.list_polygons[-1]
                                else:
                                    last_poly = Polygon(terrain_type="fairway")
                                    self.current_terrain_type = "fairway"
                                # If the grid is toggled, snap the point to the grid
                                if self.action_buttons[5].toggled:
                                    self.last_point = self.snap_to_grid(self.last_point, self.grid_size)
                                if last_poly:
                                    last_poly.add_point(self.last_point)
    
                    self.cooldown = 14
            
            self.draw()

            if self.cooldown > 0:
                self.cooldown -= 1
            
            pygame.display.flip()
            self.clock.tick(self.fps)