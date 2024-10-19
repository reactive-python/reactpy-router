export interface ReactPyLocation {
  pathname: string;
  search: string;
}

export interface HistoryProps {
  onHistoryChangeCallback: (location: ReactPyLocation) => void;
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

export interface FirstLoadProps {
  onFirstLoadCallback: (location: ReactPyLocation) => void;
}
