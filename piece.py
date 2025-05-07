# piece.py
"""
This file defines the basic Qwirkle tile pieces.
Yeh file Qwirkle ke basic tile pieces ko define karti hai.
Each tile is a combination of a color and a shape.
Har tile ek unique color aur shape ka combination hoti hai.
"""

class COLORS:
    # Colors constants - yahan har color define hai.
    RED = 'red'
    YELLOW = 'yellow'
    GREEN = 'green'
    CYAN = 'cyan'
    MAGENTA = 'magenta'
    BLUE = 'blue'

class SHAPES:
    # Shapes constants - yahan har shape define hai.
    TRIANGLE = '▲'
    DIAMOND = '◆'
    SQUARE = '■'
    CIRCLE = '●'
    STAR = '★'
    SPARKLE = '❈'

class Piece:
    """
    Represents a single tile (Piece) in Qwirkle.
    Yeh class ek tile ko represent karti hai jo color aur shape se mil kar banti hai.
    
    Rule Implementation:
    - Har tile ka color aur shape unique combination hona chahiye.
    """
    def __init__(self, color, shape):
        """
        Constructor: Set karta hai tile ka color aur shape.
        """
        self.color = color
        self.shape = shape

    def __str__(self):
        """
        Returns a string representation for printing the tile.
        Yeh tile ko print karne ke liye friendly format provide karta hai.
        """
        return f"{self.color} {self.shape}"

    def __repr__(self):
        """
        Representation method, simply same as __str__.
        """
        return self.__str__()
