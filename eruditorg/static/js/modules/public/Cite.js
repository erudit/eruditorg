import '!!script!jquery.validation/dist/jquery.validate.min';
import '!!script!jquery.validation/src/localization/messages_fr';
import '!!script!magnific-popup/dist/jquery.magnific-popup.min';

class CiteModal {

  constructor(el) {

    el.magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 750,
      type: 'ajax',
      closeOnBgClick: false,
      closeBtnInside: true,
      items: {
        src: el.data('modal-id'),
        type: 'inline'
      }
    });
  }

}

export default CiteModal;
