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
      let form = $('form#filter_form');
      let footer = $('footer#site-footer');
      let footerOffsetY = footer.offset().top - footer.height() - 80;
      let filterFormTopOffset = form.offset().top;

      if (filterFormTopOffset > footerOffsetY) {
        form.hide();
      } else if (filterFormTopOffset < footerOffsetY - 100) {
        form.show();
      }

      if ($(window).scrollTop() >= offset) {
        form.addClass('sticky');
      } else {
        form.removeClass('sticky');
      }
    }

    function stickyItemsMenu(offset) {
      let menu = $('#items_menu');
      let footer = $('footer#site-footer');
      let footerOffsetY = footer.offset().top - footer.height();
      let filterFormTopOffset = menu.offset().top;

      if (filterFormTopOffset > footerOffsetY) {
        menu.hide();
      } else if (filterFormTopOffset < footerOffsetY - 100) {
        menu.show();
      }

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
