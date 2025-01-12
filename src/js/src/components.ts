import React from "preact/compat";
import ReactDOM from "preact/compat";
import { createLocationObject, pushState, replaceState } from "./utils";
import { HistoryProps, LinkProps, NavigateProps } from "./types";

/**
 * Interface used to bind a ReactPy node to React.
 */
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

/**
 * History component that captures browser "history go back" actions and notifies the server.
 */
export function History({ onHistoryChangeCallback }: HistoryProps): null {
  // Tell the server about history "popstate" events
  React.useEffect(() => {
    const listener = () => {
      onHistoryChangeCallback(createLocationObject());
    };

    // Register the event listener
    window.addEventListener("popstate", listener);

    // Delete the event listener when the component is unmounted
    return () => window.removeEventListener("popstate", listener);
  });

  // Tell the server about the URL during the initial page load
  React.useEffect(() => {
    onHistoryChangeCallback(createLocationObject());
    return () => {};
  }, []);
  return null;
}

/**
 * Link component that captures clicks on anchor links and notifies the server.
 *
 * This component is not the actual `<a>` link element. It is just an event
 * listener for ReactPy-Router's server-side link component.
 */
export function Link({ onClickCallback, linkClass }: LinkProps): null {
  React.useEffect(() => {
    // Event function that will tell the server about clicks
    const handleClick = (event: Event) => {
      let click_event = event as MouseEvent;
      if (!click_event.ctrlKey) {
        event.preventDefault();
        let to = (event.currentTarget as HTMLElement).getAttribute("href");
        pushState(to);
        onClickCallback(createLocationObject());
      }
    };

    // Register the event listener
    let link = document.querySelector(`.${linkClass}`);
    if (link) {
      link.addEventListener("click", handleClick);
    } else {
      console.warn(`Link component with class name ${linkClass} not found.`);
    }

    // Delete the event listener when the component is unmounted
    return () => {
      if (link) {
        link.removeEventListener("click", handleClick);
      }
    };
  });
  return null;
}

/**
 * Client-side portion of the navigate component, that allows the server to command the client to change URLs.
 */
export function Navigate({
  onNavigateCallback,
  to,
  replace = false,
}: NavigateProps): null {
  React.useEffect(() => {
    if (replace) {
      replaceState(to);
    } else {
      pushState(to);
    }
    onNavigateCallback(createLocationObject());
    return () => {};
  }, []);

  return null;
}
