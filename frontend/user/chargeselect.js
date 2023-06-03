
var username = sessionStorage.getItem("username");
var nameText = document.getElementById("u62");
nameText.textContent = username;

// 定义变量用于存储充电模式、充电数量和电池容量
var fast = true;
var amount = 0;
var totalAmount = 0;

// 获取充电模式选择框元素
var chargeModeSelect = document.getElementById("u74_input");
var amount = document.querySelector("#u75_input").value;
var totalAmount = document.querySelector("#u76_input").value;

// 获取提交按钮元素
var submitButton = document.getElementById("u73");

// 监听提交按钮的点击事件
submitButton.addEventListener("click", function () {  
  amount = document.querySelector("#u75_input").value;
  totalAmount = document.querySelector("#u76_input").value;
  if (amount.trim() === "") {
    alert("请输入充电量");
    return ;
  } else if (totalAmount.trim() === "") {
    alert("请输入电池容量");
    return ;
  }
  // 判断选择的充电模式是否为快充
  if (chargeModeSelect.value === "快充") {
    fast = true;
  } else {
    fast = false;
  }

  // 发送 AJAX 请求
  var xhr = new XMLHttpRequest();
  xhr.withCredentials = true;

  xhr.open("POST", config.apiBaseUrl + "/charge");
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Accept", "*/*");

  var data = JSON.stringify({
    amount: amount,
    totalAmount: totalAmount,
    fast: fast,
  });

  xhr.send(data);

  xhr.addEventListener("readystatechange", function () {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        console.log("申请成功");

        var data = JSON.parse(xhr.responseText);
        var pile = data.pile;
        var amount = data.amount;
        var status = data.status;
        var totalAmount = data.totalAmount;
        var chargingArea = data.chargingArea;
        var position = data.position;
        var waitingArea = data.waitingArea;
        var fast = data.fast;
        sessionStorage.setItem("pile", pile);
        sessionStorage.setItem("amount", amount);
        sessionStorage.setItem("status", status);
        sessionStorage.setItem("totalAmount", totalAmount);
        sessionStorage.setItem("chargingArea", chargingArea);
        sessionStorage.setItem("position", position);
        sessionStorage.setItem("waitingArea", waitingArea);
        sessionStorage.setItem("fast", fast);
        window.location.href = "checkcurrentbill.html";
      } else {
        alert("error: sumbit failed");
        return;
      }
    } else {
      return;
    }
  });
});
