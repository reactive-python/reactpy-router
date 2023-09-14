import React from "react";
import ReactDOM from "react-dom";
import htm from "htm";

const html = htm.bind(React.createElement);

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
  // capture changes to the browser's history
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

export function Link({ to, onClick, children, ...props }) {
  const handleClick = (event) => {
    event.preventDefault();
    window.history.pushState({}, to, new URL(to, window.location));
    onClick({
      pathname: window.location.pathname,
      search: window.location.search,
    });
  };

  return html`<a href=${to} onClick=${handleClick} ...${props}>${children}</a>`;
}
