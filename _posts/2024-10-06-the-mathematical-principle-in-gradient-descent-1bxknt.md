---
title: 梯度下降中的数学原理
mermaid: false
chart: false
mathjax: true
mathjax_autoNumber: true
tags: 机器学习
---



众所周知，在机器学习中梯度下降是一种广泛使用的极值点搜索算法，其执行流程可以很简单地概括为：求取函数在当前点的梯度方向，然后往梯度方向迈一小步，到达函数的下一个点，不断循环直到收敛，这个过程也常被通俗地称为下山法。如果从常识来看，这似乎是一件很显然的事，毕竟梯度指示了你下山的方向，但如果真要细究这件事就会有点说不清了：凭什么说沿梯度方向前进就一定能到达极值点？这篇文章我们就来仔细地讨论这件事。

## 最优性证明

我们给出梯度下降的数学描述：假设关于 $d$ 维变量 $\vec{X} = (x_1, x2, \cdots, x_d)$ 的实函数 $F(\vec{X})$ 在点 $\vec{X}_t$ 处有定义且可导，为了最小化 $F(\vec{X})$，则变量 $\vec{X}$ 的迭代公式为

$$
\vec{X}_{t+1} =  \vec{X}_t - \eta \nabla F(\vec{X}_t)
$$

其中 $\eta > 0$ 为一个足够小的正数，这也就是我们常说的学习率，$t \geq 0$ 也就是迭代次数。下面我们将证明梯度方向总是指向函数值变小的方向，并且是最优的方向。

首先我们假设 $d$ 元函数 $F(\vec{X})$ 在某点 $X_t(x_1, x_2, \cdots, x_d)$ 上可微，并且点 $X_t(x_1, x_2, \cdots, x_d)$ 与曲线上邻域内的另一点 $X_{t+1}(x_1 +\Delta x_1, x_2 +\Delta x_2, \cdots, x_d +\Delta x_d)$ 构成向量 $X_tX_{t+1} = (\Delta x_1, \Delta x_2, \cdots, \Delta x_d)$ ，在梯度下降场景中，这个向量也就是我们可能的下山方向。

根据全微分的性质，有

$$
F(X_{t+1}) - F(X_t) = \frac{\partial F}{\partial x_1}\Big|_{X_t} \Delta x_1 + \frac{\partial F}{\partial x_2}\Big|_{X_t} \Delta x_2 + \cdots +\frac{\partial F}{\partial x_d}\Big|_{X_t} \Delta x_d + o(|| X_tX_{t+1}||)
$$

那么对于 $F(\vec{X})$ 在某点 $X_t$ 上的变化率，代入上式，有

$$
\begin{split}
\lim_{|| X_tX_{t+1}|| \rightarrow0} \frac{F(X_{t+1}) - F(X_t)}{|| X_tX_{t+1}||} 
&= \lim_{|| X_tX_{t+1}|| \rightarrow0}\Big[ 
 \frac{\partial F}{\partial x_1}\Big|_{X_t} \frac{\Delta x_1 }{|| X_tX_{t+1}||}
+  \frac{\partial F}{\partial x_2}\Big|_{X_t} \frac{\Delta x_2 }{|| X_tX_{t+1}||}
+ \cdots
+\frac{\partial F}{\partial x_d}\Big|_{X_t} \frac{\Delta x_d }{|| X_tX_{t+1}||}
+ \frac{o(||X_tX_{t+1}||)}{||X_tX_{t+1}||}
\Big]
\\
&=\frac{\partial F}{\partial x_1}\Big|_{X_t} \cos\alpha_1 + \frac{\partial F}{\partial x_2}\Big|_{X_t} \cos\alpha_2 + \cdots + \frac{\partial F}{\partial x_d}\Big|_{X_t} \cos\alpha_d
\end{split}
$$

其中 $\alpha_i$ 为坐标轴 $x_i$ 与向量 $X_tX_{t+1}$ 的夹角。显然我们可以很容易地找到与向量 $X_tX_{t+1}$ 方向一致的单位向量 $l_t$

$$
\begin{split}
l_t &= \frac{X_tX_{t+1}}{||X_tX_{t+1}||} = \Big(\frac{\Delta x_1}{||XtX_{t+1}||}, \frac{\Delta x_2}{||XtX_{t+1}||}, \cdots, \frac{\Delta x_d}{||XtX_{t+1}||}\Big) \\
&= (\cos\alpha_1, \cos\alpha_2, \cdots, \cos\alpha_d)
\end{split}
$$

