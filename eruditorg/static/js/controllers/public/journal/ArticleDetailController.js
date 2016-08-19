import '!!script!sticky-kit/jquery.sticky-kit.min';
import '!!script!clipboard.js/clipboard.min';
import '!!script!scrollspy/build/scrollspy';
import getPrefix from 'get-prefix/dist/get-prefix';
import SavedCitationList from '../../../modules/public/SavedCitationList';
import Toolbox from '../../../modules/public/Toolbox';

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
  },

  sticky_elements : function () {

  	var $sticky_header 			  = this.article.find('.article-header-sticky'),
  		  $sticky_elements 		  = this.article.find('.article-table-of-contents, .toolbox'),
  		  transform 				    = getPrefix('transform');

    // save sticky header height
    this.sticky_header_height = $sticky_header.outerHeight() - 20;


    // sticky elements
  	$sticky_elements
      .css('padding-bottom', this.sticky_header_height)
  		.stick_in_parent()
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
    this.article.find('.article-table-of-contents').on('click', 'a', (e) => {
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
          setTimeout(() => { $(e.currentTarget).removeClass('success error'); }, 3000);
        },
        () => {
          $(e.currentTarget).addClass('error');
          setTimeout(() => { $(e.currentTarget).removeClass('success error'); }, 3000);
        }
      );
      return false;
    });
  },

  scrollspy : function () {

    var spy_target      = this.article.find('#article-content')[0],
        toc_body        = this.article.find('.article-table-of-contents .article-table-of-contents--body'),
        toc_body_anchor = toc_body.find('a');

    var spy = new ScrollSpy( spy_target, {
      nav: 'nav.article-table-of-contents ul li a',
      className: 'is-inview',
      callback: function(elements) {

        if( toc_body_anchor.hasClass('is-inview') ) toc_body.addClass('is-inview')
        else toc_body.removeClass('is-inview');
      }
    });

    var subspy = new ScrollSpy( spy_target, {
      nav: '.article-table-of-contents--body ol li a',
      className: 'is-insubview'
    });
  }

};
