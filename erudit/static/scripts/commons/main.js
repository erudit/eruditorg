ROUTER.registerController('commons:main', {

  init: function() {
    // main init
    this.scrollToTop();
    this.svg();
    this.xhr();

    // init UI components
    ROUTER.execAction('commons:modals');
  },

  scrollToTop : function() {
    // scroll window to top
    $('#scroll-top').on('click', function(e) {

      if( e ) {
        e.preventDefault();
        e.stopPropagation();
      };

      $('html, body').animate( { scrollTop: 0 }, 750 );
      return false;
    });
  },

  // transform any .svg element inlined
  svg : function() {
    inlineSVG.init({
      svgSelector: 'img.inline-svg', // the class attached to all images that should be inlined
      initClass: 'js-inlinesvg', // class added to <html>
    });
  },

  // after any XHR call
  xhr : function() {
    $(document).ajaxComplete(function() {
      // init ROUTER controllers
      ROUTER.findControllers();
    });
  }

});
