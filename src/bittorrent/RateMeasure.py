# Written by Bram Cohen
# see LICENSE.txt for license information

from time import time

class RateMeasure:
    def __init__(self, left):
        self.start = None
        self.last = None
        self.rate = 0
        self.remaining = None
        self.left = left
        self.broke = False
        self.got_anything = False

    def data_came_in(self, amount):
        if not self.got_anything:
            self.got_anything = True
            self.start = time() - 2
            self.last = self.start
            self.left -= amount
            return
        self.update(time(), amount)

    def data_rejected(self, amount):
        self.left += amount

    def get_time_left(self):
        if not self.got_anything:
            return None
        t = time()
        if t - self.last > 15:
            self.update(t, 0)
        return self.remaining

    def get_size_left(self):
        return self.left

    def update(self, t, amount):
        self.left -= amount
        try:
            self.rate = ((self.rate * (self.last - self.start)) + amount) / (t - self.start)
            self.last = t
            self.remaining = self.left / self.rate
            if self.start < self.last - self.remaining:
                self.start = self.last - self.remaining
        except ZeroDivisionError:
            self.remaining = None
        if self.broke and self.last - self.start < 20:
            self.start = self.last - 20
        if self.last - self.start > 20:
            self.broke = True
