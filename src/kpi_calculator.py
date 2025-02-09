class KpiCalculator:
    
    def SMA(series, window):
        return series.rolling(window=window).mean()