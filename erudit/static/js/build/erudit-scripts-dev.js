var CONTROLLERS, ROUTER;


/*
 * The CONTROLLERS objets will hold all the controllers
 * registered for the application.
 *
 * A controller is a Javascript object that must be of the following form:
 *
 *   awesomeController = {
 *     init: function() {
 *       // Do something
 *     },
 *     other_action: function() {
 *       // Do something else
 *     },
 *   }
 *
 * A controller must define an "init" attribute pointing to a function containing
 * initialization code. It can also define other actions that can contain other JS code.
 *
 * The "init" action is mandatory and will always be executed whenever the controller
 * is used.
 */
CONTROLLERS = {
  /*
   * The "common" controller.
   * This one will be executed on any page.
   */
  common: {
    init: function() {
      // scroll window to top
      $('#scroll-top').on('click', function(e) {

        if( e ) {
          e.preventDefault();
          e.stopPropagation();
        };

        $('html, body').animate( { scrollTop: 0 }, 750 );
        return false;
      });
    },
  },
};


/*
 * The ROUTER object is responsible for executing controllers.
 * When the script is loaded, the ROUTER object will execute the code
 * of the "common" controller object and will try to determine if there
 * is a controller associated with the current page.
 *
 * The controller to be executed is determined using a "data-controller" data-attribute
 * that must be defined inside the page's <body> tag. The value of the "data-controller"
 * data-attribute defines the codename of the controller that must be executed.
 * If a controller with a given name exists, the ROUTER object will execute its "init"
 * action. Note that the "init" action is ALWAYS executed if a controller is found.
 * If a "data-action" data-attribute is found inside the page's <body> tag, the ROUTER
 * will try to execute the corresponding action on the controller associated with the
 * current page.
 */
ROUTER = {
  /*
   * Executes the given action associated with the considered controller.
   * @param {string} controller - The codename of the controller.
   * @param {string} action - The name of the action to execute (can be null).
   */
  execAction: function(controller, action){
    action = (action === undefined) ? 'init' : action;

    if (controller !== '' && CONTROLLERS[controller] && typeof CONTROLLERS[controller][action] == 'function') {
      CONTROLLERS[controller][action]();
    }
  },

  /*
   * Registers the given controller in order to make it available to the router.
   * @param {string} name - The codename of the controller.
   * @param {string} controller - The controller object.
   */
  registerController: function(name, controller){
    CONTROLLERS[name] = controller;
  },

  /*
   * Initializes the router object.
   */
  init: function(){
    if (document.body) {
      var body = document.body,
      controller = body.getAttribute('data-controller'),
      action = body.getAttribute('data-action');

      ROUTER.execAction('common');  // common init action
      if (controller) {
        ROUTER.execAction(controller);  // init action
        ROUTER.execAction(controller, action);
      }
    }
  },
};


$(document).ready(ROUTER.init);

ROUTER.registerController('public:home', {

  init: function() {
  	this.layout();
    this.sticky_elements();
    this.smooth_scroll();
  },

  layout : function () {

  	var window_height 		= $(window).height(),
  		sticky_nav_height 	= $('#homepage-content .homepage--sticky-nav').outerHeight(),
  		header_height 		= window_height / 3 >> 0,
  		search_height 		= window_height - header_height - sticky_nav_height;

  	$('#homepage-header').css('height', header_height);
  	$('#homepage-content .search-module').css('height', search_height);
  },

  sticky_elements : function () {
  	$('#homepage-content .homepage--sticky-nav').stick_in_parent();
  },

  smooth_scroll : function () {
  	$('#homepage-content .homepage--sticky-nav').on('click', 'a', function(e) {
  		if( e ) {
  			e.preventDefault();
  			e.stopPropagation();
  		}

  		var target = $(this).attr('href').replace('#', '');
  		if( !target ) return false;

		  $('html, body').animate( { scrollTop: $('#homepage-content a[name="'+target+'"]').offset().top }, 750 );
		  return false;
  	});
  }


});

ROUTER.registerController('public:journal:article-detail', {

  init: function() {
    console.log("Article detail init");
    this.sticky_elements();
  },

  sticky_elements : function () {

    	var $article 				= $('#article-detail'),
    		$sticky_header 			= $article.find('.article-header-sticky'),
    		$sticky_elements 		= $article.find('.article-table-of-contents, .article-tools'),
    		sticky_header_height 	= $sticky_header.outerHeight() - 20,
    		transform 				= getPrefix('transform');

    	// sticky elements
  	$sticky_elements
  		.stick_in_parent()
  		.first()
  		.on("sticky_kit:stick", function(e) {
  			setTimeout(function(){
  				$sticky_elements.css(transform, 'translate(0, '+sticky_header_height+'px)');
  				$sticky_header.css(transform, 'translate(-50%, 0%)');
  			}, 0);
  		})
  		.on("sticky_kit:unstick", function(e) {
  			setTimeout(function(){
  				$sticky_elements.css(transform, 'translate(0, 0)');
  				$sticky_header.css(transform, 'translate(-50%, -100%)');
  			}, 0);
  		});


  }


});

ROUTER.registerController('public:journal:journal-list', {

  init: function() {
    this.smooth_scroll();
  },

  smooth_scroll : function () {
  	$('#journal-list .disciplines').on('click', 'a', function(e) {
  		if( e ) {
  			e.preventDefault();
  			e.stopPropagation();
  		};

  		var target = $(this).attr('href').replace('#', '');
  		if( !target ) return false;

		$('html, body').animate( { scrollTop: $('#journal-list a[name="'+target+'"]').offset().top }, 750 );
		return false;
  	});
  }


});

ROUTER.registerController('userspace:editor:form', {
  init: function() {
    var journals = $('#id_editor_form_metadata').data('journals');
    function resetContactField() {
      $("#id_contact").val("");
      $("#id_contact").find("option").hide();
    }

    resetContactField();
    $("#id_journal").change(function(){
      var journal_id = $(this).val();
      var members = journals[journal_id];
      resetContactField();
      for (len = members.length, i=0; i<len; ++i) {
        $("#id_contact").find("option[value='"+members[i]+"']").show();
      }
    });

    function checkUploads(ev) {
      var filesAddedCount = $('#id_submissions').data('files-added');
      var filesUploadingCount = $('#id_submissions').data('files-uploading');
      if (!filesAddedCount && !filesUploadingCount) {
        return;
      }

      if(filesAddedCount) {
        r = confirm(gettext("Certains de vos fichiers n'ont pas étés téléversés. Êtes-vous sûr ?"));
        if (r == true) { return; }
      }

      if(filesUploadingCount) {
        r = confirm(gettext("Certains de vos fichiers ne sont pas complètement téléversés. Êtes-vous sûr ?"));
        if (r == true) { return; }
      }

      ev.preventDefault();
    }

    $('form').submit(checkUploads);
    $('a:not(form a)').click(checkUploads);
    window.onbeforeunload = checkUploads;
  },
});
