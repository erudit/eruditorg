import '!!script-loader!select2/dist/js/select2.full.min';


export default {

  init: function() {
    this.smoothScroll();
    this.stickyElements();
    $('#id_disciplines').select2();

    // Make filters sidebar scrollable for short screens
    this.scrollableFilters();
    $('#id_disciplines').on('change', this.scrollableFilters);
    $(window).on('resize', this.scrollableFilters);
  },

  smoothScroll: function() {
    $('#journal_list_per_names .alpha-nav').on('click', 'a', function(e) {
      e.preventDefault();
      e.stopPropagation();
      var target = $(this).attr('href').replace('#', '');
      $('html, body').animate( { scrollTop: $('ul[id="'+target+'"]').offset().top - 137 }, 750);
      return false;
    });
  },

  stickyElements: function() {
    function stickyFilterForm(offset) {
      let form = $('.filters');

      if ($(window).scrollTop() >= offset) {
        form.addClass('sticky');
      } else {
        form.removeClass('sticky');
      }
    }

    function stickyItemsMenu(offset) {
      let menu = $('.list-header');

      if ($(window).scrollTop() >= offset) {
        menu.addClass('sticky');
      } else {
        menu.removeClass('sticky');
      }
    }

    var listPerNames = $('#journal_list_per_names');

    if (listPerNames.length) {

      $(window).scroll(function () {
        var origOffsetY = $('#journal_list_per_names').offset().top + 390;
        stickyFilterForm(origOffsetY);
        stickyItemsMenu(origOffsetY);
      });

    }

  },

  scrollableFilters: function() {
    // If the filters aside height is greater than the window size minus the
    // top navigation bar (60px) and a small padding (10px), it means the
    // filter is not fully visible.
    // So, we make the filters form sidebar scrollable
    var asideFilters = $('aside.filters')
    if ($(window).height() - 70 < asideFilters.height()) {
      asideFilters.addClass('scrollable');
    } else {
      asideFilters.removeClass('scrollable');
    }

  },

};
