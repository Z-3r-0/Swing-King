from src.scene import Scene, SceneType

import src.utils.level_export as export
from src.hud.level_creator_hud import *
from src.hud.level_creator_hud import obstacle_selection_buttons
from src.utils import load_json_level, json_to_list


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

        # HUD to load and modify existing levels
        self.HUD_load_level = False
        self.loadable_levels = [f for f in os.listdir("data/levels/") if f.endswith(".json")]
        self.loadable_levels = sort_levels(self.loadable_levels)
        self.load_level_scroll_offset = 0

        self.has_been_interacted = False
        self.export_feedback_timer = 0
        self.export_font = pygame.font.SysFont("Impact", 110)

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
            self.action_buttons[9]: (lambda: self.load_list_levels()),

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

        #Hud for loading levels
        if self.HUD_load_level:
            # Define HUD properties
            hud_width = self.width * 0.3
            hud_height = self.height * 0.6
            hud_x = (self.width - hud_width) / 2
            hud_y = (self.height - hud_height) / 2
            hud_rect = pygame.Rect(hud_x, hud_y, hud_width, hud_height)

            # Draw a semi-transparent background for the HUD
            hud_surface = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
            hud_surface.fill((50, 50, 50, 220))
            self.screen.blit(hud_surface, (hud_x, hud_y))
            pygame.draw.rect(self.screen, (200, 200, 200), hud_rect, 2)

            # Draw the title
            title_font = pygame.font.SysFont("Arial", 26)
            title_surface = title_font.render("Select a Level", True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(self.width / 2, hud_y + 25))
            self.screen.blit(title_surface, title_rect)

            # Define the area where the list items will be drawn
            list_area_rect = pygame.Rect(hud_x + 10, hud_y + 50, hud_width - 20, hud_height - 60)

            # --- SCROLLBAR LOGIC ---
            button_height_with_padding = 40
            content_height = len(self.loadable_levels) * button_height_with_padding
            visible_area_height = list_area_rect.height

            if content_height > visible_area_height:
                # Draw scrollbar track
                scrollbar_track_rect = pygame.Rect(list_area_rect.right - 12, list_area_rect.top, 10,
                                                   list_area_rect.height)
                pygame.draw.rect(self.screen, (30, 30, 30), scrollbar_track_rect)

                # Draw scrollbar thumb
                thumb_height = max(20, (visible_area_height / content_height) * visible_area_height)
                scroll_percentage = self.load_level_scroll_offset / (content_height - visible_area_height)
                thumb_y = list_area_rect.top + scroll_percentage * (visible_area_height - thumb_height)
                scrollbar_thumb_rect = pygame.Rect(scrollbar_track_rect.left, thumb_y, 10, thumb_height)
                pygame.draw.rect(self.screen, (150, 150, 150), scrollbar_thumb_rect)

            # --- LIST DRAWING LOGIC ---
            # Set a clipping region to prevent drawing outside the list area
            self.screen.set_clip(list_area_rect)

            button_width = list_area_rect.width - 15  # Make space for scrollbar
            button_height = 35
            start_y = list_area_rect.top

            for i, level_name in enumerate(self.loadable_levels):
                button_x = list_area_rect.left
                # Calculate button position with scroll offset
                button_y = start_y + i * button_height_with_padding - self.load_level_scroll_offset

                display_name = level_name.replace(".json", "").replace("_", " ").title()
                level_button = Button(
                    position=pygame.Vector2(button_x, button_y),
                    dimensions=pygame.Vector2(button_width, button_height),
                    text=display_name,
                    color=(80, 80, 120),
                    font_size=20
                )

                # Only draw the button if it's visible within the clipped area
                if level_button.rect.colliderect(list_area_rect):
                    if level_button.rect.collidepoint(mouse_pos):
                        level_button.color = (110, 110, 150)
                    level_button.draw(self.screen)

            # Reset the clipping region to the full screen
            self.screen.set_clip(None)

        if self.export_feedback_timer > 0:
            # 1. Create the text surface
            text_to_render = "EXPORTED WITH SUCCES AND LOTS OF FUN"
            text_surface = self.export_font.render(text_to_render, True, (255,255,255))  # Bright green color

            # 2. Rotate the text surface
            rotated_surface = pygame.transform.rotate(text_surface, -10)  # Rotate 30 degrees counter-clockwise

            # 3. Get the new rectangle and center it on the screen
            rotated_rect = rotated_surface.get_rect(center=(self.screen.get_rect().centerx, self.screen.get_rect().centery - 100))

            # 4. Draw (blit) the rotated text onto the screen
            self.screen.blit(rotated_surface, rotated_rect)

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

    def load_list_levels(self):
        """Load the list of levels from the levels directory."""
        self.loadable_levels = [f for f in os.listdir("data/levels/") if f.endswith(".json")]
        self.loadable_levels = sort_levels(self.loadable_levels)
        setattr(self, "HUD_load_level", not self.HUD_load_level)

    def load_level_from_name(self, level_name: str):
        """Handles the action of clicking a level in the load HUD."""
        self.restart_level()
        poly_data, obs_data = load_json_level(f"data/levels/{level_name}")
        self.list_polygons, self.generated_obstacles = json_to_list(poly_data, self.screen, 0, True), json_to_list(obs_data, self.screen, 1, True)
        self.HUD_load_level = False  # Close the HUD after selection

    def run(self):
        
        super().run()
        
        while self.running:
            self.interacted = False
            clicked_control_point = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.moving_obstacle = None
        
                elif event.type == pygame.KEYDOWN and event.key in self.action_keys.keys() and not self.HUD_load_level:
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
        
        
        
                elif event.type == pygame.KEYDOWN and event.key in self.selection_keys.keys() and self.selection_keys[event.key] != self.current_terrain_type and not self.HUD_load_level:
                    self.list_polygons, self.current_terrain_type = add_polygon_of_type(self.list_polygons, self.current_terrain_type, self.selection_keys[event.key])

                elif event.type == pygame.MOUSEWHEEL and self.HUD_load_level:
                    scroll_speed = 20  # Pixels to scroll per wheel turn
                    self.load_level_scroll_offset -= event.y * scroll_speed

                    # Define the scrollable area height
                    hud_height = self.height * 0.6
                    content_height = len(self.loadable_levels) * 40  # 35px button + 5px padding
                    visible_area_height = hud_height - 60  # Subtract padding for title etc.

                    # Clamp the scroll offset to prevent scrolling past the content
                    max_scroll = max(0, content_height - visible_area_height)
                    self.load_level_scroll_offset = max(0, min(self.load_level_scroll_offset, max_scroll))
                    self.interacted = True  # Prevent other actions while scrolling

                # Detect a mouse button press
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.cooldown <= 0:
                    self.last_point = pygame.Vector2(event.pos[0], event.pos[1])

                    # If the load level HUD is open, handle its clicks exclusively.
                    if self.HUD_load_level:
                        hud_width = self.width * 0.3
                        hud_height = self.height * 0.6
                        hud_x = (self.width - hud_width) / 2
                        hud_y = (self.height - hud_height) / 2

                        # Check for a click on the close button (which isn't in the main button list)
                        close_button_rect = pygame.Rect(hud_x + hud_width - 35, hud_y + 5, 30, 30)
                        if close_button_rect.collidepoint(self.last_point):
                            self.HUD_load_level = False
                            self.interacted = True
                            self.cooldown = 14
                            continue  # Skip all other click logic

                        # Check for clicks on the dynamic level buttons
                        list_area_rect = pygame.Rect(hud_x + 10, hud_y + 50, hud_width - 20, hud_height - 60)
                        if list_area_rect.collidepoint(self.last_point):
                            button_width = list_area_rect.width - 15
                            button_height = 35
                            button_height_with_padding = 40
                            start_y = list_area_rect.top

                            for i, level_name in enumerate(self.loadable_levels):
                                button_y = start_y + i * button_height_with_padding - self.load_level_scroll_offset
                                level_button_rect = pygame.Rect(list_area_rect.left, button_y, button_width,
                                                                button_height)

                                # Check if this specific button was clicked
                                if level_button_rect.collidepoint(self.last_point):
                                    self.load_level_from_name(level_name)
                                    self.interacted = True
                                    self.cooldown = 14
                                    break  # Exit the loop once a button is clicked
                            continue  # Skip all other click logic

                        # If the click was on the HUD but not on a button, still consume the click
                        if pygame.Rect(hud_x, hud_y, hud_width, hud_height).collidepoint(self.last_point):
                            self.interacted = True
                            continue

                    for button in self.button_to_action.keys():

                        if button.rect.collidepoint(self.last_point) and self.cooldown <= 0:
                            # To avoid triggering the terrain selection buttons when the terrain button is not toggled
                            if button in self.terrain_selection_buttons and not self.action_buttons[0].toggled:
                                continue
                            if button == self.action_buttons[7]:
                                self.export_feedback_timer = 180
                            self.button_to_action[button]()
                            self.cooldown = 60
                            self.interacted = True
                    if self.HUD_load_level:
                        continue
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

            if self.export_feedback_timer > 0:
                self.export_feedback_timer -= 1
            
            pygame.display.flip()
            self.clock.tick(self.fps)