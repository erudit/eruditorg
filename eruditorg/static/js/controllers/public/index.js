import HomeController from './HomeController';
import LoginController from './LoginController';
import SearchUnitCollectionDetailController from './greyLiterature/SearchUnitCollectionDetailController';
import SearchUnitDocumentDetailController from './greyLiterature/SearchUnitDocumentDetailController';
import ArticleDetailController from './journal/ArticleDetailController';
import IssueDetailController from './journal/IssueDetailController';
import JournalListController from './journal/JournalListController';
import AdvancedSearchController from './search/AdvancedSearchController';
import ResultsController from './search/ResultsController';
import CollectionListController from './thesis/CollectionListController';
import SavedCitationListController from './citations/SavedCitationListController';


const controllers = {
  'public:home': HomeController,
  'public:login': LoginController,
  'public:search:advanced-search': AdvancedSearchController,
  'public:search:results': ResultsController,
  'public:grey_literature:collection_detail': SearchUnitCollectionDetailController,
  'public:grey_literature:document_detail': SearchUnitDocumentDetailController,
  'public:journal:article_detail': ArticleDetailController,
  'public:journal:issue_detail': IssueDetailController,
  'public:journal:journal_list': JournalListController,
  'public:thesis:collection_list': CollectionListController,
  'public:citations:list': SavedCitationListController,
};

export default controllers;
