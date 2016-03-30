

class Nav {

  constructor() {
    // auto init
    this.init();
  }

  init() {
    this.searchBar();
  }

  /*
   * Register login modal
   */
  searchBar() {
    var siteHeader       = "header#site-header";
    var searchBarTrigger = "nav#main-nav [data-trigger-search-bar]";
    var searchBar        = "nav#main-nav .search-form";
    var searchInput        = "nav#main-nav .search-form input.search-terms";
    console.log("search bar init");

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
