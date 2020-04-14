import '!!script-loader!jquery-validation/dist/jquery.validate.min';
import '!!script-loader!jquery-validation/dist/localization/messages_fr';
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
    },
    messages: {
      username: gettext("Ce champ est obligatoire."),
      password: gettext("Ce champ est obligatoire."),
    }
  });
}

class LoginModal {

  constructor() {
    this.previousURL = null;
    this.modalSelector = "#login-modal, #article-login-modal, #journal-login-modal";

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
    $(this.modalSelector).magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 750,
      type: 'ajax',
      closeOnBgClick: false,
      closeBtnInside: true,
      ajax: {
        settings: {
          // this enable Django to handle the request as PJAX template
          beforeSend: (xhr) => {
            xhr.setRequestHeader('X-PJAX', 'true');
          }
        }
      },
      callbacks: {
        // store current location
        beforeOpen: () => {
          this.previousURL = window.location.pathname;
        },
        // on open, replaceState with current modal window XHR request url
        open: () => {
          history.replaceState(null, null, $($.magnificPopup.instance.currItem.el).attr('href'));
          $('body').addClass('modal-open');
        },
        // when ajax content is added in DOM
        ajaxContentAdded : () => {
          LoginFormValidation();
        },
        // replace state with previous url before modal was open
        close: () => {
          history.replaceState(null, null, this.previousURL);
          $('body').removeClass('modal-open');
        }
      }
    });
  }

}

export default LoginModal;
