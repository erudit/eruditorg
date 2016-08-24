import CiteModal from '../../../modules/public/Cite';

export default {
  init() {
    /*
     * Update the text that displays the total count of selected documents.
     */
    function updateDocumentSelectionCount() {
      let documentsSelectedCount = $('ul.documents .document-checkbox-wrapper input[type=checkbox]:checked').length;
      let gettextContext = {count: documentsSelectedCount, };

      let fmts = ngettext('%(count)s document sélectionné', '%(count)s documents sélectionnés', gettextContext.count);
      let s = interpolate(fmts, gettextContext, true);
      $('.selection-action-wrapper p').text(s);
      if (documentsSelectedCount) { $('#id_selection_tools').show(); } else { $('#id_selection_tools').hide(); }
    }

    /*
     * Update the count of a document of a specific type if we remove it.
     * @param {JQuery selector} $document - The selector of the document object.
     */
    function updateDocumentTypeCount($document) {
      let documentType = $document.data('document-type');
      let $documentTypeCountBlock = $('[data-' + documentType + '-count]');
      let documentTypeCount = parseInt($documentTypeCountBlock.data(documentType + '-count'));
      documentTypeCount -= 1;
      // Update the count of the related document type
      if (documentTypeCount) {
        let gettextContext = {count: documentTypeCount, };
        let fmts = undefined;
        if (documentType === 'scientific-article') {
          fmts = ngettext('%(count)s article savant', '%(count)s articles savants', gettextContext.count);
        } else if (documentType === 'cultural-article') {
          fmts = ngettext('%(count)s article culturel', '%(count)s articles culturels', gettextContext.count);
        } else if (documentType === 'search-unit-document') {
          fmts = ngettext('%(count)s document (littérature grise)', '%(count)s documents (littérature grise)', gettextContext.count);
        } else if (documentType === 'thesis') {
          fmts = ngettext('%(count)s thèse', '%(count)s thèses', gettextContext.count);
        }
        let s = interpolate(fmts, gettextContext, true);
        $documentTypeCountBlock.text(s);
        $documentTypeCountBlock.data(documentType + '-count', documentTypeCount);
      } else {
        $documentTypeCountBlock.remove();
      }
    }

    /*
     * Remove a specific document from the saved citations list.
     * The function also updates the texts displaying the number of documents associated with the
     * document type of the document being removed.
     * @param {JQuery selector} $document - The selector of the document object.
     */
    function removeDocument($document) {
      let documentId = $document.data('document-id');
      $.ajax({
        type: 'POST',
        url: Urls['public:citations:remove_citation'](documentId),
      }).done(function() {
        $document.remove();
        updateDocumentSelectionCount();
        updateDocumentTypeCount($document);
      });
    }

    /*
     * Returns the list of documents IDs that are selected.
     */
    function getSelectedDocumentIds() {
      var documentIds = new Array();
      $('ul.documents .document-checkbox-wrapper input[type=checkbox]:checked').each(function() {
        let $document = $(this).parents('li');
        documentIds.push($document.data('document-id'));
      });
      return documentIds;
    }

    $('.documents-head input[type=checkbox]').on('change', function(ev) {
      if ($(this).is(':checked')) {
        // Check all the checkboxes associated with each document
        $('ul.documents .document-checkbox-wrapper input[type=checkbox]').each(function() {
          $(this).prop('checked', true);
        });
      } else {
        // Uncheck all the checkboxes associated with each document
        $('ul.documents .document-checkbox-wrapper input[type=checkbox]').each(function() {
          $(this).prop('checked', false);
        });
      }
      $('ul.documents .document-checkbox-wrapper input[type=checkbox]').change();
    });

    $('ul.documents .document-checkbox-wrapper input[type=checkbox]').on('change', updateDocumentSelectionCount);

    $('a[data-remove]').click(function(ev) {
      ev.preventDefault();
      let $document = $(this).parents('li');
      removeDocument($document);
    });

    $('#id_selection_tools a.remove-selection').click(function(ev) {
      ev.preventDefault();

      var r = confirm(gettext("Voulez-vous vraiment supprimer votre sélection ?"));
      if (r == false) { return; }

      var documentIds = getSelectedDocumentIds();

      $.ajax({
        type: 'POST',
        url: Urls['public:citations:remove_citation_batch'](),
        data: { document_ids: documentIds },
        traditional: true
      }).done(function() {
        $('ul.documents .document-checkbox-wrapper input[type=checkbox]:checked').each(function() {
          let $document = $(this).parents('li');
          updateDocumentTypeCount($document);
          $document.remove();
          updateDocumentSelectionCount();
        });
      });
    });

    $('#export_citation_enw').click(function(ev) {
      ev.preventDefault();
      var documentIds = getSelectedDocumentIds();
      var export_url = Urls['public:citations:citation_enw']() + '?' + $.param({document_ids: documentIds}, true);
      window.location.href = export_url;
    });
    $('#export_citation_ris').click(function(ev) {
      ev.preventDefault();
      var documentIds = getSelectedDocumentIds();
      var export_url = Urls['public:citations:citation_ris']() + '?' + $.param({document_ids: documentIds}, true);
      window.location.href = export_url;
    });
    $('#export_citation_bib').click(function(ev) {
      ev.preventDefault();
      var documentIds = getSelectedDocumentIds();
      var export_url = Urls['public:citations:citation_bib']() + '?' + $.param({document_ids: documentIds}, true);
      window.location.href = export_url;
    });

    // Initializes the citation modals
    $('a[data-cite]').each(function(){
      new CiteModal($(this));
    });
  },
};
