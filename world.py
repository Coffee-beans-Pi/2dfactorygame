import math
import random

from settings import (
    INITIAL_ZOOM,
    MAP_HEIGHT,
    MAP_WIDTH,
    TILE_COLORS,
    TILE_SIZE,
)


class Tile:
    def __init__(self, x, y, kind="grass"):
        self.x = x
        self.y = y
        self.kind = kind

    @property
    def color(self):
        return TILE_COLORS.get(self.kind, TILE_COLORS["grass"])


class World:
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.tiles = [
            [Tile(x, y) for x in range(width)]
            for y in range(height)
        ]

    def set_kind(self, x, y, kind):
        tile = self.get_tile(x, y)
        if tile is not None:
            tile.kind = kind

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def get_tile_at_world_position(self, world_x, world_y):
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)
        return self.get_tile(tile_x, tile_y)

    def generate(self):
        for y in range(self.height):
            for x in range(self.width):
                if (x * 3 + y) % 11 == 0:
                    self.set_kind(x, y, "rock")
                elif (x + y * 2) % 7 == 0:
                    self.set_kind(x, y, "sand")

        for y in range(self.height):
            for x in range(self.width):
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
                            local_distortion = (
                                distortion + random.uniform(-0.2, 0.2)
                            )
                            if distance < local_distortion:
                                self.set_kind(x + dx, y + dy, "water")


class Camera:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width / 2
        self.y = screen_height / 2
        self.zoom = INITIAL_ZOOM

    def screen_to_world(self, screen_x, screen_y):
        world_x = self.x + (screen_x - self.screen_width / 2) / self.zoom
        world_y = self.y + (screen_y - self.screen_height / 2) / self.zoom
        return world_x, world_y

    def world_to_screen(self, world_x, world_y):
        screen_x = (world_x - self.x) * self.zoom + self.screen_width / 2
        screen_y = (world_y - self.y) * self.zoom + self.screen_height / 2
        return int(screen_x), int(screen_y)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def resize_screen(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def center_on_world(self, world):
        self.x = world.width * TILE_SIZE / 2
        self.y = world.height * TILE_SIZE / 2
        self.clamp_to_world(world)

    def zoom_at(self, screen_x, screen_y, new_zoom):
        world_x, world_y = self.screen_to_world(screen_x, screen_y)
        self.zoom = new_zoom
        self.x = world_x - (screen_x - self.screen_width / 2) / self.zoom
        self.y = world_y - (screen_y - self.screen_height / 2) / self.zoom

    def clamp_to_world(self, world):
        world_width = world.width * TILE_SIZE
        world_height = world.height * TILE_SIZE
        self.x = max(0, min(world_width, self.x))
        self.y = max(0, min(world_height, self.y))
