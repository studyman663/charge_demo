// 在页面加载完成后绑定事件监听器
window.addEventListener("DOMContentLoaded", function () {
  
  // 获取登录按钮元素
  var loginButton = document.getElementById("u17");

  // 绑定点击事件监听器
  loginButton.addEventListener("click", function (event) {
    var backendUrl = document.getElementById("back-end_input").value;
    // 阻止表单默认提交行为
    event.preventDefault();

    // 获取用户名和密码输入框的值
    var username = document.getElementById("u10_input").value;
    var password = document.getElementById("u16_input").value;
    var backendUrl = document.getElementById("back-end_input").value;

    // console.log(backendUrl);
    if (username.trim() === "用户名") {
      alert("请输入用户名");
      return false;
    } else if (password.trim() === "密码") {
      alert("请输入密码");
      return false;
    }

    if (username.trim().length < 8 && username.trim().length > 100) {
      alert("用户名长度在8至100之间");
      return false;
    } else if (password.trim().length < 6 && password.trim().length > 20) {
      alert("密码长度在6至20之间");
      return false;
    }

    // 发送 AJAX 请求
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.addEventListener("readystatechange", function () {
      if (this.readyState === 4) {
        var data = JSON.parse(xhr.responseText);
        console.log(data);
        if (data.code === 0) {
          localStorage.setItem("clock", "0");
          if (username.trim() === "admin123" && password.trim() === "123456") {
            var backendUrl = document.getElementById("back-end_input").value;
            if (backendUrl !== "") {
              console.log(2);
              sessionStorage.setItem("token", data.token);
              sessionStorage.setItem("username", username);
            }
            console.log(1);
            localStorage.setItem("backendUrl", backendUrl);

            // console.log(config.apiBaseUrl);
            window.location.href = "../admin/admin-manage.html";
          } else {
            console.log(1);
            console.log("登录成功");
            var backendUrl = document.getElementById("back-end_input").value;
            console.log(backendUrl);
            if (backendUrl !== "") {
              localStorage.setItem("backendUrl", backendUrl);
              // console.log(config.apiBaseUrl);
            }

            var token = data.token; // 这里假设您从后端获取的 token

            // 将 token 存储在 sessionStorage 中
            sessionStorage.setItem("token", token);
            sessionStorage.setItem("username", username);

            window.location.href = "chargeSelect.html";
          }
        } else {
          alert("error: login failed");
        }
      }
    });

    xhr.open("POST", backendUrl + "/user/login");
    xhr.withCredentials = false;
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Accept", "*/*");

    var data = JSON.stringify({
      username: username,
      password: password,
    });

    xhr.send(data);
  });
});
