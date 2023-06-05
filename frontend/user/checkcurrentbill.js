var state;

var username = sessionStorage.getItem("username");
var nameText = document.getElementById("u145");
nameText.textContent = username;
var nameText1 = document.getElementById("u175");
nameText1.textContent = username;

var pileelement = document.getElementById("u182");
var amountelement = document.getElementById("u186");
var totalAmountelement = document.getElementById("u184");
var positionelement = document.getElementById("u178");
var waitingAreaelement = document.getElementById("u180");
var chargingAreaelement = document.getElementById("u189");
var statuselement = document.getElementById("u192");
var fastelement = document.getElementById("u196");
myFunction();
setInterval(myFunction, 4000); // 每秒执行一次 myFunction 函数

window.addEventListener("load", myFunction);

function myFunction() {
  // WARNING: For GET requests, body is set to null by browsers.

  var xhr = new XMLHttpRequest();
  xhr.withCredentials = false;

  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      var data = JSON.parse(xhr.responseText);
      if (data.code === 0) {
        console.log(data);
        state = data.status;
        // console.log(data.waitingArea);
        pileelement.textContent = data.pile;
        amountelement.textContent = data.amount;
        totalAmountelement.textContent = data.totalAmount;
        positionelement.textContent = data.position;
        statuselement.textContent = data.status;
        fast = data.fast;
        waitingArea = data.waitingArea;
        chargingArea = data.chargingArea;
        // waitingAreaelement.textContent = data.waitingArea；
        waitingAreaelement.textContent =
          data.waitingArea === true ? "是" : "否";
        if (fast === true) {
          fastelement.textContent = "  快充";
        } else {
          fastelement.textContent = "  慢充";
        }
        chargingAreaelement.textContent =
          data.chargingArea === true ? "是" : "否";

        if (data.status === "等候区排队中") {
          var modify = document.getElementById("u199");
          modify.style.display = "block";
          var cancel = document.getElementById("u200");
          cancel.style.display = "block";
          var finish = document.getElementById("u201");
          finish.style.display = "none";
        } else if (data.status === "充电完成") {
          var modify = document.getElementById("u199");
          modify.style.display = "none";
          var cancel = document.getElementById("u200");
          cancel.style.display = "none";
          var finish = document.getElementById("u201");
          finish.style.display = "block";
          finish.textContent = "    拔出充电桩".replace(/ /g, "\u00A0");
          finish.style.backgroundColor = "rgb(68, 193, 193)";
          console.log("拔出");
        } else if (data.status === "充电中") {
          var modify = document.getElementById("u199");
          modify.style.display = "none";
          var cancel = document.getElementById("u200");
          cancel.style.display = "block";
          var finish = document.getElementById("u201");
          finish.style.display = "none";
        } else {
          var modify = document.getElementById("u199");
          modify.style.display = "none";
          var cancel = document.getElementById("u200");
          cancel.style.display = "block";
          var finish = document.getElementById("u201");
          finish.style.display = "none";
        }
      } else {
        var notFound = document.getElementById("u215");
        notFound.style.display = "block";
      }
    }
  });

  xhr.open("GET", localStorage.getItem("backendUrl") + "/charge");
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  xhr.send();
}

var notFounud = document.getElementById("u220");
notFounud.addEventListener("click", function () {
  var frame = document.getElementById("u215");
  frame.style.display = "none";
  window.location.href = "chargeselect.html";
});

var cancelModify = document.getElementById("u214");
cancelModify.addEventListener("click", function () {
  var frame = document.getElementById("u205");
  frame.style.display = "none";
});

var modify = document.getElementById("u199");
modify.addEventListener("click", function () {
  var frame = document.getElementById("u205");
  frame.style.display = "block";
});

var confirmModify = document.getElementById("u213");
confirmModify.addEventListener("click", function () {
  var chargeModeSelect = document.getElementById("u208_input");
  amount = document.querySelector("#u210_input").value;
  totalAmount = document.querySelector("#u212_input").value;
  if (amount.trim() === "") {
    alert("请输入充电量");
    return;
  } else if (totalAmount.trim() === "") {
    alert("请输入电池容量");
    return;
  }
  // 判断选择的充电模式是否为快充
  if (chargeModeSelect.value === "快充") {
    fast = true;
  } else {
    fast = false;
  }

  var frame = document.getElementById("u205");
  frame.style.display = "none";

  // 发送 AJAX 请求
  var xhr = new XMLHttpRequest();
  xhr.withCredentials = false;

  xhr.open("PUT", localStorage.getItem("backendUrl") + "/charge");
  xhr.setRequestHeader("Content-Type", "application/json");
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  var data = JSON.stringify({
    amount: amount,
    totalAmount: totalAmount,
    fast: fast,
  });

  xhr.send(data);

  xhr.addEventListener("readystatechange", function () {
    if (xhr.readyState === 4) {
      var data = JSON.parse(xhr.responseText);
      console.log("申请成功");

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
      return;
    }
  });
});

