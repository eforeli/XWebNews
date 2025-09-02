#!/usr/bin/env python3
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from collections import Counter
import re
from typing import Dict, List, Any
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

class Web3TweetAnalyzer:
    def __init__(self, json_file: str):
        """
        初始化Web3推文分析器
        
        Args:
            json_file: 包含推文數據的JSON文件路徑
        """
        self.data = self.load_data(json_file)
        self.df = self.create_dataframe()
        
    def load_data(self, json_file: str) -> Dict[str, List[Dict[str, Any]]]:
        """加載JSON數據文件"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"載入數據文件時發生錯誤: {str(e)}")
            return {}
    
    def create_dataframe(self) -> pd.DataFrame:
        """將JSON數據轉換為pandas DataFrame"""
        all_tweets = []
        for category, tweets in self.data.items():
            all_tweets.extend(tweets)
        
        if not all_tweets:
            return pd.DataFrame()
            
        df = pd.DataFrame(all_tweets)
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        return df
    
    def generate_category_report(self) -> Dict[str, Any]:
        """生成各類別詳細報告"""
        if self.df.empty:
            return {}
            
        report = {}
        
        for category in self.df['category'].unique():
            category_df = self.df[self.df['category'] == category]
            
            report[category] = {
                'total_tweets': len(category_df),
                'avg_likes': category_df['like_count'].mean(),
                'avg_retweets': category_df['retweet_count'].mean(),
                'avg_replies': category_df['reply_count'].mean(),
                'top_tweet': {
                    'text': category_df.loc[category_df['like_count'].idxmax(), 'text'] if not category_df.empty else '',
                    'likes': category_df['like_count'].max(),
                    'url': category_df.loc[category_df['like_count'].idxmax(), 'url'] if not category_df.empty else ''
                },
                'verified_ratio': (category_df['verified'].sum() / len(category_df)) * 100,
                'engagement_score': (category_df['like_count'] + category_df['retweet_count'] + category_df['reply_count']).mean()
            }
            
        return report
    
    def find_trending_keywords(self, min_frequency: int = 3) -> Dict[str, List[tuple]]:
        """找出各類別中的熱門關鍵字"""
        if self.df.empty:
            return {}
            
        trending_keywords = {}
        
        for category in self.df['category'].unique():
            category_df = self.df[self.df['category'] == category]
            
            # 合併所有推文文字
            all_text = ' '.join(category_df['text'].fillna('').astype(str))
            
            # 提取關鍵字（去除常見詞彙、URL、用戶名等）
            words = re.findall(r'#\w+|\$\w+|\b[A-Z]{2,}\b|\b\w{4,}\b', all_text.upper())
            
            # 過濾常見詞彙
            stop_words = {'THE', 'AND', 'FOR', 'ARE', 'WITH', 'THIS', 'THAT', 'HAVE', 'FROM', 'THEY', 'BEEN', 'WILL', 'MORE', 'THAN', 'HTTPS', 'HTTP'}
            filtered_words = [word for word in words if word not in stop_words]
            
            # 計算詞頻
            word_counts = Counter(filtered_words)
            trending_keywords[category] = [(word, count) for word, count in word_counts.most_common(10) if count >= min_frequency]
            
        return trending_keywords
    
    def create_visualizations(self, save_path: str = 'web3_analysis_plots.png'):
        """創建數據視覺化圖表"""
        if self.df.empty:
            print("沒有數據可視覺化")
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Web3 Twitter 趨勢分析', fontsize=16, fontweight='bold')
        
        # 1. 各類別推文數量
        category_counts = self.df['category'].value_counts()
        axes[0, 0].bar(range(len(category_counts)), category_counts.values)
        axes[0, 0].set_xticks(range(len(category_counts)))
        axes[0, 0].set_xticklabels(category_counts.index, rotation=45, ha='right')
        axes[0, 0].set_title('各類別推文數量')
        axes[0, 0].set_ylabel('推文數')
        
        # 2. 互動度分布（讚數 vs 轉推數）
        axes[0, 1].scatter(self.df['like_count'], self.df['retweet_count'], alpha=0.6, c=pd.Categorical(self.df['category']).codes)
        axes[0, 1].set_xlabel('讚數')
        axes[0, 1].set_ylabel('轉推數')
        axes[0, 1].set_title('互動度分布')
        axes[0, 1].set_xscale('log')
        axes[0, 1].set_yscale('log')
        
        # 3. 各類別平均互動度
        engagement_by_category = self.df.groupby('category').agg({
            'like_count': 'mean',
            'retweet_count': 'mean',
            'reply_count': 'mean'
        })
        
        x_pos = range(len(engagement_by_category))
        width = 0.25
        
        axes[1, 0].bar([x - width for x in x_pos], engagement_by_category['like_count'], width, label='平均讚數', alpha=0.8)
        axes[1, 0].bar(x_pos, engagement_by_category['retweet_count'], width, label='平均轉推數', alpha=0.8)
        axes[1, 0].bar([x + width for x in x_pos], engagement_by_category['reply_count'], width, label='平均回復數', alpha=0.8)
        
        axes[1, 0].set_xticks(x_pos)
        axes[1, 0].set_xticklabels(engagement_by_category.index, rotation=45, ha='right')
        axes[1, 0].set_title('各類別平均互動度')
        axes[1, 0].legend()
        axes[1, 0].set_ylabel('互動次數')
        
        # 4. 認證用戶比例
        verified_ratio = self.df.groupby('category')['verified'].mean() * 100
        axes[1, 1].pie(verified_ratio.values, labels=verified_ratio.index, autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('各類別認證用戶比例')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"圖表已保存到 {save_path}")
    
    def generate_summary_report(self, save_path: str = 'web3_summary_report.txt'):
        """生成綜合分析報告"""
        if self.df.empty:
            print("沒有數據可分析")
            return
            
        report_lines = []
        report_lines.append("=" * 50)
        report_lines.append("Web3 Twitter 趨勢分析報告")
        report_lines.append("=" * 50)
        report_lines.append(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"總推文數: {len(self.df)}")
        report_lines.append(f"涵蓋類別: {len(self.df['category'].unique())}")
        report_lines.append("")
        
        # 各類別詳細報告
        category_report = self.generate_category_report()
        for category, stats in category_report.items():
            report_lines.append(f"【{category}】")
            report_lines.append(f"  推文數量: {stats['total_tweets']}")
            report_lines.append(f"  平均讚數: {stats['avg_likes']:.1f}")
            report_lines.append(f"  平均轉推數: {stats['avg_retweets']:.1f}")
            report_lines.append(f"  認證用戶比例: {stats['verified_ratio']:.1f}%")
            report_lines.append(f"  互動度評分: {stats['engagement_score']:.1f}")
            report_lines.append(f"  熱門推文: {stats['top_tweet']['text'][:100]}...")
            report_lines.append(f"  推文連結: {stats['top_tweet']['url']}")
            report_lines.append("")
        
        # 熱門關鍵字
        trending_keywords = self.find_trending_keywords()
        report_lines.append("【熱門關鍵字】")
        for category, keywords in trending_keywords.items():
            if keywords:
                report_lines.append(f"{category}: {', '.join([f'{word}({count})' for word, count in keywords[:5]])}")
        report_lines.append("")
        
        # 整體趨勢洞察
        report_lines.append("【趋勢洞察】")
        most_active_category = self.df['category'].value_counts().index[0]
        report_lines.append(f"• 最活躍賽道: {most_active_category}")
        
        highest_engagement_category = self.df.groupby('category')['like_count'].mean().idxmax()
        report_lines.append(f"• 最高互動賽道: {highest_engagement_category}")
        
        # 保存報告
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print('\n'.join(report_lines))
        print(f"\n完整報告已保存到 {save_path}")

def main():
    # 分析最新的推文數據文件
    import glob
    import os
    
    # 尋找最新的JSON數據文件
    json_files = glob.glob("web3_tweets_*.json")
    if not json_files:
        print("找不到推文數據文件，請先執行 twitter_web3_crawler.py")
        return
    
    latest_file = max(json_files, key=os.path.getctime)
    print(f"分析數據文件: {latest_file}")
    
    # 創建分析器
    analyzer = Web3TweetAnalyzer(latest_file)
    
    # 生成分析報告
    analyzer.generate_summary_report()
    
    # 創建視覺化圖表
    analyzer.create_visualizations()

if __name__ == "__main__":
    main()