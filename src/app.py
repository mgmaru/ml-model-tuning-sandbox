import statistics
from pathlib import Path
from typing import cast

import pandas as pd
import plotly.express as px
import streamlit as st

# CSV FILE PATH
DATA_SOURCE_DIR = Path(__file__).parent.parent / "data/raw/bike_sharing"
HOUR_CSV_FILE_PATH = DATA_SOURCE_DIR / "hour.csv"
DAY_CSV_FILE_PATH = DATA_SOURCE_DIR / "day.csv"


# load data
def load_csv_data(
    file_path: Path, parse_dates: list[str] | None = None
) -> pd.DataFrame:
    return pd.read_csv(file_path, parse_dates=parse_dates)


# display data
def display_dataframe_row_and_columns(df: pd.DataFrame) -> None:
    print(f"row:{df.shape[0]}, column:{df.shape[1]}")


def display_dataframe_info(df: pd.DataFrame) -> None:
    df.info()


def display_dataframe_startdate_and_enddate(df: pd.DataFrame) -> None:
    print(f"start_date:{df['dteday'].min()}, end_date:{df['dteday'].max()}")


# Average for each time period within the specified period
def calc_cnt_average_each_month_for_the_period(
    df: pd.DataFrame, start_date: str, end_date: str
) -> pd.DataFrame:

    if "hr" not in df.columns:  # error
        print("The dataframe does not contain a column named hr.")
        return pd.DataFrame()

    else:
        df_for_the_period = df[
            (df["dteday"] >= pd.to_datetime(start_date))
            & (df["dteday"] <= pd.to_datetime(end_date))
        ]

        df_for_the_period["datetime"] = pd.to_datetime(  # add "datetime" column
            df_for_the_period["dteday"]
        ) + pd.to_timedelta(df_for_the_period["hr"], unit="h")

        monthly_avg_cnt = (
            df_for_the_period.resample(rule="ME", on="datetime")["cnt"]
            .mean()
            .reset_index(name= "cnt_avg")
        )  # 平均を算出
        return monthly_avg_cnt


def calc_cnt_average_each_time_for_the_period(
    df: pd.DataFrame, start_date: str, end_date: str
):
    if "hr" not in df.columns:  # error
        print("The dataframe does not contain a column named hr.")
        return pd.DataFrame()
    else:
        df_for_the_period = df[  # 期間内の行を抽出
            (df["dteday"] >= pd.to_datetime(start_date))
            & (df["dteday"] <= pd.to_datetime(end_date))
        ]
        # 時間帯ごとのcntを抽出
        time_and_cnt_dict: dict[int, list[int]] = {}  # キー：hr 値：cntのリスト
        for _, row in df_for_the_period.iterrows():
            key = cast(int, row["hr"])
            value = cast(int, row["cnt"])
            if key not in time_and_cnt_dict:
                time_and_cnt_dict[
                    key
                ] = []  # キーがない場合、空のリストを作ってからappend
            time_and_cnt_dict[key].append(value)  # Pythonのmapのキーの順序は保証される
        # 時間帯ごとの平均cntを計算
        time_and_cnt_avg_dict: dict[int, list[float]] = {}
        for key, value in time_and_cnt_dict.items():
            if key not in time_and_cnt_avg_dict:
                time_and_cnt_avg_dict[key] = []
            time_and_cnt_avg_dict[key].append(statistics.mean(value))
        # convert dict to DataFrame (key to column, value to row)
        df_time_and_cnt_avg = pd.DataFrame(time_and_cnt_avg_dict).T.reset_index()
        df_time_and_cnt_avg.columns = ["time_zone", "cnt_avg"]
    return df_time_and_cnt_avg


