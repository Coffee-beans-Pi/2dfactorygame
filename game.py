import pygame

from inventory import Hotbar, Inventory
from settings import (
    CAMERA_MOVE_SPEED,
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
        self.camera.clamp_to_world(self.world)
        self.inventory = Inventory()
        self.hotbar = Hotbar()
        self.inventory_visible = False
        self.running = True
        self.drag_last_pos = None

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
        if key == pygame.K_e:
            self.inventory_visible = not self.inventory_visible

    def update(self, keys):
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
