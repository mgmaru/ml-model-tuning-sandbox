# notes

## ドキュメント概要
`ml-model-tuning-sandbox`の開発における反省(やったこと、わかったこと、疑問点など)を記載する。

## 反省
### 2026-07-01
#### やったこと
- `uv`で`Python`の環境を構築
- `csv`ファイルを読み込む簡単なスクリプトを作成
- `Python`の基本知識の勉強
#### わかったこと
- `Python`におけるリスト
  - `list`：可変長、型が混在
  - `array`：可変長、型固定
  - `ndarray`：配列/Vecの連続メモリ（数値計算用の配列）
  - `tuple`：固定長、変更不可（イミュータブル）
---
### 2026-07-02 / 2026-07-03
#### やったこと
- 機能を実装
    - `CSV`読み込み機能（データソース読み込み）
    - 選択した商品の現在価格、SNS言及数、出品数、検索関心を折れ線グラフで表示する機能
    - スナップショット、イベントデータを表で表示
#### わかったこと
- `basedpyright`は、Pythonの静的型チェッカー。
  - microsoftの`pyright`をフォークしたもので、`pyright`よりも厳格。
  - 主に、`Any`を検出して、制限してくれる。
- `Dataframe`の特定の行に対する重複削除は、`drop_duplicates()`で簡単にできる。
- `Dataframe`の特定の行に対するソートは、`sort_values()`で簡単にできる。
#### わからなかったところ
- 実装の際に、一時変数でおくべきか、おかなくても良いかが迷った。
1. 一時変数で置く例：
```python
def extract_selected_item_data(
  selected_item: str, items_data: pd.DataFrame
) -> pd.DataFrame:
    selected_item_data = items_data[items_data["item_name"] == selected_item]
  return selected_item_data
```
2. 一時変数で置かない例：
```python
def extract_selected_item_data(
  selected_item: str, items_data: pd.DataFrame
) -> pd.DataFrame:
  return items_data[items_data["item_name"] == selected_item]
```
---
### 2026-07-05
#### やったこと
- サンプルデータを架空のデータから実データに置き換え（bike_sharingへ）
- csvを読み込んで、
#### わかったこと
- `hour.csv`などの時間ごとのデータを時系列で表すときは、横軸は時間まで直したものにする。
  - 修正前：`dteday`（`2011-01-01`）
  - 修正後：`dteday` + `hr` （`2011-01-01 05:00:00`）
実装例：
```python
data["datetime"] = (
    pd.to_datetime(data["dteday"])
    + pd.to_timedelta(data["hr"], unit="h")
)
```
- `pandas`のデータフレームにおいて条件で行抽出を行うとき、`and`は使えない。
  - エラー：`data[data["dteday"] >= start_date and data["dteday"] <= end_date]`
  - 正しい：`data[(data["dteday"] >= start_date) & (data["dteday"] <= end_date)]`
- データフレームの時刻については、**日付型に変換（`pd.to_datetime()`を使用）して、条件比較などを行う。**
  - 良くない：`data[data["dteday"] >= start_date and data["dteday"] <= end_date]`
  - 正しい：`data[(data["dteday"] >= pd.to_datetime(start_date)) & (data["dteday"] <= pd.to_datetime(end_date))]`
---
### 2026-07-06
#### やったこと
- 基本統計量をstreamlitで出力
- 月毎のcntのグラフを出力
#### わかったこと
- `DataFrame`の中の型はそのまま使用した方が良い。無駄な変換はしない。
- **`DataFrame`の破壊的変更と非破壊的変更の違い**がわからなかった。
  - 元のデータフレーム：`df`
  1. 新しい変数に格納する場合：`df2 = df` -> `df2`の変更が`df`に影響する（破壊的）
  2. 元のデータフレームを`copy`して新しい変数に格納する場合：`df2 = df.copy()` -> `df2`の変更は`df`に影響しない（非破壊的）
  3. 元のデータフレームの条件を絞って、新しい変数に格納：`df2 = df[条件]` -> `df2`の変更は`df`には影響しない（非破壊的）
  4. 元のデータフレームの条件を絞ってコピーして新しい変数に格納：`df2 = df[条件].copy()` -> `df2`の変更は`df`には影響しない（非破壊的）
- **`DataFrame.resample`：indexが日付の場合に、集計を行うのに便利。**
#### わからなかったこと
- `DataFrame`の基本的なデータの扱いがまだわかっていない。
  - データフレームの扱いを学ぶ。
- グラフの種類ごとにどこで使うべきなのかを学ぶ必要がある。
  - ヒストグラムはどのような場合に採用するのか？
  - 折れ線グラフはどのような場合に採用するのか？　など
