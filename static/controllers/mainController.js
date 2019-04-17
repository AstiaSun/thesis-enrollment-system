angular.module('myApp')
  .controller('MainController', ['$scope', '$rootScope', '$http', function($scope, $rootScope, $http) {
  $scope.showInstructor = $rootScope.user.role == 'instructor';
  $scope.showStudent = $rootScope.user.role == 'student';
  $scope.showStudentThesis = $scope.showStudent && $rootScope.user.thesis_id;
  $scope.showStudentNoThesis = !$scope.showStudentThesis;

  $scope.nonstop_thesis = [];

  if($scope.showStudentNoThesis){
    $http.get('/api/thesis/all').then(
        function(response){
            var data = response.data;
            $scope.nonstop_thesis = data;
            console.log(data);
        },
        function(){
            console.log('error getting thesis data');
        }
    );
  }

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

    $scope.thesis_name = '';
    $scope.description = '';
    $scope.year = '1';
    $scope.difficulty = '1';
    $scope.tags = '';

    $scope.onSubmitAddThesis = function(){
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