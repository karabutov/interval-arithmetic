from decimal import Decimal
import decimal
import math

ZERO = Decimal('0')
pi = Decimal('3.141592653589793')

class Interval:

    prec = decimal.getcontext().prec
    round_floor_context = decimal.Context(prec=prec, rounding=decimal.ROUND_FLOOR, traps=[decimal.Overflow])
    round_ceiling_context = decimal.Context(prec=prec, rounding=decimal.ROUND_CEILING, traps=[decimal.Overflow])

    def __init__(
            self,
            left_boundary,
            right_boundary,
    ):
        self.left_boundary = Decimal(left_boundary)
        self.right_boundary = Decimal(right_boundary)

    def __str__(self):
        return str(self.left_boundary) if self.left_boundary == self.right_boundary else '[' + str(self.left_boundary) + ', ' + str(self.right_boundary) + ']'

    def __repr__(self):
        return self.__str__()

    def __round__(self, n=None):
        left_endpoint, right_endpoint = self.get_endpoints_with_accuracy(n)
        self.left_boundary = left_endpoint
        self.right_boundary = right_endpoint

    def __add__(self, other):
        other = to_interval(other)
        cur_context = decimal.getcontext()
        decimal.setcontext(self.round_floor_context)
        left_endpoint = self.left_boundary + other.left_boundary
        decimal.setcontext(self.round_ceiling_context)
        right_endpoint = self.right_boundary + other.right_boundary
        decimal.setcontext(cur_context)
        return Interval(left_endpoint, right_endpoint)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        other = to_interval(other)
        cur_context = decimal.getcontext()
        decimal.setcontext(self.round_floor_context)
        left_endpoint = self.left_boundary - other.right_boundary
        decimal.setcontext(self.round_ceiling_context)
        right_endpoint = self.right_boundary - other.left_boundary
        decimal.setcontext(cur_context)
        return Interval(left_endpoint, right_endpoint)

    def __rsub__(self, other):
        other = to_interval(other)
        return other.__sub__(self)

    def __mul__(self, other):
        other = to_interval(other)
        cur_context = decimal.getcontext()
        decimal.setcontext(self.round_floor_context)
        left_possible_boundaries = (self.left_boundary * other.left_boundary,
                                    self.left_boundary * other.right_boundary,
                                    self.right_boundary * other.left_boundary,
                                    self.right_boundary * other.right_boundary)
        decimal.setcontext(self.round_ceiling_context)
        right_possible_boundaries = (self.left_boundary * other.left_boundary,
                                     self.left_boundary * other.right_boundary,
                                     self.right_boundary * other.left_boundary,
                                     self.right_boundary * other.right_boundary)
        left_boundary = min(left_possible_boundaries)
        right_boundary = max(right_possible_boundaries)
        decimal.setcontext(cur_context)
        return Interval(left_boundary, right_boundary)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __pow__(self, other):
        if not isinstance(other, Interval):
            other = Decimal(other)
            cur_context = decimal.getcontext()
            decimal.setcontext(self.round_floor_context)
            left_possible_boundaries = [self.left_boundary**other, self.right_boundary**other]
            decimal.setcontext(self.round_ceiling_context)
            right_possible_boundaries = [self.left_boundary**other, self.right_boundary**other]
            if self.__contains__(ZERO):
                left_possible_boundaries.append(ZERO)
            left_boundary = min(left_possible_boundaries)
            right_boundary = max(right_possible_boundaries)
            decimal.setcontext(cur_context)
            return Interval(left_boundary, right_boundary)
        else:
            raise ValueError()
            # l = ln(self)
            # m = l * other
            # res = exp(m)
            # return res

    def __not_zero_div(self, other):
        other = to_interval(other)
        cur_context = decimal.getcontext()
        decimal.setcontext(self.round_floor_context)
        left_possible_boundaries = (self.left_boundary / other.left_boundary,
                                    self.left_boundary / other.right_boundary,
                                    self.right_boundary / other.left_boundary,
                                    self.right_boundary / other.right_boundary)
        decimal.setcontext(self.round_ceiling_context)
        right_possible_boundaries = (self.left_boundary / other.left_boundary,
                                     self.left_boundary / other.right_boundary,
                                     self.right_boundary / other.left_boundary,
                                     self.right_boundary / other.right_boundary)
        left_boundary = min(left_possible_boundaries)
        right_boundary = max(right_possible_boundaries)
        decimal.setcontext(cur_context)
        return Interval(left_boundary, right_boundary)

    def __zero_div(self, other):
        cur_context = decimal.getcontext()
        if other.left_boundary == 0:
            decimal.setcontext(self.round_floor_context)
            left_boundary = min(self.left_boundary / other.right_boundary,
                                self.right_boundary / other.right_boundary)
            decimal.setcontext(cur_context)
            return Interval(left_boundary, "Infinity")
        elif other.right_boundary == 0:
            decimal.setcontext(self.round_ceiling_context)
            right_boundary = max(self.left_boundary / other.left_boundary,
                                 self.right_boundary / other.left_boundary)
            decimal.setcontext(cur_context)
            return Interval("-Infinity", right_boundary)
        else:
            decimal.setcontext(self.round_ceiling_context)
            right_boundary = max(self.left_boundary / other.left_boundary,
                                 self.right_boundary / other.left_boundary)
            decimal.setcontext(cur_context)
            res1 =  Interval("-Infinity", right_boundary)
            decimal.setcontext(self.round_floor_context)
            left_boundary = min(self.left_boundary / other.right_boundary,
                                self.right_boundary / other.right_boundary)
            res2 = Interval(left_boundary, "Infinity")
            return res1, res2

    def __truediv__(self, other):
        other = to_interval(other)
        if other.__contains__(ZERO):
            return self.__zero_div(other)
        return self.__not_zero_div(other)

    def __rtruediv__(self, other):
        other = to_interval(other)
        return other.__truediv__(self)

    def __lt__(self, other):
        other = to_interval(other)
        return self.right_boundary < other.left_boundary

    def __gt__(self, other):
        other = to_interval(other)
        return self.left_boundary > other.right_boundary

    def __eq__(self, other):
        other = to_interval(other)
        return self.right_boundary == other.right_boundary and self.left_boundary == other.left_boundary

    def __ne__(self, other):
        other = to_interval(other)
        return self.right_boundary != other.right_boundary or self.left_boundary != other.left_boundary

    def __len__(self):
        return self.width()

    def __neg__(self):
        return Interval(-self.right_boundary, -self.left_boundary)

    def __pos__(self):
        return self

    def __and__(self, other):
        left_boundary = max(self.left_boundary, other.left_boundary)
        right_boundary = min(self.right_boundary, other.right_boundary)
        if left_boundary > right_boundary:
            return None
        return Interval(left_boundary, right_boundary)

    def __abs__(self):
        possible_boundaries = [abs(self.left_boundary), abs(self.right_boundary)]
        if self.__contains__(ZERO):
            possible_boundaries.append(ZERO)
        left_boundary = min(possible_boundaries)
        right_boundary = max(possible_boundaries)
        return Interval(left_boundary, right_boundary)

    def width(self):
        return self.right_boundary - self.left_boundary

    def absolute_value(self):
        return max(abs(self.left_boundary), abs(self.right_boundary))

    def midpoint(self):
        return (self.left_boundary + self.right_boundary) / 2

    def radius(self):
        return (self.right_boundary - self.left_boundary) / 2

    def __contains__(self, item):
        if self.left_boundary <= item <= self.right_boundary:
            return True
        return False

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

    def add_to_bounds(self, left, right):
        left = Decimal(left)
        right = Decimal(right)
        cur_context = decimal.getcontext()
        decimal.setcontext(self.round_floor_context)
        self.left_boundary += left
        decimal.setcontext(self.round_ceiling_context)
        self.right_boundary += right
        decimal.setcontext(cur_context)
        return self

    @staticmethod
    def set_prec(value):
        value = Decimal(value)
        Interval.prec = value
        Interval.round_floor_context.prec = value
        Interval.round_ceiling_context.prec = value


