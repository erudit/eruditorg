export default {

  init: function() {
    this.smooth_scroll();
  },

  smooth_scroll : function () {
    $('#journal_list_per_names .index').on('click', 'a', function(e) {
  		e.preventDefault();
  		e.stopPropagation();
      var target = $(this).attr('href').replace('#', '');
  		$('html, body').animate( { scrollTop: $('a[name="'+target+'"]').offset().top -100 }, 750 );
  		return false;
  	});
  	$('#journal_list_per_disciplines .index').on('click', 'a', function(e) {
  		e.preventDefault();
  		e.stopPropagation();
      var target = $(this).attr('href').replace('#', '');
  		$('html, body').animate( { scrollTop: $('a[name="'+target+'"]').offset().top }, 750 );
  		return false;
  	});
  }
};
