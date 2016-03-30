const siteHeader   = "header#site-header";
const minTopScroll = 300;

class Nav {

  constructor() {
    // auto init
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
      var top = $(window).scrollTop();
      if (top >= minTopScroll) {
        $(siteHeader).addClass('compact');
      } else {
        $(siteHeader).removeClass('compact');
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

      if (!visible) {
        $(searchInput).focus();
      }

    }

    $(searchInput).on('blur', function(event) {
      toggleSearch();
    });

    // show/hide bar
    $(searchBarTrigger).on('click', function(event) {
      event.preventDefault();
      toggleSearch();
    });
  }
}

export default Nav;
