import pygame

pygame.init()

screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("factory_game")

clock = pygame.time.Clock()

running = True

TILE_SIZE = 40

camera_x = 0
camera_y = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    MIN_ZOOM = 0.5
    MAX_ZOOM = 3.0

    zoom = 1.0

    tile_size = TILE_SIZE * zoom

    zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))

    screen.fill((30,30,30))

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        camera_x -= 5
    if keys[pygame.K_RIGHT]:
        camera_x += 5
    if keys[pygame.K_UP]:
        camera_y -= 5
    if keys[pygame.K_DOWN]:
        camera_y += 5

    tile_size = int(tile_size)

    for x in range(0, 800+tile_size, tile_size):
        pygame.draw.line(
            screen,
            (80, 80, 80),
            (x - camera_x % tile_size, 0),
            (x - camera_x % tile_size, 600)
        )

    for y in range(0, 600+tile_size, tile_size):
        pygame.draw.line(
            screen,
            (80, 80, 80),
            (0, y - camera_y % tile_size),
            (800, y - camera_y % tile_size)
        )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()