def to_interval(value, right_endpoint=None):
    if value is not None and (isinstance(value, int) or isinstance(value, float)
                              or isinstance(value, Decimal) or isinstance(value, str)):
        if right_endpoint is not None \
                and (isinstance(right_endpoint, int) or isinstance(right_endpoint, float)
                     or isinstance(right_endpoint, Decimal) or isinstance(right_endpoint, str)):
            interval = Interval(value, right_endpoint)
        else:
            interval = Interval(value, value)

    elif isinstance(value, Interval):
        interval = Interval(value.left_boundary, value.right_boundary)
    else:
        raise ValueError('Could not convert ' + str(value) + 'to Interval')
    return interval


def exp(x):
    x = to_interval(x)
    cur_context = decimal.getcontext()
    decimal.setcontext(Interval.round_floor_context)
    left_possible_boundaries = [x.left_boundary.exp(), x.right_boundary.exp()]
    decimal.setcontext(Interval.round_ceiling_context)
    right_possible_boundaries = [x.left_boundary.exp(), x.right_boundary.exp()]
    left_boundary = min(left_possible_boundaries)
    right_boundary = max(right_possible_boundaries)
    decimal.setcontext(cur_context)
    return Interval(left_boundary, right_boundary)


def ln(x):
    x = to_interval(x)
    if not (x > 0):
        raise ValueError("x = " + str(x) + " but must be > 0")
    cur_context = decimal.getcontext()
    decimal.setcontext(Interval.round_floor_context)
    left_possible_boundaries = [x.left_boundary.ln(), x.right_boundary.ln()]
    decimal.setcontext(Interval.round_ceiling_context)
    right_possible_boundaries = [x.left_boundary.ln(), x.right_boundary.ln()]
    left_boundary = min(left_possible_boundaries)
    right_boundary = max(right_possible_boundaries)
    decimal.setcontext(cur_context)
    return Interval(left_boundary, right_boundary)


