// import { history } from './history';

// import React, { FunctionComponent } from 'react';
// import ReactDom from 'react-dom';
// import {
//     Router, Switch, Route, Link
// } from 'react-router-dom';
// import { Button } from './components/Button';

// const Bootstrap : FunctionComponent = () => {
//     return(
//         <>
//         <Router history={history}>
//             <div>
//                 <Link to="/">
//                     Home
//                 </Link>
//                 <Link to="/dashboard">
//                     Dashboard
//                 </Link>
//             <Switch>
//                 <Route exact keys="/">
//                     <p>home component</p>
//                 </Route>
//                 <Route keys="/dashboard">
//                     <p>dashboard component</p>
//                     <Button/>
//                 </Route>
//             </Switch>
//             </div>
//         </Router>
//         </>
//     );
// }

// ReactDom.render(
//     <Bootstrap />,
//     document.getElementById('root')
// );
import { history } from './history';

import React, { FunctionComponent } from 'react';
import ReactDom from 'react-dom';
import styled from 'styled-components';

const StyledDiv = styled.div`
    color: blue;
`;

const Bootstrap: FunctionComponent = () => {
    return (
        <>
            <StyledDiv>
                hello
            </StyledDiv>
        </>
    );
}

ReactDom.render(
    <Bootstrap />,
    document.getElementById('root')
);