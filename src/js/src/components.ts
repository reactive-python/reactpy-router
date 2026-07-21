import { React } from "@reactpy/client";
import { createLocationObject, pushState, replaceState } from "./utils";
import {
  HistoryProps,
  LinkProps,
  NavigateProps,
  ScrollRestorationProps,
} from "./types";

/**
 * Interface used to bind a ReactPy node to React.
 */
export function bind(node: HTMLElement | Element | Node) {
  return {
    create: (
      type: string,
      props: Record<string, unknown>,
      children: React.ReactNode[],
    ) => React.createElement(type, props, ...children),
    render: (element: HTMLElement | Element | Node) => {
      React.render(element, node);
    },
    unmount: () => React.render(null, node),
  };
}

/**
 * History component that captures browser "history go back" actions and notifies the server.
 */
export function History({ onHistoryPreviousCallback }: HistoryProps): null {
  // Tell the server about history "popstate" events
  React.useEffect(() => {
    const listener = () => {
      onHistoryPreviousCallback(createLocationObject());
    };

    // Register the event listener
    window.addEventListener("popstate", listener);

    // Delete the event listener when the component is unmounted
    return () => window.removeEventListener("popstate", listener);
  });
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
    // Event function that will tell the server about clicks.
    // Preserve the browser's default behavior (open in new tab/window) for
    // modifier-clicks and middle-click — only plain left-clicks are routed
    // through the SPA history handler.
    const handleClick = (event: Event) => {
      let click_event = event as MouseEvent;
      const isPlainLeftClick =
        click_event.button === 0 &&
        !click_event.ctrlKey &&
        !click_event.metaKey &&
        !click_event.shiftKey &&
        !click_event.altKey;
      if (isPlainLeftClick) {
        event.preventDefault();
        let to = (event.currentTarget as HTMLElement).getAttribute("href");
        if (to) {
          pushState(to);
          onClickCallback(createLocationObject());
        }
      }
    };

    // Register the event listener on every anchor sharing this link's class.
    // A page may render multiple links that share the unique class (e.g. when
    // the same `link` component is reused), so use querySelectorAll rather
    // than querySelector to wire all of them.
    const links = document.querySelectorAll(`.${linkClass}`);
    if (links.length === 0) {
      console.warn(`Link component with class name ${linkClass} not found.`);
    } else {
      links.forEach((link) => {
        link.addEventListener("click", handleClick);
      });
    }

    // Delete the event listeners when the component is unmounted
    return () => {
      links.forEach((link) => {
        link.removeEventListener("click", handleClick);
      });
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
    if (typeof to === "number") {
      // Relative history navigation (e.g. go back / go forward).
      // The resulting popstate event is picked up by the History
      // component, so no explicit callback is needed here.
      window.history.go(to);
    } else {
      if (replace) {
        replaceState(to);
      } else {
        pushState(to);
      }
      onNavigateCallback(createLocationObject());
    }
    return () => {};
  }, []);

  return null;
}

// Module-level scroll positions keyed by pathname. Shared across all
// ScrollRestoration component instances so saved positions survive
// unmount/remount during route transitions.
const _scrollPositions: Record<string, { x: number; y: number }> = {};

/**
 * ScrollRestoration component that saves and restores scroll positions across
 * client-side navigation. Uses the browser's History API to track scroll
 * positions keyed by URL pathname.
 *
 * On mount, it:
 * - Disables the browser's native scroll restoration
 * - Patches pushState/replaceState to save scroll positions before navigation
 * - Listens for popstate to save the leaving page's scroll
 * - Restores any previously saved scroll position for the current pathname
 *
 * Scroll positions are consumed on restore so subsequent re-renders on the same
 * page do not snap the user back. The module-level store survives the
 * component's unmount/remount cycle across route transitions.
 */
export function ScrollRestoration({}: ScrollRestorationProps): null {
  const lastPathRef = React.useRef(window.location.pathname);

  React.useEffect(() => {
    // Restore any saved scroll position for the current pathname on mount.
    // The component mounts/unmounts on route changes, so this runs once
    // per navigation. The position is consumed after restoration.
    const currentKey = window.location.pathname;
    const savedPos = _scrollPositions[currentKey];
    if (savedPos) {
      delete _scrollPositions[currentKey];
      requestAnimationFrame(() => {
        window.scrollTo(savedPos.x, savedPos.y);
      });
    }

    window.history.scrollRestoration = "manual";

    // Patch pushState to save scroll before URL changes
    const originalPushState = window.history.pushState.bind(window.history);
    window.history.pushState = (data, unused, url) => {
      const key = window.location.pathname;
      _scrollPositions[key] = { x: window.scrollX, y: window.scrollY };
      originalPushState(data, unused, url);
      lastPathRef.current = window.location.pathname;
    };

    // Patch replaceState to save scroll before URL changes
    const originalReplaceState = window.history.replaceState.bind(
      window.history,
    );
    window.history.replaceState = (data, unused, url) => {
      const key = window.location.pathname;
      _scrollPositions[key] = { x: window.scrollX, y: window.scrollY };
      originalReplaceState(data, unused, url);
      lastPathRef.current = window.location.pathname;
    };

    // On popstate, save the scroll of the page we're leaving.
    // The popstate event fires before the next render, so we use
    // lastPathRef (the pathname before navigation) as the key.
    const handlePopState = () => {
      const leavingPath = lastPathRef.current;
      _scrollPositions[leavingPath] = { x: window.scrollX, y: window.scrollY };
      lastPathRef.current = window.location.pathname;
    };

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
      window.history.pushState = originalPushState;
      window.history.replaceState = originalReplaceState;
    };
  }, []);

  return null;
}