var cancelCancel = document.getElementById("u163");
cancelCancel.addEventListener("click", function () {
  var frame = document.getElementById("u159");
  frame.style.display = "none";
});

var cancel = document.getElementById("u200");
cancel.addEventListener("click", function () {
  var frame = document.getElementById("u159");
  frame.style.display = "block";
});

var confirmCancel = document.getElementById("u165");
confirmCancel.addEventListener("click", function () {
  if (state === "充电中") {
    Finish();
    console.log("finish");
    return;
  }
  console.log("cancel");
  var frame = document.getElementById("u159");
  frame.style.display = "none";

  var xhr = new XMLHttpRequest();
  xhr.withCredentials = false;

  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      if (this.status === 200) {
        console.log(this.responseText);
        sessionStorage.setItem("pile", "");
        sessionStorage.setItem("amount", "");
        sessionStorage.setItem("status", "");
        sessionStorage.setItem("totalAmount", "");
        sessionStorage.setItem("chargingArea", "");
        sessionStorage.setItem("position", "");
        sessionStorage.setItem("waitingArea", "");
        sessionStorage.setItem("fast", "");
      } else {
        alert("cancel failed");
      }
    }
  });

  xhr.open("DELETE", localStorage.getItem("backendUrl") + "/charge");

  xhr.setRequestHeader("Content-Type", "application/json");
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  xhr.send();
});

var cancelFinish = document.getElementById("u156");
cancelFinish.addEventListener("click", function () {
  var frame = document.getElementById("u152");
  frame.style.display = "none";
});

var clickcount = 0;

var Finish = document.getElementById("u201");
Finish.addEventListener("click", function () {
  // var frame = document.getElementById("u152");
  // console.log(clickcount);
  // if (clickcount === 1) {
  //   clickcount = 0;
  //   window.location.href = "chargeselect.html";
  //   frame.style.display = "none";
  // }
  // if (clickcount === 0) {
  //   frame.style.display = "block";
  // }

  var frame = document.getElementById("u152");
  frame.style.display = "none";

  var xhr = new XMLHttpRequest();
  xhr.withCredentials = false;

  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      var data = JSON.parse(xhr.responseText);
      console.log(data);

      clickcount++;

      if (clickcount === 1) {
        myFunction();
      }
      if (clickcount >= 2) {
        window.location.href = "chargeselect.html";
        clickcount = 0;
      }
    }
  });

  xhr.open("POST", localStorage.getItem("backendUrl") + "/charge/finish");
  xhr.setRequestHeader("Content-Type", "application/json");
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  xhr.send();
});

var confirmFinish = document.getElementById("u158");
confirmFinish.addEventListener("click", function () {
  if (clickcount === 1) {
    myFunction();
  }
  var frame = document.getElementById("u152");
  frame.style.display = "none";

  var xhr = new XMLHttpRequest();
  xhr.withCredentials = false;

  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      var data = JSON.parse(xhr.responseText);
      console.log(data);

      clickcount++;
      if (clickcount >= 2) {
        window.location.href = "chargeselect.html";
        clickcount = 0;
      }
    }
  });

  xhr.open("POST", localStorage.getItem("backendUrl") + "/charge/finish");
  xhr.setRequestHeader("Content-Type", "application/json");
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  xhr.send();
});

function Finish() {
  // var frame = document.getElementById("u152");
  // console.log(clickcount);
  // if (clickcount === 1) {
  //   clickcount = 0;
  //   window.location.href = "chargeselect.html";
  //   frame.style.display = "none";
  // }
  // if (clickcount === 0) {
  //   frame.style.display = "block";
  // }

  var frame = document.getElementById("u152");
  frame.style.display = "none";

  var xhr = new XMLHttpRequest();
  xhr.withCredentials = false;

  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      var data = JSON.parse(xhr.responseText);
      console.log(data);

      clickcount++;

      if (clickcount === 1) {
        myFunction();
      }
      if (clickcount >= 2) {
        window.location.href = "chargeselect.html";
        clickcount = 0;
      }
    }
  });

  xhr.open("POST", localStorage.getItem("backendUrl") + "/charge/finish");
  xhr.setRequestHeader("Content-Type", "application/json");
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  xhr.send();
}
