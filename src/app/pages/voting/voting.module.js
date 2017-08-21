/**
 * @author v.lugovsky
 * created on 16.12.2015
 */
(function () {
  'use strict';

  angular.module('BlurAdmin.pages.voting', [])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
        .state('voting', {
          url: '/voting',
          templateUrl: 'app/pages/voting/voting.html',
          title: 'Voting',
          controller: 'VotingPageCtrl',
          sidebarMeta: {
            icon: 'ion-compose',
            order: 10,
          },
        });
  }

})();
