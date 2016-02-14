var app = angular.module('aaurbsApp', ['ngRoute', 'ui.bootstrap']);

app.config(function ($routeProvider) {
    $routeProvider.when('/', {
        templateUrl: "/snippets/home.html"
    }).when('/:templatePath', {
        template: '<ng-include src="templatePath" />',
        controller: 'CatchAllCtrl'
    });
});

app.controller("CatchAllCtrl", function ($scope, $routeParams) {
    $scope.templatePath = "snippets/" + $routeParams.templatePath + ".html";
});

app.controller("HeaderController", function($scope, $location, $http) {
    $scope.isActive = function(viewLocation) {
        return viewLocation === $location.path();
    };
    $http.get("/api/get_user_info").success(function(data) {
        $scope.loggedin = !data.error;
    });
    $scope.logout = function() {
        console.log("logout");
        $http.post("/api/logout", null);
        $scope.loggedin = false;
    };
});

app.controller("ProtectedController", function($scope, $http) {
    $http.get("/api/get_user_info").success(function(data) {
       $scope.user = data;
    });
});

app.controller("PackagesController", function($scope, $http) {
    $http.get("/api/get_packages").success(function(data) {
        $scope.packages = data;
    });
});

app.controller("AddPackageController", function($scope, $http) {
   $scope.add_package = function(package_name) {
       console.log("add_package '" + package_name + "'");
       $http.post("/api/add_package", {"package_name": package_name}).success(function(data) {
           if(data.status == "error") {
               console.log("Error");
               $scope.response = "Error while adding package: " + data.error_message;
           } else {
               console.log("Ok");
               $scope.response = "Package '" + package_name + "' was successfully added."
           }
       });
   }
});

app.controller("RegisterController", function($scope, $http) {
   $scope.register_user = function(username, pw) {
       console.log(username + " - " + pw);
       $http.post("/api/register", {"username": username, "pw": pw}).success(function(data) {
           console.log(data);
       });
   }
});

/*
app.factory("user_factory", function($http) {
    var user;
    return {
        setUser : function(aUser) {
            user = aUser;
        },
        isLoggedIn : function() {
            return(user)? user : false;
        }
    }
});*/
