import HomeController from './HomeController';
import LoginController from './LoginController';
import AdvancedSearchController from './search/AdvancedSearchController';
import ResultsController from './search/ResultsController';
import ArticleDetailController from './journal/ArticleDetailController';
import IssueDetailController from './journal/IssueDetailController';
import JournalListController from './journal/JournalListController';
import JournalDetailController from './journal/JournalDetailController';
import CollectionListController from './thesis/CollectionListController';
import SavedCitationListController from './citations/SavedCitationListController';

const controllers = {
  'public:home': HomeController,
  'public:login': LoginController,
  'public:search:advanced-search': AdvancedSearchController,
  'public:search:results': ResultsController,
  'public:journal:article_detail': ArticleDetailController,
  'public:journal:issue_detail': IssueDetailController,
  'public:journal:journal_list': JournalListController,
  'public:journal:journal_detail': JournalDetailController,
  'public:thesis:collection_list': CollectionListController,
  'public:citations:list': SavedCitationListController,
};

export default controllers;
