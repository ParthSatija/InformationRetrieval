"use strict"

function search() {
    var query = document.getElementById("search_box").value;
    var url = window.location.href;
    var current_url = url.split("/");
    window.location.href = current_url[0] + "//" + current_url[2] + "/?query=" + query + "&selection=" + url.substring(url.indexOf("selection=")+10,url.indexOf("selection=")+11);
}

function toggle() {
    var url = window.location.href;
    var query = document.getElementById("search_box").value;
    var value = (parseInt(url.substring(url.indexOf("selection=")+10,url.indexOf("selection=")+11)) % 2) + 1;
    var current_url = url.split("/");
    window.location.href = current_url[0] + "//" + current_url[2] + "/?query=" + query + "&selection=" + value;
}

$("#search_box").keyup(function (event) {
    if (event.keyCode == 13) {
        search();
    }
});