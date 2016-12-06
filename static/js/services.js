videoApp.factory('Directory', function($http){

    var Service = {};

    Service['search'] = function(query){
        var url = 'search.json?query='+query;
        return $http.get(url)
    };

    Service['search_pre'] = function(query){
        var url = 'search_pre.json?query='+query;
        return $http.get(url)
    };

    Service['latestVideos'] = function(stdate,enddate,searchval){
        var url = '/lVideos';
        return $http.get(url,{params: {stdate: stdate,enddate: enddate,searchval: searchval}})
    };

    Service['getDept'] = function(){
        var url = '/Departments';
        return $http.get(url)
    };

    Service['getVideos'] = function(dept,searchval){
        var url = '/Videos';
        return $http.get(url,{params: {dept: dept,searchval: searchval}})
    };

    return Service;
})
