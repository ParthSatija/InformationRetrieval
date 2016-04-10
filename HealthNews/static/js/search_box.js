"use strict"

function search() {
    var query = document.getElementById("search_box").value;
    var current_url = window.location.href.split("/");
    window.location.href = current_url[0] + "//" + current_url[2] + "/?query=" + query + "&selection=" + current_url[current_url.length - 1].substr(current_url[current_url.length - 1].length - 1);
}

function toggle() {
    var current_url = window.location.href;
    var value = (parseInt(current_url.substring(current_url.length - 1)) % 2) + 1;
    window.location.href = current_url.substring(0, current_url.length - 1) + value.toString();
}

$("#search_box").keyup(function (event) {
    if (event.keyCode == 13) {
        search();
    }
});