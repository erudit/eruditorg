const siteHeader   = "header#site-header";
const minTopScroll = 100;

class Nav {

  constructor() {
    this.init();
  }

  init() {
    this.subNavs();
    this.stickyHeader();
    this.searchBar();
  }

  /*
   * Sub-navs
   */
  subNavs() {
    $("[data-sub-nav]").on('click', function(event) {
      event.preventDefault();

      var $this   = $(this),
          $target = $( $this.data('sub-nav') );

      if ( $target.eq(0) ) {
        $this.toggleClass('selected');
        $target.toggleClass('visible');
      }
    });
  }

  /*
   * Search bar toggle in nav
   */
  stickyHeader() {

    // different states for the header when user scrolls the page
    var headerSize = function() {
      if ( $(window).scrollTop() >= minTopScroll ) {
        $(siteHeader).addClass('site-header__scrolled')
      } else {
        $(siteHeader).removeClass('site-header__scrolled')
      }
    };

    // register event on window scroll
    $(window).on('scroll', function(event) {
      headerSize();
    });
  }

  /*
   * Search bar toggle in nav
   */
  searchBar() {
    var searchBarTrigger = "[data-trigger-search-bar]";
    var searchBar        = "#search-form";
    var searchInput      = "#search-form input.search-terms";

    // show or hide search bar
    var toggleSearch = function() {
      var visible = $(searchBar).hasClass('visible');
      $(searchBar).toggleClass('visible');
      $(siteHeader).toggleClass('inverted-search-bar');

      // focus to field when visible
      if (!visible) $(searchInput).focus();
    };

    // elements trigger
    $(searchBarTrigger).on('click', function(e) {
      e.preventDefault();
      toggleSearch();
    });

    // close search bar on esc key press
    $(document).keyup(function(e) {
     if (e.keyCode === 27) $('.nav-search-triggers__close').click()
    });

  }
}

export default Nav;
