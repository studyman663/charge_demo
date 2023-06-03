var oInp = document.getElementById("inp");
var oBtn = document.getElementById("btn");

oBtn.onclick = function () {
  Search();
};

document.onkeydown = function () {
  if (event.keyCode == 13) {
    Search();
  }
};

function Search() {
  // WARNING: For GET requests, body is set to null by browsers.

  var xhr = new XMLHttpRequest();
  xhr.withCredentials = true;
  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      if (this.status === 200) {
        console.log(this.responseText);
        var data = JSON.parse(xhr.responseText);

        var infoBox = document.getElementById("infoBox");
        infoBox.style.display = "block";

        var idd = document.getElementById("m1");
        idd.textContent = data.id;

        var idd = document.getElementById("m2");
        idd.textContent = data.createdAt;

        var idd = document.getElementById("m3");
        idd.textContent = data.updatedAt;

        var idd = document.getElementById("m4");
        idd.textContent = data.chargeAmount;

        var idd = document.getElementById("m5");
        idd.textContent = data.chargeStartTime;

        var idd = document.getElementById("m6");
        idd.textContent = data.chargeEndTime;

        var idd = document.getElementById("m7");
        idd.textContent = data.chargeFee;

        var idd = document.getElementById("m8");
        idd.textContent = data.serviceFee;

        var idd = document.getElementById("m9");
        idd.textContent = data.totalFee;

        var idd = document.getElementById("m10");
        idd.textContent = data.userId;

        var idd = document.getElementById("m11");
        idd.textContent = data.pileId;
      }
      else{
        alert("订单不存在");
      }
    }
  });

  xhr.open("GET", config.apiBaseUrl + "/charge/bill/");
  xhr.setRequestHeader("Content-Type", "application/json");
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  xhr.send();
}
