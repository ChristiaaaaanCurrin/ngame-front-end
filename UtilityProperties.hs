data Game s m p v = Game {legal :: s -> [m], execute :: s -> m -> s}

data GameState m p = GameState {players :: [p], turn :: p}

type Utility s p v = (s -> p -> v)


maxElem :: Ord b => (a -> b) -> [a] -> a
maxElem f (x:[]) = x
maxElem f (x:y:xs)
  | f x < f y = maxElem f (y:xs)
  | otherwise = maxElem f (x:xs)

minElem :: Ord b => (a -> b) -> [a] -> a
minElem f (x:[]) = x
minElem f (x:y:xs)
  | f x > f y = minElem f (y:xs)
  | otherwise = minElem f (x:xs)


max_n :: (Ord v, Num v) => Utility (GameState m p) p v -> Game (GameState m p) m p v -> v -> GameState m p -> p -> v
max_n u g 0 s p = u s p
max_n u g d s p
  | null $ legal g s = u s p
  | otherwise        = maxElem ($ turn s) [max_n u g (d-1) ns | ns <- [execute g s m | m <- legal g s]] $ p 

bestLine  :: Ord v => Utility (GameState m p) p v -> Game (GameState m p) m p v -> p -> GameState m p -> GameState m p
bestLine  u g p s = maxElem (flip u p) [execute g s m | m <- legal g s]

worstLine :: Ord v => Utility (GameState m p) p v -> Game (GameState m p) m p v -> p -> GameState m p -> GameState m p
worstLine u g p s = minElem (flip u p) [execute g s m | m <- legal g s]

nearPref :: (Num v, Ord v) => Int -> Utility (GameState m p) p v -> Utility (GameState m p) p v -> Game (GameState m p) m p v -> GameState m p -> v
nearPref k v u g s = (1 + d) * (u s p)
  where p = maxElem (v s) $ players s
        d
         | any (\x -> v s p /= v x p) $ take k $ iterate (worstLine v g p) s = 0
         | otherwise = head $ filter (\x -> any (\y -> v s p /= v y p) $ take k $ iterate (bestLine (max_n u g x) g p) s) $ map fromInteger [1..]

--DON'T HAVE TO ITERATE!!! TRUST VALUE FUNCTION AND JUST GO 1 LEVEL DOWN.

{-
 ,,
/  \\
 /  \_____ ~,
 (  )     )```
 //_// ||/
   /  / /
-}
