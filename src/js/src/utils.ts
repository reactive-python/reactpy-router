import { ReactPyLocation } from "./types";

export function createLocationObject(): ReactPyLocation {
  return {
    path: window.location.pathname,
    query_string: window.location.search,
  };
}

export function pushState(to: any): void {
  if (typeof to !== "string") {
    console.error("pushState() requires a string argument.");
    return;
  }
  window.history.pushState(null, "", new URL(to, window.location.href));
}

export function replaceState(to: any): void {
  if (typeof to !== "string") {
    console.error("replaceState() requires a string argument.");
    return;
  }
  window.history.replaceState(null, "", new URL(to, window.location.href));
}