---
### 2026-07-07
#### やったこと
- 時間帯ごとの平均cntの計算ロジックおよび棒グラフを追加
#### わかったこと
- ヒストグラムと棒グラフの違い
  1. ヒストグラム：
    - 見た目：棒同士がくっついている。
    - 目的：数値の分布（ばらつき）を見る。
    - データ：同じデータとしてみる。
    - **横軸：階級（数値範囲）/ 縦軸：度数（データの数）**
  2. 棒グラフ：
    - 見た目：棒同士が離れている。
    - 目的：項目ごとの比較。
    - データ：1本1本が独立しているデータとしてみる。
    - **横軸：なんでも。縦軸：数値（の大きさ）**
- Pythonの`dict[key, list[value]]`にキーを追加するときの注意 -> 追加するキーが`dict`に含まれていない状態で、dictの値に`append`すると`KeyError`となる。 -> 値の`list`が作成されていないため。
  - **`Go`でいう`nilスライス`に`append`するみたい**なこと。 -> **初期化する必要**があった。
1. 誤った実装
```python 
for _, row in df_for_the_period.iterrows():
    key = cast(int, row["hr"])
    value = cast(int, row["cnt"])
    time_and_cnt_dict[key].append(value) # KeyError
```
2. 正しい実装
```python 
for _, row in df_for_the_period.iterrows():
    key = cast(int, row["hr"])
    value = cast(int, row["cnt"])
    if key not in time_and_cnt_dict:
        time_and_cnt_dict[
            key
        ] = []  # キーがない場合、空のリストを作ってからappend
    time_and_cnt_dict[key].append(value)
```
---
### 2026-07-07 / 2026-07-08
#### やったこと
- 曜日×時間の平均cntの計算ロジック & ヒートマップ実装
#### わかったこと
- `list`の中に`int`や`float`を混在させる時、型は`list[int | float]`のように書く。
- Pythonでのソート
  - `sort`：破壊的（元のデータを並び替える）
  - `sorted`：非破壊的（元のデータを複製して並び替える、元のデータには影響しない）
- 無名関数：`lambda`
  - 構文：`lambda 引数 : 返り値`
#### ロジック構築
1. `weather`のグループ分けをしてから、平均`cnt`を計算するロジック
- 自分の実装：
```python
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
```
- 完結な実装：
```python
# たったこれだけで、元の15行以上のコードと全く同じ結果になります
df_weathersit_cnt_avg = df.groupby("weathersit")["cnt"].mean().reset_index(name="cnt_avg")
```
- データフレームの`groupby`関数を使用することで完結に実装することができる。
#### 注意
- 辞書`dict`を`DataFrame`に変換するとき、値が単一の値だとエラーになる。-> **辞書をデータフレームに変換する時、値は`list`である必要**がある。
1. エラー
```python
import pandas as pd

# NG: 値がすべてスカラー値（単一の数値や文字列）
data = {"weekday": 0, "time": 9, "cnt_avg": 150.5}

# ここでエラーが発生する！
df = pd.DataFrame(data) 
# ValueError: If using all scalar values, you must pass an index
```
2. 正しい
```python
import pandas as pd

# OK: 値をリストの形にする
data = {"weekday": [0], "time": [9], "cnt_avg": [150.5]}

# これならエラーなく 1行3列 のDataFrameが作れる
df = pd.DataFrame(data)
```
---
### 2026-07-09
#### やったこと
- holidayと平均cntの関係を調査（表で表示）
#### わかったこと
- **`pd.DataFrame.groupby()`で指定したカラムは`index`になるので、`reset_index`でリセットする必要**がある。
  - `reset_index(name="...")`で、インデックス以外のカラムの名前を変更しながら、指定したカラムのインデックスをリセットすることができる。
- 自分の実装
```python
def calc_cnt_avg_for_holiday(df: pd.DataFrame) -> pd.DataFrame:
    df_avg_cnt_and_holiday = (
        df.groupby("holiday")[["cnt"]].mean().reset_index("holiday")
    )
    df_avg_cnt_and_holiday.columns = ["holiday", "cnt_avg"]
    return df_avg_cnt_and_holiday
```
- 完結な実装
```python
def calc_cnt_avg_for_holiday(df: pd.DataFrame) -> pd.DataFrame:
    # 1重ブラケットでSeriesとして扱い、name引数で一気に変換する
    return df.groupby("holiday")["cnt"].mean().reset_index(name="cnt_avg")
```
---
### 2026-07-10
#### やったこと
- グラフの観察
#### わかったこと
- **散布図だと外れ値をとらえやすい**。
  - **この外れ値がなぜ外れているのかを考察するのかが大事**だと思った。
- グラフから言えることがあくまで仮説であることを前提にすることが大切だと思った。
  - 原因を直接結びつけてはいけないと感じた。-> 複数の要因が絡み合った結果の事象である可能性があるため。
  - じゃあ、なぜ、その事象が起きているのかを確認する手段を学ぶ手段が必要であると感じた。
    - 多分、仮説を元に予測モデルを構築し、さらに正解データと予測を照らし合わせて初めてわかることだと思った（あくまで自分の中での仮説）。
