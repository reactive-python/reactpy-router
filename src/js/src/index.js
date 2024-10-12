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

export function History({ onBrowserBack }) {
  // Capture browser "history go back" action and tell the server about it
  // Note: Browsers do not allow you to detect "history go forward" actions.
  React.useEffect(() => {
    // Register a listener for the "popstate" event and send data back to the server using the `onBrowserBack` callback.
    const listener = () => {
      onBrowserBack({
        pathname: window.location.pathname,
        search: window.location.search,
      });
    };

    // Register the event listener
    window.addEventListener("popstate", listener);

    // Delete the event listener when the component is unmounted
    return () => window.removeEventListener("popstate", listener);
  });
  return null;
}

export function Link({ onClick, linkClass }) {
  // This component is not the actual anchor link.
  // It is an event listener for the link component created by ReactPy.
  React.useEffect(() => {
    // Event function that will tell the server about clicks
    const handleClick = (event) => {
      event.preventDefault();
      let to = event.target.getAttribute("href");
      window.history.pushState({}, to, new URL(to, window.location));
      onClick({
        pathname: window.location.pathname,
        search: window.location.search,
      });
    };

    // Register the event listener
    document
      .querySelector(`.${linkClass}`)
      .addEventListener("click", handleClick);

    // Delete the event listener when the component is unmounted
    return () => {
      document
        .querySelector(`.${linkClass}`)
        .removeEventListener("click", handleClick);
    };
  });
  return null;
}
