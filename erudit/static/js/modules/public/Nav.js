const siteHeader   = "header#site-header";
const minTopScroll = 300;

class Nav {

  constructor() {
    this.init();
  }

  init() {
    this.stickyHeader();
    this.searchBar();
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
    var searchBarTrigger = "nav#main-nav [data-trigger-search-bar]";
    var searchBar        = "nav#main-nav .search-form";
    var searchInput      = "nav#main-nav .search-form input.search-terms";

    // show or hide search bar
    var toggleSearch = function() {
      var visible = $(searchBar).hasClass('visible');
      $(searchBar).toggleClass('visible');
      $(siteHeader).toggleClass('inverted');

      // focus to field when visible
      if (!visible) $(searchInput).focus();
    }

    // hide search bar when focus out
    $(searchInput).on('blur', function(event) {
      toggleSearch();
    });

    // elements trigger
    $(searchBarTrigger).on('click', function(event) {
      event.preventDefault();
      toggleSearch();
    });
  }
}

export default Nav;
