jQuery ->
  "use strict"

  token = window.SIGNIN.token
  if not token
    return

  pageName = if $("body.userid").length then "userid" else "password"

  reportEvent = (eventName) ->
    $.post(
      "/events",
      page: pageName
      event: eventName
      token: token
    )

  if pageName is "userid"
    userIdWasEntered = false
    $("form #UserIDinput").change ->
      if not userIdWasEntered
        userIdWasEntered = true
        reportEvent("userid entered")

  if pageName is "password"
    passwordWasEntered = false
    passwordInput = $("form #passwordInput")
    passwordInput.change ->
      if not passwordWasEntered
        passwordWasEntered = true
        reportEvent("password entered")
    $("form").submit ->
      passwordInput.remove()
