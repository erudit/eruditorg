export default {

  init: function() {
    this.layout();
  },

  layout : function () {

    var window_height     = $(window).height(),
      sticky_nav_height   = $('#homepage .homepage--sticky-nav').outerHeight(),
      header_height     = window_height / 3 >> 0,
      search_height     = window_height - header_height - sticky_nav_height;

    $('#homepage-header').css('height', header_height);
    $('#homepage .search-module').css('height', search_height);
  }
};
