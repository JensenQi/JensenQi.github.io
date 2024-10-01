---
title: 淘宝用户购物行为数据集
mermaid: false
chart: true
mathjax: false
mathjax_autoNumber: false
tags: 数据集
---



这个博客后续会编写一系列推荐系统相关的文章，从数据安全的角度，为了避免使用公司内部的数据，我们将会采用公共的数据集进行讲解，这里我们将介绍第一份数据，也就是阿里巴巴提供的淘宝用户购物行为数据集 UserBehavior 。UserBehavior 是一份公开数据集，包含了 2017 年 11 月 25 日至 2017 年 12 月 3 日之间，有行为的约一百万随机用户的所有行为（行为包括点击、购买、加购、喜欢），用于隐式反馈推荐问题的研究。

## 数据概述

将数据集下载解压后可以看到，整个数据集只有一个文件 `UserBehavior.csv`​，数据的组织形式和 MovieLens-20M 类似，即数据集的每一行表示一条用户行为，由用户 ID、商品 ID、商品类目 ID、行为类型和行为时间戳共计 5 列组成，每一列以逗号分隔，其含义、数据类型以及数据样例如下表所示

|列名称|数据类型|说明|数据样例|
| ------------| ------------| ------------------------------------| ------------|
|用户ID|整型|序列化后的用户 ID|1|
|商品ID|整型|序列化后的商品 ID|2268318|
|商品类目ID|整型|序列化后的商品所属类目 ID|2520377|
|行为类型|字符串枚举|取值为 pv、buy、cart、fav 其中一个|pv|
|时间戳|整型|行为发生的 Unix 时间戳|1511544070|

其中行为类型的 4 个枚举值对应的业务含义为

* pv：商品详情页 page view，近似于商品点击
* buy： 商品购买
* cart： 将商品加入购物车
* fav：收藏商品

整个数据集约 1 亿（100,150,807）条记录，每条记录代表用户的一次行为，覆盖大约 1 百万（987,994）用户，1 万（9,439）类目下共计 400 万（4,162,024）商品。

## 入库处理

数据库选型我们采用常用的 SparkSQL，由于原始数据是 csv 格式, 所以我们采用 Datasource Table 的方式把表定义为 CSV 表

```sql
create table user_behavior_buffer(
   user_id bigint,
   item_id bigint,
   cate_id bigint,
   action_type string,
   action_time bigint
) using csv;
```

注意这里我们创建的是临时缓冲表，因为原始数据可能存在脏数据等待清洗，并且原始文件格式 CSV 没有压缩，会占用较多的存储资源，因此我们先建缓冲表，将数据清洗完毕后再写入目标表。

缓冲表建立完毕后，我们可以通过 `desc formatted user_behavior_buffer`​ 获取到表数据存储的 HDFS 路径，然后通过 Hadoop FS 命令将原始的 CSV 文件上传到 HDFS 路径即可

```bash
hadoop fs -put /path/to/UserBehavior.csv hdfs:///user/hive/warehouse/app.db/user_behavior_buffer
```

最后，让我们简单地执行 select 采样查看一下数据，可以看到，数据符合预期

```sql
select *
from user_behavior_buffer
where rand() < 0.01
limit 10;

user_id   item_id   cate_id   action_type     action_time
1         3239041   2355072   pv              1511939239
100       2434962   3897386   pv              1511690835
1000001   3132168   154040    pv              1511881851
1000004   40945     4756105   pv              1511703467
1000011   404297    2578647   fav             1511603262
1000011   404297    2578647   buy             1511603941
100002    4928571   4806751   pv              1512046188
1000027   2070173   4217906   cart            1511704378
1000027   646869    3692903   cart            1512144238
1000028   2808995   246844    pv              1512315622
```

我们再统计一下用户、商品、类目、行为类型、最早时间、最晚时间

