export default {
  init() {
    console.log("Advanced search!");

    let $addButton = $('#id_add_q_field');

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
  },
};
