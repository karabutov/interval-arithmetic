from decimal import Decimal
import decimal
import math
import numpy

ZERO = Decimal('0')
pi = Decimal('3.1415926535897932384626433832795028841971')
epsilon = Decimal('0.00000001')


class Interval:

    prec = 1/Decimal(10**decimal.getcontext().prec)
    round_floor_context = decimal.Context(rounding=decimal.ROUND_FLOOR, traps=[decimal.Overflow])
    round_ceiling_context = decimal.Context(rounding=decimal.ROUND_CEILING, traps=[decimal.Overflow])

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
        try:
            other = to_interval(other)
        except ValueError:
            return NotImplemented
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
        try:
            other = to_interval(other)
        except ValueError:
            return NotImplemented
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
        try:
            other = to_interval(other)
        except ValueError:
            return NotImplemented
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

        # l = ln(self)
        # m = l * other
        # res = exp(m)
        # return res

    def __rpow__(self, other):
        x = Decimal(other)
        if x < 0:
            raise ValueError('x = ' + str(x) + 'but must be > 0')
        cur_context = decimal.getcontext()
        decimal.setcontext(Interval.round_floor_context)
        left_possible_boundaries = [other ** self.left_boundary, other ** self.right_boundary]
        decimal.setcontext(Interval.round_ceiling_context)
        right_possible_boundaries = [other ** self.left_boundary, other ** self.right_boundary]
        left_boundary = min(left_possible_boundaries)
        right_boundary = max(right_possible_boundaries)
        decimal.setcontext(cur_context)
        return Interval(left_boundary, right_boundary)

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

    def __contains__(self, item):
        item_i = to_interval(item)
        if self.left_boundary <= item_i.left_boundary and item_i.right_boundary <= self.right_boundary:
            return True
        return False

    def width(self):
        return self.right_boundary - self.left_boundary

    def absolute_value(self):
        return max(abs(self.left_boundary), abs(self.right_boundary))

    def midpoint(self):
        return (self.left_boundary + self.right_boundary) / 2

    def radius(self):
        return (self.right_boundary - self.left_boundary) / 2

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

    # def sin1(self):
    #     cur_context = decimal.getcontext()
    #     decimal.setcontext(Interval.round_floor_context)
    #     left_possible_boundaries = [math.sin(self.left_boundary), math.sin(self.right_boundary)]
    #     decimal.setcontext(Interval.round_ceiling_context)
    #     right_possible_boundaries = [math.sin(self.left_boundary), math.sin(self.right_boundary)]
    #     decimal.setcontext(cur_context)
    #     pi2 = 2 * pi
    #     pi05 = pi / 2
    #     if math.ceil((self.left_boundary - pi05) / pi2) <= math.floor((self.right_boundary - pi05) / pi2):
    #         right_boundary = 1
    #     else:
    #         right_boundary = max(right_possible_boundaries)
    #
    #     if math.ceil((self.left_boundary + pi05) / pi2) <= math.floor((self.right_boundary + pi05) / pi2):
    #         left_boundary = -1
    #     else:
    #         left_boundary = min(left_possible_boundaries)
    #     return Interval(left_boundary, right_boundary)

    def cos(self):
        left_cos = self.cos_approximation(self.left_boundary)
        right_cos = self.cos_approximation(self.right_boundary)
        left_possible_boundaries = [left_cos.left_boundary, right_cos.left_boundary]
        right_possible_boundaries = [left_cos.right_boundary, right_cos.right_boundary]

        pi2 = 2 * pi
        if math.ceil(self.left_boundary / pi2) <= math.floor(self.right_boundary / pi2):
            right_boundary = 1
        else:
            right_boundary = max(right_possible_boundaries)
        if math.ceil((self.left_boundary - pi) / pi2) <= math.floor((self.right_boundary - pi) / pi2):
            left_boundary = -1
        else:
            left_boundary = min(left_possible_boundaries)
        return Interval(left_boundary, right_boundary)

    def sin(self):
        x = to_interval(self)
        x = x - pi_i / 2
        return x.cos()

    def ln(self):
        if not (self > 0):
            raise ValueError("x = " + str(self) + " but must be > 0")
        left_ln = self.ln_approximation(self.left_boundary)
        right_ln = self.ln_approximation(self.right_boundary)
        left_possible_boundaries = [left_ln.left_boundary, right_ln.left_boundary]
        right_possible_boundaries = [left_ln.right_boundary, right_ln.right_boundary]
        left_boundary = min(left_possible_boundaries)
        right_boundary = max(right_possible_boundaries)
        return Interval(left_boundary, right_boundary)

    def exp(self):
        cur_context = decimal.getcontext()
        decimal.setcontext(Interval.round_floor_context)
        left_possible_boundaries = [self.left_boundary.exp(), self.right_boundary.exp()]
        decimal.setcontext(Interval.round_ceiling_context)
        right_possible_boundaries = [self.left_boundary.exp(), self.right_boundary.exp()]
        left_boundary = min(left_possible_boundaries)
        right_boundary = max(right_possible_boundaries)
        decimal.setcontext(cur_context)
        return Interval(left_boundary, right_boundary)

    @staticmethod
    def cos_approximation(x):
        sign_x = numpy.sign(x)
        x_i = to_interval(x)
        while not (to_interval(0 - 100 * Interval.prec, 2 * pi_i.right_boundary + 100 * Interval.prec).__contains__(x_i)):
            x_i = x_i - sign_x * (pi_i + pi_i)

        if x_i > pi_i:
            x_i = pi_i + pi_i - x_i

        i = 1
        res = to_interval(0)
        prev_res = to_interval(1)
        sign = -1
        while abs(res - prev_res) > Interval.prec:
            prev_res = res
            tmp = sign * (x_i - pi_i / 2) ** i / math.factorial(i)
            res += tmp
            sign *= -1
            i += 2
        return res.add_to_bounds(-Interval.prec, Interval.prec)

    @staticmethod
    def ln_approximation(z):
        if not (z > 0):
            raise ValueError("x = " + str(z) + " but must be > 0")
        z_i = to_interval(z)
        x = (z_i-1)/(z_i+1)
        i = 1
        res = to_interval(0)
        prev_res = to_interval(1)
        while abs(res.midpoint() - prev_res.midpoint()) > (Interval.prec/10):
            prev_res = res
            res += x**i/i
            i += 2
        res = res * 2
        return res.add_to_bounds(-Interval.prec, Interval.prec)

    @staticmethod
    def set_prec(value):
        Interval.prec = 1/(10**Decimal(value))
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


pi_i = Interval('3.1415926535897932384626433832795028841971', '3.1415926535897932384626433832795028841972')
e_i = Interval('2.7182818284590452353602874713526624977572', '2.7182818284590452353602874713526624977573')

print(to_interval(2*pi_i + 2*pi_i).sin())
print(to_interval(pi_i/3 - 4*pi_i).sin())
print((pi_i/3).sin())
print((pi_i/3).sin1())
print(to_interval(0.5).ln())
print(to_interval(e_i * e_i).ln())
print(to_interval(pi_i/2 + 6*pi_i).sin())
print(to_interval(pi_i/4 - 8*pi_i).sin())



