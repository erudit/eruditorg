import '@babel/polyfill';

import '!!script-loader!akkordion/dist/akkordion.min';
import '!!script-loader!bootstrap-sass/assets/javascripts/bootstrap.min';
import '!!script-loader!inline-svg/dist/inlineSVG.min';
import '!!script-loader!lazysizes/lazysizes.min';
import '!!script-loader!lazysizes/plugins/aspectratio/ls.aspectratio.min';

import modules from './modules';
import DOMRouter from './core/DOMRouter';

import ArticleDetailController from './controllers/public/journal/ArticleDetailController';
import IssueDetailController from './controllers/public/journal/IssueDetailController';
import JournalListController from './controllers/public/journal/JournalListController';
import JournalDetailController from './controllers/public/journal/JournalDetailController';
import SavedCitationListController from './controllers/public/citations/SavedCitationListController';

const controllers = {
  'public:journal:article_detail': ArticleDetailController,
  'public:journal:issue_detail': IssueDetailController,
  'public:journal:journal_list': JournalListController,
  'public:journal:journal_detail': JournalDetailController,
  'public:citations:list': SavedCitationListController,
};

export default controllers;


// Defines the router and initializes it!
let router = new DOMRouter(controllers);
$(document).ready(function(ev) {
  // Initializes the router
  router.init();
});
