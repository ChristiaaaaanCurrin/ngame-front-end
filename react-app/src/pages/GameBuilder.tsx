import React, { FunctionComponent } from 'react';
import styled from 'styled-components';

const Wrapper = styled.div`
    text-align: left;
    color: red;
    display: flex;
    justify-content: space-around;
`;

export const GameBuilder: FunctionComponent = () => {
    return(
        <Wrapper>
            <div>
                left    
            </div>
            <div>
                middle
            </div>
            <div>
                right
            </div>
        </Wrapper>
    );
}