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

export function History({ onChange }) {
    // capture changes to the browser's history
    React.useEffect(() => {
        const listener = () => {
            onChange({
                pathname: window.location.pathname,
                search: window.location.search,
            });
        };
        window.addEventListener("popstate", listener);
        return () => window.removeEventListener("popstate", listener);
    });
    return null;
}
