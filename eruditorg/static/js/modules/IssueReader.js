import "!!script-loader!bookreader/BookReader/jquery-ui-1.12.0.min.js";
import "!!script-loader!bookreader/BookReader/jquery.browser.min.js";
import "!!script-loader!bookreader/BookReader/dragscrollable-br.js";
import "!!script-loader!bookreader/BookReader/jquery.colorbox-min.js";
import "!!script-loader!bookreader/BookReader/jquery.bt.min.js";
import "!!script-loader!bookreader/BookReader/BookReader.js";
import "!!script-loader!bookreader/BookReader/plugins/plugin.url.js";


function IssueReader(options) {
  BookReader.call(this, options);
};
IssueReader.prototype = Object.create(BookReader.prototype);

/**
 * Determines the initial mode for starting if a mode is not already present in
 * the params argument.
 *
 * This method is overridden to make sure that we are in one page mode when we
 * view the reader from a mobile and in two pages mode when we view the reader
 * from a desktop.
 *
 * See node_modules/bookreader/BookReader/BookReader.js for the original.
 *
 * @param {object} params
 * @return {number} the mode
 */
IssueReader.prototype.getInitialMode = function(params) {
  var nextMode;
  if (typeof(params.mode) != "undefined") {
    // If a mode is present in the params, use it.
    nextMode = params.mode;
  } else if ($(window).width() <= this.onePageMinBreakpoint) {
    // If the window is smaller than the breakpoint, use one page mode.
    nextMode = this.constMode1up;
  } else {
    // Otherwise, use the two pages mode.
    nextMode = this.constMode2up;
  }
  return nextMode;
};

/**
 * Initialize the navigation bar (bottom)
 *
 * This method is overridden to remove unwanted elements from the bottom
 * navigation bar.
 *
 * See node_modules/bookreader/BookReader/BookReader.js for the original.
 *
 * @return {jqueryElement}
 */
IssueReader.prototype.initNavbar = function() {
  this.refs.$BRnav = $(
    "<div class=\"BRnav BRnavDesktop\">"
    +"  <div class=\"BRnavpos desktop-only\">"
    +"    <div class=\"BRpager\"></div>"
    +"    <div class=\"BRnavline\"></div>"
    +"  </div>"
    +"  <div class=\"BRpage\">"
    +     "<span class=\"BRcurrentpage\"></span>"
    +     "<button class=\"BRicon book_left js-tooltip\"></button>"
    +     "<button class=\"BRicon book_right js-tooltip\"></button>"
    +     "<button class=\"BRicon onepg js-tooltip\"></button>"
    +     "<button class=\"BRicon twopg js-tooltip\"></button>"
    +     "<button class=\"BRicon zoom_out js-tooltip\"></button>"
    +     "<button class=\"BRicon zoom_in js-tooltip\"></button>"
    +"  </div>"
    +"</div>"
  );
  this.refs.$br.append(this.refs.$BRnav);

  // Page slider events.
  var self = this;
  this.$(".BRpager").slider({
    animate: true,
    min: 0,
    max: this.getNumLeafs() - 1,
    value: this.currentIndex(),
    range: "min"
  })
  .bind("slide", function(event, ui) {
    self.updateNavPageNum(ui.value);
    return true;
  })
  .bind("slidechange", function(event, ui) {
    self.updateNavPageNum(ui.value);
    if ($(this).data("swallowchange")) {
      $(this).data("swallowchange", false);
    } else {
      self.jumpToIndex(ui.value);
    }
    return true;
  });
  this.updateNavPageNum(this.currentIndex());

  return this.refs.$BRnav;
};

/**
 * This method builds the html for the toolbar.
 *
 * This method is overridden to remove unwanted elements from the top toolbar.
 *
 * See node_modules/bookreader/BookReader/BookReader.js for the original.
 *
 * @return {jqueryElement}
 */
BookReader.prototype.buildToolbarElement = function() {
  this.refs.$BRtoolbar = $(
    "<div class=\"BRtoolbar header\">"
    + "<div class=\"BRtoolbarbuttons\">"
    +   "<div class=\"BRtoolbarLeft\">"
    +     "<span class=\"BRtoolbarSection BRtoolbarSectionTitle\">"
    +       "<a href=\"" + this.bookUrl + "\" title=\"" + this.bookUrlText + "\" class=\"BRreturn\">"
    +         this.bookUrlText
    +       "</a>"
    +     "</span>"
    +   "</div>"
    +  "</div>"
    +"</div>"
  );
  return this.refs.$BRtoolbar;
}

/**
 * Navigation bar strings
 *
 * This method is overridden to make the strings translatable.
 *
 * See node_modules/bookreader/BookReader/BookReader.js for the original.
 */
BookReader.prototype.initUIStrings = function() {
  var titles = {
    ".book_left": gettext("Page précédente"),
    ".book_right": gettext("Page suivante"),
    ".onepg": gettext("Une page"),
    ".twopg": gettext("Deux pages"),
    ".zoom_in": gettext("Zoom avant"),
    ".zoom_out": gettext("Zoom arrière"),
  };
  for (var icon in titles) {
    if (titles.hasOwnProperty(icon)) {
      this.$(icon).prop("title", titles[icon]);
    }
  }
}

IssueReader.prototype.constructor = IssueReader;

export default IssueReader;
