import pygame
import random
import math
from pathlib import Path
import os

pygame.init()

os.environ["SDL_VIDEO_WINDOW_POS"] = "center"

pygame.display.set_mode()

ASSET_DIR = Path(__file__).parent/ "assets"

ITEM_IMAGES = {
    "pickaxe": pygame.image.load(
        ASSET_DIR / "PickNew.png"
    ).convert_alpha()
}

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("factory_game")

clock = pygame.time.Clock()

TILE_SIZE = 40
camera_x = SCREEN_WIDTH / 2
camera_y = SCREEN_HEIGHT / 2
zoom = 1.0
MIN_ZOOM = 0.5
MAX_ZOOM = 3.0

TILE_COLORS = {
    "grass": (110, 170, 90),
    "water": (74, 120, 180),
    "rock": (128, 122, 112),
    "sand": (214, 194, 120),
}


class Tile:
    def __init__(self, x, y, kind="grass"):
        self.x = x
        self.y = y
        self.kind = kind
        self.selected = False

    @property
    def color(self):
        return TILE_COLORS.get(self.kind, TILE_COLORS["grass"])

    def handle_click(self):
        self.selected = not self.selected
        return self


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = []

        for y in range(height):
            row = []
            for x in range(width):
                row.append(Tile(x, y, "grass"))
            self.tiles.append(row)

    def set_kind(self, x, y, kind):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x].kind = kind

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def get_tile_from_screen(self, screen_x, screen_y):
        world_x = camera_x + (screen_x - SCREEN_WIDTH / 2) / zoom
        world_y = camera_y + (screen_y - SCREEN_HEIGHT / 2) / zoom
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)
        return self.get_tile(tile_x, tile_y)

    def draw(self, surface):
        tile_pixels = max(1, int(TILE_SIZE * zoom))

        for row in self.tiles:
            for tile in row:
                world_x = tile.x * TILE_SIZE
                world_y = tile.y * TILE_SIZE
                screen_x = int((world_x - camera_x) * zoom + SCREEN_WIDTH / 2)
                screen_y = int((world_y - camera_y) * zoom + SCREEN_HEIGHT / 2)

                if (
                    screen_x + tile_pixels < -10
                    or screen_x > SCREEN_WIDTH + 10
                    or screen_y + tile_pixels < -10
                    or screen_y > SCREEN_HEIGHT + 10
                ):
                    continue

                pygame.draw.rect(surface, tile.color, (screen_x, screen_y, tile_pixels, tile_pixels))

                pygame.draw.line(surface, (63, 63, 63), (screen_x, screen_y), (screen_x + tile_pixels, screen_y), 1)
                pygame.draw.line(surface, (63, 63, 63), (screen_x, screen_y), (screen_x, screen_y + tile_pixels), 1)
                pygame.draw.line(surface, (63, 63, 63), (screen_x + tile_pixels, screen_y), (screen_x + tile_pixels, screen_y + tile_pixels), 1)
                pygame.draw.line(surface, (63, 63, 63), (screen_x, screen_y + tile_pixels), (screen_x + tile_pixels, screen_y + tile_pixels), 1)

                if tile.selected:
                    pygame.draw.rect(surface, (255, 255, 255), (screen_x, screen_y, tile_pixels, tile_pixels), 3)


map_data = Map(300, 200)

def map_creation():
    for y in range(map_data.height):
        for x in range(map_data.width):
            if (x * 3 + y) % 11 == 0:
                map_data.set_kind(x, y, "rock")
            elif (x + y * 2) % 7 == 0:
                map_data.set_kind(x, y, "sand")

    for y in range(map_data.height):
        for x in range(map_data.width):
            if random.random() < 0.0025:
                radius_x = random.uniform(5, 8)
                radius_y = random.uniform(5, 8)
                angle = random.uniform(0, 2 * math.pi)

                distortion = random.uniform(0.7, 1.3)

                for dy in range(-10, 11):
                    for dx in range(-10, 11):
                        rx = dx * math.cos(angle) - dy * math.sin(angle)
                        ry = dx * math.sin(angle) + dy * math.cos(angle)

                        distance = (
                            (rx / radius_x) ** 2
                            + (ry / radius_y) ** 2
                        )

                        local_distortion = distortion + random.uniform(-0.2, 0.2)
                        if distance < local_distortion:
                            map_data.set_kind(x + dx, y + dy, "water")


