import game


def main():
    my_game = game.Game()
    my_game.init()
    my_game.loop()
    my_game.release()


if __name__ == "__main__":
    main()
