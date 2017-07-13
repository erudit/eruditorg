class SavedCitationList {
  constructor(options={}) {
    // Defines options ; any of these options can be overridden using the 'options' argument.
    let defaults = {
      documentAddDataAttribute: 'citation-save',
      documentRemoveDataAttribute: 'citation-remove',
      documentButtonSelector: '[data-citation-list-button]',
      documentIdDataAttribute: 'document-id',
      documentIsSavedDataAttribute: 'is-in-citation-list',
    };
    this.options = Object.assign(defaults, options);

    // Initializes some usefull attributes
    this.addButtonSelector = '[data-' + this.options.documentAddDataAttribute + ']';
    this.removeButtonSelector = '[data-' + this.options.documentRemoveDataAttribute + ']';
  }

  /*
   * Saves the considered document to the user's citation list.
   * @param {JQuery selector} $document - The selector of the document object.
   */
  save($document) {
    let documentId = $document.data(this.options.documentIdDataAttribute);
    let documentAttrId = $document.attr('id');
    $.ajax({
      type: 'POST',
      url: Urls['public:citations:add_citation'](documentId),
    }).done(() => {
      $document.data(this.options.documentIsSavedDataAttribute, true);
      $('[data-' + this.options.documentAddDataAttribute + '="#' + documentAttrId + '"]').hide();
      $('[data-' + this.options.documentRemoveDataAttribute + '="#' + documentAttrId + '"]').show();
    });
  }

  /*
   * Removes the considered document from the user's citation list.
   * @param {JQuery selector} $document - The selector of the document object.
   */
  remove($document) {
    let documentId = $document.data(this.options.documentIdDataAttribute);
    let documentAttrId = $document.attr('id');
    $.ajax({
      type: 'POST',
      url: Urls['public:citations:remove_citation'](documentId),
    }).done(() => {
      $document.data(this.options.documentIsSavedDataAttribute, false);
      $('[data-' + this.options.documentAddDataAttribute + '="#' + documentAttrId + '"]').show();
      $('[data-' + this.options.documentRemoveDataAttribute + '="#' + documentAttrId + '"]').hide();
    });
  }

  /*
   * Initializes the citation list object.
   */
  init() {
    // Associates the proper actions to execute when clicking on "save" buttons
    $(this.addButtonSelector).on('click', (ev) => {
      var $document = $($(ev.currentTarget).data(this.options.documentAddDataAttribute));
      this.save($document);
      ev.preventDefault();
    });

    // Associates the proper actions to execute when clicking on "remove" buttons
    $(this.removeButtonSelector).on('click', (ev) => {
      var $document = $($(ev.currentTarget).data(this.options.documentRemoveDataAttribute));
      this.remove($document);
      ev.preventDefault();
    });

    // Display or hide buttons allowing to save or remove citations.
    $('[data-' + this.options.documentIdDataAttribute + ']').each((index, element) => {
      let documentAttrId = $(element).attr('id');
      let documentIsSaved = $(element).data(this.options.documentIsSavedDataAttribute);
      if (documentIsSaved == true) {
        $('[data-' + this.options.documentAddDataAttribute + '="#' + documentAttrId + '"]').hide();
        $('[data-' + this.options.documentRemoveDataAttribute + '="#' + documentAttrId + '"]').show();
      } else {
        $('[data-' + this.options.documentAddDataAttribute + '="#' + documentAttrId + '"]').show();
        $('[data-' + this.options.documentRemoveDataAttribute + '="#' + documentAttrId + '"]').hide();
      }
    });
  }
}

export default SavedCitationList;