并且根据梯度的定义，函数 $F(\vec{X})$ 在某点 $X_t(x_1, x_2, \cdots, x_d)$ 上的梯度为

$$
\nabla F(\vec{X_t})= \Big(\frac{\partial F}{\partial x_1}\Big|_{X_t}, \frac{\partial F}{\partial x_2}\Big|_{X_t},  \cdots , \frac{\partial F}{\partial x_d}\Big|_{X_t}\Big)
$$

那么极限就可以改写为梯度 $\nabla F(\vec{X_t})$ 与方向向量 $l_t$ 的内积形式

$$
\lim_{|| X_tX_{t+1}|| \rightarrow0} \frac{F(X_{t+1}) - F(X_t)}{|| X_tX_{t+1}||}  =\nabla F(\vec{X_t}) \cdot l_t
$$

根据柯西-施瓦茨不等式，有

$$
|\nabla F(\vec{X_t}) \cdot l_t| \leq ||\nabla F(\vec{X_t})|| *  ||l_t|| \leq ||\nabla F(\vec{X_t})||
$$

上述不等式当且仅当 $\nabla F(\vec{X_t})$ 与方向向量 $l_t$ 方向相同时等号成立。也就意味着，点 $X_t$ 与邻域内的另一点 $X_{t+1}$ 构成的向量 $X_tX_{t+1}$ 方向与函数 $F(\vec{X})$ 在点 $X_t$ 上的梯度方向一致时，函数的变化率 $\lim_{\lvert \lvert  X_tX_{t+1} \rvert \rvert  \rightarrow0} \frac{F(X_{t+1}) - F(X_t)}{\lvert \lvert X_tX_{t+1}\rvert \rvert}$ 取到最大值，也就是函数增长最快的方向（注意这里是增长最快的方向，不是增长最快的点，因为点还需要考虑到步长等因素），对应的，当方向相反时变化率取到最小值，这也就是梯度下降的最优性证明。

当然我们讨论的最优性只是针对与某一点 $X_t$ 而言，也就是如果只知道 $X_t$ 这个点上的信息，那么梯度方向是最优的，但这种最优只是保证其能收敛到局部的极值点，至于这个极值点好还是不好，梯度下降并不能保证，所以才有了动量项、二阶矩等其他优化方法来改进梯度下降这一弱点。

## 蒙特卡罗视角

接下来我们从蒙特卡罗视角下来考虑 Loss 函数最优化这个问题。假设我们有一批训练数据 $D=\{x_1, x_2, \cdots, x_N\}$, 这些训练数据是从一个真实但未知的分布 $p(x)$ 产生出来的，即 $x_i∼p(x),i∈\{1,...,N\}$。

现在我们假设模型的参数为 $W$，那么在训练过程中，我们需要做的是搜索一个最优的参数 $W$，使得期望风险最小化，或者说最小化损失函数 $Loss(W,x)$ 的期望值，也就意味着，我们想要最小化的实际上是

$$
\mathcal{L}(W)=E_x[Loss(W,x)]=\int Loss(W,x)p(x)dx
$$

换言之，我们希望做的是，针对未知分布 $p(x)$ 所有可能的样本 $x_i$，我们计算损失函数的取值，然后求取期望，这才是理想情况下的最优化目标。但实际中我们无法获取到所有可能的样本，但先不管这个，我们先假设我们能获取到所有可能的样本，那么优化目标的梯度为：

$$
\nabla_W\mathcal{L}(W)=\nabla_W E_x[Loss(W,x)]=E_x[\nabla_WLoss(W,x)]
$$

则梯度下降中使用的更新公式为

$$
W_{t+1}=W_t−\eta E_x[\nabla_WLoss(W,x)]
$$

然而不幸的是，期望 $E_x[\nabla_WL(W,x)]$ 无法计算，因为我们并不知道真实的分布 $p(x)$ 是什么，也无法获取到所有可能的样本 $x_i$。 对于求期望的问题，自然而言就会想到用蒙特卡罗来做近似估计，因此期望可以近似为

$$
E_x[\nabla_WLoss(W,x)]\approx\frac{1}{M}\sum_{i=1}^M\nabla_WLoss(W,x_i)
$$

其中 $M$ 为真实的分布 $p(x)$ 下随机采样的样本数，由蒙特卡洛算法的特点可知，越大的 $M$ 值，对期望的近似会越准确，其收敛的速度为 $O(\sqrt M)$，即期望估计的误差每减少一倍，则需要的样本量 $M$ 需要增大一个平方量级。那么对于梯度下降而言，就有

