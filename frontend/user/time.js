function updateTimestamp() {
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
}

let intervalId = setInterval(updateTimestamp, 1000);
// setTimeout(function () {
//   clearInterval(intervalId);
//   console.log("定时器已暂停");
// }, 3000);
var timeStop = document.getElementById("timeStop");
var click = 0;
console.log("11");
timeStop.addEventListener("click", function () {
  if (click === 1) {
    // 如果没有停止函数的执行，重新启动定时器
    intervalId = setInterval(updateTimestamp, 1000);
    console.log("Function started.");
    timeStop.textContent = "停止";
    click = 0;
  } else {
    clearInterval(intervalId);
    console.log("Function stopped.");
    timeStop.textContent = "开始";
    click = 1;
  }
});
