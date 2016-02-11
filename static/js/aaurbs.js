var aaurbsApp = angular.module('aaurbsApp', ['ngRoute']);

aaurbsApp.config(function ($routeProvider) {
    $routeProvider.when('/', {
        templateUrl: 'main.html',
        controller: 'MainController'
    }).when('/:countryId', {
        templateUrl: 'country-detail.html',
        controller: 'CountryDetailCtrl'
    }).otherwise({
        redirectTo: '/'
    });
});