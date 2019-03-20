
export default {

  init: function() {
    var fragment_to_activate = this.find_url_fragment();
    this.set_active_fragment(fragment_to_activate[0], fragment_to_activate[1]);
  },

  find_url_fragment : function () {
    var element_li = null;
    var element_section = null;
    if (window.location.hash) {
      var anchor_id = window.location.hash.substring(1);
      var li_id = anchor_id + "-li";
      element_li = $("#" + li_id);
      element_section = $("#" + anchor_id);
    }
    return [element_li, element_section]
  },

  set_active_fragment : function (element_li, element_section) {
    /*
     * modify the attributes of the elements corresponding to the anchor if it
     * exists otherwise modify the attributes of the first elements
     */

    if (!element_li) {
      element_li = $('[role="presentation"]').first();
    }

    if (!element_section) {
      element_section  = $('[role="tabpanel"]').first();
    }
    $(element_li).addClass("active");
    $(element_section).addClass("active");
  }
};
