/**
 * 归档项目 API 测试脚本
 * 在浏览器控制台中运行此脚本来测试 API
 * 
 * 使用方法：
 * 1. 打开浏览器开发者工具 (F12)
 * 2. 切换到 Console 标签
 * 3. 复制粘贴此脚本并运行
 */

// 配置
const CONFIG = {
    baseUrl: 'http://localhost:8000/api',
    token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2NzUxOTg4MH0.XZkpt0TMHnVv1dAyLSyDPJS-BPaBKF7WuUDi3ehyVwg',
    skip: 0,
    limit: 12
};

// 测试函数
async function testArchivedProjectsAPI() {
    console.log('=== 归档项目 API 测试 ===\n');
    
    // 1. 检查 localStorage
    console.log('1. 检查 LocalStorage Token:');
    const storedToken = localStorage.getItem('token');
    console.log('   - LocalStorage token:', storedToken ? storedToken.substring(0, 50) + '...' : '未找到');
    console.log('   - Token 长度:', storedToken ? storedToken.length : 0);
    console.log('   - 使用配置中的 token:', CONFIG.token.substring(0, 50) + '...\n');
    
    // 2. 使用 Fetch API 测试
    console.log('2. 使用 Fetch API 测试:');
    try {
        const url = `${CONFIG.baseUrl}/archived-projects/?skip=${CONFIG.skip}&limit=${CONFIG.limit}`;
        console.log('   - URL:', url);
        console.log('   - Headers:', {
            'Authorization': `Bearer ${CONFIG.token.substring(0, 30)}...`,
            'Content-Type': 'application/json'
        });
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${CONFIG.token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('   - 状态码:', response.status, response.statusText);
        console.log('   - 响应头:', Object.fromEntries(response.headers.entries()));
        
        const data = await response.json();
        console.log('   - 响应数据:', data);
        console.log('   - 数据长度:', Array.isArray(data) ? data.length : 'N/A');
        
        if (response.ok) {
            console.log('   ✅ Fetch API 测试成功\n');
        } else {
            console.log('   ❌ Fetch API 测试失败\n');
        }
    } catch (error) {
        console.error('   ❌ Fetch API 错误:', error);
        console.log('');
    }
    
    // 3. 使用 Axios 测试（如果可用）
    if (typeof axios !== 'undefined') {
        console.log('3. 使用 Axios 测试:');
        try {
            const url = `${CONFIG.baseUrl}/archived-projects/`;
            console.log('   - URL:', url);
            
            const response = await axios.get(url, {
                params: {
                    skip: CONFIG.skip,
                    limit: CONFIG.limit
                },
                headers: {
                    'Authorization': `Bearer ${CONFIG.token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('   - 状态码:', response.status);
            console.log('   - 请求配置:', {
                url: response.config.url,
                method: response.config.method,
                headers: response.config.headers,
                params: response.config.params
            });
            console.log('   - 响应数据:', response.data);
            console.log('   - 数据长度:', Array.isArray(response.data) ? response.data.length : 'N/A');
            console.log('   ✅ Axios 测试成功\n');
        } catch (error) {
            console.error('   ❌ Axios 错误:', error.response ? {
                status: error.response.status,
                statusText: error.response.statusText,
                data: error.response.data,
                headers: error.response.headers,
                requestHeaders: error.config?.headers
            } : error.message);
            console.log('');
        }
    } else {
        console.log('3. Axios 不可用，跳过测试\n');
    }
    
    // 4. 测试前端 API 调用
    console.log('4. 测试前端 API 调用:');
    try {
        // 模拟前端的 API 调用
        const testToken = storedToken || CONFIG.token;
        console.log('   - 使用的 token:', testToken.substring(0, 50) + '...');
        
        const testUrl = `${CONFIG.baseUrl}/archived-projects/`;
        const testParams = new URLSearchParams({
            skip: CONFIG.skip.toString(),
            limit: CONFIG.limit.toString()
        });
        
        const fullUrl = `${testUrl}?${testParams.toString()}`;
        console.log('   - 完整 URL:', fullUrl);
        
        const testResponse = await fetch(fullUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${testToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('   - 状态码:', testResponse.status);
        const testData = await testResponse.json();
        console.log('   - 响应数据:', testData);
        
        if (testResponse.ok) {
            console.log('   ✅ 前端 API 调用测试成功\n');
        } else {
            console.log('   ❌ 前端 API 调用测试失败\n');
        }
    } catch (error) {
        console.error('   ❌ 前端 API 调用错误:', error);
        console.log('');
    }
    
    // 5. 检查请求拦截器
    console.log('5. 检查前端请求拦截器配置:');
    console.log('   - 请检查浏览器 Network 标签中的实际请求');
    console.log('   - 查看请求头中是否包含 Authorization header');
    console.log('   - 如果缺少，可能是请求拦截器的问题\n');
    
    console.log('=== 测试完成 ===');
    console.log('\n提示:');
    console.log('1. 检查浏览器 Network 标签，查看实际发送的请求');
    console.log('2. 确认 Authorization header 是否正确设置');
    console.log('3. 检查后端日志，查看是否收到请求');
    console.log('4. 如果 token 过期，请重新登录获取新 token');
}

// 运行测试
testArchivedProjectsAPI();

