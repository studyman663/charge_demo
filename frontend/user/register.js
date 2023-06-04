// 在页面加载完成后绑定事件监听器
window.addEventListener("DOMContentLoaded", function() {
    // 获取登录按钮元素
    var loginButton = document.getElementById("u30");
    // 绑定点击事件监听器
    loginButton.addEventListener("click", function() {
      // 获取用户名和密码输入框的值
      
      console.log("backendUrl");
      var username = document.getElementById("u36_input").value;
      var password = document.getElementById("u33_input").value;
      var confirmPassword = document.getElementById("u27_input").value;
      var backendUrl = document.getElementById("v36_input").value;
      console.log(backendUrl);
  
       if (username.trim() === '用户名') {
      alert('请输入用户名');
      return false;
    }
      else if (password.trim() === '密码') {
      alert('请输入密码');
      return false;
    }
      else if (confirmPassword.trim() === '密码') {
      alert('请输入确认密码');
      return false;
    }
      else if (password !== confirmPassword) {
      alert('密码和确认密码不一致');
      return false;
    }
  
      // 发送 AJAX 请求
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.addEventListener("readystatechange", function () {
      if (this.readyState === 4) {
        if (this.status === 201) {
         alert("register successfully!");
          // 跳转到主界面
          window.location.href = "login.html";
        } else {
      alert("error: register failed");
        }
      }
    });
    
    // var back
    xhr.open("POST", backendUrl + "/user/register");
    console.log(backendUrl + "/user/register");
    xhr.setRequestHeader("User-Agent", "Apifox/1.0.0 (https://www.apifox.com)");
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
  });