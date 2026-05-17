
(function () {
  function text(v) {
    return String(v || "").trim();
  }

  function setName(name) {
    var el = document.getElementById("web_title_user_name");
    if (!el) return;
    el.textContent = text(name) || "-";
  }

  function fallbackName() {
    var keys = [
      "xunnan_employee_display_name",
      "xunnan_display_name",
      "xunnan_employee_name",
      "xunnan_engineer_name",
      "xunnan_admin_name"
    ];
    for (var i = 0; i < keys.length; i += 1) {
      try {
        var v = localStorage.getItem(keys[i]) || sessionStorage.getItem(keys[i]);
        if (text(v)) return v;
      } catch (e) {}
    }
    return "";
  }

  setName(fallbackName() || "登入者");

  fetch("/api/app/employee/profile?ts=" + Date.now(), {
    cache: "no-store",
    credentials: "same-origin"
  })
    .then(function (res) {
      if (!res || !res.ok) return null;
      return res.json();
    })
    .then(function (data) {
      if (!data) return;
      var p = data.profile || data.data || data;
      var name =
        p.display_name ||
        p.acting_display_name ||
        p.login_display_name ||
        p.staff_code ||
        data.display_name ||
        data.staff_code ||
        "";
      setName(name || fallbackName() || "登入者");
    })
    .catch(function () {
      setName(fallbackName() || "登入者");
    });
})();
