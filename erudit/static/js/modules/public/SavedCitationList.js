class SavedCitationList {
  constructor(options={}) {
    // Defines options ; any of these options can be overridden using the 'options' argument.
    let defaults = {
      articleAddDataAttribute: 'citation-save',
      articleRemoveDataAttribute: 'citation-remove',
      articleButtonSelector: '[data-citation-list-button]',
      articleIdDataAttribute: 'article-id',
      articleIsSavedDataAttribute: 'is-in-citation-list',
    };
    this.options = Object.assign(defaults, options);

    // Initializes some usefull attributes
    this.addButtonSelector = '[data-' + this.options.articleAddDataAttribute + ']';
    this.removeButtonSelector = '[data-' + this.options.articleRemoveDataAttribute + ']';
  }

  /*
   * Saves the considered article to the user's citation list.
   * @param {JQuery selector} $article - The selector of the article object.
   */
  save($article) {
    let _ = this;
    let articleId = $article.data(this.options.articleIdDataAttribute);
    $.ajax({
      type: 'POST',
      url: Urls['public:citations:add-citation'](articleId),
    }).done(function() {
      $article.data(_.options.articleIsSavedDataAttribute, true);
      $article.find(_.addButtonSelector).hide();
      $article.find(_.removeButtonSelector).show();
    });
  }

  /*
   * Removes the considered article from the user's citation list.
   * @param {JQuery selector} $article - The selector of the article object.
   */
  remove($article) {
    let _ = this;
    let articleId = $article.data(this.options.articleIdDataAttribute);
    $.ajax({
      type: 'POST',
      url: Urls['public:citations:remove-citation'](articleId),
    }).done(function() {
      $article.data(_.options.articleIsSavedDataAttribute, false);
      $article.find(_.removeButtonSelector).hide();
      $article.find(_.addButtonSelector).show();
    });
  }

  /*
   * Initializes the citation list object.
   */
  init() {
    let _ = this;

    // Associates the proper actions to execute when clicking on "save" buttons
    $(this.addButtonSelector).on('click', function(ev) {
      var $article = $($(this).data(_.options.articleAddDataAttribute));
      _.save($article);
      ev.preventDefault();
    });

    // Associates the proper actions to execute when clicking on "remove" buttons
    $(this.removeButtonSelector).on('click', function(ev) {
      var $article = $($(this).data(_.options.articleRemoveDataAttribute));
      _.remove($article);
      ev.preventDefault();
    });

    // Display or hide buttons allowing to save or remove citations.
    $('[data-' + _.options.articleIsSavedDataAttribute + '=false] ' + this.addButtonSelector).show();
    $('[data-' + _.options.articleIsSavedDataAttribute + '=false] ' + this.removeButtonSelector).hide();
    $('[data-' + _.options.articleIsSavedDataAttribute + '=true] ' + this.addButtonSelector).hide();
    $('[data-' + _.options.articleIsSavedDataAttribute + '=true] ' + this.removeButtonSelector).show();
  }
}

export default SavedCitationList;
