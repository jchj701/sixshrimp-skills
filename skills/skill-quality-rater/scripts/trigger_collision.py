#!/usr/bin/env python3
"""
触发词冲突检测脚本

检测多个Skill的description触发词是否重叠或冲突。

使用方法：
    python trigger_collision.py skill1_path skill2_path [skill3_path ...]

输出：
    - 冲突的触发词对
    - 相似度评分
"""

import os
import re
import sys
from collections import defaultdict
from typing import List, Dict, Tuple


def extract_frontmatter(content: str) -> Dict:
    """从SKILL.md提取frontmatter"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}
    
    frontmatter_str = match.group(1)
    frontmatter = {}
    
    for line in frontmatter_str.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    return frontmatter


def extract_triggers(description: str) -> List[str]:
    """从description提取触发词"""
    # 移除YAML多行字符串标记
    description = re.sub(r'^\|?\s*', '', description)
    
    # 提取关键词
    triggers = []
    
    # 中文关键词
    chinese_pattern = r'[\u4e00-\u9fff]+'
    triggers.extend(re.findall(chinese_pattern, description))
    
    # 英文关键词（至少3个字母）
    english_pattern = r'\b[a-zA-Z]{3,}\b'
    triggers.extend(re.findall(english_pattern, description.lower()))
    
    # 特定格式关键词
    specific_patterns = [
        r'pdf|word|excel|json|csv|yaml|xml',  # 文件格式
        r'提取|转换|分析|生成|处理',  # 动作词
        r'sql|api|http|url',  # 技术术语
    ]
    
    for pattern in specific_patterns:
        triggers.extend(re.findall(pattern, description.lower()))
    
    return list(set(triggers))


def calculate_overlap(triggers1: List[str], triggers2: List[str]) -> Tuple[float, List[str]]:
    """计算两组触发词的重叠度"""
    if not triggers1 or not triggers2:
        return 0.0, []
    
    set1 = set(triggers1)
    set2 = set(triggers2)
    
    overlap = set1 & set2
    union = set1 | set2
    
    jaccard = len(overlap) / len(union) if union else 0.0
    
    return jaccard, list(overlap)


def check_collision(skill_paths: List[str]) -> List[Dict]:
    """检查多个Skill之间的触发词冲突"""
    skills_data = []
    
    for path in skill_paths:
        skill_md = os.path.join(path, 'SKILL.md')
        if not os.path.exists(skill_md):
            print(f"警告: {skill_md} 不存在")
            continue
        
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = extract_frontmatter(content)
        description = frontmatter.get('description', '')
        triggers = extract_triggers(description)
        
        skills_data.append({
            'path': path,
            'name': frontmatter.get('name', os.path.basename(path)),
            'description': description,
            'triggers': triggers
        })
    
    collisions = []
    
    # 两两比较
    for i in range(len(skills_data)):
        for j in range(i + 1, len(skills_data)):
            skill1 = skills_data[i]
            skill2 = skills_data[j]
            
            overlap_score, common_triggers = calculate_overlap(
                skill1['triggers'],
                skill2['triggers']
            )
            
            if overlap_score > 0.3:  # 阈值
                collisions.append({
                    'skill1': skill1['name'],
                    'skill2': skill2['name'],
                    'overlap_score': round(overlap_score, 2),
                    'common_triggers': common_triggers,
                    'severity': 'high' if overlap_score > 0.5 else 'medium'
                })
    
    return collisions


def main():
    if len(sys.argv) < 2:
        print("使用方法: python trigger_collision.py skill1_path [skill2_path ...]")
        sys.exit(1)
    
    skill_paths = sys.argv[1:]
    collisions = check_collision(skill_paths)
    
    if not collisions:
        print("✅ 未发现触发词冲突")
        return
    
    print(f"⚠️ 发现 {len(collisions)} 个潜在冲突:\n")
    
    for collision in collisions:
        severity_icon = '🔴' if collision['severity'] == 'high' else '🟠'
        print(f"{severity_icon} {collision['skill1']} <-> {collision['skill2']}")
        print(f"   重叠度: {collision['overlap_score']}")
        print(f"   共同触发词: {', '.join(collision['common_triggers'])}")
        print()


if __name__ == '__main__':
    main()
