import DOMRouter from './core/DOMRouter';
import IssueDetailController from './controllers/public/journal/IssueDetailController';


$(document).ready(function() {
  new DOMRouter({
    'public:journal:issue_detail': IssueDetailController,
  }).init();
});
