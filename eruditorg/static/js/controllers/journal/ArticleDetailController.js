import '!!script!sticky-kit/jquery.sticky-kit.min';
import '!!script!clipboard.js/clipboard.min';
import '!!script!scrollspy/build/scrollspy';
import getPrefix from 'get-prefix/dist/get-prefix';
import SavedCitationList from '../../modules/SavedCitationList';
import Toolbox from '../../modules/Toolbox';
import '!!script!magnific-popup/dist/jquery.magnific-popup.min';

export default {

  init: function() {
    this.article                = $('#article_detail');
    this.sticky_header_height   = 0;
    this.toolbox                = new Toolbox( this.article );

    // Initializes the citation list
    this.saved_citations = new SavedCitationList();
    this.saved_citations.init();

    this.sticky_elements();
    this.smooth_scroll();
    this.clipboard();
    this.scrollspy();
    this.display_pdf_based_on_mimetype();
    this.lightbox();
  },

  sticky_elements : function () {

    var $sticky_header         = this.article.find('.article-header-sticky'),
        $sticky_elements       = this.article.find('.article-table-of-contents, .toolbox-wrapper'),
        transform             = getPrefix('transform');

    // save sticky header height
    this.sticky_header_height = $sticky_header.outerHeight() - 20;


    // sticky elements
    $sticky_elements
      .css('padding-bottom', this.sticky_header_height)
      .stick_in_parent({offset_top: 20})
      .first()
      .on("sticky_kit:stick", (e) => {
        setTimeout(function(){
          $sticky_elements.css(transform, 'translate(0, ' + this.sticky_header_height+'px)');
          $sticky_header.css(transform, 'translate(-50%, 0%)');
        }, 0);
      })
      .on("sticky_kit:unstick", (e) => {
        setTimeout(function(){
          $sticky_elements.css(transform, 'translate(0, 0)');
          $sticky_header.css(transform, 'translate(-50%, -100%)');
        }, 0);
      });
  },

  smooth_scroll : function () {
    this.article.on('click', 'a[href^="#"]', (e) => {
      if( e ) {
        e.preventDefault();
        e.stopPropagation();
      }

      var target = $(e.currentTarget).attr('href').replace('#', '');
      if( !target ) return false;

      $('html, body').animate( { scrollTop: this.article.find('#'+target).offset().top - this.sticky_header_height - 30 }, 750 );
      return false;
    });
  },

  clipboard : function () {
    this.article.find('.clipboard-data').on('click', (e) => {
      if( e ) {
        e.preventDefault();
        e.stopPropagation();
      }

      clipboard.copy( $(e.currentTarget).attr('href') ).then(
        () => {
          $(e.currentTarget).addClass('success');
          setTimeout(() => { $(e.currentTarget).removeClass('success error'); }, 3000);
        },
        () => {
          $(e.currentTarget).addClass('error');
          setTimeout(() => { $(e.currentTarget).removeClass('success error'); }, 3000);
        }
      );
      return false;
    });
  },

  scrollspy : function () {

    var spy_target      = this.article.find('#article-content')[0],
        toc_body        = this.article.find('.article-table-of-contents .article-table-of-contents--body'),
        toc_body_anchor = toc_body.find('a');

    if (toc_body.length > 0) {
      var spy = new ScrollSpy( spy_target, {
        nav: 'nav.article-table-of-contents ul li a',
        className: 'is-inview',
        callback: function(elements) {

          if( toc_body_anchor.hasClass('is-inview') ) toc_body.addClass('is-inview')
          else toc_body.removeClass('is-inview');
        }
      });
    }

    if (toc_body.length > 0) {
      // Abstracts do not have a body
      console.log('length');
      var subspy = new ScrollSpy( spy_target, {
        nav: '.article-table-of-contents--body ol li a',
        className: 'is-insubview'
      });
    }

  },

  display_pdf_based_on_mimetype : function () {
    var can_display_pdf = false;

    // Chrome and Safari can display PDFs when they have 'application/pdf' in their mimeTypes.
    if (navigator.mimeTypes['application/pdf'] !== undefined) {
      can_display_pdf = true;
    }

    // Firefox does not have 'application/pdf' in its mimeTypes but can display PDFs since version 19.0.
    else {
      var re = /Firefox\/(\d+\.\d+)/
      var ff_version = navigator.userAgent.match(re)
      if (ff_version && ff_version[1] > 19.0) {
        can_display_pdf = true;
      }
    }

    if (!can_display_pdf) {
      $('#pdf-viewer').hide();
      $('#pdf-viewer-menu-link').hide();
    }
    else {
      $('#pdf-download').hide();
      $('#pdf-download-menu-link').hide();
    }
  },

  lightbox : function () {
    $('.lightbox').magnificPopup({
      type: 'image',
      closeOnContentClick: true,
      closeBtnInside: false,
      fixedContentPos: true,
      mainClass: 'mfp-no-margins mfp-with-zoom',
      image: {
        verticalFit: false,
        titleSrc: false,
        markup: '<div class="mfp-figure">' +
                  '<div class="mfp-close"></div>' +
                  '<figure>' +
                    '<div class="mfp-top-bar">' +
                      '<div class="mfp-title"></div>' +
                    '</div>' +
                    '<div class="mfp-img"></div>' +
                    '<figcaption>' +
                      '<div class="mfp-bottom-bar">' +
                        '<div class="mfp-counter"></div>' +
                      '</div>' +
                    '</figcaption>' +
                  '</figure>' +
                '</div>',
      },
      callbacks: {
        open: function() {
          var figure = $(this.currItem.el).parent('figure')
          var grfigure = figure.parent('div.grfigure')

          // Figure group text (figure numbers).
          // To get only the figure group text and not the text from every children, we clone the
          // element, select all the children, remove all the children, go back to first element and
          // get the text.
          var grfigure_number = grfigure.clone().children().remove().end().text()
          // Figure group caption.
          var grfigure_caption = grfigure.find('p.alinea')
          // Figure number.
          var figure_number = figure.find('p.no')
          // Figure caption.
          var figure_caption = figure.find('p.legende')

          // Figure notes.
          var figure_notes = figure.find('p.alinea')
          // Figure source.
          var figure_source = $('<p>').html(figure.find('cite.source').html())

          // Put the figure number(s) and caption(s) above the figure.
          $(this.content).find('.mfp-top-bar .mfp-title').prepend(
            grfigure_number,
            grfigure_caption.clone(),
            figure_number.clone(),
            figure_caption.clone(),
          );

          // Put the figure note(s) and source(s) under the figure.
          $(this.content).find('.mfp-bottom-bar').prepend(
            figure_notes.clone(),
            figure_source.clone(),
          );

          // Make sure the caption is not out of the window for big figures.
          $(this.content).parent('.mfp-content').css('margin-top',
            $(this.content).find('.mfp-top-bar').height() - 20
          );
        },
      },
      zoom: {
        enabled: true,
        duration: 300
      }
    });
  }


};
