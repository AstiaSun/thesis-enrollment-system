angular.module('myApp')
  .controller('MainController', ['$scope', '$rootScope', '$http', function($scope, $rootScope, $http) {
  $scope.showInstructor = $rootScope.user.role == 'instructor';
  $http.get('/api/user').then(
        function(response){
            var data = response.data;
            $rootScope.user = data;
            console.log(data);
            $scope.showInstructor = $rootScope.user.role == 'instructor';
        },
        function(){
            console.log('error getting user data');
        }
    );

    $scope.currentYear = new Date().getFullYear();

    $scope.thesis_name = '';
    $scope.description = '';
    $scope.year = $scope.currentYear + '';
    $scope.difficulty = '1';
    $scope.tags = '';

    $scope.onSubmit = function(){
        var data = {
            thesis_name: $scope.thesis_name,
            description: $scope.description,
            year: $scope.year,
            difficulty: $scope.difficulty,
            tags: $scope.tags
        }
        $http.post('/api/thesis/add', data).then(
            function(response){
                console.log(response);
            },
            function(response){
                console.log(response);
            }
        )
    };
  }]);