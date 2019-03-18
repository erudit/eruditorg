
export default {

  init: function() {
    this.check_fragment();
  },

  check_fragment : function () {
    if(window.location.hash) {
      var anchor_id = window.location.hash.substring(1);
        var li_id = anchor_id + "-li";
        var element_li = document.getElementById(li_id);
        var element_section = document.getElementById(anchor_id);
        update_attributes(element_li, element_section);
    }else {
      update_attributes(null, null);
    }
  },

  update_attributes : function (element_li, element_section) {
    /*
     * modify the attributes of the elements corresponding to the anchor if it
     * exists otherwise modify the attributes of the first elements
     */
    if (element_li && element_section) {
      element_li.setAttribute("class", "active");
      var attribute_value = element_section.getAttribute("class");
      attribute_value = attribute_value + " active";
      element_section.setAttribute("class", attribute_value);
    }else {
      var element = document.querySelector('[role="presentation"]');
      if (element != null) {
        element.setAttribute("class", "active");
        element  = document.querySelector('[role="tabpanel"]');
        if (element != null) {
          var attribute_value = element.getAttribute("class");
          attribute_value = attribute_value + " active";
          element.setAttribute("class", attribute_value);
        }
      }
    }
  }
};
