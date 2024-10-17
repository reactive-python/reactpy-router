document.querySelector(".UUID").addEventListener(
  "click",
  (event) => {
    // Prevent default if ctrl isn't pressed
    if (!event.ctrlKey) {
      event.preventDefault();
      let to = event.target.getAttribute("href");
      let new_url = new URL(to, window.location);

      // Deduplication needed due to ReactPy rendering bug
      if (new_url.href !== window.location.href) {
        window.history.pushState(null, "", new URL(to, window.location));
      }
    }
  },
  { once: true },
);
