#!/usr/bin/env python3
"""
测试泄露检测脚本

检测Skill中的测试用例是否有泄露风险（包含敏感信息或预期答案）。

使用方法：
    python leakage_detector.py skill_path

输出：
    - 泄露风险项目
    - 建议修复方案
"""

import os
import re
import sys
from typing import List, Dict


# 敏感信息模式
SENSITIVE_PATTERNS = [
    (r'password\s*[:=]\s*["\']?[^"\'\s]+', '密码'),
    (r'api[_-]?key\s*[:=]\s*["\']?[^"\'\s]+', 'API密钥'),
    (r'secret\s*[:=]\s*["\']?[^"\'\s]+', '密钥'),
    (r'token\s*[:=]\s*["\']?[^"\'\s]+', '令牌'),
    (r'[\w\.-]+@[\w\.-]+\.\w+', '邮箱地址'),
    (r'\b\d{11,}\b', '可能的长数字ID'),
    (r'Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+', 'JWT令牌'),
]

# 硬编码答案模式
ANSWER_PATTERNS = [
    (r'expected\s*[:=]\s*["\'][^"\']+["\']', '硬编码预期值'),
    (r'answer\s*[:=]\s*["\'][^"\']+["\']', '硬编码答案'),
    (r'result\s*[:=]\s*["\'][^"\']+["\']', '硬编码结果'),
]


def scan_file(filepath: str) -> List[Dict]:
    """扫描单个文件的泄露风险"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return [{'file': filepath, 'error': str(e)}]
    
    # 检测敏感信息
    for pattern, desc in SENSITIVE_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # 找到行号
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                'file': filepath,
                'line': line_num,
                'type': 'sensitive',
                'description': desc,
                'content_preview': match.group()[:50] + '...' if len(match.group()) > 50 else match.group(),
                'severity': 'high'
            })
    
    # 检测硬编码答案
    for pattern, desc in ANSWER_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                'file': filepath,
                'line': line_num,
                'type': 'hardcoded_answer',
                'description': desc,
                'content_preview': match.group()[:50] + '...' if len(match.group()) > 50 else match.group(),
                'severity': 'medium'
            })
    
    return issues


def scan_skill(skill_path: str) -> Dict:
    """扫描整个Skill目录的泄露风险"""
    results = {
        'skill_path': skill_path,
        'total_files': 0,
        'issues': []
    }
    
    # 扫描所有文件
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if file.endswith(('.py', '.js', '.json', '.yaml', '.yml', '.md')):
                filepath = os.path.join(root, file)
                results['total_files'] += 1
                
                file_issues = scan_file(filepath)
                results['issues'].extend(file_issues)
    
    return results


def generate_report(results: Dict) -> str:
    """生成检测报告"""
    report = []
    report.append(f"# 泄露检测报告")
    report.append(f"\n## 基本信息")
    report.append(f"- Skill路径: {results['skill_path']}")
    report.append(f"- 扫描文件数: {results['total_files']}")
    report.append(f"- 发现问题数: {len(results['issues'])}")
    
    if not results['issues']:
        report.append(f"\n✅ 未发现泄露风险")
        return '\n'.join(report)
    
    # 按严重程度分组
    high_severity = [i for i in results['issues'] if i.get('severity') == 'high']
    medium_severity = [i for i in results['issues'] if i.get('severity') == 'medium']
    
    if high_severity:
        report.append(f"\n## 🔴 高风险问题 ({len(high_severity)}个)")
        for issue in high_severity:
            report.append(f"\n- **文件**: {issue['file']}")
            if 'line' in issue:
                report.append(f"  - **行号**: {issue['line']}")
            report.append(f"  - **类型**: {issue['description']}")
            report.append(f"  - **内容预览**: `{issue['content_preview']}`")
    
    if medium_severity:
        report.append(f"\n## 🟠 中风险问题 ({len(medium_severity)}个)")
        for issue in medium_severity:
            report.append(f"\n- **文件**: {issue['file']}")
            if 'line' in issue:
                report.append(f"  - **行号**: {issue['line']}")
            report.append(f"  - **类型**: {issue['description']}")
    
    # 修复建议
    report.append(f"\n## 💡 修复建议")
    report.append(f"\n1. 将敏感信息移至环境变量或配置文件")
    report.append(f"2. 使用占位符替换硬编码的敏感值")
    report.append(f"3. 在.gitignore中添加敏感配置文件")
    
    return '\n'.join(report)


def main():
    if len(sys.argv) < 2:
        print("使用方法: python leakage_detector.py skill_path")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    if not os.path.exists(skill_path):
        print(f"错误: 路径 {skill_path} 不存在")
        sys.exit(1)
    
    results = scan_skill(skill_path)
    report = generate_report(results)
    print(report)


if __name__ == '__main__':
    main()
