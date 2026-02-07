#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
statistical_tests.py
---------------------------------
IC统计检验模块 - 生产级量化因子统计检验

功能包括：
- IC时间序列的t-statistic计算（Newey-West调整）
- p-value计算（单尾/双尾检验）
- Information Ratio (IR) 计算
- 年化IR和置信区间
- 自相关调整后的统计检验
- 多重比较校正（Bonferroni, FDR）
- 滚动窗口统计稳定性分析

Author: Beta (NLP Sentiment Factor Refactor)
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json
import logging


@dataclass
class ICStatisticalTest:
    """IC统计检验结果数据类"""
    # 基本统计量
    ic_mean: float
    ic_std: float
    ic_skewness: float
    ic_kurtosis: float
    n_observations: int
    
    # t统计量（标准和新调整）
    t_stat_standard: float
    t_stat_newey_west: float
    
    # p-value
    p_value_one_tailed: float
    p_value_two_tailed: float
    p_value_newey_west: float
    
    # 信息比率
    ir_daily: float
    ir_annualized: float
    ir_confidence_interval_95: Tuple[float, float]
    
    # 统计显著性判断
    is_significant_5pct: bool
    is_significant_1pct: bool
    is_significant_newey_west_5pct: bool
    
    # 自相关调整
    autocorrelation_lag1: float
    effective_sample_size: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'ic_mean': round(self.ic_mean, 6),
            'ic_std': round(self.ic_std, 6),
            'ic_skewness': round(self.ic_skewness, 4),
            'ic_kurtosis': round(self.ic_kurtosis, 4),
            'n_observations': self.n_observations,
            't_stat_standard': round(self.t_stat_standard, 4),
            't_stat_newey_west': round(self.t_stat_newey_west, 4),
            'p_value_one_tailed': round(self.p_value_one_tailed, 6),
            'p_value_two_tailed': round(self.p_value_two_tailed, 6),
            'p_value_newey_west': round(self.p_value_newey_west, 6),
            'ir_daily': round(self.ir_daily, 4),
            'ir_annualized': round(self.ir_annualized, 4),
            'ir_ci_95_lower': round(self.ir_confidence_interval_95[0], 4),
            'ir_ci_95_upper': round(self.ir_confidence_interval_95[1], 4),
            'is_significant_5pct': self.is_significant_5pct,
            'is_significant_1pct': self.is_significant_1pct,
            'is_significant_newey_west_5pct': self.is_significant_newey_west_5pct,
            'autocorrelation_lag1': round(self.autocorrelation_lag1, 4),
            'effective_sample_size': round(self.effective_sample_size, 2)
        }


def calculate_newey_west_tstat(ic_series: pd.Series, lags: int = 5) -> float:
    """
    计算Newey-West调整的t统计量
    
    Newey-West调整用于处理时间序列中的异方差和自相关问题，
    是量化金融中IC检验的标准做法。
    
    Args:
        ic_series: IC时间序列
        lags: 滞后阶数，默认5（约一周交易日）
        
    Returns:
        Newey-West调整后的t统计量
    """
    if len(ic_series) < lags + 2:
        return np.nan
    
    ic_array = ic_series.dropna().values
    n = len(ic_array)
    ic_mean = np.mean(ic_array)
    
    # 计算方差
    residuals = ic_array - ic_mean
    variance = np.sum(residuals ** 2) / n
    
    # Newey-West调整
    for lag in range(1, lags + 1):
        weight = 1 - lag / (lags + 1)
        autocov = np.sum(residuals[:-lag] * residuals[lag:]) / n
        variance += 2 * weight * autocov
    
    # 确保方差为正
    variance = max(variance, 1e-10)
    
    # 计算标准误
    se = np.sqrt(variance / n)
    
    # t统计量
    t_stat = ic_mean / se if se > 0 else 0
    
    return t_stat


def calculate_autocorrelation(ic_series: pd.Series, max_lags: int = 5) -> Dict[str, float]:
    """
    计算IC序列的自相关系数
    
    Args:
        ic_series: IC时间序列
        max_lags: 最大滞后阶数
        
    Returns:
        包含各阶自相关系数的字典
    """
    ic_clean = ic_series.dropna()
    n = len(ic_clean)
    
    if n < max_lags + 2:
        return {f'lag_{i}': 0.0 for i in range(1, max_lags + 1)}
    
    autocorr = {}
    for lag in range(1, max_lags + 1):
        if n > lag:
            corr = np.corrcoef(ic_clean[:-lag], ic_clean[lag:])[0, 1]
            autocorr[f'lag_{lag}'] = 0.0 if np.isnan(corr) else round(corr, 4)
        else:
            autocorr[f'lag_{lag}'] = 0.0
    
    return autocorr


