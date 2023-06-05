var datetimeInput = document.getElementById("datetimeInput");

// WARNING: For GET requests, body is set to null by browsers.

var xhr = new XMLHttpRequest();
xhr.withCredentials = false;

xhr.addEventListener("readystatechange", function () {
  if (this.readyState === 4) {
    console.log(this.responseText);
    var data = JSON.parse(this.responseText);
    console.log(data.time);

    datetimeInput.value = data.time;
  }
});

xhr.open("GET", localStorage.getItem("backendUrl") + "/time");
console.log(localStorage.getItem("backendUrl"));
var token = sessionStorage.getItem("token");
xhr.setRequestHeader("Authorization", "Bearer " + token);
xhr.setRequestHeader("Accept", "*/*");

xhr.send();

var username = sessionStorage.getItem("username");
var nameText = document.getElementById("u108");
nameText.textContent = username;
