var app = angular.module('aaurbsApp', ['ngRoute', 'ui.bootstrap', 'ngAnimate']);

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

app.controller("HeaderController", function ($scope, $rootScope, $location, $http) {
    $scope.isActive = function (viewLocation) {
        return viewLocation === $location.path();
    };
    $http.get("/api/get_user_info").success(function (data) {
        $rootScope.loggedin = data.status != "error";
        $rootScope.user = data;
    });
    $scope.logout = function () {
        $http.post("/api/logout", null).success(function(data) {
            $rootScope.loggedin = false;
            $rootScope.user = null;
            $location.path("/");
        });
    };
});

app.controller("ProfileController", function ($scope, $rootScope, $http) {
    $rootScope.roles = ["Administator", "Guest"];
    $http.get("/api/get_user_info").success(function (data) {
        if (data.status == "error") {
            $scope.error_message = data.error_message;
        } else {
            $scope.user = data;
        }
    });
});

app.controller("PackagesController", function ($scope, $rootScope, $http, $uibModal) {
    $rootScope.reasons = ["Unknown", "Success", "Unknown error!", "A failure occurred in check()."];
    $scope.sortField = 'package_name';
    $scope.reverse = false;
    $http.get("/api/get_packages").success(function (data) {
        $scope.packages = data;
    });

    $scope.openModal = function (package_info) {
        var modalInstance = $uibModal.open({
            templateUrl: 'snippets/package_info_modal.html',
            controller: 'ModalController',
            size: "lg",
            resolve: {
                package_info: function () {
                    return package_info;
                }
            }
        });
        modalInstance.result.then(function (return_array) {
            if (return_array[0]) {
                $scope.packages.forEach(function(element, index) {
                    if (element.package_name == return_array[1]) {
                        $scope.packages.splice(index, 1);
                    }
                });
            }
        });
    }
});

app.controller("ModalController", function ($scope, $rootScope, $http, $uibModalInstance, $uibModal, package_info) {
    $scope.package = package_info;
    $scope.isCollapsed = true;
    $scope.close = function () {
        $uibModalInstance.close([false]);
    };
    $scope.toggle_log = function () {
        if ($scope.log_loaded === true) {
            $scope.isCollapsed = !$scope.isCollapsed;
            return;
        } // fetch the log only the first time
        $scope.log_loaded = true;
        $http.get("/api/get_build_log", {params: {package_name: $scope.package.package_name}}).success(function (data) {
            $scope.build_log = data;
            $scope.isCollapsed = false;
        });
    };
    $scope.remove_dialog = function(package_name) {
        var modalInstance = $uibModal.open({
            templateUrl: 'snippets/confirmation_dialog.html',
            controller: 'ConfirmationDialogController',
            resolve: {
                package_name: function () {
                    return package_name;
                }
            }
        });
        modalInstance.result.then(function (return_array) {
            if (return_array[0]) {
                $uibModalInstance.close(return_array);
            }
        });
    };
});

app.controller("ConfirmationDialogController", function($scope, $uibModalInstance, $http, package_name) {
    $scope.package_name = package_name;
    $scope.cancel = function() {
        $uibModalInstance.close(false);
    };
    $scope.remove = function(package_name) {
        console.log("Removing package '" + package_name + "'.");
        $http.post("/api/remove_package", {"package_name": package_name}).success(function (data) {
            if (data.status == "error") {
                $scope.response = "Error while removing package: " + data.error_message;
            } else {
                console.log("Package '" + package_name + "' was successfully removed.");
                $uibModalInstance.close([true, package_name]);
            }
        });
    }
});

app.controller("AddPackageController", function ($scope, $http) {
    $scope.add_package = function (package_name) {
        $http.post("/api/add_package", {"package_name": package_name}).success(function (data) {
            if (data.status == "error") {
                $scope.response = "Error while adding package: " + data.error_message;
            } else {
                $scope.response = "Package '" + package_name + "' was successfully added."
            }
        });
    }
});

app.controller("RegisterController", function ($scope, $http) {
    $scope.register_user = function (username, pw) {
        $http.post("/api/register", {"username": username, "pw": pw}).success(function (data) {
            if (data.status == "error") {
                $scope.response = "Error while registering: " + data.error_message;
            } else {
                $scope.response = "User '" + username + "' was successfully registered.";
                $scope.success = true;
                $scope.username = "";
                $scope.pw = "";
            }
        });
    }
});

app.controller("LoginController", function($scope, $http, $location, $rootScope) {
    $scope.login = function (username, pw) {
        $http.post("/api/login", {"username": username, "pw": pw}).success(function (data) {
            if (data.status == "error") {
                $scope.response = "Error while logging in: " + data.error_message;
            } else {
                $scope.response = "You were successfully logged in.";
                $rootScope.loggedin = true;
                $location.path("profile"); // redirect to profile
            }
        });
    }
});
