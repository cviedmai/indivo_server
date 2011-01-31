from indivo.models import Record, Carenet

RECORD, CARENET = 'record', 'carenet'

PREFIX_TO_OBJECT_MAPPINGS = {
  'R': Record,
  'C': Carenet
}

# reverse the mappings
OBJECT_TO_PREFIX_MAPPINGS = dict([(v,k) for k,v in PREFIX_TO_OBJECT_MAPPINGS.iteritems()])

class Docbox:
  """
  An object that contains documents, for now either a record or a carenet.
  This needs some rethinking, but for now it will work.
  """

  record, carenet = None, None

  def __init__(self, obj=None):
    if obj: self.set(obj)

  def set(self, obj):
    if obj:
      if isinstance(obj, Record):   self.record   = obj
      if isinstance(obj, Carenet):  self.carenet  = obj
      self.check()
    return self

  def check(self):
    if self.carenet and not self.record:
      self.record = self.carenet.record
    return True

  ##
  ## some methods to express a docbox ID in a way that can be reparsed
  ##
  @classmethod
  def is_docbox(cls, id):
    prefix, rest = id[0], id[1:]
    
    return PREFIX_TO_OBJECT_MAPPINGS.has_key(prefix)

  @classmethod
  def get_by_id(cls, id):
    prefix, rest = id[0], id[1:]
  
    if not PREFIX_TO_OBJECT_MAPPINGS.has_key(prefix):
      raise Exception("no such docbox")
    
    return cls(PREFIX_TO_OBJECT_MAPPINGS[prefix].objects.get(id = rest))

  @property
  def id(self):
    type = None
    if self.carenet:
      type=Carenet
    if self.record:
      type=Record

    return "%s%s" % (OBJECT_TO_PREFIX_MAPPINGS[type], getattr(self.carenet or self.record, 'id'))
