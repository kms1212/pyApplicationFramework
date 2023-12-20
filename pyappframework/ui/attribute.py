# Library Imports
import wx
import abc
from typing import Callable, Optional, Generic, Any, TypeVar, Union

# Internal Imports
from ..decorators import event_handler
from ..mutable import Mutable, MutationEvent

# R: Generic type for root
# P: Generic type for parent
# T: Generic type for Target
# V: Generic type for Value
R, P, T = (TypeVar("R"), TypeVar("P"), TypeVar("T"))
class AttributeContainer(Generic[R, P, T]):
    def __init__(self):
        self.__attrib_delegates = []

    def addAttribDelegate(self, func: Callable[[R, P, T], None]):
        self.__attrib_delegates.append(func)

    def runAttribDelegates(self, root: R, parent: P, target: T):
        for delegate in self.__attrib_delegates:
            delegate(root, parent, target)

R, P, T = (TypeVar("R"), TypeVar("P"), TypeVar("T"))
class AttributeBase(Generic[R, P, T]):
    def __init__(self, obj: AttributeContainer[R, P, T], count: int = -1):
        self.obj = obj
        self.count = count

    def checkCount(self):
        if self.count >= 0:
            assert self.count > 0
            self.count -= 1

    def __call__(self, *args) -> Any:
        self.checkCount()
        self._handle_value(*args)
        return self.obj
    
    @abc.abstractmethod
    def _handle_value(self, *args):
        pass

R, P, T, V = (TypeVar("R"), TypeVar("P"), TypeVar("T"), TypeVar("V"))
class Attribute(Generic[R, P, T, V], AttributeBase[R, P, T]):
    def __init__(self, obj: AttributeContainer[R, P, T], default: Optional[V] = None, count: int = -1):
        super().__init__(obj, count)
        self.value = default

    def _handle_value(self, value: V):
        self.value = value

R, P, T = (TypeVar("R"), TypeVar("P"), TypeVar("T"))
class ArgumentAttribute(Generic[R, P, T], Attribute[R, P, T, tuple[tuple, dict]]):
    def __init__(self, obj: AttributeContainer[R, P, T], count: int = -1):
        super().__init__(obj, ((), {}), count)

    def __call__(self, *args, **kw) -> Any:
        return Attribute.__call__(self, (args, kw))

class SizerChildAttribute(ArgumentAttribute[wx.Window, wx.Window, wx.Window]):
    def __init__(self, obj: AttributeContainer[wx.Window, wx.Window, wx.Window]):
        super().__init__(obj, 1)

    def _handle_value(self, value: tuple[dict, tuple]):
        self.obj.addAttribDelegate(self._delegate(value))

    def _delegate(self, value: tuple[dict, tuple]):
        def func(root: wx.Window, parent: wx.Window, target: wx.Window):
            parent_sizer = target.GetParent().GetSizer()
            if parent_sizer is not None:
                parent_sizer.Add(target, *value[0], **value[1])
        return func

class FontAttribute(AttributeBase[wx.Window, wx.Window, wx.Window]):
    def __init__(self, obj: AttributeContainer[wx.Window, wx.Window, wx.Window]):
        super().__init__(obj, 1)

    def _handle_value(self, font: Union[wx.Font, wx.FontInfo]):
        self.obj.addAttribDelegate(self._delegate(wx.Font(font)))

    def _delegate(self, font: wx.Font):
        def func(root: wx.Window, parent: wx.Window, target: wx.Window):
            target.SetFont(font)
        return func

R, P, T = (TypeVar("R"), TypeVar("P"), TypeVar("T"))
class EventHandlerAttribute(AttributeBase[R, P, T]):
    def _handle_value(self, evt: wx.Event, func: Callable[[wx.Event], None]):
        self.obj.addAttribDelegate(self._delegate(evt, func))

    def _delegate(self, evt: wx.Event, handler: Callable[[wx.Event], None]):
        def func(root, parent, target):
            root.Bind(evt, handler, target)
        return func

class ToolTipAttribute(AttributeBase[wx.Window, wx.Window, wx.Window]):
    def __init__(self, obj: AttributeContainer[wx.Window, wx.Window, wx.Window]):
        super().__init__(obj, 1)

    def _handle_value(self, tto: Union[wx.ToolTip, str]):
        self.obj.addAttribDelegate(self._delegate(tto))

    def _delegate(self, tto: Union[wx.ToolTip, str]):
        def func(root: wx.Window, parent: wx.Window, target: wx.Window):
            target.SetToolTip(tto)
        return func

R, P, T = (TypeVar("R"), TypeVar("P"), TypeVar("T"))
class ExportAttribute(AttributeBase[R, P, T]):
    def __init__(self, obj: AttributeContainer[R, P, T]):
        super().__init__(obj, 1)

    def _handle_value(self, attr: str):
        self.obj.addAttribDelegate(self._delegate(attr))

    def _delegate(self, attr: str):
        def func(root: R, parent: P, target: T):
            setattr(root, attr, target)
        return func

C = TypeVar("C")
CONTENTS_LIST_TYPE = list[C]

C = TypeVar("C")
CONTENTS_LIST_INPUT_TYPE = list[Union[C, CONTENTS_LIST_TYPE[C]]]

R, P, T, V = (TypeVar("R"), TypeVar("P"), TypeVar("T"), TypeVar("V"))
class BodyAttribute(Generic[R, P, T, V], AttributeBase[R, P, T]):
    def __init__(self, obj: AttributeContainer[R, P, T]):
        super().__init__(obj, 1)
        self.body = []

    def _handle_value(self, l: CONTENTS_LIST_INPUT_TYPE[V]):
        for litem in l:
            if isinstance(litem, list):
                self.body.extend(litem)
            else:
                self.body.append(litem)

    __getitem__ = AttributeBase.__call__
