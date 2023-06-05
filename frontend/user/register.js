// 在页面加载完成后绑定事件监听器
window.addEventListener("DOMContentLoaded", function () {
  // 获取登录按钮元素
  var loginButton = document.getElementById("u30");
  // 绑定点击事件监听器
  loginButton.addEventListener("click", function () {
    // 获取用户名和密码输入框的值
    var username = document.getElementById("u36_input").value;
    var password = document.getElementById("u33_input").value;
    var confirmPassword = document.getElementById("u27_input").value;
    var backendUrl = document.getElementById("v36_input").value;

    if (username.trim() === "用户名") {
      alert("请输入用户名");
      return false;
    } else if (password.trim() === "密码") {
      alert("请输入密码");
      return false;
    } else if (confirmPassword.trim() === "密码") {
      alert("请输入确认密码");
      return false;
    } else if (password !== confirmPassword) {
      alert("密码和确认密码不一致");
      return false;
    }
    console.log(username.trim().length);
    if (username.trim().length < 8 && username.trim().length > 100) {
      alert("用户名长度在8至100之间");
      return false;
    } else if (password.trim().length < 6 && password.trim().length > 20) {
      alert("密码长度在6至20之间");
      return false;
    }
    // 发送 AJAX 请求
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = false;
    xhr.addEventListener("readystatechange", function () {
      if (this.readyState === 4) {
        var data = JSON.parse(xhr.responseText);
        console.log("data" + data);
        if (data.code === 0) {
          alert("register successfully!");
          var data = JSON.parse(xhr.responseText);
          // 跳转到主界面
          window.location.href = "index.html";
        }
      }
    });

    xhr.open("POST", backendUrl + "/user/register");
    console.log(backendUrl + "/user/register");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Accept", "*/*");

    var data = JSON.stringify({
      username: username,
      password: password,
    });

    xhr.send(data);

    // // 发送 AJAX 请求
    // var xhr = new XMLHttpRequest();
    // xhr.addEventListener("readystatechange", function () {
    //   if (this.readyState === 4) {
    //     var data = JSON.parse(xhr.responseText);
    //     console.log(data);
    //     if (data.code === 0) {
    //       alert("register successfully!");
    //       var data = JSON.parse(xhr.responseText);
    //       console.log(data);
    //       // 跳转到主界面
    //       window.location.href = "index.html";
    //     }
    //   }

    //   // var back
    //   xhr.open("POST", backendUrl + "/user/register");
    //   xhr.withCredentials = false;
    //   xhr.setRequestHeader("Content-Type", "application/json");
    //   xhr.setRequestHeader("Accept", "*/*");
    //   var data = JSON.stringify({
    //     username: username,
    //     password: password,
    //   });

    //   xhr.send(data);
    // });
  });
});
