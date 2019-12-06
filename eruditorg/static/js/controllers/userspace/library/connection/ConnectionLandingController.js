import '!!script-loader!clipboard-polyfill/dist/clipboard-polyfill';

export default {

  init: function() {

    this.landing = $('#connection');
    this.clipboard();

  },

  clipboard : function () {
    this.landing.find('.clipboard-data').on('click', (e) => {
      if( e ) {
        e.preventDefault();
        e.stopPropagation();
      }

      clipboard.writeText( $(e.currentTarget).attr('data-clipboard-text') ).then(
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

};
