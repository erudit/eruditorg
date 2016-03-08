ROUTER.registerController('commons:modals', {

  init: function() {
    this.registerModals();
    this.triggerCloseElements();
  },

  /*
   * Register different type of modal windows
   */
  registerModals : function() {

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
          previousURL = window.location.pathname;
        },
        // on open, replaceState with current modal window XHR request url
        open: function() {
          history.replaceState(null, null, $(this.currItem.el).attr('href'));
        },
        // replace state with previous url before modal was open
        close: function() {
          history.replaceState(null, null, previousURL);
        }
      }
    });


  },

  /*
   * Close elements for any modal
   */
  triggerCloseElements : function() {
    $(document).on('click', '[data-close-modal]', function(event) {
      event.preventDefault();
      /* Act on the event */
      $.magnificPopup.close();
    });
  }

});
