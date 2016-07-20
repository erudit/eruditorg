export default {

  init: function() {
    this.smoothScroll();
    this.stickyElements();
  },

  smoothScroll: function() {
    $('#journal_list_per_names .index').on('click', 'a', function(e) {
  		e.preventDefault();
  		e.stopPropagation();
      var target = $(this).attr('href').replace('#', '');
  		$('html, body').animate( { scrollTop: $('a[name="'+target+'"]').offset().top -190 }, 750);
  		return false;
  	});
  	$('#journal_list_per_disciplines .index').on('click', 'a', function(e) {
  		e.preventDefault();
  		e.stopPropagation();
      var target = $(this).attr('href').replace('#', '');
  		$('html, body').animate( { scrollTop: $('a[name="'+target+'"]').offset().top }, 750 );
  		return false;
  	});
  },

  stickyElements: function() {
    function stickyFilterForm(offset) {
      var form = $('form#filter_form');
      if ($(window).scrollTop() >= offset) {
        form.addClass('sticky');
      } else {
        form.removeClass('sticky');
      }
    }

    function stickyItemsMenu(offset) {
      var menu = $('#items_menu');
      if ($(window).scrollTop() >= offset) {
        menu.addClass('sticky');
      } else {
        menu.removeClass('sticky');
      }
    }

    $(window).scroll(function () {
      var origOffsetY = $('#journal_list_per_names').offset().top + 100;
      stickyFilterForm(origOffsetY);
      stickyItemsMenu(origOffsetY);
    });
  },
};
