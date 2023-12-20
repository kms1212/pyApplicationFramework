# Library Imports
import unittest
import wx
from wx.lib import scrolledpanel as sp

# Internal Imports
import pyappframework as pyaf
from pyappframework import ui
from pyappframework.ui import controls as ctl

class TestWindow(ui.Window):
    ToolBar: wx.ToolBar
    NormalTool: wx.ToolBarToolBase
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetTitle("TestWindow")

    def body(self) -> ctl.Panel:
        return (
            ctl.ScrollablePanel(wx.BoxSizer(wx.VERTICAL))
                .body [[
                ctl.ToolBar(style=wx.TB_HORIZONTAL | wx.TB_TEXT)
                    .export("ToolBar")
                    .sizer(proportion=1, flag=wx.EXPAND)
                    .body [[
                    ctl.NormalTool(wx.ID_ANY, "Tool1", wx.NullBitmap)
                        .export("NormalTool"),
                    ctl.NormalTool(wx.ID_ANY, "Tool2", wx.Image("test/resources/test_image.png", type=wx.BITMAP_TYPE_PNG).Rescale(50, 50).ConvertToBitmap(), wx.NullBitmap, wx.ITEM_CHECK),
                    ctl.ToolSeparator(),
                    ctl.RadioTool(wx.ID_ANY, "Tool6", wx.Image("test/resources/test_image.png", type=wx.BITMAP_TYPE_PNG).Rescale(50, 50).ConvertToBitmap())
                        .eventHandler(wx.EVT_RADIOBUTTON, self.eventHandlerTest),
                    ctl.RadioTool(wx.ID_ANY, "Tool7", wx.Image("test/resources/test_image.png", type=wx.BITMAP_TYPE_PNG).Rescale(50, 50).ConvertToBitmap()),
                    ctl.RadioTool(wx.ID_ANY, "Tool8", wx.Image("test/resources/test_image.png", type=wx.BITMAP_TYPE_PNG).Rescale(50, 50).ConvertToBitmap()),
                    ctl.ToolSpacer(),
                    ctl.ControlTool("Tool3")
                        .control(
                            ctl.Choice(choices=[f"Choice{n}" for n in range(6)])
                                .tooltip("ToolTip")
                        ),
                ]]
            ]]
        )

    def eventHandlerTest(self, evt: wx.Event):
        print("event")

class AttributesTest(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = None

    def tearDown(self):
        wx.CallAfter(self.app.ExitMainLoop)
        self.app.MainLoop()
        assert self.frame is not None
        self.frame.Destroy()
        self.app.Destroy()

    def runTest(self):
        self.frame = TestWindow()
        self.frame.Show()
        self.assertTrue(isinstance(self.frame.ToolBar, wx.ToolBar))
        self.assertTrue(isinstance(self.frame.NormalTool, wx.ToolBarToolBase))
