
(function () {
  function byId(id) {
    return document.getElementById(id);
  }

  function setStatus(text, tone) {
    var box = byId("security_status");
    box.textContent = text;
    box.classList.remove("ok", "err");
    if (tone) {
      box.classList.add(tone);
    }
  }

  function clearForm() {
    ["old_pin", "new_pin", "new_pin2"].forEach(function (id) {
      byId(id).value = "";
    });
    setStatus("\u8acb\u8f38\u5165\u539f PIN \u8207\u65b0 PIN\u3002", "");
  }

  async function changePassword() {
    var oldPin = byId("old_pin").value.trim();
    var newPin = byId("new_pin").value.trim();
    var newPin2 = byId("new_pin2").value.trim();

    if (!oldPin || !newPin || !newPin2) {
      setStatus("\u8acb\u8f38\u5165\u539f PIN \u8207\u65b0 PIN\u3002", "err");
      return;
    }

    if (newPin !== newPin2) {
      setStatus("\u5169\u6b21\u65b0 PIN \u4e0d\u4e00\u81f4\u3002", "err");
      return;
    }

    if (newPin.length < 4) {
      setStatus("PIN \u81f3\u5c11 4 \u78bc\u3002", "err");
      return;
    }

    setStatus("\u6b63\u5728\u66f4\u65b0 PIN...", "");

    var res = await fetch("/api/app/employee/change-password", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({
        old_pin: oldPin,
        new_pin: newPin,
        new_pin2: newPin2
      })
    });

    var data = await res.json().catch(function () {
      return {};
    });

    if (!res.ok || !data.ok) {
      setStatus(data.error || "\u5bc6\u78bc\u4fee\u6539\u5931\u6557\u3002", "err");
      return;
    }

    clearForm();
    setStatus("\u5bc6\u78bc\u5df2\u66f4\u65b0\u3002", "ok");
    alert("\u5bc6\u78bc\u5df2\u66f4\u65b0");
  }

  document.addEventListener("DOMContentLoaded", function () {
    byId("change_pin_btn").addEventListener("click", changePassword);
    byId("clear_btn").addEventListener("click", clearForm);
  });
})();
