import HomeController from './HomeController';
import LoginController from './LoginController';
import ArticleDetailController from './journal/ArticleDetailController';
import JournalListController from './journal/JournalListController';


const controllers = {
  'public:home': HomeController,
  'public:login': LoginController,
  'public:journal:article-detail': ArticleDetailController,
  'public:journal:journal-list': JournalListController,
};

export default controllers;
