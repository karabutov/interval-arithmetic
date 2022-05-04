from Interval import *
from decimal import Decimal
import math


class IntervalFunction:

    prec = Decimal(1)/Decimal(decimal.getcontext().prec)

    def __init__(
            self,
            func,
            funcd
    ):
        self.func = func
        self.funcd = funcd

    def __call__(self, x):
        x = to_interval(x)
        derivative = self.funcd(x)

        res1 = self.func(x.left_boundary) + derivative * (x - x.left_boundary)
        res2 = self.func(x.right_boundary) + derivative * (x - x.right_boundary)
        res12 = res1 & res2

        c_left = self.c_left(x)
        c_right = self.c_right(x)
        res3 = self.func(c_left) + derivative * (x - c_left)
        res4 = self.func(c_right) + derivative * (x - c_right)
        res34 = res3 & res4
        return res1 & res2

    def derivative(self, x, prec):
        delta = Decimal(0.0001)
        prev_res = 0
        cur_res = 1
        while abs(cur_res - prev_res) > prec:
            prev_res = cur_res
            delta /= 10
            fx = self.func(x)
            fd = self.func(x - delta)
            cur_res = (self.func(x) - self.func(x - delta))/delta
        return cur_res

    def cut(self, x):
        der = self.funcd((to_interval(x)))
        point = der.midpoint() / der.radius()
        if point > 1:
            return 1
        elif point < -1:
            return -1
        else:
            return point

    def c_left(self, x):
        x = to_interval(x)
        cut = self.cut(x)
        return x.midpoint() - cut * x.radius()

    def c_right(self, x):
        x = to_interval(x)
        cut = self.cut(x)
        return x.midpoint() + cut * x.radius()


def func1(x):
    return x**3 - 3*(x**2) + 4*x + 2


def func1d(x):
    return 3*(x**2) - 6 * x + 4


def func2(x):
    return exp(x) / ln(x)


def func2d(x):
    return (exp(x) * ln(x) - exp(x) / x) / (ln(x))**2


f1 = IntervalFunction(func1, func1d)
f2 = IntervalFunction(func2, func2d)
i = to_interval(1.2, 2)
print(func1(i))
print(f1(i))
print(func2(i))
print(f2(i))
