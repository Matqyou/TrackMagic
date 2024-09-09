class Numbers:
    @staticmethod
    def clamp(value, minimum, maximum):
        if value < minimum:
            return minimum
        elif value > maximum:
            return maximum
        return value

    @staticmethod
    def clamp_bottom(value, minimum):
        if value < minimum:
            return minimum
        return value
