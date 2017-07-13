export default {

  init: function() {
    this.article = $('#journal_detail');
    this.sticky_header_height = 0;

    this.smooth_scroll();
  },

  smooth_scroll : function () {
    this.article.on('click', 'a[href*="#"]', (e) => {
      if( e ) {
        e.preventDefault();
        e.stopPropagation();
      }

      var target = $(e.currentTarget).attr('href').replace('#', '');
      if( !target ) return false;

      $('html, body').animate( { scrollTop: this.article.find('#'+target).offset().top - this.sticky_header_height - 30 }, 750 );
      return false;
    });
  },

};
