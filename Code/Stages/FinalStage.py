
from ..RenderStage import RenderStage


class FinalStage(RenderStage):

    """ This stage is the final stage and outputs the shaded scene to the
    screen """

    def __init__(self, pipeline):
        RenderStage.__init__(self, "FinalStage", pipeline)

    def get_produced_pipes(self):
        return {}

    def get_input_pipes(self):
        return ["ShadedScene"]

    def create(self):
        self._target = self._create_target("FinalStage")
        self._target.add_color_texture()
        self._target.prepare_offscreen_buffer()
        self._target.make_main_target()

    def set_shaders(self):
        self._target.set_shader(self._load_shader("Stages/FinalStage.fragment"))

    def resize(self):
        RenderStage.resize(self)
        self.debug("Resizing pass")

    def cleanup(self):
        RenderStage.cleanup(self)
        self.debug("Cleanup pass")
