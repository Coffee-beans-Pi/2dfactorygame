import math
import random

import pygame

from inventory import Hotbar, Inventory
from recipes import craft_recipe, get_craftable_recipes
from settings import (
    CAMERA_MOVE_SPEED,
    CRAFTING_MARGIN,
    CRAFTING_ROW_HEIGHT,
    CRAFTING_ROW_WIDTH,
    EXTRA_RESOURCE_CHANCE_BY_TIER,
    EXTRA_RESOURCES_BY_TILE_AND_TIER,
    INVENTORY_COLUMNS,
    INVENTORY_HOTBAR_GAP,
    INVENTORY_PANEL_PADDING,
    INVENTORY_ROWS,
    MAP_HEIGHT,
    MAP_WIDTH,
    MAX_ZOOM,
    MIN_ZOOM,
    RESOURCE_BY_TILE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SLOT_GAP,
    SLOT_SIZE,
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
        self.cursor_item = None
        self.cursor_count = 0
        self.item_effects = []

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
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button in (1, 3)
            ):
                shift_held = bool(
                    pygame.key.get_mods() & pygame.KMOD_SHIFT
                )
                self._handle_inventory_click(
                    event.pos,
                    event.button,
                    shift_held,
                )
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
                self._spawn_item_effect(resource, screen_position)
                extra_resources = EXTRA_RESOURCES_BY_TILE_AND_TIER.get(
                    (tile.kind, self.hotbar.pickaxe_tier),
                    (),
                )
                extra_chance = EXTRA_RESOURCE_CHANCE_BY_TIER.get(
                    self.hotbar.pickaxe_tier,
                    0,
                )
                if extra_resources and random.random() < extra_chance:
                    extra_resource = random.choice(extra_resources)
                    self.inventory.add(extra_resource)
                    self._spawn_item_effect(extra_resource, screen_position)

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
                if craft_recipe(self.inventory, recipe):
                    self._spawn_item_effect(
                        recipe.result,
                        screen_position,
                        recipe.amount,
                    )
                return True
        return False

    def _spawn_item_effect(self, item, screen_position, amount=1):
        for _ in range(min(amount, 6)):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(70, 150)
            self.item_effects.append({
                "item": item,
                "x": float(screen_position[0]),
                "y": float(screen_position[1]),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "rotation": random.uniform(0, 360),
                "rotation_speed": random.choice((-1, 1))
                * random.uniform(180, 540),
                "age": 0.0,
                "lifetime": 0.55,
            })

    def _handle_inventory_click(
        self,
        screen_position,
        button,
        shift_held=False,
    ):
        if (
            button == 1
            and not shift_held
            and self._handle_crafting_click(screen_position)
        ):
            return

        slot_step = SLOT_SIZE + SLOT_GAP
        grid_x = (
            self.camera.screen_width
            - (
                INVENTORY_COLUMNS * SLOT_SIZE
                + (INVENTORY_COLUMNS - 1) * SLOT_GAP
                + INVENTORY_PANEL_PADDING * 2
            )
        ) // 2 + INVENTORY_PANEL_PADDING
        slot_rows_height = (
            INVENTORY_ROWS * SLOT_SIZE + (INVENTORY_ROWS - 1) * SLOT_GAP
        )
        grid_y = (
            self.camera.screen_height
            - (
                slot_rows_height + INVENTORY_HOTBAR_GAP + SLOT_SIZE
                + INVENTORY_PANEL_PADDING * 2
            )
        ) // 2 + INVENTORY_PANEL_PADDING

        for index in range(INVENTORY_COLUMNS * INVENTORY_ROWS):
            row, column = divmod(index, INVENTORY_COLUMNS)
            x = grid_x + column * slot_step
            y = grid_y + row * slot_step
            if pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE).collidepoint(
                screen_position
            ):
                if shift_held and button == 1:
                    self._quick_move_inventory_slot(index)
                else:
                    self._click_inventory_slot(index, button)
                return

        hotbar_y = grid_y + slot_rows_height + INVENTORY_HOTBAR_GAP
        for index in range(len(self.hotbar.slots)):
            x = grid_x + index * slot_step
            if pygame.Rect(x, hotbar_y, SLOT_SIZE, SLOT_SIZE).collidepoint(
                screen_position
            ):
                if shift_held and button == 1:
                    self._quick_move_hotbar_slot(index)
                else:
                    self._click_hotbar_slot(index, button)
                return

    def _quick_move_inventory_slot(self, index):
        items = list(self.inventory.items.items())
        if index >= len(items):
            return

        item, count = items[index]
        if item == "pickaxe":
            return
        if not self.hotbar.quick_add(item, count):
            return
        self.inventory.remove(item, count)

    def _quick_move_hotbar_slot(self, index):
        item = self.hotbar.slots[index]
        count = self.hotbar.counts[index]
        if item is None or item == "pickaxe":
            return

        self.inventory.add(item, count)
        self.hotbar.remove_from_slot(index, count)

    def _click_inventory_slot(self, index, button):
        items = list(self.inventory.items.items())
        target = items[index] if index < len(items) else None

        if self.cursor_item is None:
            if target is None or target[0] == "pickaxe":
                return
            item, count = target
            amount = count if button == 1 else (count + 1) // 2
            if amount == 0:
                return
            self.inventory.remove(item, amount)
            self.cursor_item = item
            self.cursor_count = amount
            return

        if target is not None and target[0] == "pickaxe":
            return

        if target is not None and target[0] != self.cursor_item:
            if button == 1:
                item, count = target
                self.inventory.remove(item, count)
                self.inventory.add(self.cursor_item, self.cursor_count)
                self.cursor_item = item
                self.cursor_count = count
            return

        amount = self.cursor_count if button == 1 else 1
        self.inventory.add(self.cursor_item, amount)
        self._reduce_cursor_stack(amount)

    def _click_hotbar_slot(self, index, button):
        target_item = self.hotbar.slots[index]
        target_count = self.hotbar.counts[index]

        if self.cursor_item is None:
            if target_item is None or target_item == "pickaxe":
                return
            amount = (
                target_count if button == 1 else (target_count + 1) // 2
            )
            if amount == 0:
                return
            self.hotbar.remove_from_slot(index, amount)
            self.cursor_item = target_item
            self.cursor_count = amount
            return

        if target_item == "pickaxe":
            return
        if target_item is not None and target_item != self.cursor_item:
            if button == 1:
                self.hotbar.set_slot(
                    index,
                    self.cursor_item,
                    self.cursor_count,
                )
                self.cursor_item = target_item
                self.cursor_count = target_count
            return

        amount = self.cursor_count if button == 1 else 1
        self.hotbar.add_to_slot(index, self.cursor_item, amount)
        self._reduce_cursor_stack(amount)

    def _reduce_cursor_stack(self, amount):
        self.cursor_count -= amount
        if self.cursor_count == 0:
            self.cursor_item = None

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

    def update(self, keys, delta_time=1 / 60):
        active_effects = []
        for effect in self.item_effects:
            previous_age = effect["age"]
            effect["age"] += delta_time
            if effect["age"] >= effect["lifetime"]:
                continue
            progress = (
                previous_age + effect["age"]
            ) / (2 * effect["lifetime"])
            speed_factor = max(0, 1 - progress)
            effect["x"] += effect["vx"] * delta_time * speed_factor
            effect["y"] += effect["vy"] * delta_time * speed_factor
            effect["rotation"] = (
                effect["rotation"]
                + effect["rotation_speed"] * delta_time * speed_factor
            ) % 360
            active_effects.append(effect)
        self.item_effects = active_effects

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