def calculate_effective_sample_size(ic_series: pd.Series, max_lags: int = 5) -> float:
    """
    计算有效样本量（考虑自相关）
    
    公式: n_eff = n / (1 + 2 * sum(autocorrelations))
    
    Args:
        ic_series: IC时间序列
        max_lags: 最大滞后阶数
        
    Returns:
        有效样本量
    """
    n = len(ic_series.dropna())
    autocorr = calculate_autocorrelation(ic_series, max_lags)
    
    # 计算自相关和
    autocorr_sum = sum(max(0, v) for v in autocorr.values())  # 只考虑正自相关
    
    # 有效样本量
    n_eff = n / (1 + 2 * autocorr_sum) if autocorr_sum >= 0 else n
    
    return max(n_eff, 10)  # 至少10个样本


def calculate_information_ratio(
    ic_series: pd.Series, 
    annualization_factor: int = 252
) -> Tuple[float, float, Tuple[float, float]]:
    """
    计算Information Ratio (IR)
    
    IR = IC_mean / IC_std
    
    Args:
        ic_series: IC时间序列
        annualization_factor: 年化因子（日度数据=252）
        
    Returns:
        (日度IR, 年化IR, 95%置信区间)
    """
    ic_clean = ic_series.dropna()
    n = len(ic_clean)
    
    if n < 2:
        return 0.0, 0.0, (0.0, 0.0)
    
    ic_mean = ic_clean.mean()
    ic_std = ic_clean.std()
    
    # 日度IR
    ir_daily = ic_mean / ic_std if ic_std > 0 else 0.0
    
    # 年化IR
    ir_annual = ir_daily * np.sqrt(annualization_factor)
    
    # 95%置信区间（基于标准误）
    se = ic_std / np.sqrt(n)
    ci_lower = (ic_mean - 1.96 * se) / ic_std if ic_std > 0 else 0.0
    ci_upper = (ic_mean + 1.96 * se) / ic_std if ic_std > 0 else 0.0
    
    return ir_daily, ir_annual, (round(ci_lower, 4), round(ci_upper, 4))


def perform_ic_statistical_test(
    ic_series: pd.Series,
    ic_type: str = "IC",
    newey_west_lags: int = 5
) -> ICStatisticalTest:
    """
    执行完整的IC统计检验
    
    Args:
        ic_series: IC时间序列（日度）
        ic_type: IC类型标识（用于日志）
        newey_west_lags: Newey-West滞后阶数
        
    Returns:
        ICStatisticalTest对象
    """
    ic_clean = ic_series.dropna()
    n = len(ic_clean)
    
    if n < 10:
        logging.warning(f"{ic_type}样本量不足({n})，统计检验可能不可靠")
    
    # 基本统计量
    ic_mean = ic_clean.mean()
    ic_std = ic_clean.std()
    ic_skewness = ic_clean.skew()
    ic_kurtosis = ic_clean.kurtosis()
    
    # 标准t统计量
    t_stat_standard = ic_mean / (ic_std / np.sqrt(n)) if ic_std > 0 else 0.0
    
    # Newey-West调整t统计量
    t_stat_newey_west = calculate_newey_west_tstat(ic_clean, newey_west_lags)
    
    # p-value
    p_value_two_tailed = 2 * (1 - stats.t.cdf(abs(t_stat_standard), n - 1))
    p_value_one_tailed = 1 - stats.t.cdf(abs(t_stat_standard), n - 1)
    p_value_nw = 2 * (1 - stats.t.cdf(abs(t_stat_newey_west), n - 1))
    
    # Information Ratio
    ir_daily, ir_annual, ir_ci = calculate_information_ratio(ic_clean)
    
    # 自相关
    autocorr = calculate_autocorrelation(ic_clean)
    autocorr_lag1 = autocorr.get('lag_1', 0.0)
    n_eff = calculate_effective_sample_size(ic_clean)
    
    # 显著性判断
    is_sig_5pct = p_value_two_tailed < 0.05
    is_sig_1pct = p_value_two_tailed < 0.01
    is_sig_nw_5pct = p_value_nw < 0.05
    
    return ICStatisticalTest(
        ic_mean=round(ic_mean, 6),
        ic_std=round(ic_std, 6),
        ic_skewness=round(ic_skewness, 4),
        ic_kurtosis=round(ic_kurtosis, 4),
        n_observations=n,
        t_stat_standard=round(t_stat_standard, 4),
        t_stat_newey_west=round(t_stat_newey_west, 4),
        p_value_one_tailed=round(p_value_one_tailed, 6),
        p_value_two_tailed=round(p_value_two_tailed, 6),
        p_value_newey_west=round(p_value_nw, 6),
        ir_daily=round(ir_daily, 4),
        ir_annualized=round(ir_annual, 4),
        ir_confidence_interval_95=ir_ci,
        is_significant_5pct=is_sig_5pct,
        is_significant_1pct=is_sig_1pct,
        is_significant_newey_west_5pct=is_sig_nw_5pct,
        autocorrelation_lag1=round(autocorr_lag1, 4),
        effective_sample_size=round(n_eff, 2)
    )


