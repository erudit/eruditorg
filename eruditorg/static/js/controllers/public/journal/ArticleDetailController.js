import '!!script-loader!clipboard-polyfill/dist/clipboard-polyfill.promise';
import '!!script-loader!sticky-kit/dist/sticky-kit.min';

import Scrollspy from 'scrollspy-js/src/js/scrollspy';
import getPrefix from 'get-prefix/dist/get-prefix';
import SavedCitationList from '../../../modules/SavedCitationList';
import Toolbox from '../../../modules/Toolbox';

export default {

  init: function() {
    this.article                = $('#article_detail');
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

    var $sticky_elements       = this.article.find('.article-table-of-contents, .toolbox-wrapper'),
        transform             = getPrefix('transform');

    // sticky elements
    $sticky_elements
      .css('padding-bottom', 20)
      .stick_in_parent({offset_top: 20})
      .first()
      .on("sticky_kit:stick", (e) => {
        setTimeout(function(){
          $sticky_elements.css(transform, 'translate(0, 0)');
        }, 0);
      })
      .on("sticky_kit:unstick", (e) => {
        setTimeout(function(){
          $sticky_elements.css(transform, 'translate(0, 0)');
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

      $('html, body').animate( { scrollTop: this.article.find('#'+target).offset().top - 10 }, 750 );
      return false;
    });
  },

  clipboard : function () {
    this.article.find('.clipboard-data').on('click', (e) => {
      if( e ) {
        e.preventDefault();
        e.stopPropagation();
      }

      clipboard.writeText( $(e.currentTarget).attr('href') ).then(
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
      prependTo: $('.full-article'),
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
          var figure = $(this.currItem.el).closest('.figure, .tableau')
          var grfigure = figure.closest('.grfigure, .grtableau')
          var grfigure_caption = grfigure.find('.grfigure-caption')

          // Figure group numbers.
          var grfigure_number = grfigure_caption.find('.no')
          // Figure group caption.
          var grfigure_legend = grfigure_caption.find('div.legende')
          // Figure number.
          var figure_number = figure.find('.no')
          // Figure caption.
          var figure_caption = figure.find('.legende')

          // Figure group bottom caption.
          var grfigure_bottom_legende = grfigure.find('div.grfigure-legende')
          // Figure bottom caption.
          var figure_bottom_legende = figure.find('div.figure-legende')
          // Figure notes.
          var figure_notes = figure.find('div.notefigtab')
          // Figure source.
          var figure_source = $('<p>').html(figure.find('.source').html())

          // Put the figure number(s) and caption(s) above the figure.
          $(this.content).find('.mfp-top-bar .mfp-title').prepend(
            grfigure_number.clone(),
            grfigure_legend.clone(),
            figure_number.clone(),
            figure_caption.clone(),
          );

          // Put the figure note(s) and source(s) under the figure.
          $(this.content).find('.mfp-bottom-bar').prepend(
            figure_bottom_legende.clone(),
            figure_notes.clone(),
            figure_source.clone(),
            grfigure_bottom_legende.clone(),
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
