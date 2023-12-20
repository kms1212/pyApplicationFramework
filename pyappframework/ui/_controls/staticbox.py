# Library Imports
import wx
from typing import Optional

# Internal Imports
from ..view import PrimitiveView
from .control import Control
from .. import attribute as attr

class StaticBox(Control):
    def __init__(self, sizer: wx.Sizer, *args, **kw):
        super().__init__()
        self.__sizer = sizer
        self.__init_args = (args, kw)
        self.body = attr.BodyAttribute[wx.Window, wx.Window, wx.Window, PrimitiveView](self)

    def _initialize(self, root: PrimitiveView, parent: PrimitiveView) -> wx.Window:
        sb = wx.StaticBox(parent.getWxInstance(), *self.__init_args[0], **self.__init_args[1])
        sb.SetSizer(self.__sizer)
        self.setWxInstance(sb)
        for view in self.body.body:
            assert isinstance(view, PrimitiveView)
            view.initialize(root, self)
        return sb