def perform_multiple_comparison_correction(
    p_values: List[float],
    method: str = "bonferroni",
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    多重比较校正
    
    Args:
        p_values: p值列表
        method: 校正方法 ('bonferroni', 'fdr_bh')
        alpha: 显著性水平
        
    Returns:
        校正结果字典
    """
    n = len(p_values)
    
    if method == "bonferroni":
        # Bonferroni校正
        corrected_pvalues = [min(p * n, 1.0) for p in p_values]
        significant = [p < alpha for p in corrected_pvalues]
        
        return {
            'method': 'Bonferroni',
            'original_pvalues': p_values,
            'corrected_pvalues': corrected_pvalues,
            'significant': significant,
            'n_tests': n,
            'alpha': alpha
        }
    
    elif method == "fdr_bh":
        # Benjamini-Hochberg FDR校正
        sorted_indices = np.argsort(p_values)
        sorted_pvalues = np.array(p_values)[sorted_indices]
        
        corrected = np.zeros(n)
        for i, p in enumerate(sorted_pvalues):
            corrected[sorted_indices[i]] = min(p * n / (i + 1), 1.0)
        
        significant = [p < alpha for p in corrected]
        
        return {
            'method': 'Benjamini-Hochberg FDR',
            'original_pvalues': p_values,
            'corrected_pvalues': corrected.tolist(),
            'significant': significant,
            'n_tests': n,
            'alpha': alpha
        }
    
    else:
        raise ValueError(f"未知的校正方法: {method}")


def rolling_ic_stability_analysis(
    ic_series: pd.Series,
    window: int = 63,  # 约3个月
    step: int = 21     # 约1个月
) -> pd.DataFrame:
    """
    滚动窗口IC稳定性分析
    
    Args:
        ic_series: IC时间序列
        window: 滚动窗口大小
        step: 滚动步长
        
    Returns:
        滚动统计结果DataFrame
    """
    ic_clean = ic_series.dropna().reset_index(drop=True)
    results = []
    
    for start in range(0, len(ic_clean) - window + 1, step):
        end = start + window
        window_ic = ic_clean.iloc[start:end]
        
        if len(window_ic) < window * 0.8:  # 要求至少80%数据
            continue
        
        ic_mean = window_ic.mean()
        ic_std = window_ic.std()
        ir = ic_mean / ic_std if ic_std > 0 else 0
        
        # 简单t统计量
        t_stat = ic_mean / (ic_std / np.sqrt(len(window_ic))) if ic_std > 0 else 0
        
        results.append({
            'window_start': start,
            'window_end': end,
            'ic_mean': round(ic_mean, 4),
            'ic_std': round(ic_std, 4),
            'ir': round(ir, 4),
            't_stat': round(t_stat, 4),
            'n_obs': len(window_ic)
        })
    
    return pd.DataFrame(results)


def generate_ic_statistical_report(
    ic_df: pd.DataFrame,
    output_path: str = "reports/ic_statistical_report.json"
) -> Dict[str, Any]:
    """
    生成IC统计检验完整报告
    
    Args:
        ic_df: 包含IC和RankIC的DataFrame
        output_path: 输出文件路径
        
    Returns:
        完整报告字典
    """
    report = {
        'report_type': 'IC Statistical Test Report',
        'generated_at': pd.Timestamp.now().isoformat(),
        'methodology': {
            't_statistic': 'Standard t-test with Newey-West adjustment',
            'newey_west_lags': 5,
            'ir_annualization': 252,
            'confidence_level': 0.95
        }
    }
    
    # IC统计检验
    if 'IC' in ic_df.columns:
        ic_test = perform_ic_statistical_test(ic_df['IC'], ic_type="IC")
        report['ic_test'] = ic_test.to_dict()
    
    # Rank-IC统计检验
    if 'RankIC' in ic_df.columns:
        rank_ic_test = perform_ic_statistical_test(ic_df['RankIC'], ic_type="Rank-IC")
        report['rank_ic_test'] = rank_ic_test.to_dict()
    
    # 滚动稳定性分析
    if 'IC' in ic_df.columns:
        rolling_analysis = rolling_ic_stability_analysis(ic_df['IC'])
        report['rolling_stability'] = {
            'window_size': 63,
            'step_size': 21,
            'n_windows': len(rolling_analysis),
            'ic_mean_std': round(rolling_analysis['ic_mean'].std(), 4) if len(rolling_analysis) > 0 else 0,
            'windows': rolling_analysis.to_dict('records')
        }
    
    # 保存报告
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logging.info(f"IC统计检验报告已保存: {output_path}")
    
    return report


def print_ic_test_summary(test_result: ICStatisticalTest, ic_type: str = "IC") -> None:
    """
    打印IC检验结果摘要
    
    Args:
        test_result: ICStatisticalTest对象
        ic_type: IC类型名称
    """
    print(f"\n{'='*60}")
    print(f"📊 {ic_type} 统计检验结果")
    print(f"{'='*60}")
    
    print(f"\n基本统计量:")
    print(f"  • 样本量: {test_result.n_observations}")
    print(f"  • IC均值: {test_result.ic_mean:.6f}")
    print(f"  • IC标准差: {test_result.ic_std:.6f}")
    print(f"  • 偏度: {test_result.ic_skewness:.4f}")
    print(f"  • 峰度: {test_result.ic_kurtosis:.4f}")
    
    print(f"\nt统计量:")
    print(f"  • 标准t统计量: {test_result.t_stat_standard:.4f}")
    print(f"  • Newey-West调整t: {test_result.t_stat_newey_west:.4f}")
    
    print(f"\np-value:")
    print(f"  • 双尾p-value: {test_result.p_value_two_tailed:.6f}")
    print(f"  • 单尾p-value: {test_result.p_value_one_tailed:.6f}")
    print(f"  • Newey-West p-value: {test_result.p_value_newey_west:.6f}")
    
    print(f"\nInformation Ratio:")
    print(f"  • 日度IR: {test_result.ir_daily:.4f}")
    print(f"  • 年化IR: {test_result.ir_annualized:.4f}")
    print(f"  • IR 95% CI: [{test_result.ir_confidence_interval_95[0]:.4f}, {test_result.ir_confidence_interval_95[1]:.4f}]")
    
    print(f"\n显著性判断:")
    sig_5 = "✅ 显著" if test_result.is_significant_5pct else "❌ 不显著"
    sig_1 = "✅ 显著" if test_result.is_significant_1pct else "❌ 不显著"
    sig_nw = "✅ 显著" if test_result.is_significant_newey_west_5pct else "❌ 不显著"
    print(f"  • 5%显著性水平: {sig_5}")
    print(f"  • 1%显著性水平: {sig_1}")
    print(f"  • Newey-West 5%: {sig_nw}")
    
    print(f"\n自相关分析:")
    print(f"  • 一阶自相关: {test_result.autocorrelation_lag1:.4f}")
    print(f"  • 有效样本量: {test_result.effective_sample_size:.1f}")
    
    print(f"{'='*60}")


if __name__ == "__main__":
    # 示例用法
    import argparse
    
    parser = argparse.ArgumentParser(description="IC统计检验")
    parser.add_argument("--ic_file", default="data/processed/ic_results.csv", help="IC数据文件")
    parser.add_argument("--output", default="reports/ic_statistical_report.json", help="输出报告路径")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    
    if Path(args.ic_file).exists():
        ic_df = pd.read_csv(args.ic_file)
        report = generate_ic_statistical_report(ic_df, args.output)
        
        # 打印摘要
        if 'ic_test' in report:
            test = ICStatisticalTest(**report['ic_test'])
            print_ic_test_summary(test, "IC")
        
        if 'rank_ic_test' in report:
            test = ICStatisticalTest(**report['rank_ic_test'])
            print_ic_test_summary(test, "Rank-IC")
    else:
        print(f"❌ IC数据文件不存在: {args.ic_file}")
