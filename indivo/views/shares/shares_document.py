"""
Indivo views -- Sharing
"""

import indivo.views
from indivo.views.base import *
from indivo.views.documents.document import _render_documents
from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied

from django.db.models import F

@paramloader('docbox')
@transaction.commit_on_success
def carenet_document_placement(request, docbox, document):
  """
  Place a document into a given carenet
  """

  # don't allow this for nevershare documents
  if document.nevershare:
    raise Http404

  CarenetDocument.objects.get_or_create(carenet=docbox.carenet, document=document)
  return DONE

@paramloader('docbox')
def carenet_document_delete(request, docbox, document):
  """Delete a document into a given carenet"""

  # this is always permission denied, so we can just handle it here
  # not in the access control system
  if document.record != docbox.carenet.record:
    raise Http404

  doc_share, created_p = CarenetDocument.objects.get_or_create(document = document, carenet = docbox.carenet, defaults={'share_p':False})

  if not created_p and doc_share.share_p:
    doc_share.share_p = True
    doc_share.save()

  return DONE

@paramloader('docbox')
def carenet_record(request, docbox):
  """Basic record information within a carenet

  For now, just the record label
  """
  return render_template('record', {'record': docbox.record})

@paramloader('docbox')
@marsloader
def carenet_document_list(request, docbox, limit, offset, status, order_by):
  """List documents from a given carenet

    Return both documents in the given carenet and 
    documents with the same types as in the record's autoshare

    FIXME: this needs refactoring so it's one query for the whole thing,
    rather than one query per auto-share doctype
  """
  
  try:
    doc_type_uri = request.GET.get('type', None)
    if doc_type_uri:
      requested_doc_type = DocumentSchema.objects.get(type = doc_type_uri)
    else:
      requested_doc_type = None
  except DocumentSchema.DoesNotExist:
    raise Http404

  # we want to select
  # the documents that are explicitly shared
  # plus the documents that are auto-shared
  # minus the documents that are explicitly un-shared
  
  carenet = docbox.carenet
  record = carenet.record
  
  # documents explicitly shared
  explicitly_shared = record.documents.filter(carenetdocument__share_p = True, carenetdocument__carenet = carenet, nevershare= False)
  if requested_doc_type:
    explicitly_shared = explicitly_shared.filter(type = requested_doc_type)

  # auto-shared documents that are not in the negatively shared space
  autoshared_types = DocumentSchema.objects.filter(carenetautoshare__carenet = carenet).values('id')
  implicitly_shared = record.documents.filter(type__in = autoshared_types, nevershare=False).exclude(carenetdocument__share_p = False, carenetdocument__carenet = carenet)

  if requested_doc_type:
    implicitly_shared = implicitly_shared.filter(type = requested_doc_type)

  # FIXME: we should make this lazy so that it's not evaluated right now
  all_documents = [d for d in explicitly_shared] + [d for d in implicitly_shared]

  documents = all_documents[offset:offset+limit]

  return _render_documents(request, documents, docbox.record, None, len(documents))


@paramloader('docbox')
def carenet_document(request, docbox, document):
  """Return a document given a record and carenet id

    Return the document if it is in the given carenet or 
    its type is in the record's autoshare
  """

  if document.nevershare:
    raise Http404

  try:
    if CarenetDocument.objects.filter(carenet = docbox.carenet, document = document, carenet__record = docbox.record, share_p=True) or \
          (CarenetAutoshare.objects.filter(carenet = docbox.carenet, record = docbox.record, type = document.type) and \
             not CarenetDocument.objects.filter(carenet = docbox.carenet, document = document, share_p=False)):
      return indivo.views.document(request, document_id=document.id, record_id=docbox.record.id, pha_email=None)
    else: 
      raise Http404
  except Carenet.DoesNotExist:
    raise Http404

@paramloader('docbox')
def document_carenets(request, docbox, document):
  """List all the carenets for a given document

    This view retrieves all the carenets in which  a given 
    document has been placed
  """

  if document.nevershare:
    carenets = []
  else:
    # the carenets for which a carenetdocument share exists with that particular document
    carenets = Carenet.objects.filter(carenetdocument__document = document, carenetdocument__share_p=True)
    
  return render_template('carenets', {'carenets' : carenets, 'record' : docbox.record})
