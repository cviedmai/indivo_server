"""
Indivo views -- nevershare
"""

import indivo.views
from indivo.views.base import *
from indivo.views.documents.document import _render_documents
from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied

@paramloader('docbox')
def document_set_nevershare(request, docbox, document):
  """
  Flag a document as nevershare
  """
  document.nevershare = True
  document.save()
  return DONE

@paramloader('docbox')
def document_remove_nevershare(request, docbox, document):
  """
  Remove nevershare flag
  """
  document.nevershare = False
  document.save()
  return DONE
