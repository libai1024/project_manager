#!/bin/bash
# API测试报告脚本 - 使用curl测试所有API端点
# 测试时间: $(date)

BASE_URL="http://localhost:8000"
REPORT_FILE="api_test_report.md"

# 初始化报告
echo "# API测试报告" > $REPORT_FILE
echo "" >> $REPORT_FILE
echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')" >> $REPORT_FILE
echo "" >> $REPORT_FILE
echo "---" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 计数器
PASS_COUNT=0
FAIL_COUNT=0

# 测试函数
test_api() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local token="$5"

    echo "测试: $name"

    if [ -n "$token" ]; then
        AUTH_HEADER="-H \"Authorization: Bearer $token\""
    else
        AUTH_HEADER=""
    fi

    if [ "$method" = "GET" ]; then
        if [ -n "$token" ]; then
            RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" -H "Authorization: Bearer $token")
        else
            RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint")
        fi
    elif [ "$method" = "POST" ]; then
        if [ -n "$token" ]; then
            if [ -n "$data" ]; then
                RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" -H "Content-Type: application/json" -H "Authorization: Bearer $token" -d "$data")
            else
                RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" -H "Authorization: Bearer $token")
            fi
        else
            RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" -H "Content-Type: application/json" -d "$data")
        fi
    elif [ "$method" = "PUT" ]; then
        if [ -n "$token" ]; then
            RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$endpoint" -H "Content-Type: application/json" -H "Authorization: Bearer $token" -d "$data")
        else
            RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$endpoint" -H "Content-Type: application/json" -d "$data")
        fi
    elif [ "$method" = "DELETE" ]; then
        if [ -n "$token" ]; then
            RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$endpoint" -H "Authorization: Bearer $token")
        else
            RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$endpoint")
        fi
    fi

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" = "200" ]; then
        echo "  ✅ PASS (HTTP $HTTP_CODE)"
        echo "### ✅ $name" >> $REPORT_FILE
        echo "- 方法: $method" >> $REPORT_FILE
        echo "- 端点: $endpoint" >> $REPORT_FILE
        echo "- 状态码: $HTTP_CODE" >> $REPORT_FILE
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "  ❌ FAIL (HTTP $HTTP_CODE)"
        echo "### ❌ $name" >> $REPORT_FILE
        echo "- 方法: $method" >> $REPORT_FILE
        echo "- 端点: $endpoint" >> $REPORT_FILE
        echo "- 状态码: $HTTP_CODE" >> $REPORT_FILE
        echo "- 响应: \`$BODY\`" >> $REPORT_FILE
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    echo "" >> $REPORT_FILE
}

# 登录获取Token
echo "获取认证Token..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" -d "username=admin&password=admin123")
TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "登录失败，无法获取Token"
    exit 1
fi
echo "Token获取成功"
echo ""

# ==================== 测试开始 ====================

echo "## 1. 健康检查" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "根路径" "GET" "/" "" ""
test_api "健康检查" "GET" "/health" "" ""

echo "## 2. 用户认证" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "用户登录" "POST" "/api/auth/login" "username=admin&password=admin123" ""
test_api "获取当前用户" "GET" "/api/auth/me" "" "$TOKEN"

echo "## 3. 平台管理" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "获取平台列表" "GET" "/api/platforms" "" "$TOKEN"
test_api "创建平台" "POST" "/api/platforms" '{"name":"测试平台_CURL","url":"https://test.com"}' "$TOKEN"

echo "## 4. 标签管理" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "获取标签列表" "GET" "/api/tags" "" "$TOKEN"
test_api "创建标签" "POST" "/api/tags" '{"name":"测试标签_CURL","color":"#409eff"}' "$TOKEN"

echo "## 5. 项目管理" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "获取项目列表" "GET" "/api/projects" "" "$TOKEN"