```sql
select
    count(*) as row_cnt,
    count(distinct user_id) as user_cnt,
    count(distinct item_id) as item_cnt,
    count(distinct cate_id) as cate_cnt,
    collect_set(action_type) as action_set,
    min(from_unixtime(action_time)) as min_action_time,
    max(from_unixtime(action_time)) as max_action_time
from user_behavior_buffer;

row_cnt    user_cnt  item_cnt  cate_cnt  action_set                 min_action_time      max_action_time
100150807  987994    4162024   9439      ["cart","fav","pv","buy"]  1902-05-08 06:32:46  2037-04-09 13:22:35
```

可以看到，用户、商品、类目、行为类型的查询结果与官方文档提到的完全一致，但操作时间与文档的不一致，我们不妨检查一下日期数据，首先筛选出操作日期为 `1929-02-23`​ 的记录

```sql
select *
from user_behavior_buffer
where to_date(from_unixtime(action_time)) = '1929-09-23'
limit 10;

user_id   item_id   cate_id   action_type  action_time
353279    1397732   1299190   pv           -1270954504
353279    986346    1879194   pv           -1270954491
753213    809825    2895013   pv           -1270897486
```

然后检查原始的 csv 文件，可以看到有一部分脏数据

```csv
...... 25880880 行附近
353279,4659524,4801426,pv,-1271043593
353279,717297,4801426,pv,-1271043549
353279,2706731,2920476,pv,-1271043536
353279,4659524,4801426,pv,-1271043492
353279,612782,1080785,pv,-1271043478
353279,3304918,2465336,pv,-1271043353
353279,3658621,1051370,pv,-1271043344
353279,4985790,4181361,pv,-1271043257
353279,1373275,149192,pv,-1271043232
353279,2131035,4276787,pv,-1271043167
353279,580860,321567,pv,-1271042232
353279,931853,982926,pv,-1271041816
353279,4985790,4181361,pv,-1271041789
353279,705684,982926,pv,-1270996366
353279,278976,4756105,pv,-1270996349
353279,3503179,1320293,pv,-1270996299
353279,1397732,1299190,pv,-1270954504
```

为了分析脏数据的影响，我们按 action_date 进行统计

```sql
select 
    if(dt between '2017-11-25' and '2017-12-03', dt, 'other') as dt,
    count(*) as cnt
from(
    select *, to_date(from_unixtime(action_time)) as dt
    from user_behavior_buffer
) as t 
group by if(dt between '2017-11-25' and '2017-12-03', dt, 'other')
order by dt;
```

可以看到，数据集中大约有 5W 条脏数据（时间戳为 2017-11-25 ~ 2017-12-03 之外的其他日期）

```chart
{
  "type": "bar",
  "data": {
    "datasets": [
      {
        "data": [10420015, 10664602, 10101147, 9878190, 10284073, 10447740, 10859436, 13777869, 13662159, 55576],
        "label": "每天记录总数",
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "hoverBackgroundColor": "rgba(75, 192, 192, 0.5)",
        "borderColor": "rgb(75, 192, 192)",
        "borderWidth": 1
      }
    ],
    "labels": ["2017-11-25", "2017-11-26", "2017-11-27", "2017-11-28", "2017-11-29", "2017-11-30", "2017-12-01", "2017-12-02", "2017-12-03", "其他日期"]
  },
  "options": {
    "scales": {
      "xAxes": [{"scaleLabel": {"display": true, "labelString": "日期" }}],
      "yAxes": [{"scaleLabel": {"display": true, "labelString": "记录数" }, "ticks": {"beginAtZero": true}}]
    }
  }
}



```

综合来看，脏数据量不大，只占总样本的 0.5% 左右，我们直接把这些脏数据删除掉即可。最后我们建立 orc 压缩表，并且将清洗后的数据按日期进行分区，得到最终的数据表后，则可以把 buffer 表清理掉。

