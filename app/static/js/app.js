var app = angular.module("TitleManagementApp",[]);

app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('/#');
    $interpolateProvider.endSymbol('#/');
}]);

app.controller("ParentController",["$scope","$window",function($scope,$window){
    
    $scope.go = function(url){
        $window.location.href = url;
    };
    
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
    
    $scope.go = function(url){
        console.log(url);
        $scope.$parent.go(url);
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

app.controller('ActivityListController',["$scope","ActivityService",function($scope,ActivityService){
    
    $scope.get = function(titleid,complete,current){
        var settings = {};
        settings.complete = complete;
        settings.current = current;
        
        ActivityService.get(titleid,settings)
            .then(function(result){
                $scope.activities = result;
                console.log($scope.activities);
            });
    };
}]);

app.factory('ActivityService',["$http",function($http){
    
    var ActivityService = {};
    
    ActivityService.get = function(titleid,settings){
        return $http
            .post('/api/'+titleid+'/activity',settings)
            .then(function(res){
                console.log(res);
                if(res.data.error == null){
                    return res.data.data;
                }
            });
    };
    
    return ActivityService;
}]);

app.controller('ResourceListController',["$scope","ResourceService",function($scope,ResourceService){
    
    $scope.get = function(activityid){
        ResourceService.get(activityid)
            .then(function(result){
                $scope.humanresources = result.human;
                $scope.materialresources = result.material;
                console.log($scope.activities);
            });
    };
}]);

app.factory('ResourceService',["$http",function($http){
    
    var ResourceService = {};
    
    ResourceService.get = function(activityid){
        return $http
            .get('/api/'+activityid+'/resources')
            .then(function(res){
                console.log(res);
                if(res.data.error == null){
                    return res.data.data;
                }
            });
    };
    
    return ResourceService;
}]);

app.controller('MilestoneController',["$scope","MilestoneService","$sce",function($scope,MilestoneService,$sce){
    
    $scope.get = function(titleid){
        MilestoneService.get(titleid)
            .then(function(result){
                $scope.milestones = result;
                console.log($scope.milestones);
            });
    };
    
    $scope.new = false;
    
    $scope.togglenew = function(){
        $scope.new = !$scope.new;
    };
    
    $scope.edit = false;
    
    $scope.toggleedit = function(titleid,milestone){
        $scope.milestone = milestone;
        $scope.url = $sce.trustAsUrl('/api/'+titleid+'/milestone/'+milestone.id+'/edit');
        $scope.edit = !$scope.edit;
    };
    
    
}]);

app.factory('MilestoneService',["$http",function($http){
    
    var MilestoneService = {};
    
    MilestoneService.get = function(titleid){
        return $http
            .get('/api/'+titleid+'/milestones')
            .then(function(res){
                console.log(res);
                if(res.data.error == null){
                    return res.data.data;
                }
            });
    };
    
    MilestoneService.new = function(titleid,data){
        return $http
            .post('/api/'+titleid+'/milestone/new',data)
            .then(function(res){
                console.log(res);
                if(res.data.error == null){
                    return res.data.data;
                }
            });
    };
    
    return MilestoneService;
}]);

app.controller("PhaseController",["$scope","PhaseService",function($scope,PhaseService){
    
    $scope.show = false;
    
    $scope.toggleshow = function(){
        $scope.show = !$scope.show;
    };
    
    $scope.next = function(titleid,current){
        var settings = {};
        
        console.log(titleid,current);
        
        if(current === 'Acquisition'){
            settings.next = "EditorialProduction";
        }else if(current === 'EditorialProduction'){
            settings.next = "SalesMarketing";
        }else{
            settings.next = null;
        }
        
        PhaseService.next(titleid,settings)
            .then(function(res){
                return res;
            });
    };
    
}]);

app.factory("PhaseService",["$http",function($http){
    
    var PhaseService = {};
    
    PhaseService.setBudget = function(phaseid,budget){
        var settings = {};
        settings.budget = budget;
        
        return $http
            .post("/api/phase/"+phaseid+"/budget",settings)
            .then(function(res){
                return res;
            });
    };
    
    PhaseService.next = function(titleid,settings){
        return $http
            .post("/api/"+titleid+"/stage/next",settings)
            .then(function(res){
                console.log(res);
                if(res.data.error == null){
                    return res.data.data;
                }
            });
    };
    return PhaseService;
}]);

app.controller("FileController",["$scope","$FileService",function($scope,FileService){
    
    $scope.delete = function(titleid,file){
        FileService.delete(titleid,file)
            .then(function(res){
                return res;
            });
    };
    
    
}]);

app.factory("FileService",["$http",function($http){
    
    var FileService = {};
    
    FileService.delete = function(titleid,file){
        return $http
            .delete("/api/"+titleid+"/files/"+file+"delete")
            .then(function(res){
                console.log(res);
                if(res.data.error == null){
                    return res.data.data;
                }
            });
    };
    
    return FileService;
    
}]);    

app.controller("StandardController",["$scope",function($scope){
    
    $scope.show = false;
    
    $scope.toggleshow = function(){
        $scope.show = !$scope.show;
    };
    
}]);

app.controller("SearchController",["$scope","$sce",function($scope,$sce){
    
    $scope.keyword = '';
    
    $scope.url = function(){
        return  $sce.trustAsUrl('/search?keyword='+$scope.keyword);
    };
    
}]);