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
    let _ = this;
    let documentId = $document.data(this.options.documentIdDataAttribute);
    $.ajax({
      type: 'POST',
      url: Urls['public:citations:add_citation'](documentId),
    }).done(function() {
      $document.data(_.options.documentIsSavedDataAttribute, true);
      $document.find(_.addButtonSelector).hide();
      $document.find(_.removeButtonSelector).show();
    });
  }

  /*
   * Removes the considered document from the user's citation list.
   * @param {JQuery selector} $document - The selector of the document object.
   */
  remove($document) {
    let _ = this;
    let documentId = $document.data(this.options.documentIdDataAttribute);
    $.ajax({
      type: 'POST',
      url: Urls['public:citations:remove_citation'](documentId),
    }).done(function() {
      $document.data(_.options.documentIsSavedDataAttribute, false);
      $document.find(_.removeButtonSelector).hide();
      $document.find(_.addButtonSelector).show();
    });
  }

  /*
   * Initializes the citation list object.
   */
  init() {
    let _ = this;

    // Associates the proper actions to execute when clicking on "save" buttons
    $(this.addButtonSelector).on('click', function(ev) {
      var $document = $($(this).data(_.options.documentAddDataAttribute));
      _.save($document);
      ev.preventDefault();
    });

    // Associates the proper actions to execute when clicking on "remove" buttons
    $(this.removeButtonSelector).on('click', function(ev) {
      var $document = $($(this).data(_.options.documentRemoveDataAttribute));
      _.remove($document);
      ev.preventDefault();
    });

    // Display or hide buttons allowing to save or remove citations.
    $('[data-' + _.options.documentIsSavedDataAttribute + '=false] ' + this.addButtonSelector).show();
    $('[data-' + _.options.documentIsSavedDataAttribute + '=false] ' + this.removeButtonSelector).hide();
    $('[data-' + _.options.documentIsSavedDataAttribute + '=true] ' + this.addButtonSelector).hide();
    $('[data-' + _.options.documentIsSavedDataAttribute + '=true] ' + this.removeButtonSelector).show();
  }
}

export default SavedCitationList;
