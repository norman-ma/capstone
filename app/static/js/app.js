var angular.module("newTitle",[])
app.controller("NTCtrl",function($scope,$http){
    $scope.submit=function(){
        // $scope.title
        // $scope.subtitle
        // $scope.authorF
        // $scope.authorL
        // $scope.desc
        
        $scope.data={$scope.title, scope.subtitle, $scope.authorF, $scope.authorL, $scope.desc};
        $scope.url='/title/new';
        
        $http({
            method:"GET",
            url:$scope.url,
            data:$scope.data
        }).then (function(){
            console.log("success");
        });
    };
});