```sql
create table user_behavior(
    user_id      bigint     comment '用户 ID',
    item_id      bigint     comment '商品 ID',
    cate_id      bigint     comment '类目 ID',
    action_type  string     comment '行为类型',
    action_time  string  comment '行为事件'
) comment '用户行为日志表'
partitioned by(
    dt string comment '日期分区'
) stored as orc tblproperties('orc.compress' = 'SNAPPY');

insert overwrite table user_behavior partition(dt)
select
    user_id,
    item_id,
    cate_id,
    action_type,
    from_unixtime(action_time) as action_time,
    to_date(from_unixtime(action_time)) as dt
from user_behavior_buffer
where to_date(from_unixtime(action_time)) between '2017-11-25' and '2017-12-03';

drop table user_behavior_buffer;
```

## 数据探查

接下来我们对数据进行各个维度的下钻分析，从而对数据的情况有一个初步的了解，也便于我们后续分析、建模、特征工程等相关工作的开展。

### 用户维度

首先，我们先看一下用户 id 的取值范围，从而判断用户 ID 是一个哈希值还是一个连续值

```sql
select
    count(distinct user_id) as uv,
    max(user_id) as max_id,
    min(user_id) as min_id
from user_behavior

uv      max_id    min_id
987991  1018011   1
```

可以看到，用户 ID 几乎是从 1 开始的连续值，但是总 id 量为 98 万多，而最大 id 是 1018011，说明中间有一部分取值被跳过

接着我们看一下每日的 UV 量，判断是否存在某些日期存在严重丢数的问题

```sql
select
    dt,
    count(distinct user_id) as uv
from user_behavior
group by dt
order by dt;
```

可以看到，每日 UV 量基本差不多（12.02 开始多一些，这应该与双十二大促有关，符合预期）

```chart
{
  "type": "bar",
  "data": {
    "datasets": [
      {
        "data": [706641, 715516, 710094, 709257, 718922, 730597, 740139, 970401, 966977],
        "label": "每天 UV 量",
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "hoverBackgroundColor": "rgba(75, 192, 192, 0.5)",
        "borderColor": "rgb(75, 192, 192)",
        "borderWidth": 1
      }
    ],
    "labels": ["2017-11-25", "2017-11-26", "2017-11-27", "2017-11-28", "2017-11-29", "2017-11-30", "2017-12-01", "2017-12-02", "2017-12-03"]
  },
  "options": {
    "scales": {
      "xAxes": [{"scaleLabel": {"display": true, "labelString": "日期" }}],
      "yAxes": [{"scaleLabel": {"display": true, "labelString": "用户数" }, "ticks": {"beginAtZero": true}}]
    }
  }
}


```

最后我们看下每个用户的样本量，从而判断后续是否可以进行算法建模（如果大部分用户只有 1~2 条行为记录，则用户历史数据较少的情况下，个性化推荐模型的训练难以进行）

```sql
select
    case  
        when cnt < 100 then floor(cnt / 10) * 10
        when cnt < 300 then floor(cnt / 100) * 100
        when cnt >= 300 then 300
    end as cnt,
    count(*) as uv
from(
    select
        user_id,
        count(*) as cnt
    from user_behavior
    group by user_id
) as t
group by case  
    when cnt < 100 then floor(cnt / 10) * 10
    when cnt < 300 then floor(cnt / 100) * 100
    when cnt >= 300 then 300
end
```

可以看到，大部分的用户都有 10 条以上的日志记录，因此这应该是一份对用户进行了过滤的数据，只保留了部分足迹较多的用户，因为实际的生产环境中，绝大多数用户的行为数都非常少

```chart
{
  "type": "bar",
  "data": {
    "datasets": [
      {
        "data": [18638, 67222, 81935, 81782, 77452, 70440, 63885, 56655, 50518, 45066, 252733, 83076, 38589],
        "label": "各样本量覆盖的 UV 量",
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "hoverBackgroundColor": "rgba(75, 192, 192, 0.5)",
        "borderColor": "rgb(75, 192, 192)",
        "borderWidth": 1
      }
    ],
    "labels": ["1~9", "10~19", "20~29", "30~39", "40~49", "50~59", "60~69", "70~79", "80~89", "90~99", "100~199", "200~299", "300+"]
  },
  "options": {
    "scales": {
      "xAxes": [{"scaleLabel": {"display": true, "labelString": "记录数" }}],
      "yAxes": [{"scaleLabel": {"display": true, "labelString": "用户数" }}]
    }
  }
}


```

