const chargeStationManager = document.querySelector("#u38");
chargeStationManager.addEventListener("click", () => {
  window.location.href = "./admin-manage.html";
});
const report = document.querySelector("#u41");
report.addEventListener("click", () => {
  window.location.href = "./admin-report.html";
});

var xhr = new XMLHttpRequest();
xhr.withCredentials = true;

xhr.addEventListener("readystatechange", function () {
  if (this.readyState === 4) {
    console.log(this.responseText);
    var data = JSON.parse(this.responseText);
    var tableBody = document.getElementById("table-body");
    for (var i = 0; i < data.length; i++) {
      var status = "运行";
      var row = document.createElement("tr");
      if (data[i].status === -1) {
        status = "故障";
      } else if (data[i].status === 0) {
        status = "关闭";
      } else if (data[i].status === 1) {
        status = "运行";
      }

      row.innerHTML = `
        <td class="id" data-pile-id="${data[i].id}">${data[i].id}</td>
        <td class="status" data-pile-id="${data[i].id}">${status}</td>
        <td class="fast" data-pile-id="${data[i].id}">${
        data[i].fast ? "是" : "否"
      }</td>
        <td class="created" data-pile-id="${data[i].id}">${
        data[i].created_at
      }</td>
        <td class="updated" data-pile-id="${data[i].id}">${
        data[i].updated_at
      }</td>
        <td class="deleted" data-pile-id="${data[i].id}">${
        data[i].deleted_at
      }</td>
      `;
      tableBody.appendChild(row);
    }
  }
});

xhr.open("GET", config.apiBaseUrl + "/piles?limit=10&skip=0");
console.log(config.apiBaseUrl);
var token = sessionStorage.getItem("token");
console.log(token);
xhr.setRequestHeader("Authorization", "Bearer " + token);
xhr.setRequestHeader("Accept", "*/*");

xhr.send();

// 获取所有充电桩编号元素
const pileIds = document.querySelectorAll(
  "#pile_table tbody tr td:first-child"
);

// 为每个充电桩编号添加点击事件监听器
document.addEventListener("DOMContentLoaded", () => {
  pileIds.forEach((id) => {
    id.addEventListener("click", () => {
      console.log("Clicked on pile ID: " + id.textContent);
      // 获取充电桩编号
      const pileId = Number(id.textContent);
      var token = sessionStorage.getItem("token");
      console.log(token);

      // 发送AJAX请求获取充电桩详细信息
      fetch(config.apiBaseUrl + `/pile/${pileId}`, {
        headers: {
          Authorization: "Bearer " + token,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          // 在界面中显示详细信息框
          showDetailBox(data);
        })
        .catch((error) => {
          console.error(error);
        });
    });
  });
});

function showDetailBox(data) {
  // 创建详细信息框元素
  const detailBox = document.createElement("div");
  detailBox.classList.add("detail-box");

  // 创建详细信息框内容元素
  const content = document.createElement("div");
  content.classList.add("content");

  // 向详细信息框内容元素中添加详细信息
  const keys = Object.keys(data);
  keys.forEach((key) => {
    const item = document.createElement("div");
    item.classList.add("item");
    const label = document.createElement("span");
    label.classList.add("label");
    label.textContent = key;
    const value = document.createElement("span");
    value.classList.add("value");
    value.textContent = data[key];
    item.appendChild(label);
    item.appendChild(value);
    content.appendChild(item);
  });

  // 向详细信息框中添加关闭按钮
  const closeButton = document.createElement("button");
  closeButton.classList.add("close");
  closeButton.textContent = "关闭";
  closeButton.addEventListener("click", () => {
    detailBox.remove();
  });

  // 将详细信息框内容和关闭按钮添加到详细信息框中
  detailBox.appendChild(content);
  detailBox.appendChild(closeButton);

  // 将详细信息框添加到文档中
  document.body.appendChild(detailBox);
}

const tableBody = document.querySelector("#table-body");
tableBody.addEventListener("click", handleTableClick);

function handleTableClick(event) {
  const target = event.target;
  if (target.classList.contains("status")) {
    const pileId = target.dataset.pileId;
    const form = createForm(pileId);
    target.innerHTML = "";
    target.appendChild(form);
  }
}

function createForm(pileId) {
  const form = document.createElement("form");
  const select = document.createElement("select");
  const option1 = document.createElement("option");
  const option2 = document.createElement("option");
  const option3 = document.createElement("option");
  const submitBtn = document.createElement("button");
  const cancelBtn = document.createElement("button");

  option1.value = "运行";
  option1.innerHTML = "运行";

  option2.value = "故障";
  option2.innerHTML = "故障";

  option3.value = "关闭";
  option3.innerHTML = "关闭";

  submitBtn.type = "submit";
  submitBtn.innerHTML = "提交";

  cancelBtn.type = "button";
  cancelBtn.innerHTML = "取消";

  form.appendChild(select);
  form.appendChild(submitBtn);
  form.appendChild(cancelBtn);
  select.appendChild(option1);
  select.appendChild(option2);
  select.appendChild(option3);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const selectedValue = select.value;
    updatePileStatus(pileId, selectedValue);
  });

  cancelBtn.addEventListener("click", () => {
    const selectedValue = select.value;
    updatePileStatus(pileId, selectedValue);
  });

  return form;
}

