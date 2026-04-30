#!/usr/bin/env python3
"""
环境就绪检查脚本
检查URL可达性、页面加载、元素存在、登录状态、前置数据等
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

# 尝试导入可选依赖
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


@dataclass
class CheckResult:
    """检查结果数据类"""
    check_name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = "error"  # error, warning, info


@dataclass
class EnvReadinessReport:
    """环境就绪报告"""
    overall_ready: bool
    timestamp: str
    target_url: str
    checks: List[CheckResult]
    blockers: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_ready": self.overall_ready,
            "timestamp": self.timestamp,
            "target_url": self.target_url,
            "checks": [asdict(c) for c in self.checks],
            "blockers": self.blockers,
            "warnings": self.warnings
        }


def check_url_reachability(url: str, timeout: int = 10) -> CheckResult:
    """检查URL可达性"""
    if not HAS_REQUESTS:
        return CheckResult(
            check_name="url_reachability",
            passed=True,
            message="requests库未安装，跳过HTTP检查",
            severity="warning"
        )
    
    try:
        start_time = time.time()
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        elapsed = time.time() - start_time
        
        if response.status_code < 400:
            return CheckResult(
                check_name="url_reachability",
                passed=True,
                message=f"URL可访问 (HTTP {response.status_code})",
                details={"status_code": response.status_code, "latency_ms": round(elapsed * 1000, 2)},
                severity="info"
            )
        else:
            return CheckResult(
                check_name="url_reachability",
                passed=False,
                message=f"URL返回错误状态码 {response.status_code}",
                details={"status_code": response.status_code, "latency_ms": round(elapsed * 1000, 2)},
                severity="error"
            )
    except requests.exceptions.Timeout:
        return CheckResult(
            check_name="url_reachability",
            passed=False,
            message=f"URL访问超时 ({timeout}秒)",
            severity="error"
        )
    except requests.exceptions.RequestException as e:
        return CheckResult(
            check_name="url_reachability",
            passed=False,
            message=f"URL访问失败: {str(e)}",
            severity="error"
        )


def check_page_title(driver, expected_title: Optional[str] = None) -> CheckResult:
    """检查页面标题"""
    if not HAS_SELENIUM or driver is None:
        return CheckResult(
            check_name="page_title",
            passed=True,
            message="Selenium未安装或driver不可用，跳过标题检查",
            severity="warning"
        )
    
    try:
        actual_title = driver.title
        
        if expected_title:
            if expected_title.lower() in actual_title.lower():
                return CheckResult(
                    check_name="page_title",
                    passed=True,
                    message=f"标题匹配: '{actual_title}'",
                    details={"expected": expected_title, "actual": actual_title},
                    severity="info"
                )
            else:
                return CheckResult(
                    check_name="page_title",
                    passed=False,
                    message=f"标题不匹配",
                    details={"expected": expected_title, "actual": actual_title},
                    severity="warning"
                )
        else:
            return CheckResult(
                check_name="page_title",
                passed=True,
                message=f"页面标题: '{actual_title}'",
                details={"actual": actual_title},
                severity="info"
            )
    except Exception as e:
        return CheckResult(
            check_name="page_title",
            passed=False,
            message=f"获取页面标题失败: {str(e)}",
            severity="warning"
        )


def check_required_elements(driver, required_elements: List[Dict[str, str]], timeout: int = 10) -> CheckResult:
    """检查必需元素是否存在"""
    if not HAS_SELENIUM or driver is None:
        return CheckResult(
            check_name="required_elements",
            passed=True,
            message="Selenium未安装或driver不可用，跳过元素检查",
            severity="warning"
        )
    
    if not required_elements:
        return CheckResult(
            check_name="required_elements",
            passed=True,
            message="未指定必需元素",
            severity="info"
        )
    
    missing_elements = []
    found_elements = []
    
    for elem_spec in required_elements:
        found = False
        try:
            if "id" in elem_spec:
                By.ID
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.ID, elem_spec["id"]))
                )
                found = True
                found_elements.append(f"#{elem_spec['id']}")
            elif "class" in elem_spec:
                elements = driver.find_elements(By.CLASS_NAME, elem_spec["class"])
                if elements:
                    found = True
                    found_elements.append(f".{elem_spec['class']} (找到{len(elements)}个)")
            elif "xpath" in elem_spec:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, elem_spec["xpath"]))
                )
                found = True
                found_elements.append(f"xpath:{elem_spec['xpath']}")
            elif "css" in elem_spec:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, elem_spec["css"]))
                )
                found = True
                found_elements.append(f"css:{elem_spec['css']}")
        except Exception:
            pass
        
        if not found:
            missing_elements.append(elem_spec)
    
    if missing_elements:
        return CheckResult(
            check_name="required_elements",
            passed=False,
            message=f"缺少 {len(missing_elements)} 个必需元素",
            details={"missing": missing_elements, "found": found_elements},
            severity="error"
        )
    else:
        return CheckResult(
            check_name="required_elements",
            passed=True,
            message=f"所有 {len(found_elements)} 个必需元素已找到",
            details={"found": found_elements},
            severity="info"
        )


def check_login_status(driver, login_required: bool = False) -> CheckResult:
    """检查登录状态"""
    if not HAS_SELENIUM or driver is None:
        return CheckResult(
            check_name="login_status",
            passed=True,
            message="Selenium未安装或driver不可用，跳过登录检查",
            severity="warning"
        )
    
    # 常见登录指示器
    login_indicators = [
        (By.ID, "login-form"),
        (By.CLASS_NAME, "login-container"),
        (By.XPATH, "//*[contains(text(), '登录')]"),
        (By.ID, "username"),
        (By.NAME, "email"),
    ]
    
    logout_indicators = [
        (By.ID, "logout-btn"),
        (By.CLASS_NAME, "user-profile"),
        (By.XPATH, "//*[contains(@class, 'user-info')]"),
    ]
    
    is_logged_in = False
    is_logged_out = False
    
    for by, selector in logout_indicators:
        try:
            elements = driver.find_elements(by, selector)
            if elements:
                is_logged_out = True
                break
        except Exception:
            pass
    
    if not is_logged_out:
        for by, selector in login_indicators:
            try:
                elements = driver.find_elements(by, selector)
                if elements:
                    is_logged_in = True
                    break
            except Exception:
                pass
    
    if login_required:
        if is_logged_out:
            return CheckResult(
                check_name="login_status",
                passed=False,
                message="需要登录但检测到已登出状态",
                severity="error"
            )
        else:
            return CheckResult(
                check_name="login_status",
                passed=True,
                message="登录状态检查通过",
                severity="info"
            )
    else:
        return CheckResult(
            check_name="login_status",
            passed=True,
            message=f"登录状态: {'已登录' if is_logged_out else '未检测到明确登录状态'}",
            severity="info"
        )


def check_network_latency(driver, threshold_ms: int = 3000) -> CheckResult:
    """检查网络延迟"""
    if not HAS_SELENIUM or driver is None:
        return CheckResult(
            check_name="network_latency",
            passed=True,
            message="Selenium未安装，跳过延迟检查",
            severity="warning"
        )
    
    try:
        # 使用JavaScript获取网络延迟指标
        latency = driver.execute_script("""
            return window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        """)
        
        if latency > threshold_ms:
            return CheckResult(
                check_name="network_latency",
                passed=True,  # 不阻塞，但警告
                message=f"网络延迟较高: {latency}ms (阈值: {threshold_ms}ms)",
                details={"latency_ms": latency, "threshold_ms": threshold_ms},
                severity="warning"
            )
        else:
            return CheckResult(
                check_name="network_latency",
                passed=True,
                message=f"网络延迟正常: {latency}ms",
                details={"latency_ms": latency},
                severity="info"
            )
    except Exception as e:
        return CheckResult(
            check_name="network_latency",
            passed=True,
            message=f"无法获取延迟信息: {str(e)}",
            severity="warning"
        )


def run_env_readiness_check(
    url: str,
    expected_title: Optional[str] = None,
    required_elements: Optional[List[Dict]] = None,
    login_required: bool = False,
    latency_threshold_ms: int = 3000,
    use_selenium: bool = False,
    driver_options: Optional[str] = None
) -> EnvReadinessReport:
    """
    执行完整的环境就绪检查
    
    Args:
        url: 目标URL
        expected_title: 预期页面标题
        required_elements: 必需元素列表 [{"id": "xxx"}, {"class": "xxx"}]
        login_required: 是否需要登录状态
        latency_threshold_ms: 延迟阈值(毫秒)
        use_selenium: 是否使用Selenium进行浏览器检查
        driver_options: 浏览器选项 (chrome, firefox, edge)
    
    Returns:
        EnvReadinessReport: 环境就绪报告
    """
    from datetime import datetime
    
    checks = []
    blockers = []
    warnings = []
    driver = None
    
    # 解析URL
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = f"https://{url}"
    
    # 1. URL可达性检查
    checks.append(check_url_reachability(url))
    
    # 2. Selenium检查（可选）
    if use_selenium and HAS_SELENIUM:
        try:
            if driver_options == "firefox":
                driver = webdriver.Firefox()
            elif driver_options == "edge":
                driver = webdriver.Edge()
            else:
                driver = webdriver.Chrome()
            
            driver.get(url)
            
            # 页面标题检查
            checks.append(check_page_title(driver, expected_title))
            
            # 必需元素检查
            if required_elements:
                checks.append(check_required_elements(driver, required_elements))
            
            # 登录状态检查
            checks.append(check_login_status(driver, login_required))
            
            # 网络延迟检查
            checks.append(check_network_latency(driver, latency_threshold_ms))
            
        except WebDriverException as e:
            checks.append(CheckResult(
                check_name="selenium",
                passed=False,
                message=f"Selenium执行失败: {str(e)}",
                severity="error"
            ))
            blockers.append(f"浏览器自动化失败: {str(e)}")
        finally:
            if driver:
                driver.quit()
    else:
        # 非Selenium模式，添加跳过信息
        if required_elements:
            checks.append(CheckResult(
                check_name="required_elements",
                passed=True,
                message="跳过元素检查（未启用Selenium）",
                severity="info"
            ))
    
    # 收集阻塞问题
    for check in checks:
        if check.severity == "error" and not check.passed:
            blockers.append(f"{check.check_name}: {check.message}")
        elif check.severity == "warning":
            warnings.append(f"{check.check_name}: {check.message}")
    
    overall_ready = len(blockers) == 0
    
    return EnvReadinessReport(
        overall_ready=overall_ready,
        timestamp=datetime.now().isoformat(),
        target_url=url,
        checks=checks,
        blockers=blockers,
        warnings=warnings
    )


def main():
    parser = argparse.ArgumentParser(description="环境就绪检查脚本")
    parser.add_argument("--url", required=True, help="目标URL")
    parser.add_argument("--expected_title", help="预期页面标题")
    parser.add_argument("--required_elements", help="必需元素JSON数组")
    parser.add_argument("--login_required", type=bool, default=False, help="是否需要登录")
    parser.add_argument("--latency_threshold", type=int, default=3000, help="延迟阈值(毫秒)")
    parser.add_argument("--selenium", action="store_true", help="启用Selenium浏览器检查")
    parser.add_argument("--driver", choices=["chrome", "firefox", "edge"], default="chrome", help="浏览器类型")
    parser.add_argument("--output", help="输出JSON文件路径")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    # 解析必需元素
    required_elements = None
    if args.required_elements:
        try:
            required_elements = json.loads(args.required_elements)
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}", file=sys.stderr)
            sys.exit(1)
    
    # 执行检查
    report = run_env_readiness_check(
        url=args.url,
        expected_title=args.expected_title,
        required_elements=required_elements,
        login_required=args.login_required,
        latency_threshold_ms=args.latency_threshold,
        use_selenium=args.selenium,
        driver_options=args.driver
    )
    
    # 输出结果
    if not args.quiet:
        if report.overall_ready:
            print("✅ 环境就绪检查通过")
        else:
            print("🛑 环境就绪检查未通过")
        
        for blocker in report.blockers:
            print(f"  ❌ {blocker}")
        
        for warning in report.warnings:
            print(f"  ⚠️ {warning}")
    
    # 输出JSON
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    
    # 返回码
    sys.exit(0 if report.overall_ready else 1)


if __name__ == "__main__":
    main()
