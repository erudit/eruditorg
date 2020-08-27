import '!!script-loader!magnific-popup/dist/jquery.magnific-popup.min';


class CiteModal {

  constructor(el) {

    el.magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 750,
      type: 'ajax',
      closeOnBgClick: true,
      closeBtnInside: true,
      items: {
        src: el.data('modal-id'),
        type: 'inline'
      }
    });
  }

}

export default CiteModal;