- グラフの観察において、**事実と仮説ははっきりと分けるべき**だと思った。
  - 特に【docs/observations/graph_observation_template.md】の「4. 観察メモ」の**「観察したこと」には必ず事実を書く。**
---
### 2026-07-11
#### やったこと
- グラフの観察
- 祝日と非祝日の登録者と非登録者の利用割合を円グラフで実装
- 平日と休日の登録者と非登録者の利用割合を円グラフで実装
- 仮説を立てる
#### わかったこと
- 円グラフは`plotly.express.pie()`で実装できる。
  - データ構造はデータフレーム
  - 引数には「カテゴリ」と割合の「値」を設定する。
  - カテゴリと値の最も基本的な指定方法は、データフレームのカラム名
- **１カラムの中で特定の値のみを抽出　-> `isin()`でできる。**
- グラフの数値の大きい部分は仮説として含めるべきなのは分かっていたが、変化がない部分や少ない部分は仮説に含めるべきか迷った。
  - **変化がいない部分や少ない部分についても仮説が立てられるのであれば含める**べき（ただし、無理して含めるべきではない）。
- 1つのグラフで立てた仮説について確証が低くても、**複数のグラフを組み合わせることで確証が高くなる**ような気がした。
- 月毎にgroupbyする方法として、最初は`resample(ruke=""ME)`を使用したがうまくいかなかった。
#### わからなかったところ（疑問点）
- 返り値が`None`の場合でも`return`はつけるべきか？
- 平均と絶対数で見る場合の使い分け。平均で隠れるものは何か。
- **積み上げ棒グラフを作るときの適切なデータ構造（インデックス、カラム設計）がわからなかった。**
  - 最初のカラム`year_month`/ 右の４つのカラムに4カテゴリの天気
  - `horintal_axis_data`（x軸）:`year_month`
  - `vertical_axis_data`（y軸）:`["sunny_partly_cloudy_count", "fog_cloudy_count", "light_rain_snow_count", "heavy_rain_blizzard_count"]`の値 -> `List`で渡してあげるところがポイント（**リストで指定したカラムがそのままカテゴリになる**）。
  - 以上のように、カラムをカテゴリ別にすることで、積み上げ棒で天気毎の割合を可視化できる。
#### 反省
- 各種類のグラフで意図するような表示にするためには、適切なデータ構造（インデックス、カラム設計）を選べるようにするべきだと思った。 
  - 例：「xグラフで表示するから、横軸はxx、縦軸はxx。だからデータフレームのカラムとインデックスにする」みたいな感じでパッと設計できると良い。
  - 今の自分は、「まず`dict`にしてからデータフレームにして...」みたいな感じで、**データフレーム以外のデータ構造を経由して**、グラフに適するデータフレームを作成している。
  - **データフレームのままグラフの表示に適するデータフレームの構造に変換できる**と理想。
  - 多分、データフレームのまま変換することで、計算量が少ないまま変換できる。
- 特に、積み上げ棒グラフの作り方が難しかった。
---
### 2026-07-25
#### やったこと
- 仮説のレビュー【docs/observations/graph_observation_template.md】&修正
- フロントエンドにページ遷移機能を追加
- レビューの修正
#### 間違っていたところ
- **自分で定義を作っているところがあった。** 
  - 0：土曜日, 6：日曜日　を休日 / それ以外：平日としてしまった。
  - 実際、データには「休日」「平日」という定義はない。
  - やるのであれば`workingday`で、稼働日と非稼働日で登録者と非登録者の割合を分けるべきだった。
- **割合のグラフから総数（絶対値）の仮説を立ててしまっていた。**
  - **割合のグラフ（構成比）から需要は読み取れない。** ←重要
#### 反省
- **カラムの定義を勝手にしない。**
  - 今回だったら、土曜日と日曜日とそれ以外の曜日を勝手に「休日」「平日」と定義してしまった。
  - 「平日」と「休日」という定義はデータからは`weekday`というカラムからは読み取れない。
- 今回とりあえず、Codexが示すグラフを可視化して、そこからパターンや仮説を立てたが、これが正しくもあり、間違いであったような気がする（順序が正しくなかったような気がする）。
  - **先に確認したいものを列挙した上で、グラフを可視化するようなフローで実行すると無駄のない分析を行うことができる**と感じた。
  - Codexの提案をそのままグラフで可視化すると意味のないグラフが完成する場合がある。
- 予想以上にデータ分析は頭を使う。
  - これは頭が良くないとできないかもしれない。かなり思考しないと正しくデータを読み取ることができない。
  - もう少し言うと、**思考しないと自分の都合の良いようにデータを解釈してしまう。**
  - これはロジックを組むこととはまた違う思考能力が必要であると感じた。
---
