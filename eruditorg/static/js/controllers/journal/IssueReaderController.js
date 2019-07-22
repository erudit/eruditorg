import IssueReader from "../../modules/IssueReader";


export default {
  init: function() {
    var body = $("body");
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
        return body.data("book-url") + gettext("feuilletage/") + (index + 1).toString() + ".jpg" + body.data("ticket");
      },
      bookUrl: body.data("book-url") + body.data("ticket"),
      bookUrlText: gettext("Retour au sommaire"),
      imagesBaseURL: body.data("images-base-url"),
      el: "#issue-reader",
      protected: true,
    };
    var br = new IssueReader(options);
    br.init();
  },
};
