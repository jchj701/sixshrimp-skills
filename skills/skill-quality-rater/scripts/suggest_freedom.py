#!/usr/bin/env python3
"""
自由度建议生成脚本

分析Skill中的操作，建议哪些应该用脚本，哪些应该用文字描述。

使用方法：
    python suggest_freedom.py skill_path

输出：
    - 操作分类
    - 自由度建议
"""

import os
import re
import sys
import json
from typing import List, Dict


# 脆弱操作关键词（需要脚本化）
FRAGILE_KEYWORDS = [
    '文件', 'file', '读取', 'read', '写入', 'write', '删除', 'delete',
    '创建', 'create', 'mkdir', '路径', 'path',
    'API', '请求', 'request', '调用', 'call',
    '格式转换', 'convert', 'parse', '解析',
    '编码', 'encoding', 'utf', 'gbk',
    '数据库', 'database', 'sql', 'query',
]

# 创造性任务关键词（需要高自由度）
CREATIVE_KEYWORDS = [
    '生成', 'generate', '创作', 'create', '写', 'write',
    '文案', 'copywriting', '文章', 'article',
    '设计', 'design', '风格', 'style',
    '方案', 'solution', '建议', 'suggest',
    '评估', 'evaluate', '判断', 'judge',
]


def analyze_skill_md(content: str) -> List[Dict]:
    """分析SKILL.md内容，提取操作"""
    operations = []
    
    # 提取操作步骤
    steps_pattern = r'(\d+)\.\s*([^\n]+)'
    steps = re.findall(steps_pattern, content)
    
    for num, step in steps:
        operation = {
            'step': int(num),
            'description': step.strip(),
            'recommended_approach': None,
            'reason': None,
            'confidence': 'medium'
        }
        
        # 判断是否为脆弱操作
        is_fragile = any(kw.lower() in step.lower() for kw in FRAGILE_KEYWORDS)
        is_creative = any(kw.lower() in step.lower() for kw in CREATIVE_KEYWORDS)
        
        if is_fragile and not is_creative:
            operation['recommended_approach'] = 'script'
            operation['reason'] = '涉及文件IO、API调用或格式转换，建议脚本化'
            operation['confidence'] = 'high'
        elif is_creative and not is_fragile:
            operation['recommended_approach'] = 'principle'
            operation['reason'] = '需要创意和灵活性，建议用原则约束'
            operation['confidence'] = 'high'
        elif is_fragile and is_creative:
            operation['recommended_approach'] = 'hybrid'
            operation['reason'] = '同时涉及脆弱操作和创造性任务，需要分层处理'
            operation['confidence'] = 'medium'
        else:
            operation['recommended_approach'] = 'text'
            operation['reason'] = '简单操作，可用文字描述'
            operation['confidence'] = 'low'
        
        operations.append(operation)
    
    return operations


def check_existing_scripts(skill_path: str) -> List[str]:
    """检查已存在的脚本"""
    scripts_dir = os.path.join(skill_path, 'scripts')
    scripts = []
    
    if os.path.exists(scripts_dir):
        for file in os.listdir(scripts_dir):
            if file.endswith(('.py', '.sh', '.js')):
                scripts.append(file)
    
    return scripts


def generate_suggestions(skill_path: str) -> Dict:
    """生成自由度建议"""
    skill_md = os.path.join(skill_path, 'SKILL.md')
    
    if not os.path.exists(skill_md):
        return {
            'error': f'SKILL.md not found in {skill_path}'
        }
    
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
    
    operations = analyze_skill_md(content)
    existing_scripts = check_existing_scripts(skill_path)
    
    # 生成建议
    suggestions = {
        'skill_path': skill_path,
        'existing_scripts': existing_scripts,
        'operations': operations,
        'summary': {
            'total_operations': len(operations),
            'suggest_script': sum(1 for op in operations if op['recommended_approach'] == 'script'),
            'suggest_principle': sum(1 for op in operations if op['recommended_approach'] == 'principle'),
            'suggest_hybrid': sum(1 for op in operations if op['recommended_approach'] == 'hybrid'),
            'suggest_text': sum(1 for op in operations if op['recommended_approach'] == 'text'),
        }
    }
    
    return suggestions


def format_report(suggestions: Dict) -> str:
    """格式化报告"""
    if 'error' in suggestions:
        return f"错误: {suggestions['error']}"
    
    lines = []
    lines.append("# 自由度建议报告")
    lines.append("")
    lines.append("## 概览")
    lines.append(f"- 总操作数: {suggestions['summary']['total_operations']}")
    lines.append(f"- 建议脚本化: {suggestions['summary']['suggest_script']}")
    lines.append(f"- 建议原则约束: {suggestions['summary']['suggest_principle']}")
    lines.append(f"- 建议文字描述: {suggestions['summary']['suggest_text']}")
    
    if suggestions['existing_scripts']:
        lines.append("")
        lines.append("## 已有脚本")
        for script in suggestions['existing_scripts']:
            lines.append(f"- {script}")
    
    lines.append("")
    lines.append("## 操作分析")
    
    for op in suggestions['operations']:
        approach_icon = {
            'script': '🔴',
            'principle': '🟢',
            'hybrid': '🟡',
            'text': '⚪'
        }.get(op['recommended_approach'], '⚪')
        
        confidence_icon = {
            'high': '✓',
            'medium': '~',
            'low': '?'
        }.get(op['confidence'], '?')
        
        lines.append("")
        lines.append(f"### 步骤 {op['step']}")
        lines.append(f"- 描述: {op['description']}")
        lines.append(f"- 建议: {approach_icon} {op['recommended_approach']} ({confidence_icon})")
        lines.append(f"- 原因: {op['reason']}")
    
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("使用方法: python suggest_freedom.py skill_path")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    if not os.path.exists(skill_path):
        print(f"错误: 路径 {skill_path} 不存在")
        sys.exit(1)
    
    suggestions = generate_suggestions(skill_path)
    
    # 输出JSON格式
    if '--json' in sys.argv:
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))
    else:
        print(format_report(suggestions))


if __name__ == '__main__':
    main()
