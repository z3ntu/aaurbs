var app = angular.module('aaurbsApp', ['ngRoute', 'ui.bootstrap', 'ngAnimate']);

app.config(function ($routeProvider) {
    $routeProvider.when('/', {
        templateUrl: "/snippets/home.html"
    }).when('/:templatePath', {
        template: '<ng-include src="templatePath" />',
        controller: 'CatchAllCtrl'
    });
});

app.config(['$locationProvider', function ($locationProvider) {
    $locationProvider.hashPrefix('');
}]);

app.controller("CatchAllCtrl", function ($scope, $routeParams) {
    $scope.templatePath = "snippets/" + $routeParams.templatePath + ".html";
});

app.controller("HeaderController", function ($scope, $rootScope, $location, $http) {
    $rootScope.update_user_data = function () {
        $http.get("/api/get_user_info").then(function (response) {
            $rootScope.loggedin = response.data.status !== "error";
            $rootScope.user = response.data;
        });
    };
    $scope.navCollapsed = true;
    $scope.isActive = function (viewLocation) {
        return viewLocation === $location.path();
    };
    $rootScope.update_user_data();

    $scope.logout = function () {
        $http.post("/api/logout", null).then(function () {
            $rootScope.loggedin = false;
            $rootScope.user = null;
            $location.path("/");
        });
    };
    $rootScope.$on("$routeChangeError", function () {
        console.log("failed to change routes");
    });
});

app.controller("ProfileController", function ($scope, $rootScope, $http) {
    $rootScope.roles = ["Administator", "Guest"];
    $http.get("/api/get_user_info").then(function (response) {
        if (response.data.status === "error") {
            $scope.error_message = response.data.error_message;
        } else {
            $scope.user = response.data;
        }
    });
});

app.controller("CheckOrphanController", function ($scope, $rootScope, $http) {
    $http.get("/api/check_orphans").then(function (response) {
        $scope.packages = response.data;
        console.log(response.data);
    });
});

app.controller("PackagesController", function ($scope, $rootScope, $http, $uibModal) {
    $rootScope.reasons = ["Unknown", "Success", "Unknown error!", "A failure occurred in check().", "Missing dependencies.", "Validity check failed.", "PGP signature verification failed."];
    $scope.sortField = 'package_name';
    $scope.reverse = false;
    $http.get("/api/get_packages").then(function (response) {
        $scope.packages = response.data;
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
                $scope.packages.forEach(function (element, index) {
                    if (element.package_name === return_array[1]) {
                        $scope.packages.splice(index, 1);
                    }
                });
            }
        }, angular.noop);
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
        $http.get("/api/get_build_log", {params: {package_name: $scope.package.package_name}}).then(function (response) {
            $scope.build_log = response.data;
            $scope.isCollapsed = false;
        });
    };
    $scope.remove_dialog = function (package_name) {
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
        }, angular.noop);
    };
});

app.controller("ConfirmationDialogController", function ($scope, $uibModalInstance, $http, package_name) {
    $scope.package_name = package_name;
    $scope.cancel = function () {
        $uibModalInstance.close(false);
    };
    $scope.remove = function (package_name) {
        console.log("Removing package '" + package_name + "'.");
        $http.post("/api/remove_package", {"package_name": package_name}).then(function (response) {
            if (response.data.status === "error") {
                $scope.response = "Error while removing package: " + response.data.error_message;
            } else {
                console.log("Package '" + package_name + "' was successfully removed.");
                $uibModalInstance.close([true, package_name]);
            }
        });
    }
});

app.controller("AddPackageController", function ($scope, $http, $timeout, $sce) {
    $scope.valid_package = false;
    $scope.add_package = function (package_name) {
        if ($scope.valid_package !== true) {
            $scope.response = "Invalid package.";
            return;
        }
        $http.post("/api/add_package", {"package_name": package_name}).then(function (response) {
            if (response.data.status === "error") {
                $scope.response = "Error while adding package: " + response.data.error_message;
            } else {
                $scope.response = "Package '" + package_name + "' was successfully added.";
                $scope.package_name = "";
            }
        });
    };
    $scope.change_handler = function (input) {
        if ($scope.timeout !== null) {
            $timeout.cancel($scope.timeout);
        }
        if (!input) {
            $scope.valid_package = false;
            return;
        }
        $scope.timeout = $timeout(function () {
            $http.jsonp($sce.trustAsResourceUrl("https://aur.archlinux.org/rpc/"), {
                params: {
                    v: "5",
                    type: "info",
                    "arg[]": input
                }
            }).then(function (response) {
                $scope.timeout = null;
                $scope.valid_package = response.data.resultcount !== 0;
            });
        }, 300);

    }
});

app.controller("RegisterController", function ($scope, $http) {
    $scope.register_user = function (username, pw) {
        $http.post("/api/register", {"username": username, "pw": pw}).then(function (response) {
            if (response.data.status === "error") {
                $scope.response = "Error while registering: " + response.data.error_message;
            } else {
                $scope.response = "User '" + username + "' was successfully registered.";
                $scope.success = true;
                $scope.username = "";
                $scope.pw = "";
            }
        });
    }
});

app.controller("LoginController", function ($scope, $http, $location, $rootScope) {
    $scope.login = function (username, pw) {
        $http.post("/api/login", {"username": username, "pw": pw}).then(function (response) {
            if (response.data.status === "error") {
                $scope.response = "Error while logging in: " + response.data.error_message;
            } else {
                $scope.response = "You were successfully logged in.";
                $rootScope.update_user_data(); // set $rootScope.user to the user object
                $location.path("profile"); // redirect to profile
            }
        });
    }
});
