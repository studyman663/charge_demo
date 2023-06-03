function updateTimestamp() {
  var timestampInput = document.getElementById("timestampInput");
  var datetimeInput = document.getElementById("datetimeInput");

  // WARNING: For GET requests, body is set to null by browsers.

  var xhr = new XMLHttpRequest();
  xhr.withCredentials = true;

  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      console.log(this.responseText);
      var data = JSON.parse(this.responseText);
      console.log(data);

      datetimeInput.value = data.time;
    }
  });

  xhr.open("GET", config.apiBaseUrl + "/time");
  console.log(config.apiBaseUrl);
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  xhr.send();
}

// 每0.1秒更新一次时间戳
setInterval(updateTimestamp, 1000);
