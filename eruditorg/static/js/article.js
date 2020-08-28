import DOMRouter from './core/DOMRouter';
import ArticleDetailController from './controllers/public/journal/ArticleDetailController';


$(document).ready(function() {
  new DOMRouter({
    'public:journal:article_detail': ArticleDetailController,
  }).init();
});
