ROUTER.registerController('public:journal:journal-list', {

  init: function() {
    this.smooth_scroll();
  },

  smooth_scroll : function () {
  	$('#journal-list .disciplines').on('click', 'a', function(e) {
  		if( e ) {
  			e.preventDefault();
  			e.stopPropagation();
  		};

  		var target = $(this).attr('href').replace('#', '');
  		if( !target ) return false;

		$('html, body').animate( { scrollTop: $('#journal-list a[name="'+target+'"]').offset().top }, 750 );
		return false;
  	});
  }


});
