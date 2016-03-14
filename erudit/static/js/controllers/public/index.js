import HomeController from './HomeController';
import ArticleDetailController from './journal/ArticleDetailController';
import JournalListController from './journal/JournalListController';

const controllers = {
  'public:home': HomeController,
  'public:journal:article-detail': ArticleDetailController,
  'public:journal:journal-list': JournalListController,
};

export default controllers;
