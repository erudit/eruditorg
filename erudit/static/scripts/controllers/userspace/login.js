var controlerName = 'userspace:login';

ROUTER.registerController(controlerName, {

  // formElement: function() { return $("form#id-login-form"); },

  init: function() {
    // set variables
    this.formElement = $("form#id-login-form");

    // methods
    this.validateForm();
  },

  validateForm : function() {
    var $form = CONTROLLERS[controlerName].formElement;
    $form.validate({
      rules : {
        username: {
          required: true
        },
        password: {
          required: true
        }
      }
    });
  }

});
