function updateTimestamp() {
  var datetimeInput = document.getElementById("datetimeInput");

  // WARNING: For GET requests, body is set to null by browsers.

  var xhr = new XMLHttpRequest();
  xhr.withCredentials = false;

  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      console.log(this.responseText);
      var data = JSON.parse(this.responseText);
      // console.log(data.time);
      const date = new Date(data.time);
      const year = date.getFullYear(); // 获取年份
      const month = String(date.getMonth() + 1).padStart(2, "0"); // 获取月份，并用0补齐至两位
      const day = String(date.getDate()).padStart(2, "0"); // 获取日期，并用0补齐至两位
      const hours = String(date.getHours()).padStart(2, "0"); // 获取小时，并用0补齐至两位
      const minutes = String(date.getMinutes()).padStart(2, "0"); // 获取分钟，并用0补齐至两位
      const seconds = String(date.getSeconds()).padStart(2, "0"); // 获取秒数，并用0补齐至两位

      const formattedDate = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`; // 将日期和时间部分组合成一个字符串

      console.log(formattedDate); // 输出：2021-10-08 09:30:45

      datetimeInput.value = formattedDate;
    }
  });

  xhr.open("GET", localStorage.getItem("backendUrl") + "/time");
  console.log(localStorage.getItem("backendUrl"));
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  xhr.send();
}

let intervalId = setInterval(updateTimestamp, 10000);
// setTimeout(function () {
//   clearInterval(intervalId);
//   console.log("定时器已暂停");
// }, 3000);
var click = localStorage.getItem("clock");
var timeStop = document.getElementById("timeStop");
timeStop.addEventListener("click", function () {
  click = localStorage.getItem("clock");
  console.log("click: " + click);
  if (click === "1") {
    // 如果没有停止函数的执行，重新启动定时器
    intervalId = setInterval(updateTimestamp, 1000);
    console.log("Function started.");
    timeStop.textContent = "停止";
    localStorage.setItem("clock", "0");
  } else {
    clearInterval(intervalId);
    console.log("Function stopped.");
    timeStop.textContent = "开始";
    localStorage.setItem("clock", "1");
  }
});
