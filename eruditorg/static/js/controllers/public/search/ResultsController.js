import SavedCitationList from '../../../modules/SavedCitationList';
import Toolbox from '../../../modules/Toolbox';


export default {
  init() {
    let $searchResultsMetadata = $('#id_search_results_metadata');

    this.toolbox();

    // Initializes the citation list
    this.saved_citations = new SavedCitationList();
    this.saved_citations.init();

    // Handles the save of the search parameters
    $('#id_save_search').on('click', function(ev) {
      let $form = $('form#id-search');
      $.ajax({
        type: 'POST',
        url: Urls['public:search:add_search'](),
        data: {querystring: $form.serialize(), results_count : $searchResultsMetadata.data('results-count')},
      }).done(function() {
        $('#id_save_search').addClass('disabled');
        $('#id_save_search').text(gettext("Résultats sauvegardés !"));
      });
      ev.preventDefault();
    });

    $('#id_page_size,#id_sort_by').on('change', function() {
      let $form = $('form#id-search');
      window.location.href = '?' + $form.serialize();
    });

    // For each akkordion submenu we show and hide the `Remove filters` button inside
    // the submenu and also uncheck all checked checkboxes if the user clicks the button
    $('.akkordion.filter').each(function() {

      // The current akkordion submenu
      var submenu = $(this);

      // Add listeners to every checkbox in the akkordion submenu to listen to changes
      submenu.find(':checkbox').on('change', function() {
        if ($(this).prop('checked')) {
          // Show `Remove filters` button if any checkbox checked
          submenu.find('.remove-filters').removeClass('invisible');
        } else {
          // If no checkboxes checked, hide `Remove filters` button
          if (submenu.find(':checked').length == 0) {
            submenu.find('.remove-filters').addClass('invisible');
          }
        }
      });

      // Add listener to the `Remove filters` button to uncheck all checked checkboxes in the
      // current akkordion submenu. After unchecking checkboxes, hide `Remove filters` button
      submenu.find('button').on('click', function() {
        submenu.find(':checkbox').prop('checked', false);
        submenu.find('.remove-filters').addClass('invisible');
      });

      // At page load, show `Remove filters` button in an akkordion submenu
      // if any checkbox checked
      $(document).ready(function() {
        if (submenu.find(':checked').length != 0) {
          submenu.find('.remove-filters').removeClass('invisible');
        }
      });
    });
  },

  toolbox() {
    $('#search-results .result .toolbox').each(function(){
      new Toolbox($(this));
    });
  }
};
