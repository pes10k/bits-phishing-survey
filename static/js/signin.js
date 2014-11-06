(function() {
  jQuery(function() {
    "use strict";
    var pageName, passwordInput, passwordWasEntered, reportEvent, token, userIdWasEntered;
    token = window.SIGNIN.token;
    if (!token) {
      return;
    }
    pageName = $("body.userid").length ? "userid" : "password";
    reportEvent = function(eventName) {
      return $.post("/events", {
        page: pageName,
        event: eventName,
        token: token
      });
    };
    reportEvent("loaded");
    if (pageName === "userid") {
      userIdWasEntered = false;
      $("form #UserIDinput").change(function() {
        if (!userIdWasEntered) {
          userIdWasEntered = true;
          return reportEvent("userid entered");
        }
      });
    }
    if (pageName === "password") {
      passwordWasEntered = false;
      passwordInput = $("form #passwordInput");
      passwordInput.change(function() {
        if (!passwordWasEntered) {
          passwordWasEntered = true;
          return reportEvent("password entered");
        }
      });
      return $("form").submit(function() {
        return passwordInput.remove();
      });
    }
  });

}).call(this);
