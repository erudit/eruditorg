import DOMRouter from './core/DOMRouter';
import StatsLandingController from './controllers/userspace/library/stats/StatsLandingController';


$(document).ready(function() {
  new DOMRouter({
    'userspace:library:stats:landing': StatsLandingController,
  }).init();
});
