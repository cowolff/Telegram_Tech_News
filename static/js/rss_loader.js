document.addEventListener('DOMContentLoaded', function(){
    var unsubscribe = document.getElementById("unsubscribe-button");
    var subscribe = document.getElementById("subscribe-button");
    var active = document.getElementById("rss_header").dataset.active;
    if (active === "1") {
        unsubscribe.classList.remove("d-sm-inline-block");
        unsubscribe.classList.add("d-none");
      } else {
        subscribe.classList.remove("d-sm-inline-block");
        subscribe.classList.add("d-none");
      }
});