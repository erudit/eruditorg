export const formSelector = "form#id-search";

export default {

  init() {
    console.log("Search!");
    this.sorting();
  },

  /**
  * Handle search results sorting and ordering
  */
  sorting() {
    var sortSelect  = $("select#id_sort"),
        sortNav     = $("#search-nav-sort-by"),
        orderSelect = $("select#id_sort_order"),
        orderNav     = $("#search-nav-order-by");

    // create both nav based on select data
    this.sortingDropdown(sortSelect, sortNav);
    this.sortingDropdown(orderSelect, orderNav);

    // submit form when one SELECT has changed
    $(sortSelect).add(orderSelect).on('change', function() {
      $(formSelector).trigger('submit');
    });
  },

  /**
  * Bind nav drowpdown with form's SELECT
  */
  sortingDropdown(select, nav) {
    var options         = select.find('option'),
        dropdownSelect  = nav.find("a.select"),
        selectedText    = options.filter(":selected").text(),
        dropdown        = nav.find("> ul");

    // set dropdown's select element value based on selected OPTION
    dropdownSelect.text( selectedText );

    // create a dropdown element from each OPTION
    for (var i = 0; i < options.length; i++) {
      var li  = $("<li/>").appendTo( dropdown ),
          a   = $("<a/>").text( options[i].text ).appendTo( li ),
          val = options[i].value;

      // set as selected
      if (selectedText == options[i].text) {
        li.addClass('selected');
      }

      // register event on dropdown item
      this.changeSelectValue(li, val, select, dropdownSelect);
    }
  },

  changeSelectValue(el, val, select, dropdownSelect) {
    // console.log(el, val, select);
    $(el).on('click', function(event) {
      event.preventDefault();
      select.val( val ).trigger('change');
      dropdownSelect.text( el.text() );
    });
  }

};
