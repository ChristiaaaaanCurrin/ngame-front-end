data Game s m p v = Game {legal :: s -> [m], execute :: s -> m -> s}

data GameState m p = GameState {players :: [p], turn :: p}

type Utility s p v = (s -> p -> v)

data Inf a = MINF | Finite a | INF deriving (Eq, Show, Read)

instance (Num a, Eq a) => Num (Inf a) where
  signum MINF       = signum $ fromInteger (-1)
  signum INF        = signum $ fromInteger   1
  signum (Finite x) = Finite (signum x)

  negate INF        = MINF
  negate MINF       = INF
  negate (Finite x) = Finite (negate x)

  INF      + MINF     = Finite 0
  INF      + _        = INF
  _        + MINF     = MINF
  Finite x + Finite y = Finite (x + y)
  x        + y        = y + x

  fromInteger x = Finite (fromInteger x)

  abs INF        = INF
  abs MINF       = INF
  abs (Finite x) = Finite (abs x)
  
  INF * x
    | x        == Finite 0      = 0
    | signum x == fromInteger 1 = INF
    | otherwise                 = MINF
  MINF * x = negate $ INF * x
  (Finite x) * (Finite y) = Finite (x * y)
  x * y = y * x


max_elem :: Ord b => (a -> b) -> [a] -> a
max_elem f (x:[]) = x
max_elem f (x:y:xs)
  | f x > f y = max_elem f (x:xs)
  | otherwise = max_elem f (y:xs)

max_n :: (Ord v, Integral a) => Utility (GameState m p) p v -> Game (GameState m p) m p v -> a -> GameState m p -> p -> v
max_n u g 0 s = u s $ turn s
max_n u g d s
  | null $ legal g s = u s $ turn s
  | otherwise        = maximum [max_n u g (d-1) ns | ns <- [execute g s m | m <- legal g s]] 

bestLine :: Ord v => Utility (GameState m p) p v -> Game (GameState m p) m p v -> GameState m p -> GameState m p
bestLine u g s = max_elem (flip u (turn s)) [execute g s m | m <- legal g s]

{-
nearPref :: (Ord v) => Utility (GameState m p) p v -> Game (GameState m p) m p v -> GameState m p -> v
nearPref v u g s = max_n v g  


 ,,
/  \\
 /  \_____ ~,
 (  )     )```
 //_// ||/
   /  / /
-}
