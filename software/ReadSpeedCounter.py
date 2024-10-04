from time import monotonic

class ReadSpeedCounter:
    def __init__(self, size, default_val=0):
        self._size = size
        self._pos = -size
        now = monotonic()
        self._prev_time = [now for _ in range(size)]
        self._prev_value = [default_val for _ in range(size)]

    def get_speed(self, new_value):
        now = monotonic()
        size = self._size
        cur_pos = self._pos
        if cur_pos >= 0:
            ref_pos = (cur_pos + 1) % size
            prev_time = self._prev_time[ref_pos]
            prev_val = self._prev_value[ref_pos]
        elif cur_pos < 0:
            prev_time = self._prev_time[self._size - 1]
            prev_val = self._prev_value[self._size - 1]
            ref_pos = cur_pos + 1

        runtime = now - prev_time
        speed = float((new_value - prev_val) / runtime)

        self._pos = ref_pos
        self._prev_time[ref_pos] = now
        self._prev_value[ref_pos] = new_value

        return speed

    def reset(self, default_val=0):
        size = self._size
        self._pos = -size
        now = monotonic()
        self._prev_time = [now for _ in range(size)]
        self._prev_value = [default_val for _ in range(size)]
