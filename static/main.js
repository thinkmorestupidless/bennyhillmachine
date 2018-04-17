(function () {

  'use strict';

  angular.module('BennyHillApp', [])

  .factory('service', function ($q, $http, $log, $timeout) {

    return {

      start: function(url) {

        var deferred = $q.defer();

        $http.post('/start', {"url": url}).then(
          function(response){
            deferred.resolve(response.data);
          },
          function(error){
            deferred.reject(error);
          });

        return deferred.promise;
      },

      status: function(jobID) {

      	var deferred = $q.defer();

      	var timeout = "";

  	    var poller = function() {
          // fire another request
          $http.get('/results/' + jobID).
            success(function(data, status, headers, config) {
              if(status === 202) {
                // continue to call the poller() function every 2 seconds
                // until the timeout is cancelled
                timeout = $timeout(poller, 2000);
              } else if (status === 200){
                $timeout.cancel(timeout);
                deferred.resolve(data);
              }
              
            }).
            error(function(data, status, headers, config) {
              $deferred.reject(data);
            });
        };

        poller();

        return deferred.promise;
      }
    }
  })

  .controller('BennyHillController', ['$scope', '$log', '$http', '$timeout', '$sce', 'service', function($scope, $log, $http, $timeout, $sce, $service) {
    
    $scope.loading = false;

    $scope.convert = function() {

      $scope.downloadUrl = null;
      $scope.loading = true;
      $scope.errors = null;
      // get the URL from the input
	  var userInput = $scope.input_url;

	  $service.start(userInput).then(
	  		function(response) {
	  			  $log.log(response);
	      		getWordCount(response);
	  		},
	  		function(error) {
	  			  $log.log(error);
            $scope.errors = error;
            $scope.loading = false;
	  		});
    };

    function getWordCount(jobID) {

    	$service.status(jobID).then(
    		function(response) {
				  $scope.downloadUrl = $sce.trustAsResourceUrl(response);
          $scope.loading = false;
    		},
    		function(error) {
    			$log.log(error);
          $scope.errors = error;
          $scope.loading = false;
    		});
	  }
  }

  ]);

}());