module UtilityAnalysis (Game, GameState, Utility,
                       maxElem, minElem, max_n,
                       bestLine, worstLine, nearPref) where


--Equivalent to "Piece" in piece.py and "Game" class in proto.py
data Game s m p v = Game {legal :: s -> [m], execute :: s -> m -> s}

--Equivalent to "GameState" in game_state.py and proto.py
data GameState m p = GameState {players :: [p], turn :: p}

--Any UTILITY function for a game_state
type Utility s p v = (s -> p -> v)


--Like maximum but returns the element from the list that produces the maximum output when used as the input to a function
maxElem :: Ord b => (a -> b) -> [a] -> a
maxElem f (x:[]) = x
maxElem f (x:y:xs)
  | f x < f y = maxElem f (y:xs)
  | otherwise = maxElem f (x:xs)

--See above but replace "maximum" with "minimum
minElem :: Ord b => (a -> b) -> [a] -> a
minElem f (x:[]) = x
minElem f (x:y:xs)
  | f x > f y = minElem f (y:xs)
  | otherwise = minElem f (x:xs)

--Compare to "max_n" in game_state.py. Haskell, I have missed you!
max_n :: (Ord v, Num v) => Utility (GameState m p) p v -> Game (GameState m p) m p v -> v -> GameState m p -> p -> v
max_n u g 0 s p = u s p
max_n u g d s p
  | null $ legal g s = u s p
  | otherwise        = maxElem ($ turn s) [max_n u g (d-1) ns | ns <- [execute g s m | m <- legal g s]] $ p 


--Returns the GameState (selected from legal moves on the current GameState) that has the hightest utility for a given player
bestLine  :: Ord v => Utility (GameState m p) p v -> Game (GameState m p) m p v -> p -> GameState m p -> GameState m p
bestLine  u g p s = maxElem (flip u p) [execute g s m | m <- legal g s]

--Returns the GameState (selected from legal moves on the current GameState) that has the lowest   utility for a given player
worstLine :: Ord v => Utility (GameState m p) p v -> Game (GameState m p) m p v -> p -> GameState m p -> GameState m p
worstLine u g p s = minElem (flip u p) [execute g s m | m <- legal g s]

--Scores the degeee to which a UTILITY function is NEAR PREFERENTIAL according to a gold standard VALUE function
nearPref :: (Num v, Ord v) => Utility (GameState m p) p v -> Utility (GameState m p) p v -> Game (GameState m p) m p v -> GameState m p -> v
nearPref v u g s = (1 + d) * (u s p)
  where p = maxElem (v s) $ players s
        d
         | v s p /= v (worstLine v g p s) p = 0
         | otherwise = head $ filter (\x -> v s p /= v (bestLine (max_n u g x) g p s) p) $ map fromInteger [1..]


{-
A UTILITY function is NEAR PREFERENTIAL if it information about how deep of a max_n tree using the UTILITY is required
by the current winning PLAYER in order to stay winning. This relationship should follow the form:

   (u s p) * d = 1

where u is the UTILITY
      d is the depth of the max_n tree
      v is the VALUE
      p is the PLAYER most winning according to the VALUE,
      s is the GameState

 * Winningness is determined by a gold standard VALUE function
   The UTILITY function should never have an output:
     greater than the maximum output of the VALUE function
     or less than the minimum output of the VALUE function.
 
 ,,
/  \\
 /  \_____ ~,
 (  )     )```
 //_// ||/
   /  / /
-}
