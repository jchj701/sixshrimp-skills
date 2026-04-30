#!/usr/bin/env python3
"""
录制脚本清洗工具
去除噪音、合并等待事件、事件去重、规范化时间戳
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


@dataclass
class EventConfig:
    """事件配置"""
    event_type: str
    keep: bool = True
    merge_wait_threshold_ms: int = 2000  # 超过此阈值才合并等待


@dataclass
class SanitizeConfig:
    """清洗配置"""
    remove_mouse_moves: bool = True
    merge_wait_events: bool = True
    deduplicate_events: bool = True
    normalize_timestamps: bool = True
    min_wait_interval_ms: int = 100  # 最小等待间隔
    max_wait_interval_ms: int = 60000  # 最大等待间隔（防止异常值）
    similarity_threshold: float = 0.85  # 事件相似度阈值


class ScriptSanitizer:
    """录制脚本清洗器"""
    
    def __init__(self, config: SanitizeConfig):
        self.config = config
        self.event_types = {
            "click": EventConfig("click"),
            "type": EventConfig("type"),
            "keypress": EventConfig("keypress"),
            "hover": EventConfig("hover", keep=False),
            "scroll": EventConfig("scroll", keep=False),
            "mouse_move": EventConfig("mouse_move", keep=False),
            "mouse_down": EventConfig("mouse_down", keep=False),
            "mouse_up": EventConfig("mouse_up", keep=False),
            "wait": EventConfig("wait"),
            "navigate": EventConfig("navigate"),
            "screenshot": EventConfig("screenshot", keep=False),
        }
    
    def sanitize(self, events: List[Dict]) -> List[Dict]:
        """
        执行完整的清洗流程
        
        Args:
            events: 原始事件列表
        
        Returns:
            清洗后的事件列表
        """
        if not events:
            return []
        
        result = events.copy()
        
        # 1. 去除噪音事件
        result = self._remove_noise_events(result)
        
        # 2. 合并等待事件
        if self.config.merge_wait_events:
            result = self._merge_wait_events(result)
        
        # 3. 去重事件
        if self.config.deduplicate_events:
            result = self._deduplicate_events(result)
        
        # 4. 规范化时间戳
        if self.config.normalize_timestamps:
            result = self._normalize_timestamps(result)
        
        # 5. 重新编号
        result = self._renumber_events(result)
        
        return result
    
    def _remove_noise_events(self, events: List[Dict]) -> List[Dict]:
        """去除噪音事件"""
        filtered = []
        
        for event in events:
            event_type = event.get("type", event.get("event_type", "")).lower()
            
            # 检查是否应该保留
            config = self.event_types.get(event_type)
            if config and not config.keep:
                continue
            
            # 检查配置标志
            if event_type == "mousemove" and self.config.remove_mouse_moves:
                continue
            
            filtered.append(event)
        
        return filtered
    
    def _merge_wait_events(self, events: List[Dict]) -> List[Dict]:
        """合并相邻的等待事件"""
        merged = []
        accumulated_wait = 0
        last_wait_event = None
        
        for event in events:
            event_type = event.get("type", event.get("event_type", "")).lower()
            
            if event_type == "wait":
                wait_duration = event.get("duration", event.get("wait_ms", 0))
                accumulated_wait += wait_duration
                last_wait_event = event
            else:
                # 如果有累积的等待时间
                if accumulated_wait > 0:
                    # 只在等待时间超过阈值时才添加
                    if accumulated_wait >= self.config.min_wait_interval_ms:
                        merged_wait = {
                            "type": "wait",
                            "duration": min(accumulated_wait, self.config.max_wait_interval_ms),
                            "original_count": "merged"
                        }
                        merged.append(merged_wait)
                    accumulated_wait = 0
                    last_wait_event = None
                
                merged.append(event)
        
        # 处理末尾的等待事件
        if accumulated_wait > 0 and merged:
            if accumulated_wait >= self.config.min_wait_interval_ms:
                merged.append({
                    "type": "wait",
                    "duration": min(accumulated_wait, self.config.max_wait_interval_ms),
                    "original_count": "trailing"
                })
        
        return merged
    
    def _deduplicate_events(self, events: List[Dict]) -> List[Dict]:
        """去除重复事件"""
        if not events:
            return []
        
        deduplicated = []
        last_meaningful_event = None
        
        for event in events:
            event_type = event.get("type", event.get("event_type", "")).lower()
            
            # 等待事件不参与去重
            if event_type == "wait":
                deduplicated.append(event)
                continue
            
            # 检查是否与上一个有意义的事件重复
            is_duplicate = False
            
            if last_meaningful_event:
                # 相同的操作类型
                if event_type == last_meaningful_event.get("type"):
                    # 相同的目标元素
                    event_target = self._get_event_target(event)
                    last_target = self._get_event_target(last_meaningful_event)
                    
                    if event_target == last_target:
                        # 检查是否是快速连续点击
                        event_time = event.get("timestamp", 0)
                        last_time = last_meaningful_event.get("timestamp", 0)
                        
                        if isinstance(event_time, str):
                            try:
                                event_time = datetime.fromisoformat(event_time.replace("Z", "+00:00")).timestamp()
                            except:
                                event_time = 0
                        
                        if isinstance(last_time, str):
                            try:
                                last_time = datetime.fromisoformat(last_time.replace("Z", "+00:00")).timestamp()
                            except:
                                last_time = 0
                        
                        time_diff = abs(event_time - last_time) * 1000  # 转换为毫秒
                        
                        if time_diff < 500:  # 500ms内的相同操作视为重复
                            is_duplicate = True
            
            if not is_duplicate:
                deduplicated.append(event)
                last_meaningful_event = event
        
        return deduplicated
    
    def _get_event_target(self, event: Dict) -> str:
        """获取事件的标识目标"""
        # 优先级: selector > xpath > css > id > class > text
        if "selector" in event:
            return f"selector:{event['selector']}"
        if "xpath" in event:
            return f"xpath:{event['xpath']}"
        if "css" in event:
            return f"css:{event['css']}"
        if "id" in event:
            return f"id:{event['id']}"
        if "class" in event:
            return f"class:{event['class']}"
        if "text" in event:
            return f"text:{event['text']}"
        if "value" in event:
            return f"value:{event['value']}"
        return ""
    
    def _normalize_timestamps(self, events: List[Dict]) -> List[Dict]:
        """规范化时间戳为相对时间（从0开始）"""
        if not events:
            return []
        
        # 找到第一个有效时间戳
        first_timestamp = None
        for event in events:
            ts = event.get("timestamp")
            if ts is not None:
                if isinstance(ts, str):
                    try:
                        first_timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                        break
                    except:
                        continue
                elif isinstance(ts, (int, float)):
                    first_timestamp = ts
                    break
        
        if first_timestamp is None:
            # 无法规范化
            return events
        
        normalized = []
        for event in events:
            new_event = event.copy()
            ts = event.get("timestamp")
            
            if ts is not None:
                if isinstance(ts, str):
                    try:
                        current_ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                    except:
                        current_ts = 0
                elif isinstance(ts, (int, float)):
                    current_ts = ts
                else:
                    current_ts = 0
                
                relative_ms = int((current_ts - first_timestamp) * 1000)
                new_event["relative_time_ms"] = max(0, relative_ms)
            
            normalized.append(new_event)
        
        return normalized
    
    def _renumber_events(self, events: List[Dict]) -> List[Dict]:
        """重新编号事件"""
        for i, event in enumerate(events):
            event["step_id"] = i + 1
            event["order"] = i + 1
        return events
    
    def analyze(self, original: List[Dict], sanitized: List[Dict]) -> Dict[str, Any]:
        """
        分析清洗效果
        
        Returns:
            分析报告
        """
        original_count = len(original)
        sanitized_count = len(sanitized)
        removed_count = original_count - sanitized_count
        
        # 统计各类型事件
        original_types = {}
        sanitized_types = {}
        
        for event in original:
            event_type = event.get("type", event.get("event_type", "unknown"))
            original_types[event_type] = original_types.get(event_type, 0) + 1
        
        for event in sanitized:
            event_type = event.get("type", event.get("event_type", "unknown"))
            sanitized_types[event_type] = sanitized_types.get(event_type, 0) + 1
        
        # 估算执行时间
        original_duration = 0
        sanitized_duration = 0
        
        for event in original:
            if event.get("type") == "wait":
                original_duration += event.get("duration", event.get("wait_ms", 0))
        
        for event in sanitized:
            if event.get("type") == "wait":
                sanitized_duration += event.get("duration", event.get("wait_ms", 0))
        
        return {
            "summary": {
                "original_event_count": original_count,
                "sanitized_event_count": sanitized_count,
                "removed_event_count": removed_count,
                "compression_ratio": round(sanitized_count / original_count, 2) if original_count > 0 else 1.0
            },
            "event_types": {
                "original": original_types,
                "sanitized": sanitized_types
            },
            "duration": {
                "original_ms": original_duration,
                "sanitized_ms": sanitized_duration,
                "saved_ms": original_duration - sanitized_duration
            }
        }


def load_input(path: str) -> List[Dict]:
    """加载输入文件"""
    if path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # 可能包含 events 字段
                if "events" in data:
                    return data["events"]
                elif "recording" in data:
                    return data["recording"]
                else:
                    return [data]
    else:
        print(f"❌ 不支持的输入格式: {path}", file=sys.stderr)
        sys.exit(1)
    
    return []


def save_output(events: List[Dict], path: str, analysis: Optional[Dict] = None):
    """保存输出文件"""
    output = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "event_count": len(events),
        "events": events
    }
    
    if analysis:
        output["analysis"] = analysis
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="录制脚本清洗工具")
    parser.add_argument("--input", "-i", required=True, help="输入JSON文件路径")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    parser.add_argument("--remove_mouse_moves", type=bool, default=True, 
                        help="移除鼠标移动事件 (默认: True)")
    parser.add_argument("--merge_wait_events", type=bool, default=True,
                        help="合并等待事件 (默认: True)")
    parser.add_argument("--deduplicate_events", type=bool, default=True,
                        help="去除重复事件 (默认: True)")
    parser.add_argument("--normalize_timestamps", type=bool, default=True,
                        help="规范化时间戳 (默认: True)")
    parser.add_argument("--analyze", action="store_true", help="显示清洗分析报告")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    # 加载输入
    try:
        events = load_input(args.input)
    except FileNotFoundError:
        print(f"❌ 文件未找到: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not args.quiet:
        print(f"📂 加载了 {len(events)} 个原始事件")
    
    # 创建配置
    config = SanitizeConfig(
        remove_mouse_moves=args.remove_mouse_moves,
        merge_wait_events=args.merge_wait_events,
        deduplicate_events=args.deduplicate_events,
        normalize_timestamps=args.normalize_timestamps
    )
    
    # 执行清洗
    sanitizer = ScriptSanitizer(config)
    sanitized_events = sanitizer.sanitize(events)
    
    # 分析报告
    analysis = sanitizer.analyze(events, sanitized_events)
    
    if not args.quiet:
        print(f"\n📊 清洗报告:")
        print(f"   原始事件数: {analysis['summary']['original_event_count']}")
        print(f"   清洗后事件数: {analysis['summary']['sanitized_event_count']}")
        print(f"   移除事件数: {analysis['summary']['removed_event_count']}")
        print(f"   压缩比: {analysis['summary']['compression_ratio']}")
        print(f"   节省等待时间: {analysis['duration']['saved_ms']}ms")
    
    # 输出结果
    if args.output:
        save_output(sanitized_events, args.output, analysis if args.analyze else None)
        if not args.quiet:
            print(f"\n✅ 已保存到: {args.output}")
    else:
        # 输出到stdout
        output = {
            "events": sanitized_events,
            "analysis": analysis if args.analyze else None
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
