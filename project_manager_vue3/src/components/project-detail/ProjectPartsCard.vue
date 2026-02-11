<template>
  <el-card class="parts-card" v-if="project">
    <template #header>
      <div class="card-header">
        <span>元器件清单</span>
        <div>
          <el-button size="small" type="primary" @click="$emit('add')">
            <el-icon><Plus /></el-icon>
            新增/编辑
          </el-button>
          <el-button size="small" @click="$emit('export')" :disabled="parts.length === 0">
            <el-icon><Document /></el-icon>
            导出 Excel
          </el-button>
        </div>
      </div>
    </template>

    <el-table
      ref="partsTableRef"
      :data="parts"
      size="small"
      border
      class="parts-table"
    >
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="part-expand">
            <div class="part-expand-row">
              <span class="label">主要功能：</span>
              <span class="value">{{ row.remark || '—' }}</span>
            </div>
            <div class="part-expand-row">
              <span class="label">购买链接：</span>
              <span class="value">
                <a v-if="row.purchase_link" :href="row.purchase_link" target="_blank" rel="noopener noreferrer">
                  {{ row.purchase_link }}
                </a>
                <span v-else>—</span>
              </span>
            </div>
          </div>
        </template>
      </el-table-column>

      <!-- 图片列放在最前面 -->
      <el-table-column label="图片" width="110" align="center">
        <template #default="{ row }">
          <div class="part-image-cell">
            <el-image
              v-if="row.image_url && row.image_url.trim() !== ''"
              :src="row.image_url"
              fit="cover"
              class="part-image"
              :preview-src-list="[row.image_url]"
              preview-teleported
              :lazy="true"
              loading="lazy"
              :width="80"
              :height="80"
            >
              <template #error>
                <div class="part-image-placeholder">
                  <el-icon><Picture /></el-icon>
                  <span class="placeholder-text">元器件</span>
                </div>
              </template>
            </el-image>
            <div v-else class="part-image-placeholder">
              <el-icon><Picture /></el-icon>
              <span class="placeholder-text">元器件</span>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="module_name" label="功能模块名称" min-width="160">
        <template #default="{ row }">
          {{ row.module_name || '—' }}
        </template>
      </el-table-column>

      <el-table-column prop="core_component" label="核心元器件" min-width="160">
        <template #default="{ row }">
          {{ row.core_component || '—' }}
        </template>
      </el-table-column>

      <el-table-column prop="unit_price" label="单价" width="120" align="right">
        <template #default="{ row }">
          ¥{{ Number(row.unit_price || 0).toFixed(2) }}
        </template>
      </el-table-column>

      <el-table-column prop="quantity" label="数量" width="100" align="center">
        <template #default="{ row }">
          {{ row.quantity || 0 }}
        </template>
      </el-table-column>

      <el-table-column label="小计" width="120" align="right">
        <template #default="{ row }">
          <span class="subtotal-text">¥{{ (Number(row.unit_price || 0) * Number(row.quantity || 0)).toFixed(2) }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="140" fixed="right" align="center">
        <template #default="{ row, $index }">
          <div class="parts-action-buttons">
            <el-button
              type="primary"
              :icon="Edit"
              size="small"
              circle
              class="action-btn-edit"
              @click="$emit('edit', $index, row)"
              title="编辑"
            />
            <el-button
              type="danger"
              :icon="Delete"
              size="small"
              circle
              class="action-btn-delete"
              @click="$emit('delete', $index, row)"
              title="删除"
            />
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="parts-summary" v-if="parts.length > 0">
      <div class="summary-item">
        <span class="summary-label">合计条目：</span>
        <span class="summary-value">{{ parts.length }} 个</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">总价（估算）：</span>
        <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
      </div>
    </div>
    <el-empty v-else description="暂无元器件清单，点击上方按钮添加" :image-size="100" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, Document, Picture, Edit, Delete } from '@element-plus/icons-vue'
import type { Project, ProjectPart } from '@/api/project'

interface Props {
  project: Project | null
  parts: ProjectPart[]
}

const props = defineProps<Props>()

defineEmits<{
  add: []
  edit: [index: number, row: ProjectPart]
  delete: [index: number, row: ProjectPart]
  export: []
}>()

