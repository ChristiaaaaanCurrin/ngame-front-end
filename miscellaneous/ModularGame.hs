{-# LANGUAGE MultiParamTypeClasses #-}
{-# LANGUAGE FlexibleInstances #-}
import Data.Either

{-
class Set a where
  isElem :: b -> a -> Bool
  (|+|)  :: a -> a -> a
  (|&|)  :: a -> a -> a
  (|\|)  :: a -> a -> a

instance Eq a => Set [a] where
  isElem x xs = elem x xs
  xs |+| ys = xs ++ ys
  xs |&| ys = [x | x <- xs, elem x ys]
  xs |\| ys = [x | x <- xs, not $ elem x ys]

type Check a = a -> Bool 
instance Set (Check a) where
  f |+| g = \x -> f x || g x
  f |&| g = \x -> f x && g x
  f |\| g = \x -> f x && not $ g x
-}


class Set s e where
  isElem :: e -> s -> Bool

class Countable s e where
  toList   :: s -> [e]
  fromList :: [e] -> s

data U a b = U a b
data N a b = N a b
data Sub a b = Sub a b

instance (Set a e, Set b e) => Set (U a b) e where
  isElem x (U s t) = (isElem x s) || (isElem x t)

instance (Countable a e, Countable b e) => Countable (U a b) e where
  toList (U s t) = x:y:(toList $ U s' t') where
                   x = head $ toList s
                   y = head $ toList t
                   s' = fromList $ tail $ toList s
                   t' = fromList $ tail $ toList t

  fromList xs = U (fromList xs) (fromList [])

instance (Set a e, Set b e) => Set (N a b) e where
  isElem x (N s t) = (isElem x s) && (isElem x t)


