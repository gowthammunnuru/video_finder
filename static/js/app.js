'use strict';

var videoApp = angular.module('videoApp', ['ui.router','ui.bootstrap', 'chieffancypants.loadingBar', 'ngAnimate']);

videoApp.config(function($stateProvider, $urlRouterProvider) {

    var home,notFound,lvideos,dVideos;

    notFound = { name : '404', url : '/not-found', templateUrl : 'static/partials/404.html' };
    $stateProvider.state(notFound);

    home = { name : 'landingPage', url  : '/home/:query', templateUrl : 'static/partials/landingPage.html', controller : 'LandingPageCtrl' };
    $stateProvider.state(home);

    lvideos = { name : 'lVideos', url  : '/lVideos/:stdate/:enddate/:searchval', templateUrl : 'static/partials/lVideos.html', controller : 'LatestVideosCtrl' };
    $stateProvider.state(lvideos);

    dVideos = { name : 'dVideos', url  : '/dVideos/:dept/:searchval', templateUrl : 'static/partials/dVideos.html', controller : 'DepartmentVideosCtrl' };
    $stateProvider.state(dVideos);

});

videoApp.run(function($state){
	$state.go('landingPage')
});
