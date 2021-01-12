
ID = 'OP_ID'

INC   = 'OP_INC'
MAX   = 'OP_MAX'
MIN   = 'OP_MIN'
RW    = 'OP_RW'
READ  = 'OP_READ'
WRITE = 'OP_WRITE'

DAT_ACCESS_TYPES = [READ, WRITE, RW, INC]
GBL_ACCESS_TYPES = [READ, INC, MAX, MIN]


class Set:

  def __init__(self, name: str, size: int):
    self.name = name
    self.size = size


class Map:

  def __init__(self, dim: int):
    self.dim = dim
  

class Data:

  def __init__(self, set_: str, dim: int, typ: str):
    self.set = set_
    self.dim = dim
    self.typ = typ


class Const:

  def __init__(self, name: str, dim: int):
    self.name = name
    self.dim = dim


class Arg:

  def __init__(self, var: str, dim: int, typ: str, acc: str, map_: str = None, idx: int = None):
    self.var = var
    self.dim = dim
    self.typ = typ
    self.acc = acc
    self.map = map_
    self.idx = idx

    # if map_ == ID:
    #   if idx != -1:
    #     exit('incompatible index for direct access, expected -1')
    # elif map_ and idx is not None:
    #   if idx < 1 or idx > dim:
    #     exit(f'out of range index, must be in range 1-{dim}')


  @property
  def direct(self) -> bool:
    return self.map == ID


  @property
  def indirect(self) -> bool:
    return self.map is not None and self.map != ID


  @property
  def global_(self):
    return self.map is None 


class Loop:

  def __init__(self, kernel: str, set_: str, args: [Arg]):
    self.name = kernel
    self.set = set_
    self.args = dict(enumerate(args))


  @property
  def indirection(self):
    return len(self.indirects) > 0


  @property
  def directs(self):
    return { i: arg for i, arg in self.args.items() if arg.direct }


  @property
  def indirects(self):
    return { i: arg for i, arg in self.args.items() if arg.indirect }


  @property
  def globals(self):
    return { i: arg for i, arg in self.args.items() if arg.global_ }


  @property
  def indirectVars(self):
    # TODO: Tidy
    x, r = [], {}
    for i, arg in self.indirects.items():
      y = arg.var
      if y not in x:
        x.append(y)
        r[i] = arg

    return r


  @property
  def indirectMaps(self):
    # TODO: Tidy
    x, r = [], {}
    for i, arg in self.indirects.items():
      y = arg.map
      if y not in x:
        x.append(y)
        r[i] = arg

    return r


  @property
  def indirectMapRefs(self):
    # TODO: Tidy
    x, r = [], {}
    for i, arg in self.indirects.items():
      y = (arg.map, arg.idx)
      if y not in x:
        x.append(y)
        r[i] = arg

    return r
