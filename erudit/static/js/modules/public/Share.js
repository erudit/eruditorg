import '!!script!jquery.validation/dist/jquery.validate.min';
import '!!script!jquery.validation/src/localization/messages_fr';
import '!!script!magnific-popup/dist/jquery.magnific-popup.min';
import SharingUtils from '../../core/SharingUtils';

class ShareModal {

  constructor(el) {

    this.el    = el;
    this.title = el.data('title') || document.title;
    this.url   = el.data('share-url') || window.location.href;

    this.init();
  }

  init() {

    var _ = this;

    this.el.magnificPopup({
      mainClass: 'mfp-fade',
      removalDelay: 750,
      closeOnBgClick: false,
      closeBtnInside: false,
      items: {
        src: '<section class="share-modal">\
                <div class="container-fluid">\
                  <div class="row">\
                    <div class="col-lg-3 col-md-5 col-sm-6 col-xs-12 col-centered">\
                      <div class="panel">\
                        <header class="panel-heading">\
                          <h2 class="h4 panel-title text-center">Partager cette article</h2>\
                        </header>\
                        <div class="panel-body share-modal--body">\
                          <ul class="unstyled">\
                            <li><button id="share-email" class="btn btn-primary btn-block"><span class="ion ion-ios-email"></span>Courriel</button></li>\
                            <li><button id="share-twitter" class="btn btn-primary btn-block"><span class="ion ion-social-twitter"></span>Twitter</button></li>\
                            <li><button id="share-facebook" class="btn btn-primary btn-block"><span class="ion ion-social-facebook"></span>Facebook</button></li>\
                            <li><button id="share-linkedin" class="btn btn-primary btn-block"><span class="ion ion-social-linkedin"></span>LinkedIn</button></li>\
                          </ul>\
                        </div>\
                      </div>\
                    </div>\
                  </div>\
                </div>\
              </section>',
        type: 'inline'
      },
      callbacks: {
        open: function() {

          var $modal = $(this.content);

          $modal.on('click', '#share-email', function(event){ 
            event.preventDefault();

            SharingUtils.email( _.url, _.title );
            return false;
          });

          $modal.on('click', '#share-twitter', function(event){ 
            event.preventDefault();
            
            SharingUtils.twitter( _.url, _.title );
            return false;
          });

          $modal.on('click', '#share-facebook', function(event){ 
            event.preventDefault();
            
            SharingUtils.facebook( _.url, _.title );
            return false;
          });

          $modal.on('click', '#share-linkedin', function(event){ 
            event.preventDefault();
            
            SharingUtils.linkedin( _.url, _.title );
            return false;
          }); 

        },
        close: function() { 
          $(this.content).off('click');
        }
      }
    });

  }



}

export default ShareModal;
