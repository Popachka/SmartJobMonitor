(function () {
  const webApp = window.Telegram && window.Telegram.WebApp;
  if (webApp) {
    webApp.ready();
    webApp.expand();
  }

  const statusNode = document.querySelector("[data-status]");
  const actionButtons = document.querySelectorAll("[data-placeholder-action]");

  actionButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const message = "Это демо-шаблон. Логика сохранения будет подключена позже.";
      if (statusNode) {
        statusNode.textContent = message;
      }
      if (webApp && typeof webApp.showAlert === "function") {
        webApp.showAlert(message);
      }
    });
  });
})();
