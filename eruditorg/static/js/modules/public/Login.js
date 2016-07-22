import '!!script!jquery.validation/dist/jquery.validate.min';
import '!!script!jquery.validation/src/localization/messages_fr';
import '!!script!magnific-popup/dist/jquery.magnific-popup.min';

// form ID
export const formSelector = "form#id-login-form";

export function LoginFormValidation() {
  $(formSelector).validate({
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

class LoginModal {

  constructor() {
    this.previousURL = null;
    this.modalSelector = "#login-modal";

    // auto init
    this.init();
  }

  init() {
    this.modal();
  }

  /*
   * Register login modal
   */
  modal() {
    var _ = this;

    $(this.modalSelector).magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 750,
      type: 'ajax',
      closeOnBgClick: false,
      closeBtnInside: true,
      ajax: {
        settings: {
          // this enable Django to handle the request as PJAX template
          beforeSend: function(xhr) {
            xhr.setRequestHeader('X-PJAX', 'true');
          }
        }
      },
      callbacks: {
        // store current location
        beforeOpen: function() {
          _.previousURL = window.location.pathname;
        },
        // on open, replaceState with current modal window XHR request url
        open: function() {
          history.replaceState(null, null, $(this.currItem.el).attr('href'));
        },
        // when ajax content is added in DOM
        ajaxContentAdded : function() {
          LoginFormValidation();
        },
        // replace state with previous url before modal was open
        close: function() {
          history.replaceState(null, null, _.previousURL);
        }
      }
    });
  }

}

export default LoginModal;
