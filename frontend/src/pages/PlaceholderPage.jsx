import { EmptyState } from '../components/EmptyState';

const PAGE_COPY = {
  models: {
    title: '模型预测',
    stage: 'MVP-2',
    description: '管理模型版本、训练数据区间、预测分数、Top N 表现、Rank IC 和分层收益。',
    items: ['标签构建', 'LightGBM 训练', '模型版本', '预测排名'],
  },
  selection: {
    title: '选股策略',
    stage: 'MVP-2',
    description: '将模型预测转换成强推荐、观察、剔除和持有复评清单。',
    items: ['Top N 候选', '风险过滤', '推荐等级', '买入条件'],
  },
  portfolio: {
    title: '组合管理',
    stage: 'MVP-3',
    description: '从候选股票池生成目标组合，控制单票、行业和总仓位。',
    items: ['当前持仓', '目标组合', '仓位差异', '行业暴露'],
  },
  'trade-plans': {
    title: '交易计划',
    stage: 'MVP-3',
    description: '生成明确的买入、卖出、加仓、减仓计划，并执行纪律检查。',
    items: ['参考价格', '止损规则', '止盈规则', '失效条件'],
  },
  'trade-records': {
    title: '交易记录',
    stage: 'MVP-4',
    description: '记录真实成交、手续费、滑点、计划偏离和非系统交易。',
    items: ['执行记录', '计划关联', '偏离原因', '当前持仓'],
  },
  reviews: {
    title: '复盘分析',
    stage: 'MVP-4',
    description: '完成单笔交易、周度组合和月度模型的复盘归因。',
    items: ['超额收益', '最大回撤', '胜率', '纪律评分'],
  },
};

export function PlaceholderPage({ pageId }) {
  const copy = PAGE_COPY[pageId];
  return <EmptyState {...copy} />;
}
