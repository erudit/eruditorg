$(document).ready(function() {
  Article();
});

function Article() {

  	var $article 				= $('#article-detail'),
  		$sticky_header 			= $article.find('.article-header-sticky'),
  		$sticky_elements 		= $article.find('.article-table-of-contents, .article-tools'),
  		sticky_header_height 	= $sticky_header.outerHeight() - 20,
  		transform 				= getPrefix('transform');

  	// sticky elements
	$sticky_elements
		.stick_in_parent()
		.first()
		.on("sticky_kit:stick", function(e) {
			setTimeout(function(){
				$sticky_elements.css(transform, 'translate(0, '+sticky_header_height+'px)');
				$sticky_header.css(transform, 'translate(-50%, 0%)');
			}, 0);
		})
		.on("sticky_kit:unstick", function(e) {
			setTimeout(function(){
				$sticky_elements.css(transform, 'translate(0, 0)');
				$sticky_header.css(transform, 'translate(-50%, -100%)');
			}, 0);
		});


}