# Calculate the CNT average for a specific day of the week and time.
# whole period
# x= weekday / y=time_zone / z= cnt_avg
# The implementation method is map of map
def calc_cnt_avg_for_day_of_week_and_time(df: pd.DataFrame) -> pd.DataFrame:
    if "hr" not in df.columns:
        print("The dataframe does not contain a column named hr.")
        return pd.DataFrame()

    weekday_time_cnt_dict: dict[int, dict[int, list[int]]] = {}
    for _, row in df.iterrows():
        inner_key = cast(int, row["hr"])
        inner_value = cast(int, row["cnt"])
        outer_key = cast(int, row["weekday"])
        if outer_key not in weekday_time_cnt_dict:
            weekday_time_cnt_dict[outer_key] = {}
        if inner_key not in weekday_time_cnt_dict[outer_key]:
            weekday_time_cnt_dict[outer_key][inner_key] = []
        weekday_time_cnt_dict[outer_key][inner_key].append(inner_value)

    # 曜日×時間帯におけるcnt平均を計算する
    weekday_time_avg_cnt_dict: dict[int, dict[int, float]] = {}  # weekday time cnt_avg
    for weekday, dict_time_cnts in weekday_time_cnt_dict.items():
        if weekday not in weekday_time_avg_cnt_dict:
            weekday_time_avg_cnt_dict[weekday] = {}
        for hr, cnts in dict_time_cnts.items():
            weekday_time_avg_cnt_dict[weekday][hr] = statistics.mean(
                cnts
            )  # ここは普通に値なのでhrのキーエラーは発生しない
    # sort by weekday
    sorted_weekday_time_avg_cnt_dict = dict(
        sorted(
            weekday_time_avg_cnt_dict.items(),
            key=lambda x: x[0],  # sort by weekday
        )
    )
    # build DataFrame
    weekday_time_cnt_avg_list: list[list[int | float]] = []
    for weekday, value in sorted_weekday_time_avg_cnt_dict.items():
        for time, cnt_avg in value.items():
            row_data: list[int | float] = [weekday, time, cnt_avg]
            weekday_time_cnt_avg_list.append(row_data)
    df_weekday_time_cnt_avg = pd.DataFrame(
        weekday_time_cnt_avg_list, columns=["weekday", "time", "cnt_avg"]
    )
    return df_weekday_time_cnt_avg


def calc_cnt_avg_diff_weather_cond(df: pd.DataFrame):
    if "hr" not in df.columns:  # error
        print("The dataframe does not contain a column named hr.")
        return pd.DataFrame()
    else:
        # 時間帯ごとのcntを抽出
        weathersit_and_cnt_dict: dict[
            int, list[int]
        ] = {}  # キー：weathersit 値：cntのリスト
        for _, row in df.iterrows():
            key = cast(int, row["weathersit"])
            value = cast(int, row["cnt"])
            if key not in weathersit_and_cnt_dict:
                weathersit_and_cnt_dict[key] = []
            weathersit_and_cnt_dict[key].append(value)
        # 天気ごとの平均cntを計算
        weathersit_and_cnt_avg_dict: dict[int, list[float]] = {}
        for key, value in weathersit_and_cnt_dict.items():
            if key not in weathersit_and_cnt_avg_dict:
                weathersit_and_cnt_avg_dict[key] = []
            weathersit_and_cnt_avg_dict[key].append(statistics.mean(value))
        # convert dict to DataFrame (key to column, value to row)
        df_weathersit_cnt_avg = pd.DataFrame(
            weathersit_and_cnt_avg_dict
        ).T.reset_index()
        df_weathersit_cnt_avg.columns = ["weathersit", "cnt_avg"]
    return df_weathersit_cnt_avg


def calc_cnt_avg_for_holiday(df: pd.DataFrame) -> pd.DataFrame:
    df_avg_cnt_and_holiday = (
        df.groupby("holiday")[["cnt"]].mean().reset_index("holiday")
    )
    df_avg_cnt_and_holiday.columns = ["holiday", "cnt_avg"]
    return df_avg_cnt_and_holiday

