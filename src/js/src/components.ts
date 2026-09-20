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

// How long (wall-clock) to keep re-asserting a restored scroll position while the
// destination route's content is still streaming in from the server. A fixed
// *frame* count is unreliable because frame cadence varies with CPU load: under a
// loaded CI runner the document can still be short (content not yet rendered) when
// a small frame budget expires, so `scrollTo` clamps against the not-yet-tall page
// and the position is silently lost. A time window is robust to both fast and slow
// frame cadences. The loop stops as soon as the target is reached, so a generous
// window only buys time for slow content — it never fights the user's own scroll.
const _scrollRestoreWindowMs = 1000;

// Sub-pixel tolerance for considering a scroll position "reached".
const _scrollTolerancePx = 2;

/**
 * ScrollRestoration component that saves and restores scroll positions across
 * client-side navigation.
 *
 * The one-time mount effect patches pushState/replaceState to save scroll
 * before navigation and registers a popstate listener. The post-render effect
 * (no deps) restores scroll for the current pathname whenever a saved position
 * exists — the position is kept alive in the module store so it remains
 * available across Preact's render commit cycle.
 */
export function ScrollRestoration({}: ScrollRestorationProps): null {
  const lastPathRef = React.useRef(window.location.pathname);

  // One-time setup: patch history methods and register popstate listener.
  React.useEffect(() => {
    window.history.scrollRestoration = "manual";

    const originalPushState = window.history.pushState.bind(window.history);
    window.history.pushState = (data, unused, url) => {
      const key = window.location.pathname;
      _scrollPositions[key] = { x: window.scrollX, y: window.scrollY };
      originalPushState(data, unused, url);
      lastPathRef.current = window.location.pathname;
    };

    const originalReplaceState = window.history.replaceState.bind(
      window.history,
    );
    window.history.replaceState = (data, unused, url) => {
      const key = window.location.pathname;
      _scrollPositions[key] = { x: window.scrollX, y: window.scrollY };
      originalReplaceState(data, unused, url);
      lastPathRef.current = window.location.pathname;
    };

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

  // After every render, restore scroll if a saved position exists for
  // the current pathname. The position is NOT deleted — it's kept alive
  // so Preact's render commits during navigation don't lose it.
  // It will be overwritten naturally when the user navigates away.
  React.useEffect(() => {
    const key = window.location.pathname;
    const pos = _scrollPositions[key];
    if (!pos) {
      return;
    }

    const reached = () =>
      Math.abs(window.scrollY - pos.y) <= _scrollTolerancePx &&
      Math.abs(window.scrollX - pos.x) <= _scrollTolerancePx;

    // Retry across animation frames until the target is reached, bounded by a
    // wall-clock window instead of a frame count. After a client-side navigation
    // the destination content is streamed in by the server, so the document can
    // still be too short to reach `pos` and scrollTo clamps against it; a small
    // frame budget can also expire far too early when frame cadence drops under
    // CPU load. Both cases would otherwise silently drop the restored position.
    const deadline = performance.now() + _scrollRestoreWindowMs;
    let frame = requestAnimationFrame(function tryRestore() {
      // Stop the moment the target is in place so we never fight scrolling the
      // user performs after the position has been restored.
      if (reached() || performance.now() >= deadline) {
        return;
      }
      window.scrollTo(pos.x, pos.y);
      frame = requestAnimationFrame(tryRestore);
    });

    // Effect cleanup runs before the next render's effect, so a re-render (or
    // unmount) cancels this attempt and no competing loops are left running.
    return () => cancelAnimationFrame(frame);
  });

  return null;
}
