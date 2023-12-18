# Library Imports
import unittest
import wx

# Internal Imports
from pyappframework import ui
from pyappframework.ui import controls as ctl

class TestWindow(ui.Window):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetTitle("TestWindow")

    def body(self) -> ctl.Panel:
        return (
            ctl.Panel(wx.BoxSizer(wx.VERTICAL))
                .export("ValidInstanceAttribute")
                .export("InvalidInstanceAttribute")
        )

class InvalidAttrTest(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = None

    def tearDown(self):
        wx.CallAfter(self.app.ExitMainLoop)
        self.app.MainLoop()
        self.app.Destroy()

    def runTest(self):
        with self.assertRaises(AssertionError) as _:
            self.frame = TestWindow()
