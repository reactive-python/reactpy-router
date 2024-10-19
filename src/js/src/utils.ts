import { ReactPyLocation } from "./types";

export function createLocationObject(): ReactPyLocation {
  return {
    pathname: window.location.pathname,
    search: window.location.search,
  };
}
