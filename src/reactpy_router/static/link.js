document.querySelector(".UUID").addEventListener("click", (event) => {
  event.preventDefault();
  let to = event.target.getAttribute("href");
  window.history.pushState({}, to, new URL(to, window.location));
});
