'use strict';

angular.module('BlurAdmin', [
  'ngAnimate',
  'ui.bootstrap',
  'ui.sortable',
  'ui.router',
  'ngTouch',
  'toastr',
  'smart-table',
  "xeditable",
  'ui.slimscroll',
  'ngJsTree',
  'angular-progress-button-styles',

  'BlurAdmin.theme',
  'BlurAdmin.pages' 
]).service('Credentials', function () {
    var Credentials = {
      username: '',
      password: '',
    }
    var Clearance = false;
    return {
      getProperty: function () {
        return Credentials;
      },
      setProperty: function(value1, value2) {
        Credentials.username = value1;
        Credentials.password = value2;
      },
      clearProperties: function () {
        Credentials.username = '';
        Credentials.password = '';
        Clearance = false;
      },
      setClearance: function (value) {
        Clearance = value;
      },
      getClearance: function () {
        return Credentials.clearance;
      }
  };
}).service('CandidatesList', function($http) {
    var candidatesList = {}
    return {
      getProperty: function () {
        return candidatesList;
      },
      setProperty: function (value) {
        $http.post('http://localhost:3000', value).then(function(data) {
          candidatesList = data;
        });
      }
    }
});