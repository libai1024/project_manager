# 代码重构拆分计划

## 目标
- 单一页面控制在5000行以内
- 组件控制在1500行以内

## 需要拆分的文件

### 1. ProjectDetail.vue (6623行) → 需要拆分

#### 拆分方案：
- **ProjectInfoCard.vue** (~100行) - 项目基本信息卡片 ✅
- **ProjectRequirementsCard.vue** (~100行) - 项目需求卡片 ✅
- **ProjectStepsTimeline.vue** (~800行) - 项目步骤时间线
- **ProjectLogsCard.vue** (~600行) - 项目日志卡片
- **ProjectPartsCard.vue** (~400行) - 元器件清单卡片
- **ProjectPartsEditDialog.vue** (~500行) - 元器件清单编辑对话框
- **ProjectAttachmentsCard.vue** (~800行) - 项目附件卡片
- **ProjectEditDialog.vue** (~200行) - 编辑项目对话框
- **FilePreviewDialog.vue** (~300行) - 文件预览对话框
- **ProjectDetail.vue** (主文件，剩余~2000行)

### 2. Todos.vue (2520行) → 需要拆分

#### 拆分方案：
- **TodoDateSelector.vue** (~300行) - 日期选择器
- **TodoList.vue** (~400行) - 待办列表
- **TodoDetailDialog.vue** (~400行) - 待办详情对话框
- **TodoCreateDialog.vue** (~300行) - 创建待办对话框
- **TodoCalendar.vue** (~300行) - 日历组件
- **Todos.vue** (主文件，剩余~800行)

### 3. ResourceManager.vue (1886行) → 需要拆分

#### 拆分方案：
- **ProjectSidebar.vue** (~400行) - 项目侧边栏
- **FileManager.vue** (~600行) - 文件管理器
- **FileContextMenu.vue** (~200行) - 文件右键菜单
- **ResourceManager.vue** (主文件，剩余~700行)

## 执行步骤

1. 创建组件目录结构
2. 逐个创建组件文件
3. 更新主文件引用组件
4. 测试功能完整性
5. 验证行数符合规范

