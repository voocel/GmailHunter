import random
from typing import List
import os
import argparse

class UsernameGenerator:
    """用户名生成器 - 生成高质量、易读的用户名"""
    
    def __init__(self):
        # 第一组词（放在前面）
        self.first_words = [
            # 颜色
            'blue', 'red', 'gold', 'jade', 'ruby', 'cyan', 'pink', 'rose',
            'gray', 'mint', 'lime', 'rust', 'wine',
            
            # 自然元素
            'sky', 'sun', 'moon', 'star', 'snow', 'rain', 'wind', 'leaf',
            'ice', 'fire', 'sand', 'rock', 'wood', 'tree', 'seed', 'dawn',
            'dusk', 'mist', 'fog', 'dust', 'wave', 'lake', 'sea', 'bay',
            
            # 动物
            'fox', 'wolf', 'bear', 'owl', 'hawk', 'swan', 'deer', 'bird',
            'fish', 'seal', 'lynx', 'dove', 'cat', 'lion', 'crow', 'duck',
            'frog', 'goat', 'hare',
            
            # 金属/宝石
            'iron', 'gold', 'jade', 'ruby', 'opal', 'pearl', 'gem',
            
            # 积极/描述性词汇
            'zen', 'soul', 'mind', 'wild', 'pure', 'dark', 'soft', 'calm',
            'wise', 'bold', 'free', 'hope', 'joy', 'love', 'life', 'flow',
            'peak', 'cool', 'fair', 'kind', 'true', 'real', 'deep', 'high',
            
            # 科技/现代
            'tech', 'byte', 'code', 'data', 'node', 'web', 'net', 'bit',
            'cyber', 'nano', 'pixel',
            
            # 其他名词
            'book', 'tale', 'song', 'tune', 'art', 'poem', 'word', 'note',
            'path', 'road', 'way', 'gate', 'door', 'arch', 'ring', 'coin',
            'silk', 'clay', 'ink', 'time', 'echo', 'pulse', 'beam'
        ]
        
        # 第二组词（放在后面）
        self.second_words = [
            # 自然
            'sky', 'sea', 'bay', 'ray', 'day', 'sun', 'moon', 'star',
            'leaf', 'tree', 'rain', 'snow', 'wind', 'wave', 'lake', 'rock',
            'wood', 'seed', 'mist', 'ice', 'fire',
            
            # 动物
            'fox', 'owl', 'cat', 'wolf', 'bear', 'hawk', 'swan', 'deer',
            'bird', 'fish', 'seal', 'dove', 'lion',
            
            # 时间/空间
            'time', 'way', 'path', 'road', 'gate', 'zone', 'line', 'edge',
            'side', 'spot',
            
            # 其他
            'soul', 'mind', 'life', 'hope', 'joy', 'love', 'art', 'song',
            'tale', 'code', 'byte', 'data', 'tech', 'web', 'net', 'zen',
            'flow', 'beam', 'wave', 'tone', 'mode', 'type', 'view', 'mark'
        ]
        
        # 单独成词（6-7个字母的完整词）
        self.single_words = [
            # 自然/宇宙相关
            'zenith', 'aurora', 'cosmos', 'nebula', 'astral', 'sunset',
            'cosmic', 'galaxy', 'meteor', 'arctic',
            
            # 科技/数字相关
            'cipher', 'binary', 'photon', 'quartz', 'matrix', 'quantum',
            'digital', 'crypto',
            
            # 神秘/魔幻
            'mystic', 'oracle', 'enigma', 'mythic', 'legend', 'wisdom',
            'spirit', 'vision',
            
            # 其他
            'crystal', 'prism', 'vertex', 'nexus', 'cipher', 'sylph',
            'zephyr', 'azure', 'plasma', 'rhythm', 'melody', 'harmony'
        ]

    def combine_words(self) -> str:
        """组合两个词"""
        word1 = random.choice(self.first_words)
        word2 = random.choice(self.second_words)
        # 避免重复单词
        while word2 == word1:
            word2 = random.choice(self.second_words)
        combined = word1 + word2
        return combined[:7] if len(combined) > 7 else combined

    def generate_usernames(self, count: int = 100) -> List[str]:
        """生成用户名列表"""
        usernames = set()
        
        while len(usernames) < count:
            # 80%概率组合词, 20%概率使用单个词
            if random.random() < 0.8:
                username = self.combine_words()
            else:
                username = random.choice(self.single_words).lower()
            
            if 6 <= len(username) <= 7:
                usernames.add(username.lower())
        
        return sorted(list(usernames))

    @staticmethod
    def save_to_file(usernames: List[str]) -> str:
        """保存用户名到文件"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', 'usernames.txt')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for username in usernames:
                f.write(f"{username}\n")
        
        return filepath

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Gmail用户名生成器')
    parser.add_argument('-n', '--number', type=int, default=100,
                      help='要生成的用户名数量 (默认: 100)')
    args = parser.parse_args()
    
    print("🚀 开始生成用户名...")
    
    generator = UsernameGenerator()
    usernames = generator.generate_usernames(args.number)
    filepath = UsernameGenerator.save_to_file(usernames)
    
    print(f"✅ 已生成 {len(usernames)} 个用户名")
    print(f"📄 已保存到文件: {filepath}")
    print("\n示例用户名:")
    for username in usernames[:5]:
        print(f"- {username}")

if __name__ == "__main__":
    main()