### 商品维度

与用户维度类似，我们先看下商品 id 的分布情况

```sql
select
    count(distinct item_id) as item_cnt,
    max(item_id) as max_id,
    min(item_id) as min_id
from user_behavior

item_cnt    max_id    min_id
4161138     5163070   1
```

400 万商品，id 取值从 1 到 500 多万，近似可以认为是连续映射

接着看下商品的覆盖 UV 量

```sql
select
    case
        when uv < 10 then uv
        when uv < 100 then floor(uv / 10) * 10
        when uv < 300 then floor(uv / 100) * 100
        when uv >= 300 then 300
    end as uv,
    count(*) as item_cnt
from(
    select
        item_id,
        count(distinct user_id) as uv
    from user_behavior
    group by item_id
) as t
group by case
    when uv < 10 then uv
    when uv < 100 then floor(uv / 10) * 10
    when uv < 300 then floor(uv / 100) * 100
    when uv >= 300 then 300
end
order by uv
```

可以看到，有 35% 的商品只有 1 个用户有行为，大部分商品覆盖的 UV 量都不超过 30 个用户，这种明显的长尾性说明商品维度大概率没有经过规则过滤，即，每个用户的商品足迹大概率是比较齐全的，接近于真实的生产系统

```chart
{
  "type": "bar",
  "data": {
    "datasets": [
      {
        "data": [1428790, 587126, 342400, 231723, 171562, 133097, 107551, 88612, 74260, 396424, 166171, 94942, 61855, 43481, 32742, 25201, 19886, 16432, 76255, 25539, 37089],
        "label": "各商品覆盖的 UV 量",
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "hoverBackgroundColor": "rgba(75, 192, 192, 0.5)",
        "borderColor": "rgb(75, 192, 192)",
        "borderWidth": 1
      }
    ],
    "labels": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10~19", "20~29", "30~39", "40~49", "50~59", "60~69", "70~79", "80~89", "90~99", "100~199", "200~299", "300+"]
  },
  "options": {
    "scales": {
      "xAxes": [{"scaleLabel": {"display": true, "labelString": "覆盖用户数" }}],
      "yAxes": [{"scaleLabel": {"display": true, "labelString": "商品数" }}]
    }
  }
}


```

### 类目维度

类目维度同理，我们先看下类目 ID 分布

```sql
select
    count(distinct cate_id) as cate_cnt,
    max(cate_id) as max_id,
    min(cate_id) as min_id
from user_behavior

cate_cnt   max_id   min_id
9437       5162429  80
```

可以看到，9437 个类目，最小 ID 为 80，最大 ID 为 5162429，因此可以认为类目 ID 是不连续的 hash 值。

接下来看下类目覆盖的商品数量级

```sql
select
    case
        when item_cnt < 10 then item_cnt
        when item_cnt < 100 then floor(item_cnt / 10) * 10
        when item_cnt < 300 then floor(item_cnt / 100) * 100
        when item_cnt >= 300 then 300
    end as item_cnt,
    count(*) as cate_cnt
from(
    select
        cate_id,
        count(distinct item_id) as item_cnt
    from user_behavior
    group by cate_id
) as t
group by case
    when item_cnt < 10 then item_cnt
    when item_cnt < 100 then floor(item_cnt / 10) * 10
    when item_cnt < 300 then floor(item_cnt / 100) * 100
    when item_cnt >= 300 then 300
end
order by item_cnt
```

可以看到商品的类目分布得比较均匀，大部分类目都覆盖了 10 个以上的商品，不存在较多的类目只有少数几个商品的情况

