import { ReactPyLocation } from "./types";

export function createLocationObject(): ReactPyLocation {
  return {
    pathname: window.location.pathname,
    search: window.location.search,
  };
}

export function pushState(to: string): void {
  window.history.pushState(null, "", new URL(to, window.location.href));
}

export function replaceState(to: string): void {
  window.history.replaceState(null, "", new URL(to, window.location.href));
}
