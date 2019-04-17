angular.module('myApp')
  .controller('HeaderController', ['$scope', '$location', function($scope, $location) {
    $scope.name = 'KekHub';
    $scope.location = $location;
  }]);