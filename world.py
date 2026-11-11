import math
import random

from item_data import get_item_properties
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
        self.placed_object = None
        self.machine = None
        self.bonsai = None

    @property
    def color(self):
        return TILE_COLORS.get(self.kind, TILE_COLORS["grass"])


class World:
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.machines = []
        self.bonsais = []
        self.render_revision = 0
        self.tiles = [
            [Tile(x, y) for x in range(width)]
            for y in range(height)
        ]

    def set_kind(self, x, y, kind):
        tile = self.get_tile(x, y)
        if tile is not None and tile.kind != kind:
            tile.kind = kind
            self.render_revision += 1

    def place_object(self, x, y, object_kind):
        tile = self.get_tile(x, y)
        if tile is None or tile.placed_object is not None:
            return False
        tile.placed_object = object_kind
        self.render_revision += 1
        if object_kind == "furnace":
            tile.machine = Furnace()
            self.machines.append(tile.machine)
        elif object_kind == "bonsai":
            tile.bonsai = Bonsai()
            self.bonsais.append(tile.bonsai)
        return True

    def update_machines(self, delta_time):
        for machine in self.machines:
            machine.update(delta_time)
        for bonsai in self.bonsais:
            if bonsai.update(delta_time):
                self.render_revision += 1

    def insert_item(self, x, y, item):
        tile = self.get_tile(x, y)
        if tile is None or tile.machine is None:
            return False
        return tile.machine.insert_item(item)

    def take_machine_output(self, x, y):
        tile = self.get_tile(x, y)
        if tile is None or tile.machine is None:
            return None
        return tile.machine.take_output()

    def remove_object(self, x, y):
        tile = self.get_tile(x, y)
        if tile is None or tile.placed_object is None:
            return None, []

        object_kind = tile.placed_object
        recovered_items = []
        if tile.machine is not None:
            recovered_items = tile.machine.get_all_items()
            self.machines.remove(tile.machine)
        if tile.bonsai is not None:
            self.bonsais.remove(tile.bonsai)
        tile.placed_object = None
        tile.machine = None
        tile.bonsai = None
        self.render_revision += 1
        return object_kind, recovered_items

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


class Furnace:
    def __init__(self):
        self.fuel_items = []
        self.smelt_queue = []
        self.output_items = []
        self.smelt_timer = 0.0
        self.burning = False

    def insert_item(self, item):
        properties = get_item_properties(item)
        if properties.burnable:
            self.fuel_items.append(item)
            self.burning = True
            return True
        if properties.smeltable and properties.smelt_result is not None:
            self.smelt_queue.append(item)
            return True
        return False

    def update(self, delta_time):
        if self.fuel_items and self.smelt_queue:
            self.burning = True
            self.smelt_timer += delta_time
            while (
                self.smelt_timer >= 1
                and self.fuel_items
                and self.smelt_queue
            ):
                self.smelt_timer -= 1
                self.fuel_items.pop(0)
                item = self.smelt_queue.pop(0)
                result = get_item_properties(item).smelt_result
                if result is not None:
                    self.output_items.append(result)

        self.burning = bool(self.fuel_items)
        if not self.fuel_items or not self.smelt_queue:
            self.smelt_timer = 0.0

    def take_output(self):
        if not self.output_items:
            return None
        return self.output_items.pop(0)

    def insert_fuel(self, item):
        if not get_item_properties(item).burnable:
            return False
        self.fuel_items.append(item)
        self.burning = True
        return True

    def insert_material(self, item):
        properties = get_item_properties(item)
        if not properties.smeltable or properties.smelt_result is None:
            return False
        self.smelt_queue.append(item)
        return True

    def get_all_items(self):
        items = self.fuel_items + self.smelt_queue + self.output_items
        self.fuel_items = []
        self.smelt_queue = []
        self.output_items = []
        self.smelt_timer = 0.0
        self.burning = False
        return items


class Bonsai:
    GROWTH_TIME = 30.0
    SOIL_AMOUNT = 8
    PLANT_YIELDS = {
        "seed": "hemp",
        "sapling": "wood",
    }
    PLANT_ITEMS = tuple(PLANT_YIELDS)

    def __init__(self):
        self.dirt_filled = False
        self.planted_item = None
        self.growth_timer = 0.0
        self.grown = False

    def add_dirt(self, amount):
        if self.dirt_filled or amount < self.SOIL_AMOUNT:
            return False
        self.dirt_filled = True
        return True

    def plant(self, item):
        if (
            not self.dirt_filled
            or self.planted_item is not None
            or self.grown
            or item not in self.PLANT_ITEMS
        ):
            return False
        self.planted_item = item
        self.growth_timer = 0.0
        return True

    def update(self, delta_time):
        if self.planted_item is None or self.grown:
            return False
        self.growth_timer += delta_time
        if self.growth_timer < self.GROWTH_TIME:
            return False
        self.grown = True
        return True

    def harvest(self):
        if not self.grown or self.planted_item is None:
            return None
        yield_item = self.PLANT_YIELDS[self.planted_item]
        self.planted_item = None
        self.growth_timer = 0.0
        self.grown = False
        return yield_item


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
