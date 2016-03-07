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
    action = (action === undefined || action.length === 0) ? 'init' : action;

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
      // commons init site's wide functions
      ROUTER.execAction('commons:main');

      // find any controllers in source
      ROUTER.findControllers();
    }
  },

  findControllers : function() {
    $(document).find('[data-controller]').not('[data-controller-initialized]').each(function() {
      var controller = $(this).data('controller'),
          action     = $(this).data('action');

      if (controller) {
        console.warn('Controller found : ', controller);
        console.warn('Action found : ', action);

        // init found controller
        ROUTER.execAction(controller, action);

        // set element as initialized
        $(this).attr('data-controller-initialized', 'true');
      }

    });
  }

};


$(document).ready(ROUTER.init);
