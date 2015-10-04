
from panda3d.core import Texture, Vec3

from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectFrame import DirectFrame

from ..Util.Generic import rgb_from_string
from DraggableWindow import DraggableWindow
from BetterOnscreenText import BetterOnscreenText
from BetterOnscreenImage import BetterOnscreenImage

from ..Globals import Globals


class PipeViewer(DraggableWindow):

    """ Small tool which displays the order of the graphic pipes """

    _STAGE_MGR = None

    @classmethod
    def register_stage_mgr(cls, mgr):
        cls._STAGE_MGR = mgr

    def __init__(self, pipeline):
        DraggableWindow.__init__(self, width=1300, height=900,
                                 title="Pipe Inspector")
        self._pipeline = pipeline
        self._scroll_width = 8000
        self._scroll_height = 2000
        self._created = False
        self._create_components()
        self.hide()

    def toggle(self):
        """ Toggles the pipe viewer """
        if self._visible:
            Globals.base.taskMgr.remove("UpdatePipeViewer")
            self.hide()
        else:
            Globals.base.taskMgr.add(self._update_task, "UpdatePipeViewer")
            if not self._created:
                self._populate_content()
            self.show()

    def _update_task(self, task=None):
        """ Updates the viewer """
        scroll_value = self._content_frame.horizontalScroll["value"]
        scroll_value *= 2.45
        self._pipe_descriptions.set_x(scroll_value * 2759.0)
        return task.cont

    def _populate_content(self):
        """ Reads the pipes and stages from the stage manager and renders those
        into the window """
        self._created = True
        self._pipe_node = self._content_node.attach_new_node("pipes")
        self._pipe_node.set_scale(1, 1, -1)
        self._stage_node = self._content_node.attach_new_node("stages")
        current_pipes = []
        pipe_pixel_size = 3

        # Generate stages
        for offs, stage in enumerate(self._STAGE_MGR._stages):
            node = self._content_node.attach_new_node("stage")
            node.set_pos(220 + offs * 200.0, 0, 20)
            node.set_scale(1, 1, -1)
            DirectFrame(parent=node, frameSize=(10, 150, 0, -3600),
                        frameColor=(0.2, 0.2, 0.2, 1))
            BetterOnscreenText(text=str(stage.get_name().replace("Stage", "")),
                               parent=node, x=20, y=25, size=15)

            for output_pipe, pipe_tex in stage.get_produced_pipes().iteritems():
                pipe_idx = 0
                r, g, b = rgb_from_string(output_pipe)
                if output_pipe in current_pipes:
                    pipe_idx = current_pipes.index(output_pipe)
                else:
                    current_pipes.append(output_pipe)
                    pipe_idx = len(current_pipes) - 1
                    DirectFrame(parent=node,
                                frameSize=(0, 8000, pipe_pixel_size / 2,
                                           -pipe_pixel_size / 2),
                                frameColor=(r, g, b, 1),
                                pos=(10, 1, -95 - pipe_idx * 110.0))
                w = 160
                h = Globals.base.win.get_y_size() /\
                    float(Globals.base.win.get_x_size()) * w
                DirectFrame(parent=node,
                            frameSize=(-pipe_pixel_size, w + pipe_pixel_size,
                                       h / 2 + pipe_pixel_size,
                                       -h / 2 - pipe_pixel_size),
                            frameColor=(r, g, b, 1),
                            pos=(0, 1, -95 - pipe_idx * 110.0))

                if pipe_tex.get_z_size() > 1:
                    self.debug("Ignoring 3D image", pipe_tex.get_name())
                    continue

                if pipe_tex.get_texture_type() == Texture.TT_buffer_texture:
                    self.debug("Ignoring texture buffer", pipe_tex.get_name())
                    continue

                BetterOnscreenImage(image=pipe_tex, parent=node,
                                    x=0, y=50 + pipe_idx * 110.0,
                                    w=w, h=h, any_filter=False,
                                    transparent=False)

            for input_pipe in stage.get_input_pipes():
                idx = current_pipes.index(input_pipe)
                r, g, b = rgb_from_string(input_pipe)
                DirectFrame(parent=node, frameSize=(0, 10, 40, -40),
                            frameColor=(r, g, b, 1),
                            pos=(5, 1, -95 - idx * 110.0))

        self._pipe_descriptions = self._content_node.attach_new_node(
            "PipeDescriptions")
        self._pipe_descriptions.set_scale(1, 1, -1)

        # Generate the pipe descriptions
        for idx, pipe in enumerate(current_pipes):
            r, g, b = rgb_from_string(pipe)
            DirectFrame(parent=self._pipe_descriptions,
                        frameSize=(0, 180, -90, -140),
                        frameColor=(r, g, b, 1.0), pos=(0, 1, -idx * 110.0))
            BetterOnscreenText(parent=self._pipe_descriptions, text=pipe,
                               x=20, y=120 + idx * 110, size=15,
                               color=Vec3(0.2, 0.2, 0.2))

    def _create_components(self):
        """ Internal method to create the window components """
        DraggableWindow._create_components(self)

        self._content_frame = DirectScrolledFrame(
            frameSize=(0, self._width - 40, 0, self._height - 80),
            canvasSize=(0, self._scroll_width, 0, self._scroll_height),
            autoHideScrollBars=False,
            scrollBarWidth=20.0,
            frameColor=(0, 0, 0, 0),
            verticalScroll_relief=False,
            horizontalScroll_relief=False,
            parent=self._node,
            pos=(20, 1, -self._height + 20))
        self._content_node = self._content_frame.getCanvas().attach_new_node("PipeComponents")
        self._content_node.set_scale(1, 1, -1)
        self._content_node.set_z(self._scroll_height)
