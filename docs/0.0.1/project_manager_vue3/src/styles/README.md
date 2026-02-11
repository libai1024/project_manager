# 主题样式指南

## 黑白极简线条风格主题

本项目采用**黑白极简线条风格**设计，所有 UI 组件都应遵循此主题规范。

## 文件结构

```
src/styles/
├── theme.css              # 全局主题变量和基础样式
├── element-plus-theme.css # Element Plus 组件主题定制
├── components.css         # 自定义组件样式
└── README.md             # 本文档
```

## 设计原则

1. **极简主义**：去除所有不必要的装饰，只保留功能性元素
2. **线条为主**：使用细线条（1-2px）作为主要视觉元素
3. **黑白灰**：只使用黑白灰三种颜色，不使用彩色
4. **小圆角**：使用 2-4px 的小圆角，或直角
5. **轻微阴影**：使用非常轻微的阴影（或不用阴影）
6. **清晰层次**：通过线条粗细和间距区分层次

## 颜色系统

### 主色调
- `--color-black`: #000000 - 主要强调色
- `--color-white`: #ffffff - 背景色
- `--color-gray-*`: 9 个灰度级别

### 功能色（使用灰度替代）
- Primary: 黑色
- Success: 深灰 (#424242)
- Warning: 中灰 (#757575)
- Danger: 深灰 (#212121)
- Info: 浅灰 (#9e9e9e)

## 使用主题变量

### 在 Vue 组件中

```vue
<style scoped>
.my-component {
  color: var(--text-primary);
  background-color: var(--bg-primary);
  border: var(--border-width-thin) solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: var(--spacing-md);
}
</style>
```

### 在 TypeScript/JavaScript 中

```typescript
const style = {
  color: 'var(--text-primary)',
  border: 'var(--border-width-thin) solid var(--border-color)',
}
```

## 常用变量

### 颜色
- `var(--text-primary)` - 主要文字颜色（黑色）
- `var(--text-secondary)` - 次要文字颜色（深灰）
- `var(--bg-primary)` - 主要背景色（白色）
- `var(--bg-secondary)` - 次要背景色（浅灰）
- `var(--border-color)` - 边框颜色（浅灰）

### 间距
- `var(--spacing-xs)` - 4px
- `var(--spacing-sm)` - 8px
- `var(--spacing-md)` - 16px
- `var(--spacing-lg)` - 24px
- `var(--spacing-xl)` - 32px

### 边框
- `var(--border-width-thin)` - 1px
- `var(--border-width-medium)` - 2px
- `var(--radius-sm)` - 2px
- `var(--radius-md)` - 4px

### 阴影
- `var(--shadow-sm)` - 轻微阴影
- `var(--shadow-md)` - 中等阴影
- `var(--shadow-none)` - 无阴影

## 组件开发规范

### 1. 按钮
- 使用 `var(--border-width-thin)` 边框
- 使用 `var(--radius-sm)` 圆角
- 悬停时改变边框颜色为黑色

### 2. 卡片
- 使用 `var(--border-width-thin)` 边框
- 使用 `var(--shadow-sm)` 阴影
- 使用 `var(--radius-sm)` 圆角

### 3. 输入框
- 使用 `var(--border-width-thin)` 边框
- 聚焦时边框变为黑色
- 使用 `var(--radius-sm)` 圆角

### 4. 表格
- 使用细线条分隔
- 表头使用 `var(--bg-secondary)` 背景
- 使用 `var(--border-width-thin)` 边框

## 工具类

在 `style.css` 中定义了一些工具类：

```html
<div class="text-primary">主要文字</div>
<div class="bg-secondary">次要背景</div>
<div class="border-thin">细边框</div>
<div class="shadow-sm">轻微阴影</div>
<div class="rounded-sm">小圆角</div>
```

## 响应式设计

主题变量在移动端和桌面端都适用，但可以通过媒体查询调整：

```css
@media (max-width: 768px) {
  .component {
    padding: var(--spacing-sm);
    font-size: var(--font-size-sm);
  }
}
```

## 保持一致性

开发新组件时，请：

1. ✅ 使用主题变量，不要硬编码颜色和尺寸
2. ✅ 遵循设计原则（极简、线条、黑白灰）
3. ✅ 使用预定义的间距和圆角
4. ✅ 保持边框宽度一致（1-2px）
5. ✅ 避免使用彩色，只使用黑白灰
6. ✅ 使用轻微的阴影或不用阴影

## 示例

查看以下文件了解如何使用主题：
- `src/layouts/MainLayout.vue` - 布局组件
- `src/views/Login.vue` - 登录页面
- `src/styles/components.css` - 自定义组件样式