const partsTableRef = ref()

const totalPrice = computed(() => {
  return props.parts.reduce((sum, p) => {
    const price = Number(p.unit_price || 0)
    const qty = Number(p.quantity || 0)
    return sum + price * qty
  }, 0)
})
</script>

<style scoped>
.parts-card {
  margin-top: 20px;
  
  .el-card__header {
    background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    border-bottom: 2px solid #e4e7ed;
    
    .card-header {
      font-weight: 600;
      color: #303133;
    }
  }
}

.parts-table {
  margin-top: 16px;
  
  :deep(.el-table) {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    
    .el-table__header-wrapper {
      .el-table__header {
        th {
          background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
          color: #303133;
          font-weight: 600;
          padding: 14px 12px;
          border-bottom: 2px solid #dcdfe6;
        }
      }
    }
    
    .el-table__body-wrapper {
      .el-table__body {
        tr {
          transition: all 0.2s;
          
          &:hover {
            background-color: #f5f9ff;
            transform: scale(1.001);
          }
          
          td {
            padding: 16px 12px;
            border-bottom: 1px solid #f0f0f0;
          }
        }
      }
    }
  }
  
  :deep(.subtotal-text) {
    font-weight: 600;
    color: #409eff;
    font-size: 15px;
  }
}

.part-image-cell {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
  height: 100%;
}

.part-image {
  width: 80px !important;
  height: 80px !important;
  min-width: 80px;
  min-height: 80px;
  max-width: 80px;
  max-height: 80px;
  border-radius: 8px;
  cursor: pointer;
  object-fit: cover;
  border: 2px solid #e4e7ed;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  display: block;
}

.part-image:hover {
  border-color: #409eff;
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.parts-table :deep(.el-image) {
  width: 80px !important;
  height: 80px !important;
  
  .el-image__inner {
    width: 80px !important;
    height: 80px !important;
    object-fit: cover;
  }
}

.part-image-placeholder {
  width: 80px !important;
  height: 80px !important;
  min-width: 80px;
  min-height: 80px;
  max-width: 80px;
  max-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  border: 2px dashed #c0c4cc;
  border-radius: 8px;
  color: #909399;
  font-size: 12px;
  gap: 4px;
  transition: all 0.3s;
  
  .el-icon {
    font-size: 24px;
  }
  
  .placeholder-text {
    font-size: 11px;
    line-height: 1;
  }
  
  &:hover {
    border-color: #409eff;
    color: #409eff;
    background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
  }
}

.parts-action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  .action-btn-edit {
    width: 32px;
    height: 32px;
    padding: 0;
    background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
    border: none;
    box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:hover {
      background: linear-gradient(135deg, #66b1ff 0%, #85c1ff 100%);
      transform: translateY(-2px) scale(1.1);
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
    }
    
    &:active {
      transform: translateY(0) scale(1.05);
    }
    
    .el-icon {
      font-size: 16px;
      color: #fff;
    }
  }
  
  .action-btn-delete {
    width: 32px;
    height: 32px;
    padding: 0;
    background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
    border: none;
    box-shadow: 0 2px 6px rgba(245, 108, 108, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:hover {
      background: linear-gradient(135deg, #f78989 0%, #f9a5a5 100%);
      transform: translateY(-2px) scale(1.1);
      box-shadow: 0 4px 12px rgba(245, 108, 108, 0.4);
    }
    
    &:active {
      transform: translateY(0) scale(1.05);
    }
    
    .el-icon {
      font-size: 16px;
      color: #fff;
    }
  }
}

.part-expand {
  padding: 16px;
  background-color: #fafafa;
}

.part-expand-row {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.part-expand-row:last-child {
  margin-bottom: 0;
}

.part-expand-row .label {
  font-weight: 600;
  color: #303133;
  min-width: 100px;
  margin-right: 12px;
}

.part-expand-row .value {
  flex: 1;
  color: #606266;
  word-break: break-all;
}

.parts-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  
  .summary-item {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .summary-label {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
    }
    
    .summary-value {
      font-size: 16px;
      color: #303133;
      font-weight: 600;
    }
    
    .total-price {
      font-weight: 700;
      font-size: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }
}
</style>

