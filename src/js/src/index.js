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

/**
 * History component that captures browser "history go back" actions and notifies the server.
 *
 * @param {Object} props - The properties object.
 * @param {Function} props.onHistoryChangeCallback - Callback function to notify the server about history changes.
 * @returns {null} This component does not render any visible output.
 * @description
 * This component uses the `popstate` event to detect when the user navigates back in the browser history.
 * It then calls the `onHistoryChangeCallback` with the current pathname and search parameters.
 * Note: Browsers do not allow detection of "history go forward" actions.
 * @see https://github.com/reactive-python/reactpy/pull/1224
 */
export function History({ onHistoryChangeCallback }) {
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
 * @param {Object} props - The properties object.
 * @param {Function} props.onClickCallback - Callback function to notify the server about link clicks.
 * @param {string} props.linkClass - The class name of the anchor link.
 * @returns {null} This component does not render any visible output.
 */
export function Link({ onClickCallback, linkClass }) {
  // FIXME: This component is currently unused due to a ReactPy core rendering bug
  // which causes duplicate rendering (and thus duplicate event listeners).
  // https://github.com/reactive-python/reactpy/pull/1224

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

/**
 * Client-side portion of the navigate component, that allows the server to command the client to change URLs.
 *
 * @param {Object} props - The properties object.
 * @param {Function} props.onNavigateCallback - Callback function that transmits data to the server.
 * @param {string} props.to - The target URL to navigate to.
 * @param {boolean} props.replace - If true, replaces the current history entry instead of adding a new one.
 * @returns {null} This component does not render anything.
 */
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

/**
 * FirstLoad component that captures the URL during the initial page load and notifies the server.
 *
 * @param {Object} props - The properties object.
 * @param {Function} props.onFirstLoadCallback - Callback function to notify the server about the first load.
 * @returns {null} This component does not render any visible output.
 * @description
 * This component sends the current URL to the server during the initial page load.
 * @see https://github.com/reactive-python/reactpy/pull/1224
 */
export function FirstLoad({ onFirstLoadCallback }) {
  // FIXME: This component only exists because of a ReactPy core rendering bug, and should be removed when the bug
  // is fixed. Ideally all this logic would be handled by the `History` component.
  React.useEffect(() => {
    onFirstLoadCallback({
      pathname: window.location.pathname,
      search: window.location.search,
    });
    return () => {};
  }, []);
  return null;
}
