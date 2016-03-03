ROUTER.registerController('public:home', {

  init: function() {
  	this.layout();
    this.sticky_elements();
    this.smooth_scroll();
  },

  layout : function () {

  	var window_height 		= $(window).height(),
  		sticky_nav_height 	= $('#homepage-content .homepage--sticky-nav').outerHeight(),
  		header_height 		= window_height / 3 >> 0,
  		search_height 		= window_height - header_height - sticky_nav_height;

  	$('#homepage-header').css('height', header_height);
  	$('#homepage-content .search-module').css('height', search_height);
  },

  sticky_elements : function () {
  	$('#homepage-content .homepage--sticky-nav').stick_in_parent();
  },

  smooth_scroll : function () {
  	$('#homepage-content .homepage--sticky-nav').on('click', 'a', function(e) {
  		if( e ) {
  			e.preventDefault();
  			e.stopPropagation();
  		}

  		var target = $(this).attr('href').replace('#', '');
  		if( !target ) return false;

		  $('html, body').animate( { scrollTop: $('#homepage-content a[name="'+target+'"]').offset().top }, 750 );
		  return false;
  	});
  }


});
