import HomeController from './HomeController';
import LoginController from './LoginController';
import SearchResultsController from './SearchResultsController';
import ArticleDetailController from './journal/ArticleDetailController';
import IssueDetailController from './journal/IssueDetailController';
import JournalListController from './journal/JournalListController';


const controllers = {
  'public:home': HomeController,
  'public:login': LoginController,
  'public:search:results': SearchResultsController,
  'public:journal:article-detail': ArticleDetailController,
  'public:journal:issue-detail': IssueDetailController,
  'public:journal:journal-list': JournalListController,
};

export default controllers;
