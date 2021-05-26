import { InlineCiteModal, AjaxCiteModal } from '../../../modules/Cite';

export default {
  init() {
    /*
     * Update the text that displays the total count of selected documents.
     */
    function updateDocumentSelectionCount() {
      // Count all selected documents, even those that are hidden.
      let documentsSelectedCount = $('.bib-records, .hidden-bib-records').find('.checkbox input[type=checkbox]:checked').length;
      let gettextContext = {count: documentsSelectedCount, };

      let fmts = ngettext('%(count)s document sélectionné', '%(count)s documents sélectionnés', gettextContext.count);
      let s = interpolate(fmts, gettextContext, true);
      $('.saved-citations strong').text(s);
      if (documentsSelectedCount) {
        $('#id_selection_tools').show();
      } else {
        $('#id_selection_tools').hide();
        // If there is no more selected document, uncheck `#select-all-on-current-page` checkbox and hide
        // `#select-all-across-all-pages` link.
        $('#select-all-on-current-page').prop('checked', false);
        $('#select-all-across-all-pages').hide();
      }
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
     * Update the total documents count
     */
    function updateTotalDocumentsCount() {
      let newTotalDocumentsCount = parseInt($('.total-documents').text()) - 1;
      $('.total-documents').text(newTotalDocumentsCount);
    }

    /*
     * Reload page if all documents were removed from the page
     */
    function reloadPageIfAllDocumentsRemoved() {
      if ($('.bib-records .bib-record').length === 0) location.reload();
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
        url: Urls['public:citations:remove_citation'](),
        data: { document_id: documentId }
      }).done(function() {
        $document.remove();
        updateDocumentSelectionCount();
        updateDocumentTypeCount($document);
        reloadPageIfAllDocumentsRemoved()
        updateTotalDocumentsCount();
      });
    }

    /*
     * Returns the list of documents IDs that are selected.
     */
    function getSelectedDocumentIds() {
      var documentIds = new Array();
      // Get all selected document IDs, even those that are hidden.
      $('.bib-records, .hidden-bib-records').find('.checkbox input[type=checkbox]:checked').each(function() {
        let $document = $(this).parents('li\.bib-record');
        documentIds.push($document.data('document-id'));
      });
      return documentIds;
    }

    $('#select-all-across-all-pages').on('click', function(ev) {
      // Select all documents, even those that are hidden.
      $('.bib-records, .hidden-bib-records').find('.checkbox input[type=checkbox]').prop('checked', true);
      $(this).hide()
      $('#unselect-all').show();
      updateDocumentSelectionCount();
      ev.preventDefault();
    });

    $('#unselect-all').on('click', function(ev) {
      // Unselect all documents, even those that are hidden.
      $('.bib-records, .hidden-bib-records').find('.checkbox input[type=checkbox]').prop('checked', false);
      $('#select-all-on-current-page').prop('checked', false);
      $(this).hide()
      updateDocumentSelectionCount();
      ev.preventDefault();
    });

    $('#select-all-on-current-page').on('change', function(ev) {
      if ($(this).is(':checked')) {
        // If this checkbox is checked, show the `#select-all-across-all-pages` link if there are
        // citation not on current page.
        if ($('.hidden-bib-records .checkbox').length) {
          $('#select-all-across-all-pages').show();
        }
        // Select all documents on current page.
        $('.bib-records .checkbox input[type=checkbox]').prop('checked', true);
        // Make sure hidden documents are not selected.
        $('.hidden-bib-records .checkbox input[type=checkbox]').prop('checked', false);
      } else {
        // If this checkbox is not checked, hide the `#select-all-across-all-pages` and
        // `#unselect-all` links.
        $('#select-all-across-all-pages, #unselect-all').hide();
        // Unselect all documents, even those that are hidden.
        $('.bib-records, .hidden-bib-records').find('.checkbox input[type=checkbox]').prop('checked', false);
      }
      updateDocumentSelectionCount();
    });

    $('#citations_list .bib-records .checkbox input[type=checkbox]').on('change', function(ev) {
      if ($(this).not(':checked')) {
        // If a citation is unselected, unselect all hidden documents.
        $('.hidden-bib-records').find('.checkbox input[type=checkbox]').prop('checked', false);
        // Show the `#select-all-across-all-pages` link if there are citation not on current page.
        if ($('.hidden-bib-records .checkbox').length) {
          $('#select-all-across-all-pages').show();
        }
        $('#unselect-all').hide();
      }
      updateDocumentSelectionCount();
    });

    $('a[data-remove]').click(function(ev) {
      ev.preventDefault();
      let $document = $(this).parents('li\.bib-record');
      $document.find('.checkbox input[type=checkbox]').prop('checked', false);  // Uncheck checkbox
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
        $('#select-all-on-current-page').prop('checked', false);
        $('#select-all-across-all-pages, #unselect-all').hide();
        $('.bib-records, .hidden-bib-records').find('.checkbox input[type=checkbox]:checked').each(function() {
          $(this).prop('checked', false);
          let $document = $(this).parents('li\.bib-record');
          updateDocumentTypeCount($document);
          $document.remove();
          updateDocumentSelectionCount();
          reloadPageIfAllDocumentsRemoved()
          updateTotalDocumentsCount();
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

    // Initializes the citation modals for thesis
    $('a[data-cite-inline]').each(function(){
      new InlineCiteModal($(this));
    });
    // Initializes the citation modals for articles
    $('a[data-cite-ajax]').each(function(){
      new AjaxCiteModal($(this));
    });
  },
};
