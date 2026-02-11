/**
 * 快速修复 Token 脚本
 * 
 * 使用方法：
 * 1. 打开浏览器开发者工具 (F12)
 * 2. 切换到 Console 标签
 * 3. 复制粘贴以下代码并运行
 * 
 * 或者直接在控制台运行：
 * localStorage.setItem('token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2NzUxOTg4MH0.XZkpt0TMHnVv1dAyLSyDPJS-BPaBKF7WuUDi3ehyVwg');
 */

// 设置 token
const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2NzUxOTg4MH0.XZkpt0TMHnVv1dAyLSyDPJS-BPaBKF7WuUDi3ehyVwg';

console.log('=== 快速修复 Token ===');

// 1. 检查当前 token
const currentToken = localStorage.getItem('token');
console.log('1. 当前 token:', currentToken ? currentToken.substring(0, 50) + '...' : '未找到');

// 2. 设置新 token
localStorage.setItem('token', TOKEN);
console.log('2. ✅ Token 已设置');

// 3. 验证设置
const newToken = localStorage.getItem('token');
console.log('3. 验证 token:', newToken ? newToken.substring(0, 50) + '...' : '设置失败');

// 4. 测试 API
console.log('4. 测试 API...');
fetch('http://localhost:8000/api/archived-projects/?skip=0&limit=12', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json'
    }
})
.then(response => {
    console.log('API 响应状态:', response.status, response.statusText);
    return response.json();
})
.then(data => {
    console.log('✅ API 测试成功！');
    console.log('响应数据:', data);
    console.log('\n=== 修复完成 ===');
    console.log('请刷新页面并重新访问归档项目页面');
})
.catch(error => {
    console.error('❌ API 测试失败:', error);
});

