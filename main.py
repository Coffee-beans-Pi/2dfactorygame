import os

import pygame

from game import Game
from renderer import Renderer
from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE


def main():
    os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.RESIZABLE,
    )
    pygame.display.set_caption(WINDOW_TITLE)

    game = Game()
    renderer = Renderer(screen)
    clock = pygame.time.Clock()

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    event.size,
                    pygame.RESIZABLE,
                )
                renderer.screen = screen
                game.resize_screen(*screen.get_size())
            else:
                game.handle_event(event)

        delta_time = clock.tick(FPS) / 1000
        game.update(pygame.key.get_pressed(), delta_time)
        renderer.draw(game)

    pygame.quit()


if __name__ == "__main__":
    main()
