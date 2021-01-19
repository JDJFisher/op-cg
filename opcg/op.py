# Standard library imports
from __future__ import annotations
from typing import TYPE_CHECKING, Final, Optional, Dict, List

# Application imports
if TYPE_CHECKING:
  from parser.common import Location


ID: Final[str] = 'OP_ID'

INC: Final[str] = 'OP_INC'
MAX: Final[str] = 'OP_MAX'
MIN: Final[str] = 'OP_MIN'
RW: Final[str] = 'OP_RW'
READ: Final[str] = 'OP_READ'
WRITE: Final[str] = 'OP_WRITE'

DAT_ACCESS_TYPES = [READ, WRITE, RW, INC]
GBL_ACCESS_TYPES = [READ, INC, MAX, MIN]


class OpError(Exception):
  message: str
  loc: Location

  def __init__(self, message: str, loc: Location = None) -> None:
    self.message = message
    self.loc = loc

  def __str__(self) -> str:
    if self.loc:
      return f'{self.loc}: OP error: {self.message}'
    else:
      return f'OP error: {self.message}'


class Set:
  ptr: str

  def __init__(self, ptr: str) -> None:
    self.ptr = ptr


class Map:
  from_set: str
  to_set: str
  dim: int
  ptr: str
  loc: Location

  def __init__(
    self,
    from_set: str,
    to_set: str,
    dim: int,
    ptr: str,
    loc: Location
  ) -> None:
    self.from_set = from_set
    self.to_set = to_set
    self.dim = dim
    self.ptr = ptr
    self.loc = loc
  

class Data:
  set: str
  dim: int
  typ: str
  ptr: str
  loc: Location

  def __init__(
    self,
    set_: str,
    dim: int,
    typ: str,
    ptr: str,
    loc: Location
  ) -> None:
    self.set = set_
    self.dim = dim
    self.typ = typ
    self.ptr = ptr
    self.loc = loc


class Const:
  name: str
  dim: int
  loc: Location

  def __init__(self, name: str, dim: int, loc: Location) -> None:
    self.name = name
    self.dim = dim
    self.loc = loc


class Arg:
  i: int = 0 # Loop argumnet index
  var: str   # Dataset identifier
  dim: int   # Dataset dimension (redundant)
  typ: str   # Dataset type (redundant)
  acc: str   # Dataset access operation
  loc: Location      # Source code location
  map: Optional[str] # Indirect mapping indentifier
  idx: Optional[int] # Indirect mapping index
  opt: Optional[str]

  def __init__(
    self, 
    var: str, 
    dim: int, 
    typ: str, 
    acc: str, 
    loc: Location,
    map_: str = None, 
    idx: int = None
  ) -> None:
    self.var = var
    self.dim = dim
    self.typ = typ
    self.acc = acc
    self.loc = loc
    self.map = map_
    self.idx = idx
    self.opt = None


  @property
  def direct(self) -> bool:
    return self.map == ID


  @property
  def indirect(self) -> bool:
    return self.map is not None and self.map != ID


  @property
  def global_(self) -> bool:
    return self.map is None 


class Loop:
  kernel: str
  set: str
  loc: Location
  args: List[Arg] 

  def __init__(self, kernel: str, set_: str, loc: Location, args: List[Arg]) -> None:
    self.kernel = kernel
    self.set = set_
    self.loc = loc
    self.args = args
    for i, arg in enumerate(args):
      arg.i = i


  @property
  def name(self) -> str: 
    return self.kernel # TODO: Unique name for incompatiable loops on the same kernel


  @property
  def indirection(self) -> bool:
    return len(self.indirects) > 0


  @property
  def directs(self) -> List[Arg]:
    return [ arg for arg in self.args if arg.direct ]


  @property
  def indirects(self) -> List[Arg]:
    return [ arg for arg in self.args if arg.indirect ]


  @property
  def globals(self) -> List[Arg]:
    return [ arg for arg in self.args if arg.global_ ]


  @property
  def indirectVars(self) -> List[Arg]:
    # TODO: Tidy
    x, r = [], []
    for arg in self.indirects:
      if arg.var not in x:
        x.append(arg.var)
        r.append(arg)

    return r


  @property
  def indirectMaps(self) -> List[Arg]:
    # TODO: Tidy
    x, r = [], []
    for arg in self.indirects:
      if arg.map not in x:
        x.append(arg.map)
        r.append(arg)

    return r

