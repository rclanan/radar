(function() {
  'use strict';

  var app = angular.module('radar.form');

  app.directive('rrDialysisEditor', function() {
    return {
      restrict: 'A',
      scope: {
        patient: '='
      },
      templateUrl: 'app/dialysis/dialysis-editor.html',
      controller: 'DialysisEditorController'
    };
  });

  app.controller('DialysisEditorController', function($scope, DialysisService, DialysisTypeService, lodash, humps, $q, $timeout, $filter) {
    $scope.search = '';
    $scope.sortBy = 'id';
    $scope.reverse = false;
    $scope.page = 1;
    $scope.perPage = 3;

    DialysisService.getList($scope.patient.id).then(function(items) {
      $scope.items = items;
    });

    DialysisTypeService.getDialysisTypes().then(function(dialysisTypes) {
      $scope.dialysisTypes = dialysisTypes;
    });

    $scope.$watchCollection('items', filter);
    $scope.$watch('search', filter);
    $scope.$watchCollection('filteredItems', sort);
    $scope.$watch('sortBy', sort);
    $scope.$watch('reverse', sort);
    $scope.$watchCollection('sortedItems', paginate);
    $scope.$watch('page', paginate);
    $scope.$watch('perPage', paginate);

    var original = null;

    $scope.save = save;
    $scope.edit = edit;
    $scope.remove = remove;
    $scope.cancel = cancel;
    $scope.modified = modified;

    create();
    filter();
    sort();
    paginate();

    function create() {
      original = DialysisService.create({
        patientId: $scope.patient.id
      });
      $scope.item = angular.copy(original);
    }

    function edit(item) {
      original = item;
      $scope.item = angular.copy(item);
    }

    function remove(item) {
      if (item === original) {
        $scope.form.$setPristine();
        create();
      }

      var deferred = $q.defer();

      $timeout(function() {
        item.$delete().then(function() {
          lodash.pull($scope.items, item);
          deferred.resolve();
        });
      }, 1000);

      return deferred.promise;
    }

    function cancel() {
      $scope.form.$setPristine();
      create();
    }

    function modified() {
      return $scope.form.$dirty && !angular.equals(original, $scope.item);
    }

    function filter() {
      var filteredItems = $scope.items;

      if ($scope.search) {
        filteredItems = $filter('filter')(filteredItems, $scope.search);
      }

      $scope.filteredItems = filteredItems;
    }

    function save() {
      var savedOriginal = original;

      $scope.errors = {};

      $scope.item.$save().then(function(item) {
        if (!savedOriginal.id) {
          $scope.items.push(savedOriginal);
        }

        angular.copy(item, savedOriginal);

        $scope.form.$setPristine();

        create();
      }, function(response) {
        if (response.status === 422) {
          $scope.errors = humps.camelizeKeys(response.data.errors);
        }
      });
    }

    function sort() {
      $scope.page = 1;

      var sortedItems = lodash.sortBy($scope.filteredItems, $scope.sortBy);

      if ($scope.reverse) {
        sortedItems.reverse();
      }

      $scope.sortedItems = sortedItems;
    }

    function paginate() {
      var startIndex = ($scope.page - 1) * $scope.perPage;
      var endIndex = $scope.page * $scope.perPage;
      $scope.paginatedItems = lodash.slice($scope.sortedItems, startIndex, endIndex);
    }
  });
})();