```chart
{
  "type": "bar",
  "data": {
    "datasets": [
      {
        "data": [657, 396, 263, 230, 230, 184, 165, 148, 122, 937, 553, 394, 355, 279, 266, 204, 188, 156, 1142, 601, 1967],
        "label": "各类目覆盖的商品数",
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "hoverBackgroundColor": "rgba(75, 192, 192, 0.5)",
        "borderColor": "rgb(75, 192, 192)",
        "borderWidth": 1
      }
    ],
    "labels": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10~19", "20~29", "30~39", "40~49", "50~59", "60~69", "70~79", "80~89", "90~99", "100~199", "200~299", "300+"]
  },
  "options": {
    "scales": {
      "xAxes": [{"scaleLabel": {"display": true, "labelString": "覆盖商品数" }}],
      "yAxes": [{"scaleLabel": {"display": true, "labelString": "类目数" }}]
    }
  }
}


```

最后我们校验一下商品 ID 与类目 ID 的一致性，即，检查一下是否存在一个商品对应多个类目 ID 的情况，预期上，每个商品只会对应一个类目 ID

```sql
select
    cate_cnt,
    count(*) as item_cnt
from(
    select
        item_id,
        count(distinct cate_id) as cate_cnt
    from user_behavior
    group by item_id
) as t
group by cate_cnt
order by cate_cnt;

cate_cnt   item_cnt
1          4159733
2          1395
3          8
4          2
```

可以看到，极大多数的商品只会对应一个类目 ID，只有少部分（共记 1405 个商品，占比 0.34%）存在多个类目的情况，对于这些脏数据，影响不大，保留即可

### 行为维度

行为类型的取值范围我们在入库环节已经校验过为 `buy`​、`cart`​、`fav`​、`pv`​ 四种取值，因此我们接下来直接检查一下各个行为类型覆盖的记录数以及 UV 量即可

```sql
select
    action_type,
    count(*) as cnt
from user_behavior
group by action_type
order by cnt desc
```

可以看到，pv 行为大约占 90%，cart 行为大约占 5%，fav 行为大约占 3%，buy 行为大约占 2%，行为数量的排序为 pv > cart > fav > buy，这与实际生产环境的顺序基本一致。另一方面，转化率（下单数/点击数）约为 2.25%，也跟实际生产环境的差不太多。

```chart
{
  "type": "pie",
  "data": {
    "datasets": [
      {
        "data": [2015839, 5530446, 2888258, 89660688],
        "backgroundColor": ["rgba(255, 99, 132, 0.8)", "rgba(255, 159, 64, 0.8)", "rgba(255, 205, 86, 0.8)", "rgba(75, 192, 192, 0.8)"],
        "label": "各行为类型样本数"
      }
    ],
    "labels": ["buy", "cart", "fav", "pv"]
  }
}


```

最后我们检查一下脏数据的情况，从业务逻辑上来说，购买行为往往跟在点击行为之后，换言之，不存在只有购买而没有点击的数据记录。而这份数据没有点击，只有商详浏览，那么理论上会存在一些当天只有 buy 行为而没有 pv 行为的记录，我们统计一下这样的记录有多少

```sql
select
    count(*) as buy_cnt,
    sum(is_click) as click_cnt
from(
    select
        dt,
        user_id,
        item_id,
        max(if(action_type = 'pv', 1, 0)) as is_click,
        max(if(action_type = 'buy', 1, 0)) as is_buy
    from user_behavior
    group by dt, user_id, item_id
) as t
where is_buy = 1;

buy_cnt   click_cnt
1966120   1053586
```

可以看到，超过一半的 buy 行为，在当天找不到对应的 pv 行为，这个缺失量太高了以至于我们无法快速的修复（扔掉没有 pv 行为的 buy 记录或者给 buy 记录 mock 一条 pv 记录），因此只能从样本的构建逻辑上进行处理。

## 扩展数据表

