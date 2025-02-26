from ._abstract import PriceLevels


class DirectionalChange(PriceLevels): 
    def __init__(self, threshold=5.0):
        super().__init__(threshold)

    def obstacle_trend_market(self, close):
        ''' todo: 
            iterate ten first second and compare them where up or down trend
            count up and down when compare and assign result is 1 is up or -1 if down
        '''
        pass

    def find_pivots(self, close, high, low):
        # initial value
        up_zig = False
        peak = high[0]
        peak_idx = 0
        valley = low[0]
        valley_idx = 0

        # variable to store points
        pivot_points = []

        for i in range(1, len(close)):
            if up_zig:
                if peak < high[i]:
                    peak = high[i]
                    peak_idx = i
                elif close[i] <=  peak * (1 - self.threshold):
                    pivot_points.append((peak_idx, peak, "High"))

                    up_zig = False
                    valley = low[i]
                    valley_idx = i
            else:
                if valley > low[i]:
                    valley = low[i]
                    valley_idx = i
                elif close[i] >=  valley * (1 + self.threshold):
                    pivot_points.append((valley_idx, valley, "Low"))

                    up_zig = True
                    peak = high[i]
                    peak_idx = i
                
        return pivot_points

    def fit(self, df):
        # convert series to numpy 
        close = df["Close"].to_numpy()
        high = df["High"].to_numpy()
        low = df["Low"].to_numpy()

        # find points
        pivot_points = self.find_pivots(close, high, low)
        self.pivots = [(df.index[idx], price, label) for idx, price, label in pivot_points]
                
        return self.pivots
