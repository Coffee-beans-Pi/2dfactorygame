import os

import pygame

from game import Game
from renderer import Renderer
from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE


def main():
    os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    game = Game()
    renderer = Renderer(screen)
    clock = pygame.time.Clock()

    while game.running:
        for event in pygame.event.get():
            game.handle_event(event)

        game.update(pygame.key.get_pressed())
        renderer.draw(game)
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
