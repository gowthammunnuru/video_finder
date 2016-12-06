videoApp.controller('DepartmentVideosCtrl',['$scope', '$http', '$location', '$stateParams', '$filter', 'cfpLoadingBar', 'Directory',
    function($scope, $http, $location, $stateParams, $filter, cfpLoadingBar, Directory)
{
    $scope.showgrid=false;
    $scope.showlist=false;
    $scope.showcard=true;
    var orderBy = $filter('orderBy');
    
    $scope.deptGroup = $stateParams.deptGroup;
    $scope.dept = $stateParams.dept;
    $scope.getDepartments= function(){
        Directory.getDept()
                 .then(function(dept_result){
                        $scope.departmentData = dept_result.data;
                 })
        }
    $scope.isCurrentGroup = function(group){
        return (group === 'Categories') ? true : false;
    }
    $scope.isDeptSelected = function(dept){ 
        return (dept === $scope.dept) ? true : false;
    }
    $scope.getVideos = function(dept,searchval){
        $scope.dept = dept;
        $scope.searchval = searchval;
        cfpLoadingBar.start();
        console.log('Coming here');
        Directory.getVideos($scope.dept,$scope.searchval)
                 .then(function(videos_result){
                        $scope.VideoData = videos_result.data;
                 })
        cfpLoadingBar.complete();
    }
    $scope.order = function(index) {
      $scope.predicate = index;
      $scope.reverse = ($scope.predicate === index) ? !$scope.reverse : false;
      // $scope.results = orderBy($scope.results, function(obj){  return obj[index] }, $scope.reverse);
      $scope.VideoData = orderBy($scope.VideoData, function(obj){  
            switch(index){
                case 1: return obj[index];
                case 4: return obj[index];
                case 3: return obj[7];
                case 2: return new Date(obj[index].replace(/-/g, '/'));
            }
        }, $scope.reverse);
    }
    $('#sidebar').affix({ offset: { top: 0 } });
    $('#grid').tooltip({ placement: "top" });
    $('#card').tooltip({ placement: "top" });
    $('#list').tooltip({ placement: "top" });
    $scope.getDepartments()
    $scope.getVideos($stateParams.dept)
    $scope.order(2, true);
}]);


videoApp.controller('LatestVideosCtrl',['$scope', '$http', '$location', '$filter', 'cfpLoadingBar', 'Directory',
    function($scope, $http, $location, $filter, cfpLoadingBar, Directory)
{
    $scope.showgrid=false;
    $scope.showlist=false;
    $scope.showcard=true;
    var today = new Date();
    $scope.stdate = $filter("date")(new Date(today.getTime() - 31*24*60*60*1000), 'MM-dd-yyyy');
    $scope.enddate = $filter("date")(Date.now(), 'MM-dd-yyyy');
    var orderBy = $filter('orderBy');
    
    $scope.format = 'MM-dd-yyyy';

    $scope.dateOptions = {
      formatYear: 'yy',
      startingDay: 1,
    };

    $scope.toggleMin = function() {
        $scope.maxDate = $scope.maxDate ? null : new Date();
    };
    $scope.toggleMin();

    $scope.open_stdate = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened_stdate = true;
        $scope.opened_enddate = false;
    };

    $scope.open_enddate = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened_enddate = true;
        $scope.opened_stdate = false;
    };

    $scope.lvideos= function(stdate,enddate,searchval){
        $scope.stdate = $filter("date")($scope.stdate, 'MM-dd-yyyy');
        $scope.enddate = $filter("date")($scope.enddate, 'MM-dd-yyyy');
        $scope.searchval = searchval;
        cfpLoadingBar.start();
        Directory.latestVideos($scope.stdate,$scope.enddate,$scope.searchval)
                 .then(function(video_result){
                        $scope.VideoData = video_result.data;
                        // console.log($scope.VideoData);
                 })
        cfpLoadingBar.complete();
        }

    $scope.order = function(index) {
      $scope.predicate = index;
      $scope.reverse = ($scope.predicate === index) ? !$scope.reverse : false;
      // $scope.results = orderBy($scope.results, function(obj){  return obj[index] }, $scope.reverse);
      $scope.VideoData = orderBy($scope.VideoData, function(obj){  
            switch(index){
                case 1: return obj[index];
                case 4: return obj[index];
                case 3: return obj[7];
                case 2: return new Date(obj[index].replace(/-/g, '/'));
            }
        }, $scope.reverse);
    }

    $('#sidebar').affix({ offset: { top: 0 } });
    $('#grid').tooltip({ placement: "top" });
    $('#card').tooltip({ placement: "top" });
    $('#list').tooltip({ placement: "top" });
    $scope.lvideos();
    $scope.order(2, true);
}]);


