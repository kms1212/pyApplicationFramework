# Library Imports
import wx
from typing import TypeVar, Generic, Callable, Any, Union, Optional
from typing_extensions import Self
import itertools
import threading

# Internal Imports


EVT_MUTATION = wx.NewEventType()

IDGenerator = itertools.count()

T = TypeVar("T")
class MutationEvent(Generic[T], wx.PyCommandEvent):
    def __init__(self, id: int, oldValue: T, newValue: T):
        super().__init__(EVT_MUTATION, id)
        self.__oldValue = oldValue
        self.__newValue = newValue

    @property
    def oldValue(self) -> T:
        return self.__oldValue

    @property
    def newValue(self) -> T:
        return self.__newValue

T = TypeVar("T")
SYNC_GETTER_TYPE = Union[Callable[[], T], tuple[object, str]]

T = TypeVar("T")
SYNC_SETTER_TYPE = Union[Callable[[T], None], tuple[object, str]]

T = TypeVar("T")
class MutableExpression(Generic[T]):
    def __init__(self, expr: Optional[Callable[..., T]], *args):
        self.__args = args
        self.__expr = expr
        self.rawValue = self._evaluate()
        self.evtId = next(IDGenerator)
        self.evtBinder = wx.PyEventBinder(EVT_MUTATION, 1)
        self.evtHandler = wx.EvtHandler()
        if expr is not None:
            for arg in args:
                if ismutable(arg):
                    arg.addListener(self._internal_listener)

    def _internal_listener(self, evt: MutationEvent):
        oldValue = self.rawValue
        self.rawValue = self._evaluate()
        self._raiseEvent(oldValue, self.rawValue)
        
    def _evaluate(self) -> T:
        if self.__expr is None:
            assert len(self.__args) == 1
            return valueof(self.__args[0])
        else:
            arg_tuple = (valueof(arg) for arg in self.__args)
            return self.__expr(*arg_tuple)

    def addListener(self, func: Callable[[MutationEvent], None]):
        self.evtBinder.Bind(self.evtHandler, self.evtId, wx.ID_ANY, func)
        evt = MutationEvent(self.evtId, self.rawValue, self.rawValue)
        self.evtHandler.ProcessEvent(evt)

    @property
    def value(self) -> T:
        return self.rawValue

    @value.setter
    def value(self, val: T):
        return

    def _raiseEvent(self, oldValue: T, newValue: T):
        evt = MutationEvent(self.evtId, oldValue, newValue)
        self.evtHandler.ProcessEvent(evt)

    def syncFrom(self, getter: SYNC_GETTER_TYPE[T]) -> Callable[[wx.Event], None]:
        return lambda _: None

    def syncTo(self, setter: SYNC_SETTER_TYPE[T]):
        def listener(evt: MutationEvent):
            if isinstance(setter, tuple):
                setattr(setter[0], setter[1], evt.newValue)
            else:
                setter(evt.newValue)
            evt.Skip()
        self.addListener(listener)

    def sync(self, getter: SYNC_GETTER_TYPE[T], setter: SYNC_SETTER_TYPE[T]) -> Callable[[wx.Event], None]:
        self.syncTo(setter)
        return self.syncFrom(getter)

    def __repr__(self) -> str:
        return f"(mutable[{type(self.rawValue).__name__}]) '{str(self.rawValue)}'"
    
    def toString(self):
        return MutableExpression(lambda s: str(s), self)

    def __add__(self, other):
        return MutableExpression(lambda s, o: s + o, self, other)

    def __sub__(self, other):
        return MutableExpression(lambda s, o: s - o, self, other)

    def __mul__(self, other):
        return MutableExpression(lambda s, o: s * o, self, other)

    def __matmul__(self, other):
        return MutableExpression(lambda s, o: s @ o, self, other)

    def __truediv__(self, other):
        return MutableExpression(lambda s, o: s / o, self, other)

    def __floordiv__(self, other):
        return MutableExpression(lambda s, o: s // o, self, other)

    def __mod__(self, other):
        return MutableExpression(lambda s, o: s % o, self, other)

    def __divmod__(self, other):
        return MutableExpression(lambda s, o: divmod(s, o), self, other)

    def __pow__(self, other):
        return MutableExpression(lambda s, o: s ** o, self, other)

    def __lshift__(self, other):
        return MutableExpression(lambda s, o: s << o, self, other)

    def __rshift__(self, other):
        return MutableExpression(lambda s, o: s >> o, self, other)

    def __and__(self, other):
        return MutableExpression(lambda s, o: s & o, self, other)

    def __xor__(self, other):
        return MutableExpression(lambda s, o: s ^ o, self, other)

    def __or__(self, other):
        return MutableExpression(lambda s, o: s | o, self, other)
    
    def __lt__(self, other):
        return MutableExpression(lambda s, o: s < o, self, other)
    
    def __le__(self, other):
        return MutableExpression(lambda s, o: s <= o, self, other)
    
    def __eq__(self, other):
        return MutableExpression(lambda s, o: s == o, self, other)
    
    def __gt__(self, other):
        return MutableExpression(lambda s, o: s > o, self, other)
    
    def __ge__(self, other):
        return MutableExpression(lambda s, o: s >= o, self, other)

T = TypeVar("T")
class Mutable(Generic[T], MutableExpression[T]):
    def __init__(self, val: T):
        super().__init__(None, val)

    @property
    def value(self):
        return self.rawValue

    @value.setter
    def value(self, val: T):
        oldValue = self.rawValue
        self.rawValue = val
        self._raiseEvent(oldValue, val)

    def syncFrom(self, getter: SYNC_GETTER_TYPE[T]) -> Callable[[wx.Event], None]:
        def sync_getter():
            if isinstance(getter, tuple):
                value = getattr(getter[0], getter[1])
            else:
                value = getter()
            if self.value != value:
                self.value = value
        def listener(evt: wx.Event):
            sync_getter()
            evt.Skip()
        sync_getter()
        return listener

T = TypeVar("T")
MutableOrNot = Union[MutableExpression[T], T]

def ismutable(val: Any) -> bool:
    return isinstance(val, MutableExpression)

T = TypeVar("T")
def valueof(val: Union[MutableExpression[T], T]) -> T:
    if isinstance(val, MutableExpression):
        return val.value
    else:
        return val

