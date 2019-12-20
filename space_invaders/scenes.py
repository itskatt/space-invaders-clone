class BaseScene:
    def __init__(self, game):
        self.game = game

    def switch_scene(self, scene):
        self.game.scene = scene  # TODO: adapt if necesary

    def update(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError


class MainScene(BaseScene):
    pass
