document.querySelector(".UUID").addEventListener(
  "click",
  (event) => {
    let to = event.target.getAttribute("href");
    window.history.pushState({}, to, new URL(to, window.location));
  },
  { once: true },
);
