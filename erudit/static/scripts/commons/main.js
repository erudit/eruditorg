ROUTER.registerController('commons:main', {

  init: function() {
  	console.log('init communs main');

    // main init
    this.svg();
    this.xhr();

    // init UI components
    ROUTER.execAction('commons:modals');
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
