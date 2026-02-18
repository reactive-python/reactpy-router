export interface ReactPyLocation {
  path: string;
  query_string: string;
}

export interface HistoryProps {
  onHistoryPreviousCallback: (location: ReactPyLocation) => void;
}

export interface LinkProps {
  onClickCallback: (location: ReactPyLocation) => void;
  linkClass: string;
}

export interface NavigateProps {
  onNavigateCallback: (location: ReactPyLocation) => void;
  to: string;
  replace?: boolean;
}
