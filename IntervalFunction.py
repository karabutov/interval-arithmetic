from Interval import *
from decimal import Decimal


class IntervalFunction:

    prec = Decimal(0.00001)
    density = Decimal(1000)
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
        der_inter = self.derivative_interval(x)

        res1 = self.func(x.left_boundary) + derivative * (x - x.left_boundary)
        res2 = self.func(x.right_boundary) + derivative * (x - x.right_boundary)
        res12 = res1 & res2

        res5 = self.func(to_interval(x.left_boundary)) + der_inter * (x - x.left_boundary)
        res6 = self.func(to_interval(x.right_boundary)) + der_inter * (x - x.right_boundary)
        res56 = res5 & res6

        c_left = self.c_left(x)
        c_right = self.c_right(x)
        res3 = self.func(c_left) + derivative * (x - c_left)
        res4 = self.func(c_right) + derivative * (x - c_right)
        res34 = res3 & res4

        res_n = self.func(x)

        #print(x)
        # print('der: ' + str(res12))
        # print('cut: ' + str(res34))
        # print('app der: ' + str(res56))
        # print('natural: ' + str(res_n))
        # #print(to_interval(self.func(x.left_boundary).left_boundary, self.func(x.right_boundary).right_boundary))
        #print('')

        return res12 & res34 & res56 & res_n

    def derivative(self, x):
        delta = 1 / Decimal(1000000)
        prev_res = 0
        cur_res = 1
        while abs(cur_res - prev_res) > self.prec:
            prev_res = cur_res
            delta /= 10
            cur_res = (self.func(x) - self.func(x - delta))/delta
        return to_interval(cur_res).add_to_bounds(-self.prec, self.prec)

    def derivative_interval(self, x):
        steps = int(self.density * x.width())
        delta = 1 / self.density
        cur_x = to_interval(x.left_boundary)
        cur_der = self.derivative(cur_x)
        max_d = cur_der.right_boundary
        min_d = cur_der.left_boundary
        for i in range(1, steps + 1):
            cur_x = to_interval(x.left_boundary + i * delta)
            cur_der = self.derivative(cur_x)
            if cur_der.right_boundary > max_d:
                max_d = cur_der.right_boundary
            if cur_der.left_boundary < min_d:
                min_d = cur_der.left_boundary
        return Interval(min_d, max_d)

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
    return 3 * (x-1)**2 + 1


def func2(x):
    return exp(x) / ln(x)


def func2d(x):
    return (exp(x) * ln(x) - exp(x) / x) / (ln(x))**2


def func3(x):
    return x * cos(x)


def func3d(x):
    return cos(x) - x * sin(x)

