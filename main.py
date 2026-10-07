import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("factory_game")

clock = pygame.time.Clock()

TILE_SIZE = 40
camera_x = 0
camera_y = 0
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
        world_x = (screen_x + camera_x) / zoom
        world_y = (screen_y + camera_y) / zoom
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)
        return self.get_tile(tile_x, tile_y)

    def draw(self, surface):
        tile_pixels = max(1, int(TILE_SIZE * zoom))

        for row in self.tiles:
            for tile in row:
                world_x = tile.x * TILE_SIZE
                world_y = tile.y * TILE_SIZE
                screen_x = int(world_x * zoom - camera_x)
                screen_y = int(world_y * zoom - camera_y)

                if (
                    screen_x + tile_pixels < -10
                    or screen_x > SCREEN_WIDTH + 10
                    or screen_y + tile_pixels < -10
                    or screen_y > SCREEN_HEIGHT + 10
                ):
                    continue

                pygame.draw.rect(surface, tile.color, (screen_x, screen_y, tile_pixels, tile_pixels))

                if tile.selected:
                    pygame.draw.rect(surface, (255, 255, 255), (screen_x, screen_y, tile_pixels, tile_pixels), 3)


map_data = Map(300, 200)

for y in range(map_data.height):
    for x in range(map_data.width):
        if (x + y) % 8 == 0:
            map_data.set_kind(x, y, "water")
        elif (x * 3 + y) % 11 == 0:
            map_data.set_kind(x, y, "rock")
        elif (x + y * 2) % 7 == 0:
            map_data.set_kind(x, y, "sand")

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_tile = map_data.get_tile_from_screen(*event.pos)
            if clicked_tile is not None:
                clicked_tile.handle_click()
        elif event.type == pygame.MOUSEWHEEL:
            old_zoom = zoom
            zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom + event.y * 0.1))

            if zoom != old_zoom:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = (mouse_x + camera_x) / old_zoom
                world_y = (mouse_y + camera_y) / old_zoom

                camera_x = world_x * zoom - mouse_x
                camera_y = world_y * zoom - mouse_y

    screen.fill((30, 30, 30))

    keys = pygame.key.get_pressed()
    move_speed = 5 * zoom

    if keys[pygame.K_LEFT]:
        camera_x -= move_speed
    if keys[pygame.K_RIGHT]:
        camera_x += move_speed
    if keys[pygame.K_UP]:
        camera_y -= move_speed
    if keys[pygame.K_DOWN]:
        camera_y += move_speed

    map_data.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()