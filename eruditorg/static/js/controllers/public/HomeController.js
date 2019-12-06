//import '!!script-loader!sticky-kit/dist/sticky-kit.min';

export default {

  init: function() {
    this.layout();
    //this.sticky_elements();
    //this.smooth_scroll();
  },

  layout : function () {

    var window_height     = $(window).height(),
      sticky_nav_height   = $('#homepage .homepage--sticky-nav').outerHeight(),
      header_height     = window_height / 3 >> 0,
      search_height     = window_height - header_height - sticky_nav_height;

    $('#homepage-header').css('height', header_height);
    $('#homepage .search-module').css('height', search_height);
  }/*,

  sticky_elements : function () {
    $('#homepage .homepage--sticky-nav').stick_in_parent();
  },

  smooth_scroll : function () {
    $('#homepage .homepage--sticky-nav').on('click', 'a', function(e) {
      if( e ) {
        e.preventDefault();
        e.stopPropagation();
      }

      var target = $(this).attr('href').replace('#', '');
      if( !target ) return false;

      $('html, body').animate( { scrollTop: $('#homepage a[name="'+target+'"]').offset().top }, 750 );
      return false;
    });
  }*/
};
