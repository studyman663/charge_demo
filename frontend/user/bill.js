window.addEventListener("load", function () {
  var xhr = new XMLHttpRequest();
  xhr.withCredentials = true;

  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      var data = JSON.parse(this.responseText);
    
        // if (data.code === 0) {
          console.log("111");
          console.log(data);
          var tableBody = document.getElementById("table-body");
          var itemsPerPage = 10;
          var currentPage = 1;
          var totalPages = Math.ceil(data.length / itemsPerPage);

          function updateTable() {
            // 清空表格内容，保留表头信息
            while (tableBody.firstChild) {
              tableBody.removeChild(tableBody.firstChild);
            }

            // 计算当前页的起始索引和结束索引
            var start = (currentPage - 1) * itemsPerPage;
            var end = start + itemsPerPage;

            // 循环添加当前页的数据到表格中
            for (var i = start; i < end && i < data.length; i++) {
              (function (index) {
                var row = document.createElement("tr");

                var infoBox = document.getElementById("infoBox");

                row.addEventListener("click", function () {
                  infoBox.style.display = "block";

                  var idd = document.getElementById("m1");
                  idd.textContent = data[index].id;

                  var idd = document.getElementById("m2");
                  idd.textContent = data[index].created_at;

                  var idd = document.getElementById("m3");
                  idd.textContent = data[index].updated_at;

                  var idd = document.getElementById("m4");
                  idd.textContent = data[index].chargeAmount;

                  var idd = document.getElementById("m5");
                  idd.textContent = data[index].chargeStartTime;

                  var idd = document.getElementById("m6");
                  idd.textContent = data[index].chargeEndTime;

                  var idd = document.getElementById("m7");
                  idd.textContent = data[index].chargeFee;

                  var idd = document.getElementById("m8");
                  idd.textContent = data[index].serviceFee;

                  var idd = document.getElementById("m9");
                  idd.textContent = data[index].totalFee;

                  var idd = document.getElementById("m10");
                  idd.textContent = data[index].userId;

                  var idd = document.getElementById("m11");
                  idd.textContent = data[index].pileId;
                });

                infoBox.addEventListener("click", function () {
                  infoBox.style.display = "none";
                });

                row.innerHTML = `
                    <td>${data[index].id}</td>
                    <td>${data[index].created_at}</td>
                    <td>${data[index].chargeStartTime}</td>
                    <td>${data[index].totalFee}</td>
                    <td>${data[index].userId}</td>
                    <td>${data[index].pileId}</td>
                  `;
                tableBody.appendChild(row);
              })(i);
            }
          }

          function updatePaginationButtons() {
            var prevButton = document.getElementById("prevButton");
            var nextButton = document.getElementById("nextButton");

            prevButton.disabled = currentPage === 1;
            nextButton.disabled = currentPage === totalPages;
          }

          function handlePrevPage() {
            if (currentPage > 1) {
              currentPage--;
              updateTable();
              updatePaginationButtons();
            }
          }

          function handleNextPage() {
            if (currentPage < totalPages) {
              currentPage++;
              updateTable();
              updatePaginationButtons();
            }
          }

          // 初始化表格和翻页按钮
          updateTable();
          updatePaginationButtons();

          // 绑定按钮点击事件
          var prevButton = document.getElementById("prevButton");
          var nextButton = document.getElementById("nextButton");

          prevButton.addEventListener("click", handlePrevPage);
          nextButton.addEventListener("click", handleNextPage);
        // }
        // else{
        //   var code =data.code;
        //   console.log(code);        
        // }
    }
  });

  xhr.open("GET", config.apiBaseUrl + "/charge/bills");
  xhr.setRequestHeader("Content-Type", "application/json");
  var token = sessionStorage.getItem("token");
  xhr.setRequestHeader("Authorization", "Bearer " + token);
  xhr.setRequestHeader("Accept", "*/*");

  xhr.send();
});
