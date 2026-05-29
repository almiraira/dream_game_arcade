import arcade
from views import MenuView
from config import SCREEN_WIDTH, SCREEN_HEIGHT


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Ловец снов", resizable=False)
    menu = MenuView()
    window.show_view(menu)
    arcade.run()


if __name__ == "__main__":
    main()
