from decimal import Decimal
import decimal

ZERO = Decimal('0')


class Interval:

    def __init__(
            self,
            left_boundary,
            right_boundary,
    ):
        self.left_boundary = Decimal(left_boundary)
        self.right_boundary = Decimal(right_boundary)
        self.prec = decimal.getcontext().prec

    def __str__(self):
        left_endpoint, right_endpoint = self.get_endpoints_with_accuracy()
        return '[' + str(left_endpoint) + ', ' + str(right_endpoint) + ']'

    def __add__(self, other):
        if isinstance(other, Interval):
            return Interval(self.left_boundary + other.left_boundary, self.right_boundary + other.right_boundary)

        raise RuntimeError

    def __sub__(self, other):
        if isinstance(other, Interval):
            return Interval(self.left_boundary - other.right_boundary, self.right_boundary - other.left_boundary)

        raise RuntimeError

    def __mul__(self, other):
        if isinstance(other, Interval):
            possible_boundaries = (self.left_boundary * other.left_boundary,
                                   self.left_boundary * other.right_boundary,
                                   self.right_boundary * other.left_boundary,
                                   self.right_boundary * other.right_boundary)
            left_boundary = min(possible_boundaries)
            right_boundary = max(possible_boundaries)
            return Interval(left_boundary, right_boundary)

        raise RuntimeError

    def __truediv__(self, other):
        if isinstance(other, Interval):
            return self * Interval(1 / other.right_boundary, 1 / other.left_boundary)

        raise RuntimeError

    def __lt__(self, other):
        if isinstance(other, Interval):
            return self.right_boundary < other.left_boundary

        raise RuntimeError

    def __gt__(self, other):
        if isinstance(other, Interval):
            return self.right_boundary > other.left_boundary

        raise RuntimeError

    def __eq__(self, other):
        if isinstance(other, Interval):
            return self.right_boundary == other.right_boundary and self.left_boundary == other.left_boundary

        raise RuntimeError

    def __ne__(self, other):
        if isinstance(other, Interval):
            return self.right_boundary != other.right_boundary or self.left_boundary != other.left_boundary

        raise RuntimeError

    def __len__(self):
        return self.width()

    def __neg__(self):
        return Interval(-self.right_boundary, -self.left_boundary)

    def __pos__(self):
        return self

    def width(self):
        return self.right_boundary - self.left_boundary

    def absolute_value(self):
        return max(abs(self.left_boundary), abs(self.right_boundary))

    def midpoint(self):
        return (self.left_boundary + self.right_boundary) / 2

    def get_endpoints_with_accuracy(self):
        cur_prec = decimal.getcontext().prec
        cur_rounding = decimal.getcontext().rounding
        decimal.getcontext().prec = self.prec

        decimal.getcontext().rounding = decimal.ROUND_FLOOR
        left_endpoint = self.left_boundary + ZERO

        decimal.getcontext().rounding = decimal.ROUND_CEILING
        right_endpoint = self.right_boundary + ZERO

        decimal.getcontext().prec = cur_prec
        decimal.getcontext().rounding = cur_rounding

        return left_endpoint, right_endpoint


i = Interval(Decimal('1.9999999'), Decimal('1.1111111'))
print(i)
i.prec = 2
print(i)

n1 = Decimal('1.99999')
n2 = Decimal('1.11111')
print(n1)
print(n2)
ctx1 = decimal.getcontext()
ctx = decimal.BasicContext
ctx.prec = 2
ctx.rounding = decimal.ROUND_FLOOR
decimal.setcontext(ctx)
print(n1)
print(n1 + 0)
decimal.getcontext().rounding = decimal.ROUND_CEILING
print(n2)
print(n2 + 0)
decimal.setcontext(ctx1)

