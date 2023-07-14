use db;

CREATE TABLE IF NOT EXISTS short_squeeze_data (
    asOfDate DATE,
    ticker VARCHAR(255),
    company VARCHAR(255),
    sector VARCHAR(255),
    industry VARCHAR(255),
    float_short_perct DECIMAL(10, 4),
    short_ratio DECIMAL(10, 2),
    high_50d_perct DECIMAL(10, 4),
    high_52w_perct DECIMAL(10, 4),
    change_open_perct DECIMAL(10, 4),
    prev_close DECIMAL(10, 2),
    current_price DECIMAL(10, 2),
    shares_float VARCHAR(255)
);
