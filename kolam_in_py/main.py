import os, sys, pygame
from config import gVar
from core.tile_data import *
from core.wfc import WFCGenerator
from utils.button import Button
from utils.colors import Colors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_tile_images(path, count, tile_size=64):
    images = []
    for i in range(count):
        fname = os.path.join(BASE_DIR, path, f"{i}.png")
        img = pygame.image.load(fname).convert_alpha()
        img = pygame.transform.smoothscale(img, (tile_size, tile_size))
        images.append(img)

    return images


def change_tileset(screen):
    gVar.TILE_DATA = gVar.TILE_SET[
        (gVar.TILE_SET.index(gVar.TILE_DATA) + 1) % len(gVar.TILE_SET)
    ]
    gVar.TILE_PATH = gVar.TILE_DATA.path
    IMAGE_COUNT = gVar.TILE_DATA.img_count
    tile_images = load_tile_images(gVar.TILE_PATH, IMAGE_COUNT, tile_size=64)
    return WFCGenerator(screen, tile_images)


def main():
    pygame.init()
    pygame.display.set_caption("Wave Function Collapse (pygame)")
    screen = pygame.display.set_mode((gVar.WIDTH, gVar.HEIGHT + 60))
    clock = pygame.time.Clock()

    # Creating Buttons

    btn_pad_x = (gVar.WIDTH - 360) // 5
    btn_pad_y = 7
    dim_inc_btn = Button(
        x=btn_pad_x,
        y=gVar.HEIGHT + btn_pad_y,
        width=90,
        height=20,
        text="Increase Dim",
    )

    dim_dcr_btn = Button(
        x=dim_inc_btn.get_topright()[0] + btn_pad_x,
        y=gVar.HEIGHT + btn_pad_y,
        width=90,
        height=20,
        text="Decrease Dim",
    )

    restart_btn = Button(
        x=dim_dcr_btn.get_topright()[0] + btn_pad_x,
        y=gVar.HEIGHT + btn_pad_y,
        width=90,
        height=20,
        text="Restart (r)",
    )

    pause_btn = Button(
        x=restart_btn.get_topright()[0] + btn_pad_x,
        y=gVar.HEIGHT + btn_pad_y,
        width=90,
        height=20,
        text="Pause (p)",
        toggle=True,
    )

    fast_toggle_btn = Button(
        x=dim_inc_btn.get_bottomleft()[0],
        y=dim_inc_btn.get_bottomleft()[1] + btn_pad_y,
        width=90,
        height=20,
        text="Fast Toggle",
        toggle=True,
    )

    exit_btn = Button(
        x=dim_dcr_btn.get_bottomleft()[0],
        y=dim_dcr_btn.get_bottomleft()[1] + btn_pad_y,
        width=90,
        height=20,
        text="Exit (Esc)",
    )

    tile_switch_btn = Button(
        x=restart_btn.get_bottomleft()[0],
        y=restart_btn.get_bottomleft()[1] + btn_pad_y,
        width=90,
        height=20,
        text="Change tiles",
    )

    symmetric_x_btn = Button(
        x=pause_btn.get_bottomleft()[0],
        y=pause_btn.get_bottomleft()[1] + btn_pad_y,
        width=40,
        height=20,
        text="Left",
        toggle=True,
    )

    symmetric_y_btn = Button(
        x=symmetric_x_btn.get_topright()[0] + 10,
        y=symmetric_x_btn.get_topright()[1],
        width=40,
        height=20,
        text="Top",
        toggle=True,
    )

    # Start of program logic

    tile_images = load_tile_images(gVar.TILE_PATH, gVar.IMAGE_COUNT, tile_size=64)
    kolam = WFCGenerator(screen, tile_images)

    running = True
    paused = False

    # we will run step() once per N frames to slow things a bit (so you can watch it)
    # but we also allow a faster mode by pressing SPACE to run fast.
    frames_between_steps = 1
    frame_count = 0

    # font = pygame.font.SysFont("Arial", 12)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    restart_btn.trigger_key_action()
                    kolam.start_over()

                elif event.key == pygame.K_p:
                    pause_btn.trigger_key_action()
                    paused = not paused

            if dim_inc_btn.check_click(event):
                kolam.dim_x += 1 + kolam.y_symmetry
                kolam.dim_y += 1 + kolam.x_symmetry

                if kolam.x_symmetry and kolam.y_symmetry:
                    kolam.dim_x -= 1
                    kolam.dim_y -= 1

                if kolam.width % kolam.dim_x != 0:
                    kolam.screen_width = (
                        kolam.screen_width // kolam.dim_x
                    ) * kolam.dim_x

                if kolam.height % kolam.dim_y != 0:
                    kolam.screen_height = (
                        kolam.screen_height // kolam.dim_y
                    ) * kolam.dim_y

                kolam.start_over()

            elif dim_dcr_btn.check_click(event):
                if kolam.dim_x == 2:
                    continue

                kolam.dim_x -= 1 + kolam.y_symmetry
                kolam.dim_y -= 1 + kolam.x_symmetry

                if kolam.x_symmetry and kolam.y_symmetry:
                    kolam.dim_x += 1
                    kolam.dim_y += 1

                if kolam.width % kolam.dim_x != 0:
                    kolam.screen_width = (
                        kolam.screen_width // kolam.dim_x
                    ) * kolam.dim_x

                if kolam.height % kolam.dim_y != 0:
                    kolam.screen_height = (
                        kolam.screen_height // kolam.dim_y
                    ) * kolam.dim_y

                kolam.start_over()

            elif restart_btn.check_click(event):
                kolam.start_over()

            elif pause_btn.check_click(event):
                paused = not paused

            elif fast_toggle_btn.check_click(event):
                if frames_between_steps == 1:
                    frames_between_steps = 0
                else:
                    frames_between_steps = 1

            elif exit_btn.check_click(event):
                running = False

            elif tile_switch_btn.check_click(event):
                kolam = change_tileset(screen)
                kolam.start_over()

            elif symmetric_x_btn.check_click(event):
                kolam.x_symmetry = not kolam.x_symmetry
                kolam.make_symmetry()
                kolam.start_over()

            elif symmetric_y_btn.check_click(event):
                kolam.y_symmetry = not kolam.y_symmetry
                kolam.make_symmetry()
                kolam.start_over()

        if not paused:
            if frames_between_steps == 0:
                # very fast (collapse many times per frame)
                for _ in range(200):
                    kolam.step()
            else:
                if frame_count % frames_between_steps == 0:
                    kolam.step()
            frame_count += 1

        screen.fill(Colors.BLACK)
        kolam.draw()

        if kolam.x_symmetry:
            left_side = pygame.Rect(0, 0, kolam.screen_width, kolam.height)
            left_side_copy = screen.subsurface(left_side).copy()
            rotated_right_side = pygame.transform.flip(left_side_copy, True, False)
            screen.blit(rotated_right_side, (kolam.screen_width, 0))

        if kolam.y_symmetry:
            top_side = pygame.Rect(0, 0, kolam.width, kolam.screen_height)
            top_side_copy = screen.subsurface(top_side).copy()
            rotated_bottom_side = pygame.transform.flip(top_side_copy, False, True)
            screen.blit(rotated_bottom_side, (0, kolam.screen_height))

        dim_inc_btn.draw(screen)
        dim_dcr_btn.draw(screen)
        restart_btn.draw(screen)
        pause_btn.draw(screen)
        fast_toggle_btn.draw(screen)
        exit_btn.draw(screen)
        tile_switch_btn.draw(screen)
        symmetric_x_btn.draw(screen)
        symmetric_y_btn.draw(screen)

        pygame.draw.rect(
            screen, Colors.LIGHT_GRAY, pygame.Rect(0, 0, gVar.WIDTH, gVar.WIDTH), 1
        )
        pygame.display.flip()
        clock.tick(gVar.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