videoApp.controller('LandingPageCtrl', ['$scope', '$filter', '$http', '$location', '$stateParams', 'Directory', '$state', '$anchorScroll', 'cfpLoadingBar',
    function($scope,$filter, $http, $location, $stateParams, Directory, $state, $anchorScroll, cfpLoadingBar) {
    var _onloadOp;
    $scope.query = '';
    $scope.results = [];
    $scope.results_pre = [];
    $scope.departmentData = [];
    $scope.showgrid=false;
    $scope.showlist=false;
    $scope.showcard=true;
    $scope.noSearchDone=false;
    $scope.titleclicked=false;
    $scope.presenterclicked=false;
    $scope.sortReverse  = false;

    var orderBy = $filter('orderBy');
    
    $scope.isCurrentGroup = function(group){
        return (group === 'Search-Results') ? true : false;
    }

    $scope.order = function(index) {
      $scope.predicate = index;
      $scope.reverse = ($scope.predicate === index) ? !$scope.reverse : false;
      // $scope.results = orderBy($scope.results, function(obj){  return obj[index] }, $scope.reverse);
      $scope.results = orderBy($scope.results, function(obj){  
            switch(index){
                case 1: return obj[index];
                case 4: return obj[index];
                case 3: return obj[7];
                case 2: return new Date(obj[index].replace(/-/g, '/'));
            }
        }, $scope.reverse);
    }

    $scope.order_pre = function(index) {
      $scope.predicate_pre = index;
      $scope.reverse_pre = ($scope.predicate_pre === index) ? !$scope.reverse_pre : false;
      $scope.results_pre = orderBy($scope.results_pre, function(obj){  
            switch(index){
                case 1: return obj[index];
                case 4: return obj[index];
                case 3: return obj[7];
                case 2: return new Date(obj[index].replace(/-/g, '/'));
            }
        }, $scope.reverse_pre);
    }

    $scope.search = function(firstLoad){
        if(!firstLoad){
            $state.go('landingPage', {query: $scope.query}, {notify: false});
        }
        $scope.noSearchDone=true;
        cfpLoadingBar.start();
        Directory.search($scope.query)
                 .then(function(result){
                        $scope.results = result.data;
                        if($scope.results.length>0){
                            $scope.titleclicked=true;
                            $scope.presenterclicked=false;
                            $scope.isDeptSelected = function(dept){ 
                                return (dept === "Title") ? true : false;
                            }
                        }
                 })
        Directory.search_pre($scope.query)
                 .then(function(result_pre){
                        $scope.results_pre = result_pre.data;
                        if($scope.results_pre.length>0){
                            $scope.titleclicked=false;
                            $scope.presenterclicked=true;
                            $scope.isDeptSelected = function(dept){ 
                                return (dept === "Presenter") ? true : false;
                            }
                        }
                 })        
        firstLoad = false;
        $scope.showdiv = false ;
        cfpLoadingBar.complete();
    }

    $scope.scrollToSearch = function(id) {
        var old=$location.hash();
        if($scope.showgrid) {
            if(id=="Title") {
                $scope.isDeptSelected = function(dept){ 
                    return (dept === "Title") ? true : false;
                }
                id="TitleGrid";
                $scope.titleclicked=true;
                $scope.presenterclicked=false;
            }
            else {
                $scope.isDeptSelected = function(dept){ 
                    return (dept === "Presenter") ? true : false;
                }
                id="PresenterGrid";
                $scope.titleclicked=false;
                $scope.presenterclicked=true;
            }
        }
        
        if($scope.showlist) {

            if(id=="Title") {
                $scope.isDeptSelected = function(dept){ 
                    return (dept === "Title") ? true : false;
                }
                id="TitleList";
                $scope.titleclicked=true;
                $scope.presenterclicked=false;
            }
            else {
                $scope.isDeptSelected = function(dept){ 
                    return (dept === "Presenter") ? true : false;
                }
                id="PresenterList";
                $scope.titleclicked=false;
                $scope.presenterclicked=true;
            }
        }
        if($scope.showcard) {
            if(id=="Title") {
                $scope.isDeptSelected = function(dept){ 
                    return (dept === "Title") ? true : false;
                }
                id="TitleCard";
                $scope.titleclicked=true;
                $scope.presenterclicked=false;
            }
            else {
                $scope.isDeptSelected = function(dept){ 
                    return (dept === "Presenter") ? true : false;
                }
                id="PresenterCard";
                $scope.titleclicked=false;
                $scope.presenterclicked=true;
            }
        }
        $location.hash(id);
        $anchorScroll.yOffset = 100;
        $anchorScroll();
        $location.hash(old);    
    };

    _onloadOp = function(){
        $scope.query = $stateParams.query;
        if($scope.query){
            $scope.search(true);
        }
        $('#grid').tooltip({ placement: "top" });
        $('#card').tooltip({ placement: "top" });
        $('#list').tooltip({ placement: "top" });
        $('#sidebar').affix({ offset: { top: 0 } });
    }
    _onloadOp();
    $scope.order(2, true);
    $scope.order_pre(2, true);

}]);

