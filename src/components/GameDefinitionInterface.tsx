import React, { FunctionComponent } from "react";

export const GameDefinitionInterface: FunctionComponent = () => {
    var entrystack = document.createElement('div')
    for (var i = 0; i < 5; i++) {
    var el = document.createElement('div');
    var child = document.createElement('input');
    child.setAttribute('type', 'text');
    el.appendChild(child);
    entrystack.appendChild(el);
    }
    
    return(
        <div>
        <div>
            Game Definition
        </div>
        </div>
    );
}