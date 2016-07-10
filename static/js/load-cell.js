var data = [[0, 0], [0, 0]];
var graph;
var line;
var x;
var y;
var avg_elt = document.getElementById('avg');
var std_dev_elt = document.getElementById('stddev');

/* implementation heavily influenced by http://bl.ocks.org/1166403 */

// define dimensions of graph
var m = [40, 40, 40, 40]; // margins
var w = 500 - m[1] - m[3]; // width
var h = 300 - m[0] - m[2]; // height

// create a simple data array that we'll plot with a line (this array represents only the Y values, X will just be the index location)
// var data = read in using /load_cell.json

function get_x(tup) { return tup[0]; }
function get_y(tup) { return tup[1]; }

var x = d3.scale.linear().domain(d3.extent(data.map(get_x))).range([0, w]);
var y = d3.scale.linear().domain(d3.extent(data.map(get_y))).range([h, 0]);
  // automatically determining max range can work something like this
  // var y = d3.scale.linear().domain([0, d3.max(data)]).range([h, 0]);

// create a line function that can convert data[] into x and y points
line = d3.svg.line()
  // assign the X function to plot our line as we wish
  .x(function(d,i) { return x(d[0]); })
  .y(function(d) { return y(d[1]); })

  // Add an SVG element with the desired dimensions and margin.
  var graph = d3.select("#graph").append("svg:svg")
        .attr("width", w + m[1] + m[3])
        .attr("height", h + m[0] + m[2])
      .append("svg:g")
        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

  // create yAxis
  var xAxis = d3.svg.axis().scale(x).tickSize(-h).tickSubdivide(true);
  // Add the x-axis.
  graph.append("svg:g")
        .attr("class", "x-axis")
        .attr("transform", "translate(0," + h + ")")
        .call(xAxis);


  // create left yAxis
  var yAxisLeft = d3.svg.axis().scale(y).ticks(4).orient("left");
  // Add the y-axis to the left
  graph.select("g")
        .attr("class", "y-axis")
        .attr("transform", "translate(-25,0)")
        .call(yAxisLeft);

  graph.append("svg:path").attr("class", "raw-line");
  graph.append("svg:path").attr("class", "avg-line");
  graph.append("svg:path").attr("class", "med-line");
  function refreshData() {
    d3.json("/load_cell.json", function(error, json) {
      if (error) return console.warn(error);
      data = json;
      var avg_data = data.map(function (_, i) {
        var s = data.slice(i, i + 50);
        return [data[i][0], d3.sum(s.map(get_y)) / s.length];
      });
      var med_data = data.map(function (_, i) {
        return [data[i][0], d3.median(data.slice(i, i + 50).map(get_y))];
      });
      if (data.length > 50) {
        var s = data.slice(data.length - 50, data.length);
        var avg = d3.sum(s.map(get_y)) / s.length;
        var stddev = Math.sqrt(
            d3.sum(s.map(function(r) { return Math.pow(r[1] - avg, 2); }))
           / (s.length - 1));
        avg_elt.innerHTML = String(avg).substring(0, 6);
        std_dev_elt.innerHTML = String(stddev).substring(0, 4);
      }
      x = d3.scale.linear().domain(d3.extent(data.map(get_x))).range([0, w]);
      y = d3.scale.linear().domain(d3.extent(data.map(get_y))).range([h, 0]);
      graph.select(".y-axis")
            .attr("transform", "translate(-25,0)")
            .call(yAxisLeft);
      graph.select(".x-axis")
            .attr("transform", "translate(0," + h + ")")
            .call(xAxis);
      graph.select(".raw-line")
        .attr("d", line(data));
      graph.select(".avg-line")
        .attr("d", line(avg_data));
      graph.select(".med-line")
        .attr("d", line(med_data));
    });
  }

window.setInterval(function() { refreshData(); }, 800);
