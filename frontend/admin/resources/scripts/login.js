// 获取登录表单元素
const form = document.querySelector("form");
// 获取用户名和密码输入框元素
const usernameInput = document.getElementById("u65_input");
const passwordInput = document.getElementById("u71_input");

var jsonData;

// 绑定表单提交事件
form.addEventListener("submit", function (event) {
  // 阻止表单默认提交行为
  event.preventDefault();

  // 获取用户名和密码
  const username = usernameInput.value;
  const password = passwordInput.value;

  // 发送 AJAX 请求
  var xhr = new XMLHttpRequest();

  xhr.withCredentials = true;
  xhr.addEventListener("readystatechange", function () {
    jsonData = JSON.parse(xhr.responseText);
    if (this.readyState === 4) {
      if (jsonData.code === 201) {
        console.log("登录成功");

        console.log(jsonData);
        // 跳转到主界面
        window.open("./admin-manage.html", "_blank");
      } else {
        console.log("登录失败");
        console.log(jsonData);
      }
    }
  });

  xhr.open("POST", "http://127.0.0.1:4523/m1/2776831-0-default/user/login");
  xhr.setRequestHeader("User-Agent", "Apifox/1.0.0 (https://www.apifox.cn)");
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Accept", "*/*");
  xhr.setRequestHeader("Host", "127.0.0.1:4523");
  xhr.setRequestHeader("Connection", "keep-alive");

  var data = JSON.stringify({
    username: username,
    password: password,
  });

  xhr.send(data);
});
