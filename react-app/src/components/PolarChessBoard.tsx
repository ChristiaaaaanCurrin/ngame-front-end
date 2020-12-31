import React, { FunctionComponent } from "react";

type PolarChessProps = {
    rings: string
    players: string
    pieces: string
}

export const PolarChessBoard: FunctionComponent = () => {
    return(
        <svg overflow="visible">
            <circle cx="115" cy="115" r="100" fill="green"></circle>
            <path d="M115,115 L115,15 A100,100 1 0,1 215,115 z"></path>
            <path d="M115,115 L115,215 A100,100 1 0,1 15,115 z"></path>

            <circle cx="115" cy="115" r="33" fill="blue"></circle>
            
        </svg>

    );
}