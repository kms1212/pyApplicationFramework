# Library Imports
import wx

# Internal Imports
from .. import attribute as attr
from ..view import PrimitiveView

class Control(PrimitiveView):
    def __init__(self):
        super().__init__()
        self.sizer = attr.SizerChildAttribute(self)
        self.eventHandler = attr.EventHandlerAttribute(self)
        self.tooltip = attr.ToolTipAttribute(self)
        self.font = attr.FontAttribute(self)
        self.export = attr.ExportAttribute(self)