单纯一个 `user_behavior`​ 表还不足以后续的数据分析、算法建模工作，所以我们还需要一些额外的扩展数据表，例如用户足迹表、用户特征表、商品特征表、样本表等。

### 样本表

​`user_behavior`​ 表包含了 2017 年 11 月 25 日至 2017 年 12 月 3 日共计 9 天数据，由于计算特征需要使用过去一段时间内的记录进行统计聚合，因此我们取 2017-12-02 这天数据作为训练集和验证集，2017-12-03 这天的数据作为测试集，其余的 2017-11-25 ~ 2017-12-01 共计 7 天数据我们用来构建特征。

由于数据集没有曝光数据，只有点击、加购、收藏、购买数据，因此这份数据只能用来训练一个 CVR 模型，无法训练 CTR 模型，所以我们的 label 是 buy。正如我们前面数据探查环节提到的，有大量的 buy 行为在当天没有 pv 行为，因此对于正负样本，我们定义为

* 正样本：如果一个 (user_id, item_id) 在当天有过 buy 行为，则 label = 1
* 负样本：如果一个 (user_id, item_id) 在当天有过 pv, fav, cart 行为（视为有点击），但没有 buy 行为，则 label = 0

基于上述定义，构建样本的逻辑如下

```sql
create table user_behavior_sample(
    user_id bigint comment '用户 ID',
    item_id bigint comment '商品 ID',
    label tinyint comment '是否购买'
) comment '样本表'
partitioned by(
    stage string comment '数据用途'
) stored as orc tblproperties('orc.compress' = 'SNAPPY');

insert overwrite table user_behavior_sample partition(stage)
select
    user_id,
    item_id,
    max(if(action_type = 'buy', 1, 0)) as label,
    case
        when dt = '2017-12-03' then 'test'
        when abs(hash(user_id) % 100) < 80 then 'train'
        else 'valid'
    end as stage
from user_behavior
where dt in('2017-12-02', '2017-12-03')
group by dt, user_id, item_id
```

上面 SQL 的逻辑为，只要 (user_id, item_id) 有过 buy 行为，则最终 max 一定等于 1，如果没有 buy 行为，那么其他行为（pv, fav, cart）都是 0，最终 max 一定等于 0，这与我们的样本逻辑定义一致。

stage 分区字段标记了 (user_id, item_id) 的用途，在 2017-12-02 的数据上，我们对 user_id 进行 hash，按用户维度切分 80% 的用户用于训练，剩余的 20% 用户用于验证，在 2017-12-03 的数据上，我们将所有的记录都用于测试。

构建完毕后，我们统计以下各环节的样本分布情况

```sql
select
    stage,
    count(*) as sample_cnt,
    count(distinct user_id) as uv,
    sum(label) as positive_sample_cnt,
    sum(1 - label) as negative_sample_cnt,
    avg(label) as cvr
from user_behavior_sample
group by stage;

stage   sample_cnt   uv       positive_sample_cnt    negative_sample_cnt   cvr
train   9280374      775983   201275                 9079099               0.021688242305751903
valid   2324445      194418   50543                  2273902               0.02174411526192274
test    11509180     966977   251597                 11257583              0.021860549578684146
```

可以看到，数据基本符合预期，训练集和验证集的用户占比为 4 = 80% / 20%，三个数据集的 cvr 均为 2.1% 左右。训练样本规模为 900 万左右，足以训练一个 CVR 模型。

### 用户足迹表

用户足迹表，即一张记录了 user_id -> [ item_trace1, item_trace2, …, item_trace_n ] 映射关系的表，主要用途有以下几点：

* 召回阶段，通过用户足迹进行 trigger selection 以及 u2i2i 召回
* 排序阶段，通过用户序列构建 i2i 特征或者 DIN 的序列特征
* 重排阶段，通过用户足迹执行偏好调权、曝光频控等策略