def clamp_camera(camera_x, camera_y):
    map_width = map_data.width * TILE_SIZE
    map_height = map_data.height * TILE_SIZE
    camera_x = max(0, min(map_width, camera_x))
    camera_y = max(0, min(map_height, camera_y))
    return camera_x, camera_y

class Hotbar:
    def __init__(self):
        self.slots = [
            "pickaxe", None, None, None, None, None, None, None, None, None
        ]
        self.selected_index = 0

        self.slot_size = 50
        self.gap = 4

    def selected_item(self):
        return self.slots[self.selected_index]

    def select(self, index):
        if 0 <= index < len(self.slots):
            self.selected_index = index

    def draw(self, screen):
        total_width = len(self.slots) * (self.slot_size + self.gap) - self.gap
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT - self.slot_size - 15

        for i, item in enumerate(self.slots):
            x = start_x + i * (self.slot_size + self.gap)

            pygame.draw.rect(
                screen, (65, 65, 65),
                (x, y, self.slot_size, self.slot_size)
            )

            if i == self.selected_index:
                color = (255, 255, 255)
                width = 3
            else:
                color = (130, 130, 130)
                width = 1

            pygame.draw.rect(
                screen, color,
                (x, y, self.slot_size, self.slot_size),
                width
            )

            if item in ITEM_IMAGES:
                image = ITEM_IMAGES[item]

                image_rect = image.get_rect(
                    center=(x + self.slot_size // 2,
                            y + self.slot_size // 2)
                )

                screen.blit(image, image_rect)

hotbar = Hotbar()

class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, item, amount=1):
        self.items[item] = self.items.get(item, 0) + amount

    def remove(self, item, amount=1):
        if self.items.get(item, 0) < amount:
            return False

        self.items[item] -= amount
        return True

    def count(self, item):
        return self.items.get(item, 0)

camera_x, camera_y = clamp_camera(camera_x, camera_y)

inventory = Inventory()

running = True
drag_last_pos = None

map_creation()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_tile = map_data.get_tile_from_screen(*event.pos)
            if clicked_tile is not None:
                clicked_tile.handle_click()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            drag_last_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            drag_last_pos = None
        elif event.type == pygame.MOUSEMOTION and drag_last_pos is not None:
            mouse_x, mouse_y = event.pos
            last_x, last_y = drag_last_pos
            camera_x -= (mouse_x - last_x) / zoom
            camera_y -= (mouse_y - last_y) / zoom
            camera_x, camera_y = clamp_camera(camera_x, camera_y)
            drag_last_pos = event.pos
        elif event.type == pygame.MOUSEWHEEL:
            mods = pygame.key.get_mods()

            if mods & pygame.KMOD_SHIFT:
                old_zoom = zoom
                zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom + event.y * 0.1))

                if zoom != old_zoom:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x = camera_x + (mouse_x - SCREEN_WIDTH / 2) / old_zoom
                    world_y = camera_y + (mouse_y - SCREEN_HEIGHT / 2) / old_zoom

                    camera_x = world_x - (mouse_x - SCREEN_WIDTH / 2) / zoom
                    camera_y = world_y - (mouse_y - SCREEN_HEIGHT / 2) / zoom

            else:
                hotbar.select(
                    (hotbar.selected_index - event.y) % len(hotbar.slots)
                )

        elif event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                hotbar.select(event.key - pygame.K_1)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_tile = map_data.get_tile_from_screen(*event.pos)

                if clicked_tile is not None:
                    inventory.add("stone", 1)

    screen.fill((30, 30, 30))

    keys = pygame.key.get_pressed()
    move_speed = 5

    if keys[pygame.K_LEFT]:
        camera_x -= move_speed
    if keys[pygame.K_RIGHT]:
        camera_x += move_speed
    if keys[pygame.K_UP]:
        camera_y -= move_speed
    if keys[pygame.K_DOWN]:
        camera_y += move_speed

    camera_x, camera_y = clamp_camera(camera_x, camera_y)

    map_data.draw(screen)
    hotbar.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()