# 创建项目（需要平台ID）
PLATFORM_ID=$(curl -s "$BASE_URL/api/platforms" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data'][0]['id'] if d.get('data') else 1)" 2>/dev/null)
test_api "创建项目" "POST" "/api/projects" "{\"title\":\"测试项目_CURL\",\"platform_id\":$PLATFORM_ID,\"price\":100.0}" "$TOKEN"

# 获取项目ID
PROJECT_ID=$(curl -s "$BASE_URL/api/projects" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data'][0]['id'] if d.get('data') else 1)" 2>/dev/null)
test_api "获取项目详情" "GET" "/api/projects/$PROJECT_ID" "" "$TOKEN"
test_api "更新项目" "PUT" "/api/projects/$PROJECT_ID" '{"title":"更新后的项目"}' "$TOKEN"

echo "## 6. 项目步骤" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "创建项目步骤" "POST" "/api/projects/$PROJECT_ID/steps" '{"name":"测试步骤","order_index":100}' "$TOKEN"

# 获取步骤ID
STEP_ID=$(curl -s "$BASE_URL/api/projects/$PROJECT_ID" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); steps=d.get('data',{}).get('steps',[]); print(steps[-1]['id'] if steps else 1)" 2>/dev/null)
test_api "更新步骤状态" "PUT" "/api/projects/steps/$STEP_ID" '{"status":"进行中"}' "$TOKEN"
test_api "切换步骤Todo" "POST" "/api/projects/steps/$STEP_ID/toggle-todo" "" "$TOKEN"

echo "## 7. Dashboard" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "Dashboard统计" "GET" "/api/dashboard/stats" "" "$TOKEN"

echo "## 8. Todo管理" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "获取Todo列表" "GET" "/api/todos" "" "$TOKEN"

echo "## 9. 步骤模板" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "获取步骤模板列表" "GET" "/api/step-templates" "" "$TOKEN"
test_api "创建步骤模板" "POST" "/api/step-templates" '{"name":"测试模板_CURL","description":"测试","steps":["步骤1","步骤2"]}' "$TOKEN"

echo "## 10. 系统设置" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "获取系统设置" "GET" "/api/system-settings" "" "$TOKEN"

echo "## 11. 清理测试数据" >> $REPORT_FILE
echo "" >> $REPORT_FILE
test_api "删除项目" "DELETE" "/api/projects/$PROJECT_ID" "" "$TOKEN"

# 获取刚创建的标签ID并删除
TAG_ID=$(curl -s "$BASE_URL/api/tags" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); tags=[t for t in d.get('data',[]) if 'CURL' in t.get('name','')]; print(tags[0]['id'] if tags else '')" 2>/dev/null)
if [ -n "$TAG_ID" ]; then
    test_api "删除标签" "DELETE" "/api/tags/$TAG_ID" "" "$TOKEN"
fi

# 获取刚创建的模板ID并删除
TEMPLATE_ID=$(curl -s "$BASE_URL/api/step-templates" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); templates=[t for t in d.get('data',[]) if 'CURL' in t.get('name','')]; print(templates[0]['id'] if templates else '')" 2>/dev/null)
if [ -n "$TEMPLATE_ID" ]; then
    test_api "删除步骤模板" "DELETE" "/api/step-templates/$TEMPLATE_ID" "" "$TOKEN"
fi

# 获取刚创建的平台ID并删除
PLATFORM_ID_NEW=$(curl -s "$BASE_URL/api/platforms" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); platforms=[p for p in d.get('data',[]) if 'CURL' in p.get('name','')]; print(platforms[0]['id'] if platforms else '')" 2>/dev/null)
if [ -n "$PLATFORM_ID_NEW" ]; then
    test_api "删除平台" "DELETE" "/api/platforms/$PLATFORM_ID_NEW" "" "$TOKEN"
fi

# ==================== 汇总 ====================
echo "" >> $REPORT_FILE
echo "---" >> $REPORT_FILE
echo "" >> $REPORT_FILE
echo "## 测试汇总" >> $REPORT_FILE
echo "" >> $REPORT_FILE
TOTAL=$((PASS_COUNT + FAIL_COUNT))
PASS_RATE=$(echo "scale=1; $PASS_COUNT * 100 / $TOTAL" | bc)
echo "| 指标 | 值 |" >> $REPORT_FILE
echo "|------|-----|" >> $REPORT_FILE
echo "| 总测试数 | $TOTAL |" >> $REPORT_FILE
echo "| 通过数 | $PASS_COUNT |" >> $REPORT_FILE
echo "| 失败数 | $FAIL_COUNT |" >> $REPORT_FILE
echo "| 通过率 | ${PASS_RATE}% |" >> $REPORT_FILE

echo ""
echo "=============================="
echo "测试完成!"
echo "总测试数: $TOTAL"
echo "通过数: $PASS_COUNT"
echo "失败数: $FAIL_COUNT"
echo "通过率: ${PASS_RATE}%"
echo "=============================="
echo ""
echo "详细报告已保存到: $REPORT_FILE"
