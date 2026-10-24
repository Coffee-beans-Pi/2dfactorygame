import pygame

from inventory import Hotbar, Inventory
from recipes import craft_recipe, get_craftable_recipes
from settings import (
    CAMERA_MOVE_SPEED,
    CRAFTING_MARGIN,
    CRAFTING_ROW_HEIGHT,
    CRAFTING_ROW_WIDTH,
    MAP_HEIGHT,
    MAP_WIDTH,
    MAX_ZOOM,
    MIN_ZOOM,
    RESOURCE_BY_TILE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from world import Camera, World


class Game:
    def __init__(self):
        self.world = World(MAP_WIDTH, MAP_HEIGHT)
        self.world.generate()
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera.center_on_world(self.world)
        self.inventory = Inventory()
        self.hotbar = Hotbar()
        self.inventory_visible = False
        self.running = True
        self.drag_last_pos = None

    def resize_screen(self, screen_width, screen_height):
        self.camera.resize_screen(screen_width, screen_height)
        self.camera.clamp_to_world(self.world)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.inventory_visible = not self.inventory_visible
            self.drag_last_pos = None
            return

        if self.inventory_visible:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_crafting_click(event.pos)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_world_click(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.drag_last_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self.drag_last_pos = None
        elif event.type == pygame.MOUSEMOTION and self.drag_last_pos is not None:
            self._handle_camera_drag(event.pos)
        elif event.type == pygame.MOUSEWHEEL:
            self._handle_mouse_wheel(event)
        elif event.type == pygame.KEYDOWN:
            self._handle_key_down(event.key)

    def _handle_world_click(self, screen_position):
        world_position = self.camera.screen_to_world(*screen_position)
        tile = self.world.get_tile_at_world_position(*world_position)
        if tile is None or tile.kind == "water":
            return

        if self.hotbar.selected_item() == "pickaxe":
            resource = RESOURCE_BY_TILE.get(tile.kind)
            if resource is not None:
                self.inventory.add(resource)

    def _handle_crafting_click(self, screen_position):
        mouse_x, mouse_y = screen_position
        recipes = get_craftable_recipes(self.inventory)
        first_recipe_y = (
            self.camera.screen_height
            - CRAFTING_MARGIN
            - CRAFTING_ROW_HEIGHT
        )
        for index, recipe in enumerate(recipes):
            recipe_y = first_recipe_y - index * CRAFTING_ROW_HEIGHT
            if (
                CRAFTING_MARGIN <= mouse_x
                < CRAFTING_MARGIN + CRAFTING_ROW_WIDTH
                and recipe_y <= mouse_y < recipe_y + CRAFTING_ROW_HEIGHT
            ):
                craft_recipe(self.inventory, recipe)
                return

    def _handle_camera_drag(self, mouse_position):
        mouse_x, mouse_y = mouse_position
        last_x, last_y = self.drag_last_pos
        self.camera.move(
            -(mouse_x - last_x) / self.camera.zoom,
            -(mouse_y - last_y) / self.camera.zoom,
        )
        self.camera.clamp_to_world(self.world)
        self.drag_last_pos = mouse_position

    def _handle_mouse_wheel(self, event):
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            new_zoom = max(
                MIN_ZOOM,
                min(MAX_ZOOM, self.camera.zoom + event.y * 0.1),
            )
            if new_zoom != self.camera.zoom:
                self.camera.zoom_at(*pygame.mouse.get_pos(), new_zoom)
        elif self.hotbar.slots:
            self.hotbar.select(
                (self.hotbar.selected_index - event.y)
                % len(self.hotbar.slots)
            )

    def _handle_key_down(self, key):
        if pygame.K_1 <= key <= pygame.K_9:
            self.hotbar.select(key - pygame.K_1)

    def update(self, keys):
        if self.inventory_visible:
            return

        dx = 0
        dy = 0
        if keys[pygame.K_a]:
            dx -= CAMERA_MOVE_SPEED
        if keys[pygame.K_d]:
            dx += CAMERA_MOVE_SPEED
        if keys[pygame.K_w]:
            dy -= CAMERA_MOVE_SPEED
        if keys[pygame.K_s]:
            dy += CAMERA_MOVE_SPEED

        self.camera.move(dx, dy)
        self.camera.clamp_to_world(self.world)