def calc_cnt_avg_day_of_week(df: pd.DataFrame):
    df_group_by_day_of_week = df.groupby("weekday")["cnt"].mean().reset_index(name= "cnt_avg")
    return df_group_by_day_of_week


def calc_basic_stat(df: pd.DataFrame) -> dict[str, float]:
    basic_statistics: dict[str, float] = {}
    basic_statistics["avg"] = df["cnt"].mean()
    basic_statistics["max"] = cast(float, df["cnt"].max())
    basic_statistics["min"] = cast(float, df["cnt"].min())
    basic_statistics["med"] = df["cnt"].median()
    return basic_statistics

def extract_holiday_or_non_holiday(df: pd.DataFrame, is_holiday: bool) -> pd.DataFrame:
    if is_holiday: # holiday
        df_group_by_holiday = df.groupby("holiday")[["registered", "casual"]].sum().iloc[1].reset_index()
        df_group_by_holiday.columns = ["registration_status", "cnt"]
        return df_group_by_holiday
    else: # non holiday
        df_group_by_holiday = df.groupby("holiday")[["registered", "casual"]].sum().iloc[0].reset_index()
        df_group_by_holiday.columns = ["registration_status", "cnt"]
        return df_group_by_holiday

def filter_weekday(df: pd.DataFrame, filter_value: list[int]) -> pd.DataFrame:
    df_filter_weekday = df[df["weekday"].isin(filter_value)] # フィルターする値のみを抽出
    return df_filter_weekday

def calc_sum_register_and_casual(df_filter_weekday: pd.DataFrame) -> pd.DataFrame:
    df_sum_casual_and_register = df_filter_weekday[["casual", "registered"]].sum().reset_index()
    df_sum_casual_and_register.columns = ["registration_status", "cnt"]
    return df_sum_casual_and_register

def display_basic_stat(basic_stat: dict[str, float]) -> str:
    basic_stat_text = f"cntの平均：{basic_stat['avg']}<br>cntの最大値：{basic_stat['max']}<br>cntの最小値：{basic_stat['min']}<br>cntの中央値：{basic_stat['med']}"
    return basic_stat_text

def extract_month_and_weathersit_count(df: pd.DataFrame) -> pd.DataFrame:
    # 期間(Period)を出したあと、その月の1日の「日付型(Timestamp)」に変換する
    df["year_month"] = df["dteday"].dt.to_period("M").dt.to_timestamp()
    # {year_month: {1: count, 2:}, {year_month: {1:count, ...} }
    year_month_and_weathersit_count_dict: dict[pd.Timestamp, dict[int, int]] = {}
    for _, row in df.iterrows():
        outer_key = cast(pd.Timestamp, row["year_month"])
        inner_key = cast(int, row["weathersit"])
        if outer_key not in year_month_and_weathersit_count_dict:
            year_month_and_weathersit_count_dict[outer_key] = {}
        if inner_key not in year_month_and_weathersit_count_dict[outer_key]:
            year_month_and_weathersit_count_dict[outer_key][inner_key] = 0
        year_month_and_weathersit_count_dict[outer_key][inner_key] +=1 # countup
    df_year_month_and_weathersit = pd.DataFrame(year_month_and_weathersit_count_dict).fillna(0).T.reset_index()
    df_year_month_and_weathersit.columns = ["year_month", "sunny_partly_cloudy_count", "fog_cloudy_count", "light_rain_snow_count", "heavy_rain_blizzard_count"]
    return df_year_month_and_weathersit

# create chart
def create_contents(text: str) -> None:
    st.markdown(
        text,
        unsafe_allow_html=True,  # html active
    )


def create_line_chart(
    df: pd.DataFrame, horintal_axis_data: str, vertical_axis_data: str
) -> None:
    fig = px.line(df, x=horintal_axis_data, y=vertical_axis_data)
    fig.update_xaxes(tickformat="%Y/%m/%d")
    st.plotly_chart(fig, width="stretch")


