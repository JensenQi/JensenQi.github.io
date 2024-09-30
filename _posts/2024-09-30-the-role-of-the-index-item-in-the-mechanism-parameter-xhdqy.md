---
title: 机制参数中指数项的作用
mermaid: false
chart: false
mathjax: true
mathjax_autoNumber: true
tags: 策略算法
---



## 背景

对于大部分的广告或推荐算法团队而言，都会通过模型对每个商品计算出一个 CTR 打分和 CVR 打分，然后将这两个模型的打分综合起来计算一个排序分数 RankScore，最后按 RankScore 倒排序阶段一定数量的商品送入重排。

在推荐场景下，RankScore 的计算公式一般为

$$
RankScore = ctr^{ctrPow}*cvr^{cvrPow}*price^{pricePow}
$$

因此可以近似地认为 RankScore \= GMV Score，而在广告场景下，需要考虑广告出价，因此一般会加上一个 cpmScore 和 GMV Score 的权重，也就是

$$
RankScore = ctr^{ctrPow}*bid + gmvWeight * ctr^{ctrPow}*cvr^{cvrPow}*price^{pricePow}
$$

这两个公式是比较显而易见的，唯一一个可能与直觉不符的点在于，CTR、CVR、Price 项都有一个指数项，这三个指数我们称之为机制参数。这些指数项的作用其目的是为了控制 RankScore 的走向：当其他 power 项不变的时候，调大 ctrPow，则 CTR 越高的商品越可能被展示，那么推荐效果会倾向于点击，对应的，如果调大 cvrPow，则 CVR 越高的商品越可能被展示，那么推荐效果会倾向于转化，同理，如果调大 pricePow，则价格越高的商品越可能被展示，则推荐效果倾向于高单价商品。

有的人可能会对上面这个结论产生疑惑：假设我们定义 ctr 为 $x$，如果 $a > b$，则 $x^a/x^b =x^{(a-b)}$ ，由于 $a-b > 0$ 且 $0 \leq x \leq 1$ ，所以 $x^a/x^b < 1$，也就意味着，ctrPow 越大，则 $ctr^{ctrPow}$ 越小，那么 rankScore 就越小，这与上面的结论矛盾。因此这篇博客我们通过严格的数学证明来证明这个结论。

## 证明

对于一个请求，召回了 N 的商品，它们的 CTR 打分为 $x_i$，CVR 打分为 $y_i$, 其余策略加权项汇总为 $\eta_i$, ctr power 和 cvr power 分别为 $\alpha$ 和 $\beta$，则它们的 RankScore 计算公式为

$$
s_i = \eta_i * x_i^\alpha * y_i^\beta
$$

由于 $\ln$ 函数是保序映射, 即对于 $x_1 > x_2$, 有 $\ln(x_1) > \ln(x_2)$，为了方便处理，我们将 rankScore 取对数，即

$$
s_i = \ln \eta_i + \alpha \ln x_i + \beta \ln y_i
$$

> 💡猜想  
> 不变的前提下， 取值越大，则越倾向于 CVR 打分

转化为数学语言，即对于队列中任意两个商品 $i$ 和 $j$，在 $\alpha$ 不变的情况下，$\beta$ 取值越大，则 CVR 打分高的商品，排在前面（rankScore 高）的概率 $p$ 越大

$$
p = P(s_i > s_j | y_i > y_j)
$$

应用条件概率公式，有

$$
p = P(s_i > s_j | y_i > y_j) = \frac{P(s_i > s_j \cap y_i > y_j)}{P(y_i > y_j)}
$$

对于 $s_i > s_j$ 事件，可以通过两者的差大于 0 来描述，即

$$
s_i - s_j = \ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j}+\beta\ln\frac{y_i}{y_j} > 0
$$

则可以改写成

$$
p = P(s_i > s_j | y_i > y_j) = \frac{P(\ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j}+\beta\ln\frac{y_i}{y_j} > 0 \cap y_i > y_j)}{P(y_i > y_j)}
$$

同理，对于另一个更大的机制参数 $\beta' > \beta$ , 它对应的概率 $p'$ 为

$$
p' = P(s_i > s_j | y_i > y_j) = \frac{P(\ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j}+\beta'\ln\frac{y_i}{y_j} > 0 \cap y_i > y_j)}{P(y_i > y_j)}
$$

如果 $p'>p$，则可以说明 $\beta$ 越大，CVR 打分高排在前面得概率越高，为此我们计算比值 $p'/p$，有

$$
\frac{p'}{p} = \frac{P(\ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j}+\beta'\ln\frac{y_i}{y_j} > 0 \cap y_i > y_j)}{P(\ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j}+\beta\ln\frac{y_i}{y_j} > 0 \cap y_i > y_j)}
$$

根据条件概率得含义，可以增加约束 $y_i > y_j$，然后简化为

$$
\frac{p'}{p} = \frac{P(\ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j}+\beta'\ln\frac{y_i}{y_j} > 0)}{P(\ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j}+\beta\ln\frac{y_i}{y_j} > 0)}， s.t~~y_i>y_j
$$

接着我们移一下项，有

$$
\frac{p'}{p} = \frac{P(\ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j} > \beta'\ln\frac{y_j}{y_i} )}{P(\ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j} > \beta\ln\frac{y_j}{y_i} )}
$$

由于 $y_i > y_j$ ，则 $\ln\frac{y_j}{y_i} < 0$，因此 $\beta' > \beta$ 两边乘上 $\ln\frac{y_j}{y_i}$ 需要变号，则

$$
\beta'\ln\frac{y_j}{y_i} < \beta \ln\frac{y_j}{y_i}
$$

记随机变量  $z_k = \ln\frac{\eta_i}{\eta_j} + \alpha \ln\frac{x_i}{x_j}$，根据累计分布的性质

$$
P(z_k > a) > P(z_k > b), s.t~~a<b
$$

有

$$
P(z_k > \beta'\ln\frac{y_j}{y_i} ) > P(z_k > \beta\ln\frac{y_j}{y_i} )
$$

因此 $p' > p$，证毕

## 悖论产生的原因

回到我们开篇提到的悖论

> 假设我们定义 ctr 为 $x$，如果 $a > b$，则 $x^a/x^b =x^{(a-b)}$ ，由于 $a-b > 0$ 且 $0 \leq x \leq 1$ ，所以 $x^a/x^b < 1$，也就意味着，ctrPow 越大，则 $ctr^{ctrPow}$ 越小，那么 rankScore 就越小

这个结论的问题出在哪里呢？问题出在  $x^a/x^b < 1$ 这个比值是无意义的，因为这个对比相当于在两套机制参数下对同一个商品的 RankScore 进行对比。而有意义的对比是什么呢？有意义的对比应该是同一套机制参数下，不同商品的 rankScore 对比。
