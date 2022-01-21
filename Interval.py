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
        return '[' + str(self.left_boundary) + ', ' + str(self.right_boundary) + ']'

    def __round__(self, n=None):
        left_endpoint, right_endpoint = self.get_endpoints_with_accuracy(n)
        self.left_boundary = left_endpoint
        self.right_boundary = right_endpoint

    def __add__(self, other):
        other = self.value_to_interval(other)
        return Interval(self.left_boundary + other.left_boundary, self.right_boundary + other.right_boundary)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        other = self.value_to_interval(other)
        return Interval(self.left_boundary - other.right_boundary, self.right_boundary - other.left_boundary)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        other = self.value_to_interval(other)
        possible_boundaries = (self.left_boundary * other.left_boundary,
                               self.left_boundary * other.right_boundary,
                               self.right_boundary * other.left_boundary,
                               self.right_boundary * other.right_boundary)
        left_boundary = min(possible_boundaries)
        right_boundary = max(possible_boundaries)
        return Interval(left_boundary, right_boundary)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        other = self.value_to_interval(other)
        return self * Interval(1 / other.right_boundary, 1 / other.left_boundary)

    def __rtruediv__(self, other):
        return self.__rtruediv__(other)

    def __lt__(self, other):
        other = self.value_to_interval(other)
        return self.right_boundary < other.left_boundary

    def __gt__(self, other):
        other = self.value_to_interval(other)
        return self.right_boundary > other.left_boundary

    def __eq__(self, other):
        other = self.value_to_interval(other)
        return self.right_boundary == other.right_boundary and self.left_boundary == other.left_boundary

    def __ne__(self, other):
        other = self.value_to_interval(other)
        return self.right_boundary != other.right_boundary or self.left_boundary != other.left_boundary

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

    def get_endpoints_with_accuracy(self, accuracy):
        cur_prec = decimal.getcontext().prec
        cur_rounding = decimal.getcontext().rounding
        decimal.getcontext().prec = accuracy

        decimal.getcontext().rounding = decimal.ROUND_FLOOR
        left_endpoint = self.left_boundary + ZERO

        decimal.getcontext().rounding = decimal.ROUND_CEILING
        right_endpoint = self.right_boundary + ZERO

        decimal.getcontext().prec = cur_prec
        decimal.getcontext().rounding = cur_rounding

        return left_endpoint, right_endpoint

    @staticmethod
    def value_to_interval(value):
        if isinstance(value, int) or isinstance(value, float) or isinstance(value, Decimal) or isinstance(value, str):
            interval = Interval(value, value)
        elif isinstance(value, Interval):
            interval = value
        else:
            raise ValueError('Could not convert ' + str(value) + 'to Interval')
        return interval


ctx1 = decimal.Context(prec=2, rounding=decimal.ROUND_FLOOR)
ctx2 = decimal.Context(prec=2, rounding=decimal.ROUND_CEILING)
op1 = Decimal("1")
op2 = Decimal("3")
decimal.setcontext(ctx1)
res1 = Decimal(op1 / op2 + 1)

decimal.setcontext(ctx2)
res2 = Decimal(op1 / op2)

op1 = Decimal(0.24)
op2 = Decimal(0.99)

decimal.setcontext(ctx1)
res1 = op1 * op2
decimal.setcontext(ctx2)
res2 = op1 * op2

i = Interval('1.9999999', '2.1111111')
print(3 + i)
round(i, 3)
print(3 + i)
