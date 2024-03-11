WIDTH, HEIGHT = 1000, 800

class Partida():
    def __init__(self):
        super().__init__()
        self.level = 1
        self.checkpoint = 0
        self.coins = 0
        self.gems = 0
        self.lives = 3


class Volume():
    def __init__(self):
        super().__init__()
        self.music_volume = 0.5
        self.sounds_volume = 0.5
