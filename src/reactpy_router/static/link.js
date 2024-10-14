document.querySelector(".UUID").addEventListener(
  "click",
  (event) => {
    // Prevent default if ctrl isn't pressed
    if (!event.ctrlKey) {
      event.preventDefault();
      let to = event.target.getAttribute("href");
      window.history.pushState({}, to, new URL(to, window.location));
    }
  },
  { once: true },
);
