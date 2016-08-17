import SavedCitationList from '../../../modules/public/SavedCitationList';
import Toolbox from '../../../modules/public/Toolbox';


export default {
  init() {
    let $searchResultsMetadata = $('#id_search_results_metadata');

    this.toolbox();

    // Initializes the citation list
    this.saved_citations = new SavedCitationList();
    this.saved_citations.init();

    // Handles the save of the search parameters
    $('#id_save_search').click(function(ev) {
      let $form = $('form#id-search');
      $.ajax({
        type: 'POST',
        url: Urls['public:search:add_search'](),
        data: {querystring: $form.serialize(), results_count : $searchResultsMetadata.data('results-count')},
      }).done(function() {
        $('#id_save_search').addClass('disabled');
        $('#id_save_search').text(gettext("Recherche sauvegardée"));
      });
      ev.preventDefault();
    });

    $('#id_page_size,#id_sort_by').change(function(ev) {
      let $form = $('form#id-search');
      window.location.href = '?' + $form.serialize();
    });
  },

  toolbox() {
    $('#search-results .search-result-item .toolbox').each(function(){
      new Toolbox($(this));
    });
  }
};