def pow(x, y):
    if not isinstance(x, Interval) and isinstance(y, Interval):
        x = Decimal(x)
        if x < 0:
            raise ValueError('x = ' + str(x) + 'but must be > 0')
        cur_context = decimal.getcontext()
        decimal.setcontext(Interval.round_floor_context)
        left_possible_boundaries = [x**y.left_boundary, x**y.right_boundary]
        decimal.setcontext(Interval.round_ceiling_context)
        right_possible_boundaries = [x**y.left_boundary, x**y.right_boundary]
        left_boundary = min(left_possible_boundaries)
        right_boundary = max(right_possible_boundaries)
        decimal.setcontext(cur_context)
        return Interval(left_boundary, right_boundary)

    else:
        return x**y


def log(a, x):
    if not isinstance(a, Interval) and isinstance(x, Interval):
        a = Decimal(a)
        lna_inverse = Decimal(1) / a.ln()
        lnx = ln(x)
        return lnx * lna_inverse
    else:
        raise ValueError()


def sin(x):
    x = to_interval(x)
    cur_context = decimal.getcontext()
    decimal.setcontext(Interval.round_floor_context)
    left_possible_boundaries = [math.sin(x.left_boundary), math.sin(x.right_boundary)]
    decimal.setcontext(Interval.round_ceiling_context)
    right_possible_boundaries = [math.sin(x.left_boundary), math.sin(x.right_boundary)]
    decimal.setcontext(cur_context)
    pi2 = 2 * pi
    pi05 = pi / 2
    if math.ceil((x.left_boundary - pi05)/pi2) <= math.floor((x.right_boundary - pi05)/pi2):
        right_boundary = 1
    else:
        right_boundary = max(right_possible_boundaries)

    if math.ceil((x.left_boundary + pi05)/pi2) <= math.floor((x.right_boundary + pi05)/pi2):
        left_boundary = -1
    else:
        left_boundary = min(left_possible_boundaries)
    return Interval(left_boundary, right_boundary)


def cos(x):
    x = to_interval(x)
    cur_context = decimal.getcontext()
    decimal.setcontext(Interval.round_floor_context)
    left_possible_boundaries = [math.cos(x.left_boundary), math.cos(x.right_boundary)]
    decimal.setcontext(Interval.round_ceiling_context)
    right_possible_boundaries = [math.cos(x.left_boundary), math.cos(x.right_boundary)]
    decimal.setcontext(cur_context)
    pi2 = 2 * pi
    if math.ceil(x.left_boundary/pi2) <= math.floor(x.right_boundary/pi2):
        right_boundary = 1
    else:
        right_boundary = max(right_possible_boundaries)
    if math.ceil((x.left_boundary - pi)/pi2) <= math.floor((x.right_boundary - pi)/pi2):
        left_boundary = -1
    else:
        left_boundary = min(left_possible_boundaries)
    return Interval(left_boundary, right_boundary)


