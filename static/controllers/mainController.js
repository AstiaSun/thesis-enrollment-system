angular.module('myApp')
  .controller('MainController', ['$scope', '$rootScope', '$http', function($scope, $rootScope, $http) {

  $scope.nonstop_thesis = [];

    $scope.refreshAll = function(){
    if(!$rootScope.user){
        return $scope.requestdo();
    }
    console.log('Hello, thesis: ' + $rootScope.user.thesis_id);
            $scope.showInstructor = $rootScope.user.role == 'instructor';
            $scope.showStudent = $rootScope.user.role == 'student';
            $scope.showStudentThesis = $scope.showStudent && $rootScope.user.thesis_id;
            $scope.showStudentNoThesis = $scope.showStudent && !$rootScope.user.thesis_id;
            $scope.my_thesis = $rootScope.user.thesis_id;
            if($scope.showStudent){
                $http.get('/api/thesis/all').then(
                    function(response){
                        var data = response.data;
                        $scope.nonstop_thesis = data;
                        $scope.nonstop_thesis_my = $scope.nonstop_thesis.filter(
                            function(item){return item.thesis_name==$scope.my_thesis});
                    },
                    function(){
                        console.log('error getting thesis data');
                    }
                );
              }
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

    $scope.thesis_name = '';
    $scope.description = '';
    $scope.year = '1';
    $scope.difficulty = '1';
    $scope.tags = '';
    $scope.my_thesis = '';
    $scope.nonstop_thesis_my = [];

    $scope.onSubmitAddThesis = function(){
        var data = {
            thesis_name: $scope.thesis_name,
            description: $scope.description,
            year: parseInt($scope.year),
            difficulty: parseInt($scope.difficulty),
            tags: $scope.tags
        }
        $http.post('/api/thesis/add', data).then(
            function(response){
                console.log(response);
            },
            function(response){
                console.log(response);
            }
        );
    };

    $scope.onSubmitEnrol = function(thesis_name){
        var data = {
            thesis_name: thesis_name
        };
        $scope.my_thesis = thesis_name;
        $http.post('/api/thesis/enrol', data).then(
            function(response){
                $rootScope.user = response.data;

                $scope.requestdo();
            },
            function(response){
                console.log(response);
            }
        );
    };
    $scope.requestdo();
  }]);