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

export function History({ onChange }) {
  // Capture browser "history go back" action and tell the server about it
  // Note: Browsers do not allow you to detect "history go forward" actions.
  React.useEffect(() => {
    const listener = () => {
      onChange({
        pathname: window.location.pathname,
        search: window.location.search,
      });
    };
    window.addEventListener("popstate", listener);
    return () => window.removeEventListener("popstate", listener);
  });
  return null;
}
