from pathlib import Path

import pygame

from settings import (
    BACKGROUND_COLOR,
    CRAFTING_MARGIN,
    CRAFTING_ROW_HEIGHT,
    CRAFTING_ROW_WIDTH,
    CRAFTING_SLOT_GAP,
    CRAFTING_SLOT_SIZE,
    GRID_COLOR,
    HOVER_COLOR,
    FURNACE_PANEL_HEIGHT,
    FURNACE_PANEL_WIDTH,
    FURNACE_HOTBAR_SLOT_STEP,
    FURNACE_HOTBAR_Y,
    FURNACE_INVENTORY_ROWS,
    FURNACE_INVENTORY_Y,
    INVENTORY_COLUMNS,
    INVENTORY_HOTBAR_GAP,
    INVENTORY_PANEL_BORDER_COLOR,
    INVENTORY_PANEL_COLOR,
    INVENTORY_PANEL_PADDING,
    INVENTORY_ROWS,
    INVENTORY_VEIL_COLOR,
    PLACEABLE_OBJECTS,
    SLOT_GAP,
    SLOT_SIZE,
    TILE_SIZE,
    UI_BORDER_COLOR,
    UI_SLOT_COLOR,
)
from recipes import ITEM_NAMES, get_craftable_recipes


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        asset_dir = Path(__file__).parent / "assets"
        item_dir = asset_dir / "spr_items"
        self.item_images = {
            "pickaxe": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_pickaxe_stone.png"
                ).convert_alpha(), 2
            ),
            "dirt": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_dirt.png"
                ).convert_alpha(), 2
            ),
            "stone": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_rock.png"
                ).convert_alpha(), 2
            ),
            "sand": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_sand.png"
                ).convert_alpha(), 2
            ),
            "bonsai": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_bonsai.png"
                ).convert_alpha(), 2
            ),
            "bonsai_clay": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_bonsai_clay.png"
                ).convert_alpha(), 2
            ),
            "glass": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_glass.png"
                ).convert_alpha(), 2
            ),
            "iron_ore": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_raw_iron.png"
                ).convert_alpha(), 2
            ),
            "copper_ore": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_raw_copper.png"
                ).convert_alpha(), 2
            ),
            "tin_ore": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_raw_tin.png"
                ).convert_alpha(), 2
            ),
            "ingot_aluminum": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_ingot_aluminum.png"
                ).convert_alpha(), 2
            ),
            "ingot_bronze": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_ingot_bronze.png"
                ).convert_alpha(), 2
            ),
            "ingot_chromium": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_ingot_chromium.png"
                ).convert_alpha(), 2
            ),
            "ingot_copper": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_ingot_copper.png"
                ).convert_alpha(), 2
            ),
            "ingot_iron": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_ingot_iron.png"
                ).convert_alpha(), 2
            ),
            "ingot_nickel": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_ingot_nickel.png"
                ).convert_alpha(), 2
            ),
            "ingot_tin": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_ingot_tin.png"
                ).convert_alpha(), 2
            ),
            "furnace": pygame.transform.scale_by(
                pygame.image.load(
                    item_dir / "item_furnace.png"
                ).convert_alpha(), 2
            ),
        }
        block_dir = asset_dir / "spr_blocks"
        block_sprite_names = {
            "grass": "grass",
            "rock": "stone",
            "sand": "sand",
            "water": "water",
        }
        self.block_images = {
            kind: pygame.image.load(
                block_dir / f"spr_block_{sprite_name}.png"
            ).convert_alpha()
            for kind, sprite_name in block_sprite_names.items()
        }
        self.object_images = {
            object_kind: pygame.image.load(
                block_dir / f"spr_block_{object_kind}.png"
            ).convert_alpha()
            for object_kind in PLACEABLE_OBJECTS.values()
        }
        self.scaled_block_images = {}
        self.scaled_object_images = {}
        self.world_surface = None
        self.world_surface_key = None
        self.count_font = pygame.font.Font(None, 24)
        self.icon_fonts = {}

    def draw(self, game):
        self.screen.fill(BACKGROUND_COLOR)
        self._draw_world(game.world, game.camera)
        if game.inventory_visible:
            self._draw_inventory_overlay(game)
        else:
            self._draw_hovered_tile(game.world, game.camera)
            self._draw_hotbar(game.hotbar)
        if game.machine_ui_position is not None:
            tile = game.world.get_tile(*game.machine_ui_position)
            if tile is not None and tile.machine is not None:
                self._draw_furnace_ui(tile.machine, game)
        if game.cursor_item is not None:
            self._draw_cursor_item(game.cursor_item, game.cursor_count)
        self._draw_item_effects(game.item_effects)
        pygame.display.flip()

    def _draw_world(self, world, camera):
        screen_size = self.screen.get_size()
        cache_key = (
            screen_size,
            camera.x,
            camera.y,
            camera.zoom,
            world.render_revision,
        )
        if cache_key != self.world_surface_key:
            self.world_surface = pygame.Surface(
                screen_size,
                pygame.SRCALPHA,
            )
            self._render_world(world, camera, self.world_surface)
            self.world_surface_key = cache_key

        self.screen.blit(self.world_surface, (0, 0))

    def _render_world(self, world, camera, target):
        tile_pixels = max(1, int(TILE_SIZE * camera.zoom))
        screen_width, screen_height = target.get_size()
        left_world = camera.x - screen_width / (2 * camera.zoom)
        top_world = camera.y - screen_height / (2 * camera.zoom)
        right_world = camera.x + screen_width / (2 * camera.zoom)
        bottom_world = camera.y + screen_height / (2 * camera.zoom)
        start_column = max(0, int(left_world // TILE_SIZE) - 1)
        end_column = min(world.width, int(right_world // TILE_SIZE) + 2)
        start_row = max(0, int(top_world // TILE_SIZE) - 1)
        end_row = min(world.height, int(bottom_world // TILE_SIZE) + 2)

        for row in world.tiles[start_row:end_row]:
            for tile in row[start_column:end_column]:
                screen_x, screen_y = camera.world_to_screen(
                    tile.x * TILE_SIZE,
                    tile.y * TILE_SIZE,
                )
                block_image = self.block_images.get(
                    tile.kind,
                    self.block_images["grass"],
                )
                block_cache_key = (tile.kind, tile_pixels)
                scaled_block = self.scaled_block_images.get(block_cache_key)
                if scaled_block is None:
                    scaled_block = pygame.transform.scale(
                        block_image,
                        (tile_pixels, tile_pixels),
                    )
                    self.scaled_block_images[block_cache_key] = scaled_block
                target.blit(scaled_block, (screen_x, screen_y))
                pygame.draw.line(
                    target, GRID_COLOR,
                    (screen_x, screen_y),
                    (screen_x + tile_pixels, screen_y),
                    1,
                )
                pygame.draw.line(
                    target, GRID_COLOR,
                    (screen_x, screen_y),
                    (screen_x, screen_y + tile_pixels),
                    1,
                )
                pygame.draw.line(
                    target, GRID_COLOR,
                    (screen_x + tile_pixels, screen_y),
                    (screen_x + tile_pixels, screen_y + tile_pixels),
                    1,
                )
                pygame.draw.line(
                    target, GRID_COLOR,
                    (screen_x, screen_y + tile_pixels),
                    (screen_x + tile_pixels, screen_y + tile_pixels),
                    1,
                )
                object_image = self.object_images.get(tile.placed_object)
                if object_image is not None:
                    object_size = (tile_pixels, tile_pixels)
                    object_cache_key = (tile.placed_object, object_size)
                    scaled_object = self.scaled_object_images.get(
                        object_cache_key
                    )
                    if scaled_object is None:
                        scaled_object = (
                            object_image
                            if object_size == object_image.get_size()
                            else pygame.transform.scale(
                                object_image,
                                object_size,
                            )
                        )
                        self.scaled_object_images[object_cache_key] = (
                            scaled_object
                        )
                    target.blit(scaled_object, (screen_x, screen_y))

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
        total_width = len(hotbar.slots) * (SLOT_SIZE + SLOT_GAP) - SLOT_GAP
        screen_width, screen_height = self.screen.get_size()
        start_x = (screen_width - total_width) // 2
        y = screen_height - SLOT_SIZE - 15

        for index, item in enumerate(hotbar.slots):
            x = start_x + index * (SLOT_SIZE + SLOT_GAP)
            self._draw_slot(x, y, SLOT_SIZE)
            border_color = (
                HOVER_COLOR if index == hotbar.selected_index
                else UI_BORDER_COLOR
            )
            border_width = 3 if index == hotbar.selected_index else 1
            pygame.draw.rect(
                self.screen,
                border_color,
                (x, y, SLOT_SIZE, SLOT_SIZE),
                border_width,
            )
            if item is not None:
                self._draw_item_icon(item, x, y, SLOT_SIZE)
                self._draw_stack_count(
                    hotbar.counts[index],
                    x,
                    y,
                )

    def _draw_inventory_overlay(self, game):
        screen_width, screen_height = self.screen.get_size()
        veil = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        veil.fill(INVENTORY_VEIL_COLOR)
        self.screen.blit(veil, (0, 0))

        slot_rows_height = (
            INVENTORY_ROWS * SLOT_SIZE + (INVENTORY_ROWS - 1) * SLOT_GAP
        )
        panel_width = (
            INVENTORY_COLUMNS * SLOT_SIZE
            + (INVENTORY_COLUMNS - 1) * SLOT_GAP
            + INVENTORY_PANEL_PADDING * 2
        )
        panel_height = (
            slot_rows_height + INVENTORY_HOTBAR_GAP + SLOT_SIZE
            + INVENTORY_PANEL_PADDING * 2
        )
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill(INVENTORY_PANEL_COLOR)
        self.screen.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(
            self.screen,
            INVENTORY_PANEL_BORDER_COLOR,
            (panel_x, panel_y, panel_width, panel_height),
            1,
        )

        grid_x = panel_x + INVENTORY_PANEL_PADDING
        grid_y = panel_y + INVENTORY_PANEL_PADDING
        items = list(game.inventory.items.items())
        slot_count = INVENTORY_COLUMNS * INVENTORY_ROWS
        mouse_position = pygame.mouse.get_pos()
        hovered_item = None

        for index in range(slot_count):
            row, column = divmod(index, INVENTORY_COLUMNS)
            x = grid_x + column * (SLOT_SIZE + SLOT_GAP)
            y = grid_y + row * (SLOT_SIZE + SLOT_GAP)
            self._draw_slot(x, y, SLOT_SIZE)
            if index < len(items):
                item_name = self._draw_inventory_item(x, y, items[index])
                if pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE).collidepoint(
                    mouse_position
                ):
                    hovered_item = item_name

        hotbar_y = grid_y + slot_rows_height + INVENTORY_HOTBAR_GAP
        for index, item in enumerate(game.hotbar.slots):
            x = grid_x + index * (SLOT_SIZE + SLOT_GAP)
            self._draw_slot(x, hotbar_y, SLOT_SIZE)
            if pygame.Rect(x, hotbar_y, SLOT_SIZE, SLOT_SIZE).collidepoint(
                mouse_position
            ):
                hovered_item = item
            if index == game.hotbar.selected_index:
                pygame.draw.rect(
                    self.screen,
                    INVENTORY_PANEL_BORDER_COLOR,
                    (x, hotbar_y, SLOT_SIZE, SLOT_SIZE),
                    2,
                )
            if item is not None:
                self._draw_item_icon(item, x, hotbar_y, SLOT_SIZE)
                self._draw_stack_count(
                    game.hotbar.counts[index],
                    x,
                    hotbar_y,
                )

        crafting_hover = self._draw_crafting_list(game, mouse_position)
        if crafting_hover is not None:
            hovered_item = crafting_hover
        if hovered_item is not None:
            self._draw_item_tooltip(hovered_item, mouse_position)

    def _draw_furnace_ui(self, furnace, game):
        hotbar = game.hotbar
        screen_width, screen_height = self.screen.get_size()
        panel = pygame.Rect(
            (screen_width - FURNACE_PANEL_WIDTH) // 2,
            (screen_height - FURNACE_PANEL_HEIGHT) // 2,
            FURNACE_PANEL_WIDTH,
            FURNACE_PANEL_HEIGHT,
        )
        veil = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 130))
        self.screen.blit(veil, (0, 0))
        pygame.draw.rect(self.screen, INVENTORY_PANEL_COLOR, panel)
        pygame.draw.rect(
            self.screen,
            INVENTORY_PANEL_BORDER_COLOR,
            panel,
            2,
        )

        title = self.count_font.render("Furnace", True, HOVER_COLOR)
        self.screen.blit(title, (panel.x + 18, panel.y + 14))
        labels = (
            ("INPUT", panel.x + 55, panel.y + 39),
            ("OUTPUT", panel.x + 420, panel.y + 69),
        )
        for label, x, y in labels:
            text = self.count_font.render(label, True, HOVER_COLOR)
            self.screen.blit(text, (x, y))

        input_position = (panel.x + 55, panel.y + 55)
        fuel_position = (panel.x + 55, panel.y + 115)
        output_position = (panel.x + 420, panel.y + 85)
        for position in (input_position, fuel_position, output_position):
            self._draw_slot(*position, SLOT_SIZE)

        self._draw_machine_stack(furnace.smelt_queue, *input_position)
        self._draw_machine_stack(furnace.fuel_items, *fuel_position)
        self._draw_machine_stack(furnace.output_items, *output_position)
        fuel_label = self.count_font.render("FUEL", True, HOVER_COLOR)
        self.screen.blit(fuel_label, (fuel_position[0], fuel_position[1] + 52))

        arrow_rect = pygame.Rect(panel.x + 180, panel.y + 95, 160, 22)
        pygame.draw.rect(self.screen, UI_SLOT_COLOR, arrow_rect)
        if furnace.burning:
            progress = min(1.0, furnace.smelt_timer)
            fill_rect = pygame.Rect(
                arrow_rect.x,
                arrow_rect.y,
                round(arrow_rect.width * progress),
                arrow_rect.height,
            )
            pygame.draw.rect(self.screen, (218, 132, 45), fill_rect)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, arrow_rect, 1)

        if furnace.burning:
            state_text = self.count_font.render("Burning", True, HOVER_COLOR)
            self.screen.blit(state_text, (panel.x + 180, panel.y + 125))

        hotbar_width = (
            len(hotbar.slots) * FURNACE_HOTBAR_SLOT_STEP - SLOT_GAP
        )
        hotbar_x = panel.x + (panel.width - hotbar_width) // 2
        inventory_label = self.count_font.render(
            "Inventory",
            True,
            HOVER_COLOR,
        )
        self.screen.blit(
            inventory_label,
            (hotbar_x, panel.y + FURNACE_INVENTORY_Y - 30),
        )
        inventory_x = hotbar_x
        inventory_y = panel.y + FURNACE_INVENTORY_Y
        inventory_items = list(game.inventory.items.items())
        for index in range(INVENTORY_COLUMNS * FURNACE_INVENTORY_ROWS):
            row, column = divmod(index, INVENTORY_COLUMNS)
            x = inventory_x + column * (SLOT_SIZE + SLOT_GAP)
            y = inventory_y + row * (SLOT_SIZE + SLOT_GAP)
            self._draw_slot(x, y, SLOT_SIZE)
            if index < len(inventory_items):
                item, count = inventory_items[index]
                self._draw_item_icon(item, x, y, SLOT_SIZE)
                self._draw_stack_count(count, x, y)

        hotbar_label = self.count_font.render("Hotbar", True, HOVER_COLOR)
        self.screen.blit(
            hotbar_label,
            (hotbar_x, panel.y + FURNACE_HOTBAR_Y - 30),
        )
        hotbar_y = panel.y + FURNACE_HOTBAR_Y
        for index, item in enumerate(hotbar.slots):
            x = hotbar_x + index * FURNACE_HOTBAR_SLOT_STEP
            self._draw_slot(x, hotbar_y, SLOT_SIZE)
            if index == hotbar.selected_index:
                pygame.draw.rect(
                    self.screen,
                    HOVER_COLOR,
                    (x, hotbar_y, SLOT_SIZE, SLOT_SIZE),
                    3,
                )
            if item is not None:
                self._draw_item_icon(item, x, hotbar_y, SLOT_SIZE)
                self._draw_stack_count(hotbar.counts[index], x, hotbar_y)

    def _draw_machine_stack(self, items, x, y):
        if not items:
            return
        item = items[0]
        self._draw_item_icon(item, x, y, SLOT_SIZE)
        self._draw_stack_count(items.count(item), x, y)

    def _draw_crafting_list(self, game, mouse_position):
        recipes = get_craftable_recipes(game.inventory, game.hotbar)
        if not recipes:
            return None

        screen_height = self.screen.get_height()
        first_recipe_y = (
            screen_height - CRAFTING_MARGIN - CRAFTING_ROW_HEIGHT
        )
        hovered_item = None

        for index, recipe in enumerate(recipes):
            recipe_y = first_recipe_y - index * CRAFTING_ROW_HEIGHT
            recipe_rect = pygame.Rect(
                CRAFTING_MARGIN,
                recipe_y,
                CRAFTING_ROW_WIDTH,
                CRAFTING_ROW_HEIGHT,
            )
            pygame.draw.rect(self.screen, INVENTORY_PANEL_COLOR, recipe_rect)
            pygame.draw.rect(
                self.screen,
                INVENTORY_PANEL_BORDER_COLOR,
                recipe_rect,
                1,
            )
            self._draw_slot(
                CRAFTING_MARGIN + 5,
                recipe_y + 6,
                CRAFTING_SLOT_SIZE,
            )
            self._draw_item_icon(
                recipe.result,
                CRAFTING_MARGIN + 5,
                recipe_y + 6,
                CRAFTING_SLOT_SIZE,
            )
            name = ITEM_NAMES.get(recipe.result, recipe.result.title())
            text = self.count_font.render(name, True, HOVER_COLOR)
            self.screen.blit(text, (CRAFTING_MARGIN + 40, recipe_y + 11))

            ingredients_x = (
                CRAFTING_MARGIN
                + CRAFTING_ROW_WIDTH
                + CRAFTING_SLOT_GAP
            )
            ingredients_rect = self._recipe_ingredients_rect(
                recipe,
                ingredients_x,
                recipe_y,
            )
            if (
                recipe_rect.collidepoint(mouse_position)
                or ingredients_rect.collidepoint(mouse_position)
            ):
                if recipe_rect.collidepoint(mouse_position):
                    hovered_item = recipe.result
                ingredient_hover = self._draw_recipe_ingredients(
                    recipe,
                    ingredients_x,
                    recipe_y,
                    mouse_position,
                )
                if ingredient_hover is not None:
                    hovered_item = ingredient_hover

        return hovered_item

    def _draw_recipe_ingredients(
        self,
        recipe,
        panel_x,
        panel_y,
        mouse_position,
    ):
        cell_width = 92
        panel_rect = self._recipe_ingredients_rect(recipe, panel_x, panel_y)
        panel_x = panel_rect.x
        pygame.draw.rect(self.screen, INVENTORY_PANEL_COLOR, panel_rect)
        pygame.draw.rect(
            self.screen,
            INVENTORY_PANEL_BORDER_COLOR,
            panel_rect,
            1,
        )
        hovered_item = None
        for index, (item, amount) in enumerate(recipe.ingredients):
            x = panel_x + INVENTORY_PANEL_PADDING + index * cell_width
            y = panel_y + (panel_rect.height - CRAFTING_SLOT_SIZE) // 2
            self._draw_slot(x, y, CRAFTING_SLOT_SIZE)
            self._draw_item_icon(item, x, y, CRAFTING_SLOT_SIZE)
            item_name = ITEM_NAMES.get(item, item.title())
            label = f"{item_name[:1]} x{amount}"
            text = self.count_font.render(label, True, HOVER_COLOR)
            self.screen.blit(
                text,
                (x + CRAFTING_SLOT_SIZE + 4, panel_y + 11),
            )
            ingredient_rect = pygame.Rect(
                x,
                y,
                CRAFTING_SLOT_SIZE,
                CRAFTING_SLOT_SIZE,
            )
            if ingredient_rect.collidepoint(mouse_position):
                hovered_item = item

        return hovered_item

    def _recipe_ingredients_rect(self, recipe, panel_x, panel_y):
        panel_width = (
            len(recipe.ingredients) * 92 + INVENTORY_PANEL_PADDING * 2
        )
        panel_x = min(panel_x, self.screen.get_width() - panel_width)
        return pygame.Rect(
            panel_x,
            panel_y,
            panel_width,
            CRAFTING_ROW_HEIGHT,
        )

    def _draw_item_tooltip(self, item, mouse_position):
        name = ITEM_NAMES.get(item, item.title())
        text = self.count_font.render(name, True, HOVER_COLOR)
        padding = 5
        tooltip = pygame.Rect(
            mouse_position[0] + 14,
            mouse_position[1] + 14,
            text.get_width() + padding * 2,
            text.get_height() + padding * 2,
        )
        tooltip.clamp_ip(self.screen.get_rect())
        pygame.draw.rect(self.screen, INVENTORY_PANEL_COLOR, tooltip)
        pygame.draw.rect(
            self.screen,
            INVENTORY_PANEL_BORDER_COLOR,
            tooltip,
            1,
        )
        self.screen.blit(text, (tooltip.x + padding, tooltip.y + padding))

    def _draw_inventory_item(self, x, y, inventory_item):
        item, count = inventory_item
        self._draw_item_icon(item, x, y, SLOT_SIZE)

        count_surface = self.count_font.render(str(count), True, HOVER_COLOR)
        count_rect = count_surface.get_rect(
            bottomright=(x + SLOT_SIZE - 5, y + SLOT_SIZE - 5)
        )
        self.screen.blit(count_surface, count_rect)
        return item

    def _draw_stack_count(self, count, x, y):
        if count <= 1:
            return
        count_surface = self.count_font.render(str(count), True, HOVER_COLOR)
        count_rect = count_surface.get_rect(
            bottomright=(x + SLOT_SIZE - 5, y + SLOT_SIZE - 5)
        )
        self.screen.blit(count_surface, count_rect)

    def _draw_cursor_item(self, item, count):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x = mouse_x - SLOT_SIZE // 2
        y = mouse_y - SLOT_SIZE // 2
        self._draw_item_icon(item, x, y, SLOT_SIZE)
        self._draw_stack_count(count, x, y)

    def _draw_item_effects(self, effects):
        icon_size = 24
        for effect in effects:
            progress = effect["age"] / effect["lifetime"]
            opacity = max(0, round(255 * (1 - progress)))
            icon = pygame.Surface(
                (icon_size, icon_size),
                pygame.SRCALPHA,
            )
            self._draw_item_icon(
                effect["item"],
                0,
                0,
                icon_size,
                target=icon,
                opacity=opacity,
            )
            icon = pygame.transform.rotate(icon, effect["rotation"])
            icon_rect = icon.get_rect(
                center=(round(effect["x"]), round(effect["y"]))
            )
            self.screen.blit(
                icon,
                icon_rect,
            )

    def _draw_item_icon(self, item, x, y, size, target=None, opacity=255):
        if target is None:
            target = self.screen
        image = self.item_images.get(item)
        if image is not None:
            width, height = image.get_size()
            scale = min(1, size / max(width, height))
            icon_size = (max(1, round(width * scale)), max(1, round(height * scale)))
            if icon_size != image.get_size():
                image = pygame.transform.smoothscale(image, icon_size)
            if opacity < 255:
                image = image.copy()
                image.set_alpha(opacity)
            image_rect = image.get_rect(center=(x + size // 2, y + size // 2))
            target.blit(image, image_rect)
            return

        font_size = max(12, round(size * 0.55))
        if font_size not in self.icon_fonts:
            self.icon_fonts[font_size] = pygame.font.Font(None, font_size)
        icon_labels = {
            "coal_ore": "C",
            "copper_ore": "Cu",
            "iron_ore": "Fe",
            "sapling": "Sa",
            "seed": "Se",
            "tin_ore": "Sn",
            "twig": "Tw",
        }
        label = icon_labels.get(item, ITEM_NAMES.get(item, item.title())[:1])
        text = self.icon_fonts[font_size].render(label, True, HOVER_COLOR)
        if opacity < 255:
            text.set_alpha(opacity)
        target.blit(
            text,
            text.get_rect(center=(x + size // 2, y + size // 2)),
        )

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
