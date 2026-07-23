import { React } from "@reactpy/client";
import { createLocationObject, pushState, replaceState } from "./utils";
import { HistoryProps, LinkProps, NavigateProps, FormProps } from "./types";

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

/**
 * Form component that intercepts form submissions and notifies the server
 * instead of performing a full page reload.
 *
 * This component is not the actual `<form>` element. It is just an event
 * listener for ReactPy-Router's server-side form component.
 */
export function Form({ onSubmitCallback, formClass }: FormProps): null {
  React.useEffect(() => {
    const handleSubmit = (event: Event) => {
      event.preventDefault();
      const form = event.currentTarget as HTMLFormElement;
      const formData = new FormData(form);

      // Serialize FormData to a Record<string, string[]>
      const serialized: Record<string, string[]> = {};
      for (const [key, value] of formData.entries()) {
        if (!serialized[key]) {
          serialized[key] = [];
        }
        serialized[key].push(value.toString());
      }

      // Build the action URL with form data as query params (GET-style)
      let action = form.getAttribute("action") || window.location.pathname;
      const params = new URLSearchParams();
      for (const [key, values] of Object.entries(serialized)) {
        for (const value of values) {
          params.append(key, value);
        }
      }
      const queryString = params.toString();
      if (queryString) {
        action += (action.includes("?") ? "&" : "?") + queryString;
      }

      pushState(action);
      onSubmitCallback({
        form_data: serialized,
        location: createLocationObject(),
      });
    };

    const forms = document.querySelectorAll(`form.${formClass}`);
    if (forms.length === 0) {
      console.warn(`Form component with class name ${formClass} not found.`);
    } else {
      forms.forEach((form) => {
        form.addEventListener("submit", handleSubmit);
      });
    }

    return () => {
      forms.forEach((form) => {
        form.removeEventListener("submit", handleSubmit);
      });
    };
  });
  return null;
}
