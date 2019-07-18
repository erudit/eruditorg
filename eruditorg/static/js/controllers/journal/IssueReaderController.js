import '!!script!bookreader/BookReader/jquery-ui-1.12.0.min.js';
import '!!script!bookreader/BookReader/jquery.browser.min.js';
import '!!script!bookreader/BookReader/dragscrollable-br.js';
import '!!script!bookreader/BookReader/jquery.colorbox-min.js';
import '!!script!bookreader/BookReader/jquery.bt.min.js';
import '!!script!bookreader/BookReader/BookReader.js';
import '!!script!bookreader/BookReader/plugins/plugin.url.js';


export default {
  init: function() {
    var body = $("body")
    var options = {
      getNumLeafs: function() {
        return body.data("num-leafs");
      },
      getPageWidth: function(index) {
        return body.data("page-width");
      },
      getPageHeight: function(index) {
        return body.data("page-height");
      },
      getPageURI: function(index, reduce, rotate) {
        return body.data("book-url") + gettext('feuilletage/') + (index + 1).toString() + '.jpg' + body.data("ticket");
      },
      bookUrl: body.data("book-url") + body.data("ticket"),
      bookUrlText: gettext("Retour au sommaire"),
      bookUrlTitle: gettext("Retour au sommaire"),
      imagesBaseURL: body.data("images-base-url"),
      showLogo: false,
      protected: true,
    };
    var br = new BookReader(options);
    br.init();
  },
};
