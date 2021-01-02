import React, { FunctionComponent } from 'react';
import styled from 'styled-components';
import { GameStateInterface } from '../components/GameStateInterface';
import { GameDefinitionInterface} from '../components/GameDefinitionInterface';
import { LegalMovesInterface} from '../components/LegalMovesInterface';

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
                <GameDefinitionInterface/>
            </div>
            <div>
                <GameStateInterface/>
            </div>
            <div>
                <LegalMovesInterface/>
            </div>
        </Wrapper>
    );
}