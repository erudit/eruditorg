import '!!script-loader!select2/dist/js/select2.full.min';


export default {
  init() {

    let $form = $('#id_search');
    let $addButton = $('#id_add_q_field');

    // Initializes the Select2 choosers
    $('#id_disciplines').select2();
    $('#id_languages').select2();
    $('#id_journals').select2();

    // Initializes the search blocks
    $('#id_advanced_q_wrapper [data-q-id]').each(function() {
      let used = $(this).find('#id_advanced_search_term' + $(this).data('q-id')).val();
      if (used) {
        $(this).show();
        $(this).data('q-used', true);
      }
    });

    $addButton.click(function(ev) {
      ev.preventDefault();

      let $qBlocks = $('#id_advanced_q_wrapper [data-q-id]');

      // Display another box containing search fields
      $qBlocks.each(function() {
        if (!$(this).data('q-used')) {
          $(this).fadeIn();
          $(this).data('q-used', true);
          return false;
        }
      });

      // Hide the button to add new fields if necessary
      let $qUsed = $qBlocks.filter(function() { return $(this).data('q-used') == true });
      if ($qUsed.length == 5) {
        $addButton.hide();
      }
    });

    $('.remove-qbox').click(function(ev) {
      ev.preventDefault();

      // Hide the corresponding search block
      let $qBlock = $(this).parents('[data-q-id]');
      $qBlock.data('q-used', false);
      $qBlock.find('#id_advanced_search_term' + $qBlock.data('q-id')).val('');
      $qBlock.find('#id_advanced_search_operator' + $qBlock.data('q-id')).prop('selectedIndex', 0);
      $qBlock.find('#id_advanced_search_field' + $qBlock.data('q-id')).prop('selectedIndex', 0);
      $qBlock.hide();

      // Shows the button to add new fields if necessary
      let $qUsed = $('#id_advanced_q_wrapper [data-q-id]').filter(function() { return $(this).data('q-used') == true });
      if ($qUsed.length < 5) {
        $addButton.show();
      }
    });

    $form.submit(function(ev) {
      $('.advanced-search-popup-error').hide();

      let mainQueryTerm = $('#id_basic_search_term').val();
      if (!mainQueryTerm) {
        $('#div_id_basic_search_term .advanced-search-popup-error').show();
        ev.preventDefault();
      }
    });

    // Handles the deletion of a search
    $('.remove-search').click(function(ev) {
      let $searchBlock = $(this).parents('.saved-search');
      $.ajax({
        type: 'POST',
        url: Urls['public:search:remove_search']($searchBlock.data('uuid')),
      }).done(function() {
        $searchBlock.remove();
      });
      ev.preventDefault();
    });
  },
};
