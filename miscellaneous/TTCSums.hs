import UtilityProperties

board = [(x, y, 0) | x <- [0..2], y <- [0..2]]

d0 b  = [(x, y, z) | (x, y, z) <- b, x == y]
d1 b  = [(x, y, z) | (x, y, z) <- b, x + y == 2]
r n b = [(x, y, z) | (x, y, z) <- b, x == n]
c n b = [(x, y, z) | (x, y, z) <- b, y == n]

legal = filter (\(x, y, z) -> z == 0) board

value xs = sum [z | (x, y, z) <- xs]

wins b = [d0 b, d1 b] ++ [f n b | n <- [0..2], f <- [r, c]]

