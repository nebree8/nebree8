var display = angular.module('nebree8.display', ['ngMaterial']);
var DisplayCtrl = function($http, $interval) {
  this.$http = $http;
  this.queue = [];
  this.updateQueue();
  $interval(angular.bind(this, this.updateQueue), 50000);
};

DisplayCtrl.prototype.updateQueue = function() {
  this.$http.get('/order-queue-test.json').then(angular.bind(this, function(resp) {
    this.queue = resp.data;
  }));
}
  
display.controller('DisplayCtrl', DisplayCtrl);
