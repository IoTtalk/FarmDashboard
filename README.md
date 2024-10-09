此branch的目的在於新增兩個資料分析的功能在DashBoard上，分別為Z-score的離群值偵測跟STL資料分解

**10/09**
跟branch plotly_html的plot.html不一樣的地方在於：
1. 視覺化跟資料分析功能界面統一了，所以以後的plot.html統稱analysis.html，該界面包含了資料視覺化(原plot.html)跟資料分析功能。
2. 繪圖改成call api.py的plotly()，並且加上了資料分解(STL)跟離群值檢測(zscore)

10/09討論覺得把stl跟zscore加在history.html上不適合，會讓使用者覺得資料分析功能四散在各頁面，因此改成新增在analysis.html上，而history.html照舊，不做更新
