document.addEventListener('DOMContentLoaded', function(){
  let ctx = document.querySelector('#newsForwardTable canvas').chart;
  // var ctx = document.getElementById("newsForwardTable");
  // var data = document.getElementById("myAreaChart").dataset.prices;
  // var labels = document.getElementById("myAreaChart").dataset.labels;
  data = [{
    label: 'News',
    data: [12, 19, 3, 5, 2, 15, 23, 4],
    backgroundColor: [
      'rgba(255, 99, 132, 0.2)'
  ],
    borderColor: [
      'rgba(200, 99, 132, .7)',
    ],
    borderWidth: 1
  },
  {
    label: 'Forwarded',
    data: [2, 3, 3, 1, 2, 6, 4, 1],
    backgroundColor: [
      'rgba(0, 137, 132, .2)'
    ],
    borderColor: [
      'rgba(0, 10, 130, .7)',
    ],
    borderWidth: 1
  }]

  // labels = JSON.parse(labels);
  // var dates = convertToDate(labels);
  ctx.data.datasets = data;
  ctx.data.labels = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"];
  ctx.update();

  let bar = document.querySelector("#newsAcceptanceRate canvas").chart;

  data =  [{
      data: [6, 34, 60]
      }]
  bar.data.datasets[0].data = [6, 34, 60];
  bar.data.labels = ["Article", "Accepted", "Forwarded but no relevant"];
  bar.update();

  var newsGathered = document.getElementById("numberNewsGathered");
  newsGathered.innerHTML = "10";

  var newsForwarded = document.getElementById("newsForwardedNumber");
  newsForwarded.innerHTML = "2";

  var priceAlerts = document.getElementById("numberPriceAlerts");
  priceAlerts.innerHTML = "4";

  var processCrashes = document.getElementById("numberProcessCrashes");
  processCrashes.innerHTML = "0";

  var userName = document.getElementById("userName");
  userName.innerHTML = "Cornelius Wolff";

  var alertNumber = document.getElementById("alertNumber");
  alertNumber.innerHTML = "7+";
});