{-# LANGUAGE MultiParamTypeClasses #-}

module UtilityProperties (Game, GameState, Utility,
                          maxElem, minElem, max_n, partisan_max_n,
                          bestLine, worstLine, nearPref) where


--Equivalent to "Piece" in piece.py and "Game" class in proto.py
type Game s m = s -> [m]

class Move m s where
  execute :: m -> s -> s

--Equivalent to "GameState" in game_state.py and proto.py
class GameState s p where
  players :: s -> [p]
  toMove  :: s ->  p

--Any UTILITY function for a game_state
type Utility s p v = (s -> p -> v)

square x = x * x

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
max_n :: (Ord v, Num v, Move m s, GameState s p) => Utility s p v -> Game s m -> v -> s -> p -> v
max_n u g 0 s p = u s p
max_n u g d s p
  | null $ g s = u s p
  | otherwise  = maxElem ($ toMove s) [max_n u g (d-1) ns | ns <- [execute m s | m <- g s]] $ p 

--Similar to max_n utility function is now player dependent (so different players evaluate the board differently)
partisan_max_n :: (Ord v, Num v, Move m s, GameState s p) => (p -> Utility s p v) -> Game s m -> v -> s -> p -> v
partisan_max_n f g 0 s p = f (toMove s) s p
partisan_max_n f g d s p
  | null $ g s = f (toMove s) s p
  | otherwise = maxElem ($ toMove s) [partisan_max_n f g (d-1) ns | ns <- [execute m s | m <- g s]] $ p

--Returns the GameState (selected from legal moves on the current GameState) that has the highest utility for a given player
bestLine  :: (Ord v, GameState s p, Move m s) => Utility s p v -> Game s m -> p -> s -> s
bestLine  u g p s = maxElem (flip u p) [execute m s | m <- g s]

--Returns the GameState (selected from legal moves on the current GameState) that has the lowest  utility for a given player
worstLine  :: (Ord v, GameState s p, Move m s) => Utility s p v -> Game s m -> p -> s -> s
worstLine  u g p s = minElem (flip u p) [execute m s | m <- g s]


--Scores the degree to which a UTILITY function is NEAR PREFERENTIAL according to a gold standard VALUE function (0 is perfect score)
nearPref :: (Num v, Ord v, Move m s, GameState s p) => Utility s p v -> Utility s p v -> Game s m -> s -> v
nearPref v u g s = square $ (1 + d) * (u s p) - 1
  where p = maxElem (v s) $ players s
        d
         | v s p /= v (worstLine v g p s) p = 0
         | otherwise = head $ filter (\x -> v s p /= v (bestLine (max_n u g x) g p s) p) $ map fromInteger [1..]

{-
A UTILITY function is NEAR PREFERENTIAL if it encodes information about how deep of a max_n tree using the UTILITY is
required by the current winning PLAYER in order to stay winning. This relationship should follow the form:

   (u s p) * d = 1

where u is the UTILITY
      d is the depth of the max_n tree
      v is the VALUE
      p is the PLAYER most winning according to the VALUE
      s is the GameState

Winningness is determined by a gold standard VALUE function.
The VALUE function should be as close as possible to a minimax optimization of itself:

    v s p = max_n v g d s p for any depth, d

The UTILITY function should never have an output:
  greater than the maximum output of the VALUE function
  or less than the minimum output of the VALUE function
 
 ,,
/  \\
 /  \_____ ~,
 (  )     )```
 //_// ||/
   /  / /
-}
