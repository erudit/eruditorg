
export default {

  init: function() {
    var url_hash = window.location.hash
    if (url_hash) {
      // If hash specified in url, go to specified tab
      $(url_hash + "-li").addClass("active");
      $(url_hash + "-section").addClass("active");
    } else {
      // Go to first tab
      $('[role="presentation"]').first().addClass("active");
      $('[role="tabpanel"]').first().addClass("active");
    }
    // Add click event listener to each tab to manage hash in url
    $( "a[role='tab']" ).on("click", function() {
        var href_str = $(this).attr("href")
        window.location.hash = href_str.substring(0, href_str.length - 8);
    });
  }
};
