import '!!script!magnific-popup/dist/jquery.magnific-popup.min';

class Modals {

  constructor() {
    this.previousURL = null;

    this.init();
  }

  init() {
    this.registerModals();
    this.triggerCloseElements();
  }  

  /*
   * Register different type of modal windows
   */
  registerModals() {

    /*
     * AJAX modal type
     */
    $('[data-open-modal-ajax]').magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 750,
      type: 'ajax',
      closeOnBgClick: false,
      closeBtnInside: false,
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
          Modals.previousURL = window.location.pathname;
          console.log(Modals.previousURL);
        },
        // on open, replaceState with current modal window XHR request url
        open: function() {
          history.replaceState(null, null, $(this.currItem.el).attr('href'));
        },
        // replace state with previous url before modal was open
        close: function() {
          history.replaceState(null, null, Modals.previousURL);
        }
      }
    });


  }

  /*
   * Close elements for any modal
   */
  triggerCloseElements() {
    $(document).on('click', '[data-close-modal]', function(event) {
      event.preventDefault();
      /* Act on the event */
      $.magnificPopup.close();
    });
  }

}

export default Modals;