构建用户足迹表，我们这里只进行简单地聚合，其中每个 item_trace 记录了 item_id, cate_id, action_type, action_time 信息，并以 json 结构存储到表中。由于我们把 2017-12-02 作为训练集和验证集，2017-12-03 作为测试集，因此构建用户足迹的时候我们需要构建两份数据，即 2017-11-25 ~ 2017-12-01 和 2017-11-26 ~ 2017-12-02 两个时间窗口，完整的代码如下所示

```sql
insert overwrite table user_behavior_trace partition(stage)
-- 训练集 & 验证集足迹
select
    user_id,
    array_sort(
        collect_list(named_struct(
            'item_id', item_id,
            'cate_id', cate_id,
            'type', action_type,
            'time', action_time
        )),
        (left, right) -> case when left.time < right.time then -1 when left.time > right.time then 1 else 0 end
    ) as trace,
    if(abs(hash(user_id) % 100) < 80, 'train', 'valid') as stage
from user_behavior
where dt between '2017-11-25' and '2017-12-01'
group by user_id

union all
-- 测试集足迹
select
    user_id,
    array_sort(
        collect_list(named_struct(
            'item_id', item_id,
            'cate_id', cate_id,
            'type', action_type,
            'time', action_time
        )),
        (left, right) -> case when left.time < right.time then -1 when left.time > right.time then 1 else 0 end
    ) as trace,
    'test' as stage
from user_behavior
where dt between '2017-11-26' and '2017-12-02'
group by user_id;
```

最后我们检查一下足迹表的数据

```sql
select trace
from user_behavior_trace
where size(trace) = 2
limit 10;

user_id trace   stage
[{"item_id":3930302,"cate_id":2892802,"type":"pv","time":"2017-11-30 22:02:21"},{"item_id":4010057,"cate_id":1216617,"type":"pv","time":"2017-12-02 14:44:56"}]
[{"item_id":3802778,"cate_id":4082778,"type":"pv","time":"2017-11-27 18:46:39"},{"item_id":4043208,"cate_id":327651,"type":"pv","time":"2017-12-02 13:01:32"}]
[{"item_id":459809,"cate_id":4147847,"type":"pv","time":"2017-11-29 11:34:55"},{"item_id":3288029,"cate_id":2887965,"type":"pv","time":"2017-12-02 20:10:40"}]
[{"item_id":3880677,"cate_id":1464116,"type":"pv","time":"2017-12-02 20:09:59"},{"item_id":4206150,"cate_id":1464116,"type":"pv","time":"2017-12-02 20:10:11"}]
[{"item_id":3467328,"cate_id":672001,"type":"pv","time":"2017-11-30 10:13:09"},{"item_id":655657,"cate_id":2188684,"type":"pv","time":"2017-12-02 22:55:11"}]
[{"item_id":3889416,"cate_id":3566034,"type":"pv","time":"2017-11-26 19:35:10"},{"item_id":2097882,"cate_id":4462359,"type":"pv","time":"2017-12-02 22:08:00"}]
[{"item_id":1095210,"cate_id":1994940,"type":"pv","time":"2017-11-27 14:36:59"},{"item_id":2639165,"cate_id":1994940,"type":"pv","time":"2017-12-02 09:32:04"}]
[{"item_id":3465547,"cate_id":55312,"type":"pv","time":"2017-11-29 08:32:09"},{"item_id":848183,"cate_id":4589142,"type":"pv","time":"2017-12-02 22:08:54"}]
[{"item_id":2063180,"cate_id":1609851,"type":"cart","time":"2017-11-28 16:59:28"},{"item_id":2190431,"cate_id":1609851,"type":"pv","time":"2017-12-02 09:42:37"}]
[{"item_id":4699951,"cate_id":982926,"type":"pv","time":"2017-11-26 07:50:39"},{"item_id":918629,"cate_id":3860845,"type":"cart","time":"2017-12-02 11:21:34"}]
```

可以看到，json 的数据格式复合我们预定义的结构。

## 相关文献

* [User Behavior Data from Taobao for Recommendation](https://tianchi.aliyun.com/dataset/649)
