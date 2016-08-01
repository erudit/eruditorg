const siteHeader   = "header#site-header";
const minTopScroll = 200;

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

    // toggle compact or regular header size
    var headerSize = function() {
      if ( $(window).scrollTop() >= minTopScroll ) {
        $(siteHeader).addClass('compact')
      } else {
        $(siteHeader).removeClass('compact')
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
    var searchBarTrigger = "#main-nav [data-trigger-search-bar]";
    var searchBar        = "#main-nav .search-form";
    var searchInput      = "#main-nav .search-form input.search-terms";

    // show or hide search bar
    var toggleSearch = function() {
      var visible = $(searchBar).hasClass('visible');
      $(searchBar).toggleClass('visible');
      $(siteHeader).toggleClass('inverted');

      // focus to field when visible
      if (!visible) $(searchInput).focus();
    };

    // elements trigger
    $(searchBarTrigger).on('click', function(event) {
      event.preventDefault();
      toggleSearch();
    });
  }
}

export default Nav;
