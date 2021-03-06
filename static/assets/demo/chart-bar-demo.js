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
  console.log(dates);
  return dates;
}

// Bar Chart Example
var ctx = document.getElementById("myBarChart");
var weeks = document.getElementById("myBarChart").dataset.weeks;
var numbers = document.getElementById("myBarChart").dataset.numbers;

console.log(weeks);
weeks = JSON.parse(weeks);
numbers = JSON.parse(numbers);
var dates = convertToDate(weeks);

var max = getMax(numbers);

var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: dates,
    datasets: [{
      label: "Revenue",
      backgroundColor: "rgba(2,117,216,1)",
      borderColor: "rgba(2,117,216,1)",
      data: numbers,
    }],
  },
  options: {
    scales: {
      xAxes: [{
        time: {
          unit: 'week'
        },
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 7
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: max,
          maxTicksLimit: 5
        },
        gridLines: {
          display: true
        }
      }],
    },
    legend: {
      display: false
    }
  }
});
