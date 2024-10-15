import React from "react";
import ReactDOM from "react-dom";

export function bind(node) {
  return {
    create: (type, props, children) =>
      React.createElement(type, props, ...children),
    render: (element) => {
      ReactDOM.render(element, node);
    },
    unmount: () => ReactDOM.unmountComponentAtNode(node),
  };
}

export function History({ onHistoryChangeCallback }) {
  // Capture browser "history go back" action and tell the server about it
  // Note: Browsers do not allow us to detect "history go forward" actions.
  React.useEffect(() => {
    // Register a listener for the "popstate" event and send data back to the server using the `onHistoryChange` callback.
    const listener = () => {
      onHistoryChangeCallback({
        pathname: window.location.pathname,
        search: window.location.search,
      });
    };

    // Register the event listener
    window.addEventListener("popstate", listener);

    // Delete the event listener when the component is unmounted
    return () => window.removeEventListener("popstate", listener);
  });

  // Tell the server about the URL during the initial page load
  // FIXME: This currently runs every time any component is mounted due to a ReactPy core rendering bug.
  // https://github.com/reactive-python/reactpy/pull/1224
  // React.useEffect(() => {
  //   onHistoryChange({
  //     pathname: window.location.pathname,
  //     search: window.location.search,
  //   });
  //   return () => {};
  // }, []);
  return null;
}

// FIXME: The Link component is unused due to a ReactPy core rendering bug
// which causes duplicate rendering (and thus duplicate event listeners).
// https://github.com/reactive-python/reactpy/pull/1224
export function Link({ onClickCallback, linkClass }) {
  // This component is not the actual anchor link.
  // It is an event listener for the link component created by ReactPy.
  React.useEffect(() => {
    // Event function that will tell the server about clicks
    const handleClick = (event) => {
      event.preventDefault();
      let to = event.target.getAttribute("href");
      window.history.pushState(null, "", new URL(to, window.location));
      onClickCallback({
        pathname: window.location.pathname,
        search: window.location.search,
      });
    };

    // Register the event listener
    let link = document.querySelector(`.${linkClass}`);
    if (link) {
      link.addEventListener("click", handleClick);
    }

    // Delete the event listener when the component is unmounted
    return () => {
      let link = document.querySelector(`.${linkClass}`);
      if (link) {
        link.removeEventListener("click", handleClick);
      }
    };
  });
  return null;
}

export function Navigate({ onNavigateCallback, to, replace }) {
  React.useEffect(() => {
    if (replace) {
      window.history.replaceState(null, "", new URL(to, window.location));
    } else {
      window.history.pushState(null, "", new URL(to, window.location));
    }
    onNavigateCallback({
      pathname: window.location.pathname,
      search: window.location.search,
    });
    return () => {};
  }, []);

  return null;
}
