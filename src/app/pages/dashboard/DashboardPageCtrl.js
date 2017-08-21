/**
 * @author v.lugovsky
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.dashboard')
      .controller('DashboardPageCtrl', DashboardPageCtrl);

  /** @ngInject */
  function DashboardPageCtrl($scope, $http, Credentials, CandidatesList, toastr, toastrConfig) {
    $scope.clearance = false;
    $scope.options = {
      "autoDismiss": false,
      "positionClass": "toast-bottom-right",
      "type": "success",
      "timeOut": "5000",
      "extendedTimeOut": "2000",
      "allowHtml": false,
      "closeButton": true,
      "tapToDismiss": false,
      "progressBar": false,
      "newestOnTop": false,
      "maxOpened": 0,
      "preventDuplicates": false,
      "preventOpenDuplicates": true
    }
    angular.extend(toastrConfig, $scope.options);
    $scope.login = function () {
      var data = {
        username : $scope.inputUsername,
        password : $scope.inputPassword
      };
      Credentials.setProperty($scope.inputUsername, $scope.inputPassword);
      $http.post('http://localhost:3000', data).success(function(data, status, headers, config) {
        CandidatesList.setProperty(data);
        Credentials.setClearance(true);
        $scope.clearance=true;
        $state.go('voting');
        toastr.success('You have been successfully logged in and redirected to the voting page.', 'Log-in Successful');
      }).error(function(data, status, headers, config) {
        $scope.clearance=false;
        toastr.error('You are either having trouble connecting to the server or your username/password is incorrect.', 'Log-in Error', {
          "autoDismiss": false,
          "positionClass": "toast-bottom-right",
          "type": "error",
          "timeOut": "5000",
          "extendedTimeOut": "2000",
          "allowHtml": false,
          "closeButton": true,
          "tapToDismiss": false,
          "progressBar": false,
          "newestOnTop": false,
          "maxOpened": 0,
          "preventDuplicates": false,
          "preventOpenDuplicates": true
        });
        console.log(
          "Unable to Send Data: " +
          JSON.stringify(data)
        );
      });
    }
    
    $scope.logout = function () {
      Credentials.clearProperties();
      $scope.clearance = false;
      $stage.reload();
    }
  }
})();
