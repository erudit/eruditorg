import '!!script!jquery.validation/dist/jquery.validate.min';
import '!!script!jquery.validation/src/localization/messages_fr';
import '!!script!magnific-popup/dist/jquery.magnific-popup.min';

class QuoteModal {

  constructor(el) {

    el.magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 750,
      type: 'ajax',
      closeOnBgClick: false,
      closeBtnInside: false,
      items: {
        src: '<section class="quote-modal">\
                <div class="container-fluid">\
                  <div class="row">\
                    <div class="col-lg-4 col-md-5 col-sm-6 col-xs-12 col-centered">\
                      <div class="panel">\
                        <header class="panel-heading">\
                          <h2 class="h4 panel-title text-center">Citer cet article</h2>\
                        </header>\
                        <div class="panel-body quote-modal--body">\
                        	<form action="#" id="id-login-form" method="post">\
                        		<div class="form-group">\
            									<textarea name="quote" id="quote" cols="30" rows="10" resizeable="no" placeholder="Votre citation..."></textarea>\
            								</div>\
            								<div class="form-group text-center">\
            									<button type="reset" class="btn btn-default btn-lg" id="submit-id-submit" data-close-modal>Annuler</button>\
            									<button type="submit" class="btn btn-primary btn-lg" id="submit-id-submit" disabled>Envoyer</button>\
            								</div>\
                        	</form>\
                        </div>\
                      </div>\
                    </div>\
                  </div>\
                </div>\
              </section>',
        type: 'inline'
      }
    });
  }

}

export default QuoteModal;