function updatePileStatus(pileId, status) {
  var status_code;
  if (status === "故障") {
    status_code = -1;
  } else if (status === "关闭") {
    status_code = 0;
  } else if (status === "运行") {
    status_code = 1;
  }
  const data = {
    status: status_code,
  };
  var token = sessionStorage.getItem("token");
  console.log(token);
  console.log(data);
  const myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");
  myHeaders.append("Authorization", "Bearer " + token);

  fetch(config.apiBaseUrl + `/pile/${pileId}`, {
    method: "PUT",
    headers: myHeaders,
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      const pileStatus = tableBody.querySelector(
        `.status[data-pile-id="${pileId}"]`
      );
      const pileFast = tableBody.querySelector(
        `.fast[data-pile-id="${pileId}"]`
      );
      const pileCreated = tableBody.querySelector(
        `.created[data-pile-id="${pileId}"]`
      );
      const pileUpdated = tableBody.querySelector(
        `.updated[data-pile-id="${pileId}"]`
      );
      const pileDeleted = tableBody.querySelector(
        `.deleted[data-pile-id="${pileId}"]`
      );
      
      pileFast.innerHTML = data.fast ? "是" : "否";
      pileCreated.innerHTML = data.created_at;
      pileUpdated.innerHTML = data.updated_at;
      pileDeleted.innerHTML = data.deleted_at;
      if (data.status > 0) {
        pileStatus.innerHTML = "运行";
      } else if (data.status === 0) {
        pileStatus.innerHTML = "关闭";
      } else if (data.status < 0) {
        pileStatus.innerHTML = "故障";
      }
    })
    .catch((error) => console.error(error));
}

const pileTable = document.getElementById("pile_table");
const details = document.getElementById("details");
const detailsTitle = document.getElementById("details-title");
const detailsDescription = document.getElementById("details-description");
const detailsList = document.getElementById("details-list");

const waits = document.getElementById("waits");
const waitsTitle = document.getElementById("waits-title");
const waitsDescription = document.getElementById("waits-description");
const waitsList = document.getElementById("waits-list");

pileTable.addEventListener("click", (event) => {
  {
    const target = event.target;
    const isPileId = target.classList.contains("id");

    if (isPileId) {
      const pileId = target.dataset.pileId;
      const xhr = new XMLHttpRequest();

      xhr.open("GET", config.apiBaseUrl + `/pile/${pileId}`, true);
      var token = sessionStorage.getItem("token");
      console.log(token);
      xhr.setRequestHeader("Authorization", "Bearer " + token);

      xhr.onload = function () {
        if (this.status === 200) {
          const pile = JSON.parse(this.responseText);
          showDetails(pile);
        }
      };

      xhr.send();
    }
  }
  {
    const target = event.target;
    const isPileId = target.classList.contains("id");

    if (isPileId) {
      const pileId = target.dataset.pileId;
      const xhr = new XMLHttpRequest();

      xhr.open("GET", config.apiBaseUrl + `/pile/${pileId}/wait`, true);
      var token = sessionStorage.getItem("token");
      xhr.setRequestHeader("Authorization", "Bearer " + token);

      xhr.onload = function () {
        if (this.status === 200) {
          const pile_1 = JSON.parse(this.responseText);
          showWaits(pile_1);
        }
      };

      xhr.send();
    }
  }
});

function showDetails(pile) {
  detailsTitle.textContent = `充电桩 #${pile.id} 详情`;
  detailsDescription.style.display = "none";
  detailsList.innerHTML = `
    <li><span>状态:</span> ${pile.status}</li>
    <li><span>是否快充:</span> ${pile.fast ? "是" : "否"}</li>
    <li><span>充电量:</span> ${pile.chargeAmount}</li>
    <li><span>充电次数:</span> ${pile.chargeTimes}</li>
    <li><span>充电时间:</span> ${pile.chargeTime}</li>
    <button id="scroll-detail">收起</button>
  `;
  details.classList.add("show");

  const scrollDetailHidden = document.getElementById("scroll-detail");

  scrollDetailHidden.addEventListener("click", (event) => {
    console.log(1);
    details.classList.remove("show");
  });
}

function showWaits(pile) {
  waitsTitle.textContent = `充电桩 #${pile.id} 等候详情`;
  waitsDescription.style.display = "none";
  var content = ``;
  for (var i = 0; i < pile.users.length; i++) {
    content += `<li><span class="user-id">用户ID:</span> ${pile.users[i].id}</li>`;
    content += `<li><span>状态:</span> ${pile.users[i].status}</li>`;
    content += `<li><span>汽车电池容量:</span> ${pile.users[i].totalAmount}</li>`;
    content += `<li><span>本次充电量:</span> ${pile.users[i].amount}</li>`;
    content += `<li><span>等待时间:</span> ${pile.users[i].waitTime}</li>`;
  }
  content += `<button id="scroll-wait">收起</button>`;
  waitsList.innerHTML = content;
  waits.classList.add("show");

  const scrollWaitHidden = document.getElementById("scroll-wait");

  scrollWaitHidden.addEventListener("click", (event) => {
    waits.classList.remove("show");
  });
}
