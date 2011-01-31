from indivo.models import Document

class DocumentUtils:

  def get_latest_doc(self, docid):
    docobj = Document.objects.get(id=docid)
    while docobj.replaced_by_id:
      docobj = Document.objects.get(id=docobj.replaced_by_id)
    return docobj

  def is_binary(self, data):
    NULL_CHR = '#'
    count, null_count  = 1.0, 0.0 
    threshold = 0.20
    if isinstance(data, str) or isinstance(data, unicode):
      printable = ''.join(["%s" % ((  ord(x) <= 127 and \
                                      len(repr(chr(ord(x))))  == 3 and \
                                      chr(ord(x))) or \
                                    NULL_CHR) 
                                for x in data])
      for char in printable:
        if char == NULL_CHR:
          null_count += 1
        count += 1
      if null_count / count  > threshold:
        return True
    return False

