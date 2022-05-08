from Interval import *
from decimal import Decimal


class IntervalVariable:

    def __init__(self, x, der=1):
        self.x = to_interval(x)
        self.der = to_interval(der)

    def __add__(self, other):
        if isinstance(other, IntervalVariable):
             der = self.der + other.der
             x = self.x + other.x
        else:
            der = self.der
            x = self.x + other
        return IntervalVariable(x, der)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, IntervalVariable):
             der = self.der - other.der
             x = self.x - other.x
        else:
            der = self.der
            x = self.x - other
        return IntervalVariable(x, der)

    def __rsub__(self, other):
        der = -self.der
        x = other - self.x
        return IntervalVariable(x, der)

    def __mul__(self, other):
        if isinstance(other, IntervalVariable):
             der = self.der * other.x + other.der * self.x
             x = self.x * other.x
        else:
            der = other * self.der
            x = other * self.x
        return IntervalVariable(x, der)

    def __rmul__(self, other):
        self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, IntervalVariable):
             der = (self.der * other.x - other.der * self.x) / other.x**2
             x = self.x / other.x
        else:
            other = to_interval(other)
            der = 1 / other
            x = self.x / other
        return IntervalVariable(x, der)

    def __rtruediv__(self, other):
        other = to_interval(other)
        der = -(other * self.der) / self.x**2
        x = other / self.x
        return IntervalVariable(x, der)

    def __pow__(self, other):
        other = Decimal(other)
        der = other * (self.x**(other-1)) * self.der
        x = self.x ** other
        return IntervalVariable(x, der)

    def __rpow__(self, other):
        other = Decimal(other)
        der = self.der  * (other**self.x) * ln(other)
        x = other**self.x
        return IntervalVariable(x, der)

    def cos(self):
        x = self.x.cos()
        der = self.der * (-self.x.sin())
        return IntervalVariable(x, der)

    def sin(self):
        x = self.x.sin()
        der = self.der * self.x.cos()
        return IntervalVariable(x, der)

    def ln(self):
        x = self.x.ln()
        der = self.der / self.x
        return IntervalVariable(x, der)


a = to_interval(1)
x = IntervalVariable(5)
a + x
x + a

