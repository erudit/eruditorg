import csrfSafeMethod from "../core/csrfSafeMethod";
import getCsrfToken from "../core/getCsrfToken";


class Commons {

  constructor() {
    this.init();
  }

  init() {
    this.scrollToTop();
    this.csrfToken();
    this.siteMessages();
  }

  /*
  * Scroll back to top of page from element
  */
  scrollToTop() {
    $(".scroll-top").on("click", function(e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      $("html,body").animate({scrollTop: 0}, 450);
      return false;
    });
  };

  /*
  * Initializes the jQuery csrf setup
  */
  csrfToken() {
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
        }
      },
      // Normally, the "X-CSRFToken" should be enough for our purpose, but
      // some proxies strip this header so it"s safer to also include it in
      // the POST values.
      data: {csrfmiddlewaretoken: getCsrfToken()}
    });
  };

  /*
  * Hide site messages if the user has closed them.
  */
  siteMessages() {
    $(".site-messages .alert").each(function() {
      var id = $(this).attr("id");
      if (document.cookie.split(";").some(function(item) {
        return item.trim().indexOf(id) == 0;
      })) {
        $(this).hide();
      } else {
        $(this).show();
      }
      $(this).find("button").on("click", function() {
        document.cookie = id + "=closed; max-age=86400; path=/";
      });
    });
  };
}

export default Commons;