def create_bar_chart(
    df: pd.DataFrame, horintal_axis_data: str, vertical_axis_data: str
) -> None:
    fig = px.bar(df, x=horintal_axis_data, y=vertical_axis_data)
    fig.update_xaxes(tickformat="%Y/%m")
    st.plotly_chart(fig, width="stretch")

def create_stacked_bar_chart(df: pd.DataFrame, horintal_axis_data: str, vertical_axis_data: list[str]) -> None:
    fig = px.bar(df, x=horintal_axis_data, y=vertical_axis_data)
    fig.update_layout(barmode='stack')
    st.plotly_chart(fig, width="stretch")


def create_histgram_chart(df: pd.DataFrame, horintal_axis_data: str) -> None:
    fig = px.histogram(df, x=horintal_axis_data)
    fig.update_xaxes(tickformat="%Y/%m")
    st.plotly_chart(fig, width="stretch")


def create_heatmap_chart(df: pd.DataFrame) -> None:
    fig = px.density_heatmap(
        df, x=df["weekday"], y=df["time"], z=df["cnt_avg"], nbinsx=7, nbinsy=24
    )
    fig.update_coloraxes(colorbar_title="cnt_avg")
    fig.update_traces(
        hovertemplate="曜日: %{x}<br>時間: %{y}<br>cnt平均値: %{z}<extra></extra>"
    )
    st.plotly_chart(fig, width="stretch")


def create_scatter_chart(
    df: pd.DataFrame, horizontal_axis_data: str, vertical_axis_data: str
) -> None:
    fig = px.scatter(df, x=horizontal_axis_data, y=vertical_axis_data)
    st.plotly_chart(fig, width="stretch")

# Note the input data structure
def create_pie_chart(df: pd.DataFrame, category: str, values: str) -> None:
    fig = px.pie(df, values=values, names=category) # names:凡例（groupbyのイメージ）　values:データ
    st.plotly_chart(fig, width="stretch")


# 実行
# データ読み込み
hour_data = load_csv_data(HOUR_CSV_FILE_PATH, ["dteday"])
day_data = load_csv_data(DAY_CSV_FILE_PATH, ["dteday"])

dict_basic_stat_hour_data = calc_basic_stat(hour_data)
dict_basic_stat_day_data = calc_basic_stat(day_data)
text_basic_stat_hour_data = display_basic_stat(dict_basic_stat_hour_data)
text_basic_stat_day_data = display_basic_stat(dict_basic_stat_day_data)

monthly_cnt_avg = calc_cnt_average_each_month_for_the_period(
    hour_data, "2011-01-01", "2012-12-31"
)
time_and_cnt_avg = calc_cnt_average_each_time_for_the_period(
    hour_data, "2011-01-01", "2012-12-31"
)

df_weekday_time_cnt_avg = calc_cnt_avg_for_day_of_week_and_time(hour_data)

df_weathersit_cnt_avg = calc_cnt_avg_diff_weather_cond(hour_data)

df_avg_cnt_holiday = calc_cnt_avg_for_holiday(day_data)

df_cnt_avg_day_of_week = calc_cnt_avg_day_of_week(day_data)

df_group_by_holiday_true = extract_holiday_or_non_holiday(day_data, True)
df_group_by_holiday_false = extract_holiday_or_non_holiday(day_data, False)

df_filter_weekdays = filter_weekday(day_data, [1, 2, 3, 4, 5]) # 平日を抽出
df_filter_non_weekdays = filter_weekday(day_data, [0, 6]) # 休日を抽出

df_sum_casual_register_weekdays = calc_sum_register_and_casual(df_filter_weekdays) # 平日の登録者と非登録者のcntを計算
df_sum_casual_register__non_weekdays = calc_sum_register_and_casual(df_filter_non_weekdays) # 平日の登録者と非登録者のcntを計算

df_year_month_and_weathersit = extract_month_and_weathersit_count(hour_data)
print(df_year_month_and_weathersit)

