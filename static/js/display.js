var display = angular.module('nebree8.display', ['ngMaterial']);
var DisplayCtrl = function($http, $interval) {
  this.$http = $http;
  this.finished_drink = null;
  this.current_drink = null;
  this.queue = [];
  this.updateQueue();
  $interval(angular.bind(this, this.updateQueue), 1000);
};

DisplayCtrl.prototype.updateQueue = function() {
  this.$http.get('/order-queue.json').then(angular.bind(this, function(resp) {
    this.finished_drink = resp.data.finished_drink;
    this.current_drink = resp.data.current_drink;
    this.queue = resp.data.queue;
  }));
}
  
display.controller('DisplayCtrl', DisplayCtrl);

