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
     * Remove a specific document from the saved citations list.
     * The function also updates the texts displaying the number of documents associated with the
     * document type of the document being removed.
     * @param {JQuery selector} $document - The selector of the document object.
     */
    function removeDocument($document) {
      let documentId = $document.data('document-id');
      let documentType = $document.data('document-type');
      $.ajax({
        type: 'POST',
        url: Urls['public:citations:remove_citation'](documentId),
      }).done(function() {
        $document.remove();
        updateDocumentSelectionCount();
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
      });
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

      // TODO
    });

    // Initializes the citation modals
    new CiteModal($('a[data-cite]'));
  },
};
