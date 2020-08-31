export default {

  init: function() {
    this.smoothScroll();
  },

  smoothScroll: function() {
    $('#journal_list_per_disciplines .discipline-nav').on('click', 'a', function(e) {
      e.preventDefault();
      e.stopPropagation();
      var target = $(this).attr('href').replace('#', '');
      $('html, body').animate( { scrollTop: $('a[id="'+target+'"]').offset().top - 100 }, 750);
      return false;
    });
  },

};