* 当 $M=1$ 时，每次只用一个样本来近似期望，也就是常说的 stochastic gradient descent
* 当 $1\leq M \leq N$ 时，每次只用样本集中的一小部分来近似期望，也就是常说的 mini-batch gradient decent
*  当 $M=N$ 时，每次用样本集中所有的样本来近似期望，也就是常说的 batch gradient decent

所以从蒙特卡罗的视角来看这个问题，SGD, batch GD, mini-batch GD 是同一个东西，唯一的差别只是期望近似时使用的样本量规模上的不同。

## 大批量梯度下降

既然从蒙特卡罗的视角看，batch size 越大，则期望近似的误差越小，那是不是 batch size 越大越好呢？毕竟除了获取到更精确的期望估计外，更大的 batch size 还可以更好地利用分布式计算，毕竟网络传输、GPU 的 host & device 数据同步等操作都需要一定的耗时，如果能使用更大的 batch size，就可以摊消掉这些时间损耗，带来更快的训练速度。

这个问题需要从几个方面看，如果只是单纯调大 batch size（或者调大 worker 数，因为调大 worker 数实际上等价于调大 batch size），而不调整 learning rate，那么对于提升训练速度这个事反而是负面的。假设总样本量为 $N$，batch size 为 $M$，学习率为 $\eta$ ，每一轮参数变更的步长为 $\Delta_i$， 那么一个训练周期内，迭代了 $N/M$ 轮，一个训练周期 epoch 内，参数总共更新的步长是

$$
\sum_{i=1}^{N/M}  \eta * \Delta_i
$$

现在我们将 batch size 调大 10 倍，其他超参数维持不变，那么对于新的配置，一个训练周期 epoch 内，参数总共更新的步长是

$$
\sum_{i=1}^{N/10M}  \eta * \Delta_i'
$$

从前面的章节可以知道，调大 batch size 只是对期望产生一个更准确的估计，因此对于每一轮的训练步长而言并不会产生量级上的变化，因此 $\Delta_i \approx \Delta_i'$，那么新配置相比于老配置而言，一个周期内参数更新步长减少了

$$
\sum_{i=1}^{N/M}  \eta * \Delta_i - \sum_{i=1}^{N/10M}  \eta * \Delta_i' \approx \sum_{i=10M}^{N/M}  \eta * \Delta_i
$$

这大约是 10 倍的差距，为了弥补这个差距，新配置需要训练的周期大约需要增长 10 倍才能达到达到跟 baseline 接近的收敛效果。如果只调大 batch size，虽然期望近似更准确了，但也带来了收敛速度过慢的问题，为了达到相同的收敛精度，需要训练的周期变长。

为了解决收敛速度的问题，我们可能会尝试调大学习率，因为从公式中我们可以看到，虽然每一轮迭代次数变少了，但如果我每一次迭代的步长加大，那么总体来说我每一轮更新的总步长大体上维持一致的，另一方面，由于更大的 batch size 带来更准确的期望估计，因此可以放心地调大 batch size，毕竟朝着正确的方向可以放开步伐大胆地迈过去，但事实真的如此吗？

如果我们把 batch size 调大 K 倍的同时，把 learning rate 也调大 K 倍，试图以此来保证每一个训练周期获取到差不多量级的参数更新量，这听起来似乎是有效的，但这没有考虑到一个问题：如果训练步长太大，那么梯度下降会陷入到震荡的状态。不过在训练的尾声这个问题不严重，因为当模型训练得差不多的时候，损失函数已经接近极值点了，此时网络参数的梯度变化不会太大并且接近于 0，即 $\Delta_i \approx \Delta_i' \approx 0$。但训练的初期这个近似假设是不成立的，因为训练的初期，在随机初始化的基础上，参数快速地变化，也就意味着 $\Delta_i \approx \Delta_i' >> 0$ ，此时需要一个较小的学习率来走出初始阶段的区域，避免在初始区域震荡。

那么这个问题的解决方案就很工程思维了：在初始阶段，我们设置一个较小的学习率，使得损失函数快速走出随机初始化的区域，然后随着训练的进行，我们逐渐调大学习率，直到学习率达到之前的 $K$ 倍，最后在训练的末期，我们逐渐调小学习率，使得模型进入到极值点。

‍
