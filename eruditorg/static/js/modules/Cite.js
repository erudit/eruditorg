class InlineCiteModal {

  constructor(el) {

    // Load the citation modal window content from inline HTML.
    // MagnificPopup will use the `data-modal-id` attribute to find the inline HTML.
    el.magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 750,
      type: 'inline',
      closeOnBgClick: true,
      closeBtnInside: true,
      items: {
        src: el.data('modal-id'),
        type: 'inline'
      },
      tLoading: gettext('Chargement en cours'),
      tClose: gettext('Fermer (Esc)'),
    });
  }

}

class AjaxCiteModal {

  constructor(el) {

    // Load the citation modal window content with AJAX.
    // MagnificPopup will use the `href` attribute to make its AJAX call.
    el.magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 750,
      type: 'ajax',
      closeOnBgClick: true,
      closeBtnInside: true,
      ajax: {
        tError: gettext('Outils de citation non disponibles pour cet article.'),
      },
      tLoading: gettext('Chargement en cours'),
      tClose: gettext('Fermer (Esc)'),
    });
  }

}

export { InlineCiteModal, AjaxCiteModal };
