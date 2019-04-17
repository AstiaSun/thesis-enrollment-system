angular.module('myApp')
  .controller('ProfileController', ['$scope', '$rootScope', '$http', function($scope, $rootScope, $http) {
    $scope.first_name = '';
    $scope.middle_name = '';
    $scope.last_name = '';
    $scope.email = '';
    $scope.password = '';

    $scope.onSubmit = function(){
        var data = {
            first_name: $scope.first_name,
            middle_name: $scope.middle_name,
            last_name: $scope.last_name,
            email: $scope.email,
        }
        if($scope.password){
            data.password = $scope.password;
        }
        console.log(data);
        $http.post('/api/profile/update', data).then(
            function(response){
            console.log(response.data);
                $rootScope.user = response.data;
                $scope.first_name = $rootScope.user.first_name;
                $scope.middle_name = $rootScope.user.middle_name;
                $scope.last_name = $rootScope.user.last_name;
                $scope.email = $rootScope.user.email;
                $scope.password = '';
            },
            function(response){
                console.log(response);
            }
        );
    };
    $scope.refreshAll = function(){
    if(!$rootScope.user){
        return $scope.requestdo();
    }
        $scope.first_name = $rootScope.user.first_name;
                $scope.middle_name = $rootScope.user.middle_name;
                $scope.last_name = $rootScope.user.last_name;
                $scope.email = $rootScope.user.email;
                $scope.password = '';
    }
    $scope.requestdo = function(){
  $http.get('/api/user').then(
        function(response){
            var data = response.data;
            $rootScope.user = data;
            console.log(data);
            $scope.refreshAll();
        },
        function(){
            console.log('error getting user data');
        }
    );};

    $scope.requestdo();
  }]);