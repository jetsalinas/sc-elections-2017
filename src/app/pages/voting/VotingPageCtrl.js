/**
 * @author v.lugovsky
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.voting')
      .controller('VotingPageCtrl', VotingPageCtrl);

  /** @ngInject */
  function VotingPageCtrl($scope, Credentials, CandidatesList, toastr, toastrConfig, $timeout, $http, $uibModal) {
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
    $scope.clearance = Credentials.getClearance();
    $scope.candidates = CandidatesList.getProperty();
    $scope.choices = {
      president: -1,
      vicePresident: -1,
      secretary: -1,
      treasurer: -1,
      auditor: -1,
    }

    $scope.stringifyChoices = function () {
      $scope.choicesString = {
        president: $scope.candidates.president[$scope.choices.president],
        vicePresident: $scope.candidates.vicePresident[$scope.choices.vicePresident],
        secretary: $scope.candidates.secretary[$scope.choices.secretary],
        treasurer: $scope.candidates.treasurer[$scope.choices.treasurer],
        auditor: $scope.candidates.auditor[$scope.choices.auditor],
      }
    }

    $scope.vote = function (index, variable) {
      $scope.choices.variable = index;
    }

    $scope.cancelVote = function (index, variable) {
      $scope.choices.variable = -1;
    }

    $scope.finishVoting = function () {
      $scope.stringifyChoices();
      $uibModal.open({
        animation: true,
        templateUrl: 'app/pages/voting/votePages/finishVoting.html',
        size: 'lg',
        resolve: {
          items: function () {
            return $scope.items;
          }
        },
      });
    }

    $scope.progressFunction = function() {
      return $timeout(function() {}, 2000);
    }

    $scope.submit = function () {
      var data = {
        credentials: Credentials.getProperty(),
        votes: $scope.choices,
      }
      $http.post('http://localhost:3000', data).success(function(data, status, headers, config) {
        Credentials.clearProperties();
        $stage.go('dashboard');
        toastr.success('We have successfully transmitted your vote to the server. Thank you for voting.', 'Vote Transmitted', {
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
        });
      }).error(function(data, status, headers, config) {
        console.log(
          "Unable to Send Data: " +
          JSON.stringify(data)
        );
        toastr.error('We were unable to transmit your vote to the server. Please try again in a moment.', 'Transmission Error', {
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
      });
    }
  }

})();
