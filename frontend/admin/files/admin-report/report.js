const chargeStationManager = document.querySelector("#u10");
chargeStationManager.addEventListener("click", () => {
  window.location.href = "./admin-manage.html";
});
const report = document.querySelector("#u13");
report.addEventListener("click", () => {
  window.location.href = "./admin-report.html";
});

var xhr = new XMLHttpRequest();
xhr.withCredentials = false;

xhr.addEventListener("readystatechange", function () {
  if (this.readyState === 4) {
    console.log(this.responseText);
    var data = JSON.parse(this.responseText);
    var tableBody = document.getElementById("table-body");
    for (var i = 0; i < data.length; i++) {
      var row = document.createElement("tr");
      row.innerHTML = `
        <td>${data[i].id}</td>
        <td>${data[i].chargeTimes}</td>
        <td>${data[i].chargeAmount}</td>
        <td>${data[i].chargeTime}</td>
        <td>${data[i].chargeFee}</td>
        <td>${data[i].serviceFee}</td>
        <td>${data[i].totalFee}</td>
      `;
      tableBody.appendChild(row);
    }
  }
});

xhr.open("GET", localStorage.getItem("backendUrl") + "/report");
var token = sessionStorage.getItem("token");
xhr.setRequestHeader("Authorization", "Bearer "+token);
xhr.setRequestHeader("Accept", "*/*");

xhr.send();

// 添加日期选择器
const dateInput = document.createElement("input");
dateInput.setAttribute("type", "date");
dateInput.setAttribute("id", "date-picker");
// dateInput.style.width = "200px";
document.getElementById("u16_div").appendChild(dateInput);

// 添加确定按钮
const submitButton = document.createElement("button");
submitButton.textContent = "确定";
submitButton.style.marginLeft = "10px";
document.getElementById("u16_div").appendChild(submitButton);

// 处理后端数据
function handleData(data) {
  console.log(data);
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";
  data.forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.id}</td>
        <td>${item.chargeTimes}</td>
        <td>${item.chargeAmount}</td>
        <td>${item.chargeTime}</td>
        <td>${item.chargeFee.toFixed(2)}</td>
        <td>${item.serviceFee.toFixed(2)}</td>
        <td>${item.totalFee.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}

// 发送请求
submitButton.addEventListener("click", () => {
  const date = document.getElementById("date-picker").value;
  var token = sessionStorage.getItem("token");
  console.log(date);
  fetch(localStorage.getItem("backendUrl") + "/report", {
    headers: {
      date: String(date),
      Authorization: "Bearer " + token,
    },
    credentials: false,
    method: "GET"
  })
    .then((response) => response.json())
    .then((data) => handleData(data));
});

