# 插件系统重构说明

## 已完成的工作

### 1. 创建复用组件
- ✅ `PluginCardHeader.vue` - 插件卡片头部组件，统一头部样式
- ✅ `BasePluginCard.vue` - 插件基础卡片组件，统一卡片结构和插件启用检查

### 2. 更新插件设置系统
- ✅ 更新 `usePluginSettings.ts` 支持新的插件类型 `parts`
- ✅ 添加元器件清单插件的启用/禁用管理

### 3. 创建新插件
- ✅ `ProjectPartsPlugin.vue` - 元器件清单插件，复用现有的 `ProjectPartsCard` 和 `ProjectPartsEditDialog` 组件

## 待完成的工作

### 1. 重构现有插件（需要手动完成）
由于代码量较大，需要手动重构以下插件：

#### GitHubPlugin.vue
- 替换 `<el-card>` 为 `<BasePluginCard>`
- 移除重复的头部代码
- 移除 `isPluginEnabled` 相关代码（BasePluginCard 已处理）
- 保留所有业务逻辑

#### GraduationPlugin.vue
- 替换 `<el-card>` 为 `<BasePluginCard>`
- 移除重复的头部代码
- 移除插件启用检查（BasePluginCard 已处理）
- 保留所有业务逻辑

### 2. 更新 ProjectDetail.vue
在 `ProjectDetail.vue` 中：
- 移除原有的元器件清单卡片代码
- 添加 `ProjectPartsPlugin` 组件
- 确保插件正确显示

### 3. 更新项目创建界面
在项目创建/编辑界面中：
- 添加插件选择功能
- 允许用户选择要启用的插件

### 4. 更新设置界面
在设置界面中：
- 添加插件管理功能
- 支持批量启用/禁用插件
- 显示插件状态统计

## 代码优化建议

### 复用组件的好处
1. **统一UI风格** - 所有插件使用相同的头部样式
2. **减少重复代码** - 头部代码从每个插件中移除
3. **易于维护** - 修改头部样式只需修改一个文件
4. **类型安全** - 统一的插件类型管理

### 插件架构
```
BasePluginCard (基础卡片)
  ├── PluginCardHeader (头部组件)
  └── 插件内容 (slot)
      ├── GitHubPlugin
      ├── GraduationPlugin
      └── ProjectPartsPlugin
```

## 使用示例

### 创建新插件
```vue
<template>
  <BasePluginCard
    :project-id="project.id"
    plugin-type="your-plugin"
    title="插件标题"
    subtitle="插件副标题"
    :icon="YourIcon"
    :icon-gradient="['#color1', '#color2']"
  >
    <template #header-actions>
      <!-- 头部操作按钮 -->
    </template>
    
    <!-- 插件内容 -->
  </BasePluginCard>
</template>
```

## 注意事项

1. 所有插件必须通过 `BasePluginCard` 包装
2. 插件类型必须在 `usePluginSettings.ts` 中定义
3. 插件启用状态由 `BasePluginCard` 自动管理
4. 保持插件业务逻辑独立，不依赖其他插件

