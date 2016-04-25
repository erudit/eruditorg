import HomeController from './HomeController';
import LoginController from './LoginController';
import SearchController from './SearchController';
import SearchResultsController from './SearchResultsController';
import ArticleDetailController from './journal/ArticleDetailController';
import IssueDetailController from './journal/IssueDetailController';
import JournalListController from './journal/JournalListController';


const controllers = {
  'public:home': HomeController,
  'public:login': LoginController,
  'public:search': SearchController,
  'public:search:results': SearchController,
  'public:journal:article-detail': ArticleDetailController,
  'public:journal:issue-detail': IssueDetailController,
  'public:journal:journal-list': JournalListController,
};

export default controllers;
