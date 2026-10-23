from pathlib import Path

import pygame

from settings import (
    BACKGROUND_COLOR,
    GRID_COLOR,
    HOVER_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
    UI_BORDER_COLOR,
    UI_SLOT_COLOR,
)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        asset_dir = Path(__file__).parent / "assets"
        self.item_images = {
            "pickaxe": pygame.image.load(
                asset_dir / "PickNew.png"
            ).convert_alpha()
        }
        self.count_font = pygame.font.Font(None, 24)

    def draw(self, game):
        self.screen.fill(BACKGROUND_COLOR)
        self._draw_world(game.world, game.camera)
        self._draw_hovered_tile(game.world, game.camera)
        self._draw_hotbar(game.hotbar)
        if game.inventory_visible:
            self._draw_inventory(game.inventory)
        pygame.display.flip()

    def _draw_world(self, world, camera):
        tile_pixels = max(1, int(TILE_SIZE * camera.zoom))

        for row in world.tiles:
            for tile in row:
                screen_x, screen_y = camera.world_to_screen(
                    tile.x * TILE_SIZE,
                    tile.y * TILE_SIZE,
                )
                if (
                    screen_x + tile_pixels < -10
                    or screen_x > SCREEN_WIDTH + 10
                    or screen_y + tile_pixels < -10
                    or screen_y > SCREEN_HEIGHT + 10
                ):
                    continue

                tile_rect = (screen_x, screen_y, tile_pixels, tile_pixels)
                pygame.draw.rect(self.screen, tile.color, tile_rect)
                pygame.draw.line(
                    self.screen, GRID_COLOR,
                    (screen_x, screen_y),
                    (screen_x + tile_pixels, screen_y),
                    1,
                )
                pygame.draw.line(
                    self.screen, GRID_COLOR,
                    (screen_x, screen_y),
                    (screen_x, screen_y + tile_pixels),
                    1,
                )
                pygame.draw.line(
                    self.screen, GRID_COLOR,
                    (screen_x + tile_pixels, screen_y),
                    (screen_x + tile_pixels, screen_y + tile_pixels),
                    1,
                )
                pygame.draw.line(
                    self.screen, GRID_COLOR,
                    (screen_x, screen_y + tile_pixels),
                    (screen_x + tile_pixels, screen_y + tile_pixels),
                    1,
                )

    def _draw_hovered_tile(self, world, camera):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x, world_y = camera.screen_to_world(mouse_x, mouse_y)
        tile = world.get_tile_at_world_position(world_x, world_y)
        if tile is None:
            return

        tile_pixels = max(1, int(TILE_SIZE * camera.zoom))
        screen_x, screen_y = camera.world_to_screen(
            tile.x * TILE_SIZE,
            tile.y * TILE_SIZE,
        )
        pygame.draw.rect(
            self.screen,
            HOVER_COLOR,
            (screen_x, screen_y, tile_pixels, tile_pixels),
            1,
        )

    def _draw_hotbar(self, hotbar):
        slot_size = 50
        gap = 4
        total_width = len(hotbar.slots) * (slot_size + gap) - gap
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT - slot_size - 15

        for index, item in enumerate(hotbar.slots):
            x = start_x + index * (slot_size + gap)
            self._draw_slot(x, y, slot_size)
            border_color = (
                HOVER_COLOR if index == hotbar.selected_index
                else UI_BORDER_COLOR
            )
            border_width = 3 if index == hotbar.selected_index else 1
            pygame.draw.rect(
                self.screen,
                border_color,
                (x, y, slot_size, slot_size),
                border_width,
            )
            if item in self.item_images:
                image = self.item_images[item]
                image_rect = image.get_rect(
                    center=(x + slot_size // 2, y + slot_size // 2)
                )
                self.screen.blit(image, image_rect)

    def _draw_inventory(self, inventory):
        slot_size = 50
        gap = 4
        slots_per_row = 9
        total_width = slots_per_row * (slot_size + gap) - gap
        start_x = (SCREEN_WIDTH - total_width) // 2
        bottom_y = SCREEN_HEIGHT - slot_size * 2 - 30
        items = list(inventory.items.items())

        for index in range(max(slots_per_row, len(items))):
            row, column = divmod(index, slots_per_row)
            x = start_x + column * (slot_size + gap)
            y = bottom_y - row * (slot_size + gap)
            self._draw_slot(x, y, slot_size)

            if index >= len(items):
                continue

            item, count = items[index]
            if item in self.item_images:
                image = self.item_images[item]
                image_rect = image.get_rect(
                    center=(x + slot_size // 2, y + slot_size // 2)
                )
                self.screen.blit(image, image_rect)

            count_surface = self.count_font.render(
                str(count), True, HOVER_COLOR
            )
            count_rect = count_surface.get_rect(
                bottomright=(x + slot_size - 5, y + slot_size - 5)
            )
            self.screen.blit(count_surface, count_rect)

    def _draw_slot(self, x, y, size):
        pygame.draw.rect(
            self.screen,
            UI_SLOT_COLOR,
            (x, y, size, size),
        )
        pygame.draw.rect(
            self.screen,
            UI_BORDER_COLOR,
            (x, y, size, size),
            1,
        )
