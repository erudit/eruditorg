import HomeController from './HomeController';
import LoginController from './LoginController';
import SearchController from './SearchController';
import ArticleDetailController from './journal/ArticleDetailController';
import JournalListController from './journal/JournalListController';


const controllers = {
  'public:home': HomeController,
  'public:login': LoginController,
  'public:search': SearchController,
  'public:journal:article-detail': ArticleDetailController,
  'public:journal:journal-list': JournalListController,
};

export default controllers;
