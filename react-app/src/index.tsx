import { history } from './history';

import React, { FunctionComponent } from 'react';
import ReactDom from 'react-dom';
import {
    Router, Switch, Route, Link, withRouter
} from 'react-router-dom';
import { GameBuilder } from './pages/GameBuilder';

const Bootstrap : FunctionComponent = () => {
    return(
        <>
            <div><GameBuilder/></div>
        </>
    );
}

ReactDom.render(
    <Bootstrap />,
    document.getElementById('root')
);
