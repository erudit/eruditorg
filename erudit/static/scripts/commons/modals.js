ROUTER.registerController('commons:modals', {

  init: function() {
    this.register();
  },

  register : function() {
    //
    $('[data-open-modal-ajax]').magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 300,
      type: 'ajax',
      closeOnBgClick: false,
      ajax: {
        settings: {
          beforeSend: function(xhr) {
            xhr.setRequestHeader('X-PJAX', 'true');
          }
        }
      },
      callbacks: {
        beforeOpen: function() {
          previousURL = window.location.pathname;
        },
        open: function() {
          history.replaceState(null, null, $(this.currItem.el).attr('href'));
        },
        close: function() {
          history.replaceState(null, null, previousURL);
        }
      }
    });
  }

});