# frontend
st.set_page_config(layout="wide")
st.header("1. 生データ")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1.1 hour.csv（時間ごとのデータ）")
    st.dataframe(hour_data, hide_index=True)

with col2:
    st.subheader("1.2 day.csv（日にちごとのデータ）")
    st.dataframe(day_data, hide_index=True)

st.subheader("1.3 cnt推移")
create_line_chart(day_data, "dteday", "cnt")


st.header("2. データ理解")

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("2.1-1 基本統計量（hour.csv）")
    create_contents(text_basic_stat_hour_data)

with col_b:
    st.subheader("2.1-2 基本統計量（day.csv）")
    create_contents(text_basic_stat_day_data)


col_c, col_d = st.columns(2)
with col_c:
    st.subheader("2.2-1 cnt分布（hour.csv）")
    create_histgram_chart(hour_data, "cnt")

with col_d:
    st.subheader("2.2-2 cnt分布（day.csv）")
    create_histgram_chart(day_data, "cnt")

col_e, col_f, col_g = st.columns(3)

with col_e:
    st.subheader("2.3 時間帯ごとの平均cnt")
    create_bar_chart(time_and_cnt_avg, "time_zone", "cnt_avg")

with col_f:
    st.subheader("2.4 月毎の平均cnt")
    create_bar_chart(monthly_cnt_avg, "datetime", "cnt_avg")

with col_g:
    st.subheader("2.4 曜日毎の平均cnt")
    create_bar_chart(df_cnt_avg_day_of_week, "weekday", "cnt_avg")

st.subheader("2.5 曜日×時間帯(全期間)")
create_heatmap_chart(df_weekday_time_cnt_avg)

col5, col6 = st.columns(2)

with col5:
    st.subheader("2.6 気温×cnt（全期間）")
    create_scatter_chart(day_data, "temp", "cnt")

    st.subheader("2.8 湿度×cnt（全期間）")
    create_scatter_chart(day_data, "hum", "cnt")

with col6:
    st.subheader("2.7 体感温度×cnt（全期間）")
    create_scatter_chart(day_data, "atemp", "cnt")

    st.subheader("2.9 風速×cnt（全期間）")
    create_scatter_chart(day_data, "windspeed", "cnt")


st.subheader("2.10 天気別×平均cnt（全期間）")
create_bar_chart(df_weathersit_cnt_avg, "weathersit", "cnt_avg")

st.subheader("2.11 holiday×平均cnt（全期間）")
st.dataframe(df_avg_cnt_holiday)

st.subheader("2.12 registerd×cnt（全期間）")
create_scatter_chart(day_data, "registered", "cnt")


st.subheader("2.13 祝日と非祝日の登録者と非登録者の利用割合（全期間）")
col7, col8 = st.columns(2)

with col7:
    st.subheader("① 非祝日の登録者と非登録者の利用割合")
    create_pie_chart(df_group_by_holiday_false, "registration_status", "cnt" )

with col8:
    st.subheader("② 祝日の登録者と非登録者の利用割合")
    create_pie_chart(df_group_by_holiday_true, "registration_status", "cnt")

st.subheader("2.14 平日と休日の登録者と非登録者の利用割合（全期間）")

col9, col10 = st.columns(2)
# weekday 0:日曜日 6:土曜日　/ other
with col9:
    st.subheader("① 平日における登録者と非登録者の利用割合（全期間）")
    create_pie_chart(df_sum_casual_register_weekdays, "registration_status", "cnt")

with col10:
    st.subheader("② 休日における登録者と非登録者の利用割合（全期間）")
    create_pie_chart(df_sum_casual_register__non_weekdays, "registration_status", "cnt")

st.subheader("月毎の天気の分布")
create_stacked_bar_chart(df_year_month_and_weathersit, "year_month", ["sunny_partly_cloudy_count", "fog_cloudy_count", "light_rain_snow_count", "heavy_rain_blizzard_count"])
