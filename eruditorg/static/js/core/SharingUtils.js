const SharingUtils = {

  facebook : function ( url_to_share, title ) {

      var data = { t: title, u: encodeURI(url_to_share) },
          url    = 'https://www.facebook.com/sharer/sharer.php?' + $.param( data ),
          width  = 575,
          height = 400,
          left   = ($(window).width()  - width)  / 2,
          top    = ($(window).height() - height) / 2,
          opts   = 'status=1' +
                   ',width='  + width  +
                   ',height=' + height +
                   ',top='    + top    +
                   ',left='   + left;

    window.open(url, 'facebook', opts);
  },

  twitter : function ( url_to_share, title ) {

    var data   = { text: title, url: encodeURI(url_to_share) },
        url    = 'https://twitter.com/intent/tweet?' + $.param(data),
        width  = 575,
        height = 400,
        left   = ($(window).width()  - width)  / 2,
        top    = ($(window).height() - height) / 2,
        opts   = 'status=1' +
                 ',width='  + width  +
                 ',height=' + height +
                 ',top='    + top    +
                 ',left='   + left;

      window.open(url, 'twitter', opts);
  },

  linkedin : function( url_to_share, title ) {

    var data   = { mini: true, title: title, url: encodeURI(url_to_share), summary: '', source: '' },
        url    = 'https://www.linkedin.com/shareArticle?' + $.param(data),
        width  = 575,
        height = 400,
        left   = ($(window).width()  - width)  / 2,
        top    = ($(window).height() - height) / 2,
        opts   = 'status=1' +
                 ',width='  + width  +
                 ',height=' + height +
                 ',top='    + top    +
                 ',left='   + left;

      window.open(url, 'linkedin', opts);
  },

  email : function( url_to_share, title, text) {
    var url = 'mailto:?subject=Érudit%20–%20' + encodeURIComponent(title.replace(/^\s+|\s+$/g,'')) +
      '&body=' + encodeURIComponent((text.replace(/^\s+|\s+$/g,'') || '') + '\n\n' + url_to_share);
    document.location.href = url;
  }

};

export default SharingUtils;
