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

document.addEventListener('DOMContentLoaded', function(){
  let ctx = document.querySelector('#newsForwardTable canvas').chart;
  // var ctx = document.getElementById("newsForwardTable");
  var data = document.getElementById("newsForwardTable").dataset.forwarded;
  var labels = document.getElementById("newsForwardTable").dataset.labels;
  var dates = convertToDate(JSON.parse(labels))
  data = JSON.parse(data)
  data = [{
    label: 'News',
    data: data.reverse(),
    backgroundColor: [
      'rgba(255, 99, 132, 0.2)'
  ],
    borderColor: [
      'rgba(200, 99, 132, .7)',
    ],
    borderWidth: 1
  } // ,
  // {
  //  label: 'Forwarded',
  //  data: [2, 3, 3, 1, 2, 6, 4, 1],
  //  backgroundColor: [
  //    'rgba(0, 137, 132, .2)'
  //  ],
  //  borderColor: [
  //    'rgba(0, 10, 130, .7)',
  //  ],
  //  borderWidth: 1
  //}
  ]

  // labels = JSON.parse(labels);
  // var dates = convertToDate(labels);
  ctx.data.datasets = data;
  ctx.data.labels = dates.reverse();
  ctx.update();

  var share = document.getElementById("newsAcceptanceRate").dataset.acceptance;
  let bar = document.querySelector("#newsAcceptanceRate canvas").chart;

  data =  [{
      data: [6, 34, 60]
      }]
  bar.data.datasets[0].data = JSON.parse(share);
  console.log(JSON.parse(share))
  bar.data.labels = ["Article", "Accepted", "Forwarded but no relevant"];
  bar.update();
  
  var newsGathered = document.getElementById("numberNewsGathered");
  newsGathered.innerHTML = newsGathered.dataset.numbernews;

  var newsForwarded = document.getElementById("newsForwardedNumber");
  newsForwarded.innerHTML = newsForwarded.dataset.newsforwarded;

  var priceAlerts = document.getElementById("numberPriceAlerts");
  priceAlerts.innerHTML = "4";

  var processCrashes = document.getElementById("numberProcessCrashes");
  processCrashes.innerHTML = processCrashes.dataset.processesnotrunning;

  var userName = document.getElementById("userName");
  userName.innerHTML = "Cornelius Wolff";

  var alertNumber = document.getElementById("alertNumber");
  alertNumber.innerHTML = "7+";
});