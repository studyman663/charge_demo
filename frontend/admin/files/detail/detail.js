const chargeStationManager = document.querySelector("#u38");
chargeStationManager.addEventListener("click", () => {
  window.location.href = "./admin-manage.html";
});
const report = document.querySelector("#u41");
report.addEventListener("click", () => {
  window.location.href = "./admin-report.html";
});

const urlParams = new URLSearchParams(window.location.search);
const id = urlParams.get("id");

var xhr = new XMLHttpRequest();
xhr.withCredentials = true;

xhr.addEventListener("readystatechange", function () {
  if (this.readyState === 4) {
    console.log(this.responseText);
    var chargeData = JSON.parse(xhr.responseText);

    const chargeCard = document.querySelector("#charge-card");
    const chargeId = document.querySelector("#charge-id");
    const chargeAmount = document.querySelector("#charge-amount");
    const chargeTimes = document.querySelector("#charge-times");
    const chargeStatus = document.querySelector("#charge-status");
    const chargeTime = document.querySelector("#charge-time");

    // Set the values for the charge station information
    chargeId.textContent = chargeData.id;
    chargeAmount.textContent = chargeData.chargeAmount;
    chargeTimes.textContent = new Date(chargeData.chargeTimes).toLocaleString();
    chargeStatus.textContent = chargeData.status;
    chargeTime.textContent = new Date(chargeData.chargeTime).toLocaleString();
  }
});

xhr.open("GET", config.apiBaseUrl + "/pile/" + id);
xhr.setRequestHeader("Authorization", "");
xhr.setRequestHeader("User-Agent", "Apifox/1.0.0 (https://www.apifox.cn)");
xhr.setRequestHeader("Accept", "*/*");
xhr.setRequestHeader("Host", config.hostUrl);
xhr.setRequestHeader("Connection", "keep-alive");

xhr.send();
