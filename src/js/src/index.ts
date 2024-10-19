import React from "preact/compat";
import ReactDOM from "preact/compat";
import { createLocationObject, pushState, replaceState } from "./utils";
import {
  HistoryProps,
  LinkProps,
  NavigateProps,
  FirstLoadProps,
} from "./types";

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
  React.useEffect(() => {
    // Register a listener for the "popstate" event and send data back to the server using the `onHistoryChange` callback.
    const listener = () => {
      onHistoryChangeCallback(createLocationObject());
    };

    // Register the event listener
    window.addEventListener("popstate", listener);

    // Delete the event listener when the component is unmounted
    return () => window.removeEventListener("popstate", listener);
  });

  // Tell the server about the URL during the initial page load
  // FIXME: This code is commented out since it currently runs every time any component
  // is mounted due to a ReactPy core rendering bug. `FirstLoad` component is used instead.
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

/**
 * Link component that captures clicks on anchor links and notifies the server.
 *
 * This component is not the actual `<a>` link element. It is just an event
 * listener for ReactPy-Router's server-side link component.
 *
 * @disabled This component is currently unused due to a ReactPy core rendering bug
 * which causes duplicate rendering (and thus duplicate event listeners).
 */
export function Link({ onClickCallback, linkClass }: LinkProps): null {
  React.useEffect(() => {
    // Event function that will tell the server about clicks
    const handleClick = (event: MouseEvent) => {
      event.preventDefault();
      let to = (event.target as HTMLElement).getAttribute("href");
      pushState(to);
      onClickCallback(createLocationObject());
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
      let link = document.querySelector(`.${linkClass}`);
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

/**
 * FirstLoad component that captures the URL during the initial page load and notifies the server.
 *
 * FIXME: This component only exists because of a ReactPy core rendering bug, and should be removed when the bug
 * is fixed. In the future, all this logic should be handled by the `History` component.
 * https://github.com/reactive-python/reactpy/pull/1224
 */
export function FirstLoad({ onFirstLoadCallback }: FirstLoadProps): null {
  React.useEffect(() => {
    onFirstLoadCallback(createLocationObject());
    return () => {};
  }, []);

  return null;
}
