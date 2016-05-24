class DOMRouter {
  constructor(controllers) {
    this.controllers = (controllers === undefined) ? {} : controllers;
  }

  /*
   * Executes the given action associated with the considered controller.
   * @param {string} controller - The codename of the controller.
   * @param {string} action - The name of the action to execute.
   */
  execAction(controller, action) {
    if (controller !== '' && this.controllers[controller] && typeof this.controllers[controller][action] == 'function') {
      this.controllers[controller][action]();
    }
  }

  /*
   * Initializes the router object.
   */
  init() {
    if (document.body) {
      var body = document.body,
      controller = body.getAttribute('data-controller'),
      action = body.getAttribute('data-action');

      if (controller) {
        this.execAction(controller, 'init');
        this.execAction(controller, action);
      }
    }
  }
}


export default DOMRouter;
