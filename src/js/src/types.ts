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
  to: string | number;
  replace?: boolean;
}

export interface FormSubmitData {
  form_data: Record<string, string[]>;
  location: ReactPyLocation;
}

export interface FormProps {
  onSubmitCallback: (data: FormSubmitData) => void;
  formClass: string;
}
