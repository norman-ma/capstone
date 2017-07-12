var app = angular.module("TitleManagementApp",[]);

app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('/#');
    $interpolateProvider.endSymbol('#/');
}]);

app.controller("InProgressController", ["$scope","TitleService","$window",function($scope,TitleService,$window){
    
    $scope.get = function(role){
        
        var settings = {};
        
        if(role === "GeneralManager"){
            settings.state = "";
            settings.stage = "";
        }else if(role ==="LeadEditor" || role === "PublishingAssistant"){
            settings.state = "IN PROGRESS";
            settings.stage = "EditorialProduction";
        }else if(role === "MarketingManager" || role === "MarketingOfficer"){
            settings.state = "IN PROGRESS";
            settings.stage = "SalesMarketing";
        }else{
            settings.state = "";
            settings.stage = "";
        }
        
        TitleService.get(settings)
            .then(function(result){
                $scope.titles = result;
                console.log($scope.titles);
            });
        
    };
    
    $scope.go = function(id){
        $window.location.href = '/title/'+id;
    };
}]);

app.factory("TitleService",["$http",function($http){
    
    var TitleService = {};
    
    TitleService.get= function(settings){
        return $http
            .post('/api/titles',settings)
            .then(function(res){
                console.log(res);
                if(res.data.error == null){
                    return res.data.data;
                }
            });
    };
    
    return TitleService;
}]);