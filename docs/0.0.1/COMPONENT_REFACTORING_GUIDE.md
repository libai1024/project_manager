# 组件拆分指南

## 当前状态
- ProjectDetail.vue: 6623行 ❌ (目标: <5000行)
- Todos.vue: 2520行 ❌ (目标: <5000行)  
- ResourceManager.vue: 1886行 ✅ (目标: <5000行)

## 拆分策略

### ProjectDetail.vue 拆分方案

#### 已创建组件：
1. ✅ `components/project-detail/ProjectInfoCard.vue` (~100行)
2. ✅ `components/project-detail/ProjectRequirementsCard.vue` (~100行)

#### 待创建组件：

**3. ProjectPartsCard.vue** (~400行)
- 位置: `components/project-detail/ProjectPartsCard.vue`
- 功能: 元器件清单显示表格
- Props: `project`, `parts`, `partsTotalPrice`
- Events: `edit`, `delete`, `export`, `add`

**4. ProjectPartsEditDialog.vue** (~500行)
- 位置: `components/project-detail/ProjectPartsEditDialog.vue`
- 功能: 元器件清单编辑对话框
- Props: `modelValue`, `project`, `editingPart`, `editingIndex`
- Events: `update:modelValue`, `save`, `cancel`

**5. ProjectStepsTimeline.vue** (~800行)
- 位置: `components/project-detail/ProjectStepsTimeline.vue`
- 功能: 项目步骤时间线
- Props: `project`, `steps`, `expandedStepId`
- Events: `update-status`, `insert-step`, `delete-step`, `update-deadline`, `toggle-expand`

**6. ProjectLogsCard.vue** (~600行)
- 位置: `components/project-detail/ProjectLogsCard.vue`
- 功能: 项目日志显示
- Props: `project`, `logs`, `loading`
- Events: `refresh`, `delete-log`, `add-snapshot`, `export`

**7. ProjectAttachmentsCard.vue** (~800行)
- 位置: `components/project-detail/ProjectAttachmentsCard.vue`
- 功能: 项目附件管理
- Props: `project`, `attachments`, `folders`
- Events: `upload`, `delete`, `preview`, `download`, `move`, `rename`

**8. ProjectEditDialog.vue** (~200行)
- 位置: `components/project-detail/ProjectEditDialog.vue`
- 功能: 编辑项目对话框
- Props: `modelValue`, `project`
- Events: `update:modelValue`, `save`, `cancel`

**9. FilePreviewDialog.vue** (~300行)
- 位置: `components/project-detail/FilePreviewDialog.vue`
- 功能: 文件预览对话框
- Props: `modelValue`, `attachment`
- Events: `update:modelValue`, `download`

### Todos.vue 拆分方案

**1. TodoDateSelector.vue** (~300行)
- 位置: `components/todos/TodoDateSelector.vue`
- 功能: 日期选择器
- Props: `selectedDate`, `dateList`
- Events: `select-date`

**2. TodoList.vue** (~400行)
- 位置: `components/todos/TodoList.vue`
- 功能: 待办列表
- Props: `todos`, `selectedDate`, `loading`
- Events: `view`, `edit`, `delete`, `complete`, `toggle-complete`

**3. TodoDetailDialog.vue** (~400行)
- 位置: `components/todos/TodoDetailDialog.vue`
- 功能: 待办详情对话框
- Props: `modelValue`, `todo`
- Events: `update:modelValue`, `edit`, `delete`

**4. TodoCreateDialog.vue** (~300行)
- 位置: `components/todos/TodoCreateDialog.vue`
- 功能: 创建待办对话框
- Props: `modelValue`, `projectId`, `selectedDate`
- Events: `update:modelValue`, `create`

**5. TodoCalendar.vue** (~300行)
- 位置: `components/todos/TodoCalendar.vue`
- 功能: 日历组件
- Props: `selectedDate`, `todos`
- Events: `select-date`

### ResourceManager.vue 拆分方案

**1. ProjectSidebar.vue** (~400行)
- 位置: `components/resource-manager/ProjectSidebar.vue`
- 功能: 项目侧边栏
- Props: `projects`, `selectedProjectId`, `searchKeyword`, `sortBy`
- Events: `select-project`, `update-search`, `update-sort`

**2. FileManager.vue** (~600行)
- 位置: `components/resource-manager/FileManager.vue`
- 功能: 文件管理器
- Props: `project`, `attachments`, `folders`, `viewMode`
- Events: `upload`, `delete`, `preview`, `download`, `move`, `rename`, `copy`, `paste`

**3. FileContextMenu.vue** (~200行)
- 位置: `components/resource-manager/FileContextMenu.vue`
- 功能: 文件右键菜单
- Props: `visible`, `position`, `attachment`
- Events: `preview`, `download`, `rename`, `move`, `delete`, `copy`

## 执行步骤

### 第一步：创建组件目录
```bash
mkdir -p src/components/project-detail
mkdir -p src/components/todos
mkdir -p src/components/resource-manager
```

### 第二步：创建组件文件
按照上述列表逐个创建组件文件

### 第三步：更新主文件
在主文件中：
1. 导入组件
2. 注册组件
3. 替换模板中的代码块
4. 传递props和监听events
5. 移除已提取的逻辑代码

### 第四步：测试
1. 功能测试
2. 样式测试
3. 性能测试

### 第五步：验证行数
```bash
wc -l src/views/*.vue src/components/**/*.vue
```

## 注意事项

1. **保持接口一致性**: 使用Props和Events进行通信
2. **共享逻辑**: 使用composables提取共享逻辑
3. **样式隔离**: 使用scoped样式
4. **类型安全**: 使用TypeScript定义Props和Events
5. **性能优化**: 使用v-if/v-show合理控制渲染

