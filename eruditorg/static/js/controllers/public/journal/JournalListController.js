export default {

  init: function() {
    this.smooth_scroll();
  },

  smooth_scroll : function () {
  	$('#journal_list .disciplines').on('click', 'a', function(e) {
  		if( e ) {
  			e.preventDefault();
  			e.stopPropagation();
  		}

  		var target = $(this).attr('href').replace('#', '');
  		if( !target ) return false;

		$('html, body').animate( { scrollTop: $('#journal_list a[name="'+target+'"]').offset().top }, 750 );
		return false;
  	});
  }
};
