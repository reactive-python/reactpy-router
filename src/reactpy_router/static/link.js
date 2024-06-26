document.getElementById("UUID").addEventListener("click", (event) => {
    event.preventDefault();
    window.history.pushState({}, to, new URL(to, window.location));
    onClick({
        pathname: window.location.pathname,
        search: window.location.search,
    });
});
