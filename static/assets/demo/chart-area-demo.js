// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';


function getMax(arr) {
  var max;
  for (var i=0 ; i<arr.length ; i++) {
      if (max == null || parseInt(arr[i]) > parseInt(max))
          max = arr[i];
  }
  return parseInt(max) + (max * 0.1);
}

function convertToDate(arr) {
  var dates = [];
  for (var i=0 ; i<arr.length ; i++) {
    var date = new Date(arr[i]*1000);
    var full_date = ""+date.getDate()+"."+(date.getMonth()+1)+"."+date.getFullYear();
    console.log(date.getDate());
    dates.push(full_date);
  }
  console.log(dates)
  return dates;
}
// Area Chart Example
var ctx = document.getElementById("myAreaChart");
var data = document.getElementById("myAreaChart").dataset.prices;
var labels = document.getElementById("myAreaChart").dataset.labels;
data = JSON.parse(data);
labels = JSON.parse(labels);
var max_value = getMax(data);
var dates = convertToDate(labels);

var myLineChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: dates,
    datasets: [{
      label: "Preis",
      lineTension: 0.3,
      backgroundColor: "rgba(2,117,216,0.2)",
      borderColor: "rgba(2,117,216,1)",
      pointRadius: 5,
      pointBackgroundColor: "rgba(2,117,216,1)",
      pointBorderColor: "rgba(255,255,255,0.8)",
      pointHoverRadius: 5,
      pointHoverBackgroundColor: "rgba(2,117,216,1)",
      pointHitRadius: 50,
      pointBorderWidth: 2,
      data: data,
    }],
  },
  options: {
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 7
        }
      }],
      yAxes: [{
        time: {
          unit: 'Euro'
        },
        ticks: {
          min: 0,
          max: max_value,
          maxTicksLimit: 5
        },
        gridLines: {
          color: "rgba(0, 0, 0, .125)",
        }
      }],
    },
    legend: {
      display: false
    }
  }
});