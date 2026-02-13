<template>
  <div class="settings-page">
    <el-row :gutter="20" class="settings-layout">
      <!-- 左侧导航栏 -->
      <el-col :xs="24" :sm="6" :md="5" class="settings-sidebar">
        <el-card class="sidebar-card">
          <el-menu
            :default-active="activeMenu"
            class="settings-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="templates">
              <el-icon><Document /></el-icon>
              <span>项目模板</span>
            </el-menu-item>
            <el-menu-item index="log-icons">
              <el-icon><InfoFilled /></el-icon>
              <span>日志图标设置</span>
            </el-menu-item>
            <el-menu-item index="plugins">
              <el-icon><Setting /></el-icon>
              <span>插件管理</span>
            </el-menu-item>
            <el-menu-item index="historical-projects">
              <el-icon><Clock /></el-icon>
              <span>历史项目设置</span>
            </el-menu-item>
            <el-menu-item index="token-management">
              <el-icon><Key /></el-icon>
              <span>Token 管理</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <!-- 右侧内容区 -->
      <el-col :xs="24" :sm="18" :md="19" class="settings-content">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span class="page-title">{{ currentMenuTitle }}</span>
            </div>
          </template>

          <!-- 项目模板管理 -->
          <TemplateSettings
            v-if="activeMenu === 'templates'"
            :templates="templates"
            @create="showCreateTemplateDialog = true"
            @action="handleTemplateAction"
          />

          <!-- 日志图标设置 -->
          <LogIconsSettings
            v-if="activeMenu === 'log-icons'"
            @reset="resetLogIcons"
            @select-icon="showIconSelector"
          />

          <!-- 插件管理 -->
          <div v-if="activeMenu === 'plugins'" class="plugins-settings-section">
            <div class="section-header">
              <div class="section-title">
                <h3>插件管理</h3>
                <p class="section-desc">
                  管理系统插件，扩展项目管理功能。
                </p>
              </div>
            </div>
            <div class="plugins-settings-body">
              <!-- 毕设插件 -->
              <el-card shadow="never" class="plugin-card" style="margin-bottom: 16px;">
                <div class="plugin-item">
                  <div class="plugin-info">
                    <div class="plugin-header">
                      <el-icon class="plugin-icon"><Document /></el-icon>
                      <span class="plugin-name">毕设插件</span>
                      <el-tag type="success" size="small">已安装</el-tag>
                    </div>
                    <p class="plugin-description">
                      提供毕设中核心文件的标记和管理功能，包括任务书、中期报告、演示视频、毕业论文、答辩PPT等文件的分类管理。
                    </p>
                    <div class="plugin-settings">
                      <div class="plugin-status-header">
                        <div class="status-info">
                          <span class="status-label">已启用项目：</span>
                          <el-tag type="success" size="small">{{ getEnabledCount('graduation') }} 个</el-tag>
                        </div>
                        <div class="status-actions">
                          <el-button size="small" @click="handleSelectAllProjects('graduation')" :disabled="loadingProjects">
                            全选
                          </el-button>
                          <el-button size="small" @click="handleDeselectAllProjects('graduation')" :disabled="loadingProjects">
                            全不选
                          </el-button>
                        </div>
                      </div>
                      <div class="plugin-projects-list" v-loading="loadingProjects">
                        <div class="projects-search">
                          <el-input
                            v-model="graduationProjectSearchKeyword"
                            placeholder="搜索项目..."
                            clearable
                            size="small"
                          >
                            <template #prefix>
                              <el-icon><Search /></el-icon>
                            </template>
                          </el-input>
                        </div>
                        <div class="projects-container">
                          <div
                            v-for="project in filteredGraduationProjects"
                            :key="project.id"
                            class="project-item"
                            :class="{ 'is-enabled': isProjectEnabled(project.id, 'graduation') }"
                            @click="toggleProject(project.id, 'graduation')"
                          >
                            <el-checkbox
                              :model-value="isProjectEnabled(project.id, 'graduation')"
                              @click.stop
                              @change="() => toggleProject(project.id, 'graduation')"
                            />
                            <div class="project-info">
                              <div class="project-title-row">
                                <span class="project-title">{{ project.title }}</span>
                                <el-tag :type="getStatusType(project.status)" size="small">
                                  {{ project.status }}
                                </el-tag>
                              </div>
                              <div class="project-meta">
                                <span class="meta-item">{{ project.student_name || '未设置' }}</span>
                                <span class="meta-divider">|</span>
                                <span class="meta-item">{{ formatDate(project.updated_at) }}</span>
                              </div>
                            </div>
                          </div>
                          <el-empty
                            v-if="filteredGraduationProjects.length === 0"
                            description="暂无项目"
                            :image-size="80"
                          />
                        </div>
                      </div>
                      <p class="setting-tip">
                        <el-icon><InfoFilled /></el-icon>
                        选择需要启用毕设插件的项目。已启用的项目将在项目详情和资源管理界面显示毕设文件标记功能。
                      </p>
                    </div>
                    <div class="plugin-features">
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>文件标记和分类</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>项目详情展示</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>右键菜单标记</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>文件上传和日志记录</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>

              <!-- GitHub插件 -->
              <el-card shadow="never" class="plugin-card" style="margin-bottom: 16px;">
                <div class="plugin-item">
                  <div class="plugin-info">
                    <div class="plugin-header">
                      <el-icon class="plugin-icon"><Link /></el-icon>
                      <span class="plugin-name">GitHub插件</span>
                      <el-tag type="success" size="small">已安装</el-tag>
                    </div>
                    <p class="plugin-description">
                      显示GitHub仓库的提交记录和分支信息，支持查看指定分支的commit历史。
                    </p>
                    <div class="plugin-settings">
                      <div class="plugin-status-header">
                        <div class="status-info">
                          <span class="status-label">已启用项目：</span>
                          <el-tag type="success" size="small">{{ getEnabledCount('github') }} 个</el-tag>
                        </div>
                        <div class="status-actions">
                          <el-button size="small" @click="handleSelectAllProjects('github')" :disabled="loadingProjects">
                            全选
                          </el-button>
                          <el-button size="small" @click="handleDeselectAllProjects('github')" :disabled="loadingProjects">
                            全不选
                          </el-button>
                        </div>
                      </div>
                      <div class="plugin-projects-list" v-loading="loadingProjects">
                        <div class="projects-search">
                          <el-input
                            v-model="githubProjectSearchKeyword"
                            placeholder="搜索项目..."
                            clearable
                            size="small"
                          >
                            <template #prefix>
                              <el-icon><Search /></el-icon>
                            </template>
                          </el-input>
                        </div>
                        <div class="projects-container">
                          <div
                            v-for="project in filteredGithubProjects"
                            :key="project.id"
                            class="project-item"
                            :class="{ 'is-enabled': isProjectEnabled(project.id, 'github') }"
                            @click="toggleProject(project.id, 'github')"
                          >
                            <el-checkbox
                              :model-value="isProjectEnabled(project.id, 'github')"
                              @click.stop
                              @change="() => toggleProject(project.id, 'github')"
                            />
                            <div class="project-info">
                              <div class="project-title-row">
                                <span class="project-title">{{ project.title }}</span>
                                <el-tag :type="getStatusType(project.status)" size="small">
                                  {{ project.status }}
                                </el-tag>
                              </div>
                              <div class="project-meta">
                                <span class="meta-item">{{ project.student_name || '未设置' }}</span>
                                <span class="meta-divider">|</span>
                                <span class="meta-item">{{ formatDate(project.updated_at) }}</span>
                              </div>
                            </div>
                          </div>
                          <el-empty
                            v-if="filteredGithubProjects.length === 0"
                            description="暂无项目"
                            :image-size="80"
                          />
                        </div>
                      </div>
                      <p class="setting-tip">
                        <el-icon><InfoFilled /></el-icon>
                        选择需要启用GitHub插件的项目。已启用的项目将在项目详情界面显示GitHub仓库功能。
                      </p>
                    </div>
                    <div class="plugin-features">
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>GitHub地址管理</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>分支列表获取</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>提交记录展示</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>时间线可视化</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>

              <!-- 元器件清单插件 -->
              <el-card shadow="never" class="plugin-card">
                <div class="plugin-item">
                  <div class="plugin-info">
                    <div class="plugin-header">
                      <el-icon class="plugin-icon"><Box /></el-icon>
                      <span class="plugin-name">元器件清单插件</span>
                      <el-tag type="success" size="small">已安装</el-tag>
                    </div>
                    <p class="plugin-description">
                      管理项目所需的元器件清单，包括功能模块、核心元器件、价格、数量等信息，支持导出Excel。
                    </p>
                    <div class="plugin-settings">
                      <div class="plugin-status-header">
                        <div class="status-info">
                          <span class="status-label">已启用项目：</span>
                          <el-tag type="success" size="small">{{ getEnabledCount('parts') }} 个</el-tag>
                        </div>
                        <div class="status-actions">
                          <el-button size="small" @click="handleSelectAllProjects('parts')" :disabled="loadingProjects">
                            全选
                          </el-button>
                          <el-button size="small" @click="handleDeselectAllProjects('parts')" :disabled="loadingProjects">
                            全不选
                          </el-button>
                        </div>
                      </div>
                      <div class="plugin-projects-list" v-loading="loadingProjects">
                        <div class="projects-search">
                          <el-input
                            v-model="partsProjectSearchKeyword"
                            placeholder="搜索项目..."
                            clearable
                            size="small"
                          >
                            <template #prefix>
                              <el-icon><Search /></el-icon>
                            </template>
                          </el-input>
                        </div>
                        <div class="projects-container">
                          <div
                            v-for="project in filteredPartsProjects"
                            :key="project.id"
                            class="project-item"
                            :class="{ 'is-enabled': isProjectEnabled(project.id, 'parts') }"
                            @click="toggleProject(project.id, 'parts')"
                          >
                            <el-checkbox
                              :model-value="isProjectEnabled(project.id, 'parts')"
                              @click.stop
                              @change="() => toggleProject(project.id, 'parts')"
                            />
                            <div class="project-info">
                              <div class="project-title-row">
                                <span class="project-title">{{ project.title }}</span>
                                <el-tag :type="getStatusType(project.status)" size="small">
                                  {{ project.status }}
                                </el-tag>
                              </div>
                              <div class="project-meta">
                                <span class="meta-item">{{ project.student_name || '未设置' }}</span>
                                <span class="meta-divider">|</span>
                                <span class="meta-item">{{ formatDate(project.updated_at) }}</span>
                              </div>
                            </div>
                          </div>
                          <el-empty
                            v-if="filteredPartsProjects.length === 0"
                            description="暂无项目"
                            :image-size="80"
                          />
                        </div>
                      </div>
                      <p class="setting-tip">
                        <el-icon><InfoFilled /></el-icon>
                        选择需要启用元器件清单插件的项目。已启用的项目将在项目详情界面显示元器件清单管理功能。
                      </p>
                    </div>
                    <div class="plugin-features">
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>元器件信息管理</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>价格和数量统计</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>图片和链接支持</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>Excel导出功能</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>

              <!-- 视频回放插件 -->
              <el-card shadow="never" class="plugin-card">
                <div class="plugin-item">
                  <div class="plugin-info">
                    <div class="plugin-header">
                      <el-icon class="plugin-icon"><VideoPlay /></el-icon>
                      <span class="plugin-name">视频回放插件</span>
                      <el-tag type="success" size="small">已安装</el-tag>
                    </div>
                    <p class="plugin-description">
                      上传视频并生成带密码保护的安全观看链接，支持设置有效期和观看次数限制，提供详细的观看统计。
                    </p>
                    <div class="plugin-settings">
                      <div class="plugin-status-header">
                        <div class="status-info">
                          <span class="status-label">已启用项目：</span>
                          <el-tag type="success" size="small">{{ getEnabledCount('video-playback') }} 个</el-tag>
                        </div>
                        <div class="status-actions">
                          <el-button size="small" @click="handleSelectAllProjects('video-playback')" :disabled="loadingProjects">
                            全选
                          </el-button>
                          <el-button size="small" @click="handleDeselectAllProjects('video-playback')" :disabled="loadingProjects">
                            全不选
                          </el-button>
                        </div>
                      </div>
                      <div class="plugin-projects-list" v-loading="loadingProjects">
                        <div class="projects-search">
                          <el-input
                            v-model="videoPlaybackProjectSearchKeyword"
                            placeholder="搜索项目..."
                            clearable
                            size="small"
                          >
                            <template #prefix>
                              <el-icon><Search /></el-icon>
                            </template>
                          </el-input>
                        </div>
                        <div class="projects-container">
                          <div
                            v-for="project in filteredVideoPlaybackProjects"
                            :key="project.id"
                            class="project-item"
                            :class="{ 'is-enabled': isProjectEnabled(project.id, 'video-playback') }"
                            @click="toggleProject(project.id, 'video-playback')"
                          >
                            <el-checkbox
                              :model-value="isProjectEnabled(project.id, 'video-playback')"
                              @click.stop
                              @change="() => toggleProject(project.id, 'video-playback')"
                            />
                            <div class="project-info">
                              <div class="project-title-row">
                                <span class="project-title">{{ project.title }}</span>
                                <el-tag :type="getStatusType(project.status)" size="small">
                                  {{ project.status }}
                                </el-tag>
                              </div>
                              <div class="project-meta">
                                <span class="meta-item">{{ project.student_name || '未设置' }}</span>
                                <span class="meta-divider">|</span>
                                <span class="meta-item">{{ formatDate(project.updated_at) }}</span>
                              </div>
                            </div>
                          </div>
                          <el-empty
                            v-if="filteredVideoPlaybackProjects.length === 0"
                            description="暂无项目"
                            :image-size="80"
                          />
                        </div>
                      </div>
                      <p class="setting-tip">
                        <el-icon><InfoFilled /></el-icon>
                        选择需要启用视频回放插件的项目。已启用的项目将在项目详情界面显示视频回放功能。
                      </p>
                    </div>
                    <div class="plugin-features">
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>视频上传和管理</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>密码保护链接</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>有效期和次数限制</span>
                      </div>
                      <div class="feature-item">
                        <el-icon><Check /></el-icon>
                        <span>观看统计分析</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>
          </div>

          <!-- 历史项目设置 -->
          <div v-if="activeMenu === 'historical-projects'" class="historical-projects-settings-section">
            <div class="section-header">
              <div class="section-title">
                <h3>历史项目功能设置</h3>
                <p class="section-desc">
                  控制历史项目功能的启用状态，包括附件管理、待办管理、日志管理、配件管理等模块对历史项目的支持。
                </p>
              </div>
            </div>
            <div class="historical-projects-settings-body">
              <el-card shadow="never" class="historical-settings-card">
                <div class="historical-settings-list" v-loading="loadingSettings">
                  <div
                    v-for="setting in historicalProjectSettings"
                    :key="setting.key"
                    class="historical-setting-item"
                    :class="{ 'is-enabled': setting.value }"
                  >
                    <div class="setting-icon-wrapper">
                      <el-icon class="setting-icon" :size="24">
                        <component :is="getSettingIcon(setting.key)" />
                      </el-icon>
                    </div>
                    <div class="setting-content">
                      <div class="setting-header-row">
                        <div class="setting-title-group">
                          <span class="setting-name">{{ setting.name }}</span>
                          <el-tag 
                            v-if="setting.value" 
                            type="success" 
                            size="small" 
                            class="setting-status-tag"
                          >
                            已启用
                          </el-tag>
                          <el-tag 
                            v-else 
                            type="info" 
                            size="small" 
                            class="setting-status-tag"
                          >
                            已禁用
                          </el-tag>
                        </div>
                        <el-switch
                          v-model="setting.value"
                          @change="handleSettingChange(setting.key, setting.value)"
                          :disabled="savingSettings"
                          :loading="savingSettings"
                          active-color="#67c23a"
                          inactive-color="#dcdfe6"
                        />
                      </div>
                      <p class="setting-description">{{ setting.description }}</p>
                      <div class="setting-features">
                        <div class="feature-badge" v-if="setting.value">
                          <el-icon><Check /></el-icon>
                          <span>功能已激活</span>
                        </div>
                        <div class="feature-badge disabled" v-else>
                          <el-icon><Close /></el-icon>
                          <span>功能已禁用</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <el-empty 
                    v-if="historicalProjectSettings.length === 0 && !loadingSettings" 
                    description="暂无设置项"
                    :image-size="100"
                  />
                </div>
              </el-card>
              <div class="settings-tip-card">
                <el-icon class="tip-icon"><InfoFilled /></el-icon>
                <div class="tip-content">
                  <div class="tip-title">使用说明</div>
                  <div class="tip-text">
                    启用相应功能后，历史项目将支持对应的管理操作。禁用功能后，相关操作将不可用，但已存在的数据不会受到影响。
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Token 管理 -->
          <div v-if="activeMenu === 'token-management'" class="token-management-section">
            <div class="section-header">
              <div class="section-title">
                <h3>Token 管理</h3>
                <p class="section-desc">
                  管理您的访问令牌、刷新令牌和登录会话，查看登录历史记录。
                </p>
              </div>
              <el-button type="danger" @click="handleLogoutAll" :loading="loggingOutAll">
                <el-icon><Delete /></el-icon>
                登出所有设备
              </el-button>
            </div>

            <div class="token-management-body">
              <!-- Token 持续时间配置 -->
              <el-card shadow="never" class="token-duration-card">
                <template #header>
                  <div class="card-header-title">
                    <el-icon><Setting /></el-icon>
                    <span>Token 持续时间设置</span>
                  </div>
                </template>
                <div class="token-duration-content" v-loading="loadingTokenDuration">
                  <div class="duration-item">
                    <div class="duration-label-group">
                      <span class="duration-label">Access Token 有效期（分钟）</span>
                      <span class="duration-hint">范围：1-1440 分钟（1分钟到24小时）</span>
                    </div>
                    <div class="duration-input-group">
                      <el-input-number
                        v-model="tokenDurationSettings.access_token_expire_minutes"
                        :min="1"
                        :max="1440"
                        :step="1"
                        :disabled="savingTokenDuration"
                        style="width: 200px"
                      />
                      <span class="duration-unit">分钟</span>
                    </div>
                  </div>
                  <div class="duration-item">
                    <div class="duration-label-group">
                      <span class="duration-label">Refresh Token 有效期（天）</span>
                      <span class="duration-hint">范围：1-365 天</span>
                    </div>
                    <div class="duration-input-group">
                      <el-input-number
                        v-model="tokenDurationSettings.refresh_token_expire_days"
                        :min="1"
                        :max="365"
                        :step="1"
                        :disabled="savingTokenDuration"
                        style="width: 200px"
                      />
                      <span class="duration-unit">天</span>
                    </div>
                  </div>
                  <div class="duration-actions">
                    <el-button
                      type="primary"
                      @click="saveTokenDuration"
                      :loading="savingTokenDuration"
                      :disabled="savingTokenDuration"
                    >
                      <el-icon><Check /></el-icon>
                      保存设置
                    </el-button>
                    <el-button
                      @click="loadTokenDuration"
                      :disabled="savingTokenDuration"
                    >
                      <el-icon><Refresh /></el-icon>
                      重置
                    </el-button>
                  </div>
                  <div class="duration-tip">
                    <el-icon><InfoFilled /></el-icon>
                    <span>修改后，新生成的 Token 将使用新的有效期设置。已存在的 Token 不受影响。</span>
                  </div>
                </div>
              </el-card>

              <!-- 当前 Token 信息 -->
              <el-card shadow="never" class="token-info-card">
                <template #header>
                  <div class="card-header-title">
                    <el-icon><Key /></el-icon>
                    <span>当前 Token 信息</span>
                  </div>
                </template>
                <div class="token-info-content">
                  <div class="info-item">
                    <span class="info-label">Token 类型：</span>
                    <el-tag type="success">Bearer Token</el-tag>
                  </div>
                  <div class="info-item">
                    <span class="info-label">有效期：</span>
                    <span class="info-value">{{ tokenDurationSettings.access_token_expire_minutes }} 分钟</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">刷新令牌有效期：</span>
                    <span class="info-value">{{ tokenDurationSettings.refresh_token_expire_days }} 天</span>
                  </div>
                </div>
              </el-card>

              <!-- 设备管理 -->
              <el-card shadow="never" class="devices-card">
                <template #header>
                  <div class="card-header-title">
                    <el-icon><Monitor /></el-icon>
                    <span>已登录设备 ({{ activeDevices.length }})</span>
                  </div>
                </template>
                <div class="devices-list" v-loading="loadingDevices">
                  <div
                    v-for="device in activeDevices"
                    :key="device.id"
                    class="device-item"
                    :class="{ 'is-current': isCurrentDevice(device) }"
                  >
                    <div class="device-icon">
                      <el-icon :size="24"><Monitor /></el-icon>
                    </div>
                    <div class="device-info">
                      <div class="device-header">
                        <span class="device-name">{{ getDeviceName(device) }}</span>
                        <el-tag v-if="isCurrentDevice(device)" type="success" size="small">当前设备</el-tag>
                        <el-tag v-else-if="device.is_revoked" type="danger" size="small">已撤销</el-tag>
                        <el-tag v-else type="success" size="small">活跃</el-tag>
                      </div>
                      <div class="device-details">
                        <div class="detail-row">
                          <el-icon><Location /></el-icon>
                          <span>{{ device.ip_address || '未知 IP' }}</span>
                        </div>
                        <div class="detail-row">
                          <el-icon><Clock /></el-icon>
                          <span>登录时间：{{ formatTime(device.created_at) }}</span>
                        </div>
                        <div v-if="device.expires_at" class="detail-row">
                          <el-icon><Clock /></el-icon>
                          <span>过期时间：{{ formatTime(device.expires_at) }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="device-actions">
                      <el-button
                        v-if="!isCurrentDevice(device) && !device.is_revoked"
                        type="danger"
                        size="small"
                        @click="handleRevokeDevice(device.id)"
                        :loading="revokingDeviceId === device.id"
                      >
                        撤销
                      </el-button>
                    </div>
                  </div>
                  <el-empty
                    v-if="activeDevices.length === 0 && !loadingDevices"
                    description="暂无已登录设备"
                    :image-size="100"
                  />
                </div>
              </el-card>

              <!-- 登录历史 -->
              <el-card shadow="never" class="login-logs-card">
                <template #header>
                  <div class="card-header-title">
                    <el-icon><Document /></el-icon>
                    <span>登录历史记录</span>
                  </div>
                </template>
                <div class="login-logs-list" v-loading="loadingLogs">
                  <div
                    v-for="log in loginLogs"
                    :key="log.id"
                    class="log-item"
                    :class="getLogStatusClass(log.status)"
                  >
                    <div class="log-icon">
                      <el-icon :size="20">
                        <Check v-if="log.status === 'success'" />
                        <Close v-else />
                      </el-icon>
                    </div>
                    <div class="log-info">
                      <div class="log-header">
                        <span class="log-status">{{ getLogStatusText(log.status) }}</span>
                        <el-tag :type="getLogStatusTagType(log.status)" size="small">
                          {{ log.status }}
                        </el-tag>
                      </div>
                      <div class="log-details">
                        <div class="detail-row">
                          <el-icon><Location /></el-icon>
                          <span>{{ log.ip_address || '未知 IP' }}</span>
                        </div>
                        <div class="detail-row">
                          <el-icon><Clock /></el-icon>
                          <span>{{ formatTime(log.created_at) }}</span>
                        </div>
                        <div v-if="log.failure_reason" class="detail-row error">
                          <el-icon><InfoFilled /></el-icon>
                          <span>{{ log.failure_reason }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <el-empty
                    v-if="loginLogs.length === 0 && !loadingLogs"
                    description="暂无登录记录"
                    :image-size="100"
                  />
                </div>
              </el-card>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建/编辑模板对话框 -->
    <StepTemplateEditor
      v-model="showCreateTemplateDialog"
      :template="editingTemplate"
      @success="handleTemplateSuccess"
      @close="showCreateTemplateDialog = false"
    />

    <!-- 重命名对话框 -->
    <el-dialog
      v-model="showRenameDialog"
      title="重命名模板"
      width="400px"
      @close="newTemplateName = ''"
    >
      <el-form>
        <el-form-item label="模板名称">
          <el-input
            v-model="newTemplateName"
            placeholder="请输入模板名称"
            @keyup.enter="confirmRename"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRenameDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="showViewDialog"
      :title="viewingTemplate ? `模板详情 - ${viewingTemplate.name}` : '模板详情'"
      width="600px"
    >
      <div v-if="viewingTemplate" class="template-detail">
        <div class="detail-item">
          <span class="detail-label">模板名称：</span>
          <span class="detail-value">{{ viewingTemplate.name }}</span>
          <el-tag v-if="viewingTemplate.is_default" type="success" size="small" style="margin-left: 8px;">默认</el-tag>
        </div>
        <div v-if="viewingTemplate.description" class="detail-item">
          <span class="detail-label">模板描述：</span>
          <span class="detail-value">{{ viewingTemplate.description }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">步骤数量：</span>
          <span class="detail-value">{{ viewingTemplate.steps.length }} 个</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">创建时间：</span>
          <span class="detail-value">{{ formatTime(viewingTemplate.created_at) }}</span>
        </div>
        <div class="detail-item steps-list">
          <span class="detail-label">步骤列表：</span>
          <div class="steps-container">
            <div
              v-for="(step, index) in viewingTemplate.steps"
              :key="index"
              class="step-detail-item"
            >
              <span class="step-index">{{ index + 1 }}</span>
              <span class="step-name">{{ step }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="showViewDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 图标选择器对话框 -->
    <el-dialog
      v-model="showIconSelectorDialog"
      :title="`选择图标 - ${editingActionName}`"
      width="600px"
    >
      <div class="icon-selector">
        <el-input
          v-model="iconSearchKeyword"
          placeholder="搜索图标..."
          clearable
          class="icon-search"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <div class="icon-grid">
          <div
            v-for="iconName in filteredIcons"
            :key="iconName"
            class="icon-option"
            :class="{ 'is-selected': iconName === selectedIcon }"
            @click="selectIcon(iconName)"
          >
            <el-icon :size="24">
              <component :is="availableIcons[iconName]" />
            </el-icon>
            <span class="icon-label">{{ iconName }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showIconSelectorDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmIconSelection">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document, Edit, Delete, CopyDocument, EditPen, View, More, Setting, InfoFilled, Refresh, Search, Check, Link, Box, VideoPlay, Clock, Close, Paperclip, List, DocumentAdd, Grid, Key, Monitor, Location } from '@element-plus/icons-vue'
import { stepTemplateApi, type StepTemplate } from '@/api/stepTemplate'
import StepTemplateEditor from '@/components/StepTemplateEditor.vue'
import { useLogIconConfig, type LogActionType, logActionNames, availableIcons, iconNames } from '@/composables/useLogIconConfig'
import { usePluginSettings } from '@/composables/usePluginSettings'
import { projectApi, type Project } from '@/api/project'
import { systemSettingsApi, type SystemSettings } from '@/api/historicalProject'
import { authApi, type LoginLog, type RefreshTokenInfo } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import router from '@/router'
import TemplateSettings from '@/components/settings/TemplateSettings.vue'
import LogIconsSettings from '@/components/settings/LogIconsSettings.vue'

const activeMenu = ref('templates')
const templates = ref<StepTemplate[]>([])
const showCreateTemplateDialog = ref(false)
const editingTemplate = ref<StepTemplate | null>(null)
const showRenameDialog = ref(false)
const renamingTemplate = ref<StepTemplate | null>(null)
const newTemplateName = ref('')
const showViewDialog = ref(false)
const viewingTemplate = ref<StepTemplate | null>(null)

// 插件设置
const {
  graduationEnabledProjectIds,
  githubEnabledProjectIds,
  partsEnabledProjectIds,
  isProjectEnabled,
  toggleProject,
  enableAllProjects,
  disableAllProjects,
  getEnabledCount,
  loadPluginSettings,
} = usePluginSettings()

// 项目列表
const loadingProjects = ref(false)
const projects = ref<Project[]>([])
const graduationProjectSearchKeyword = ref('')
const githubProjectSearchKeyword = ref('')
const partsProjectSearchKeyword = ref('')
const videoPlaybackProjectSearchKeyword = ref('')

// 加载项目列表
const loadProjects = async () => {
  loadingProjects.value = true
  try {
    const data = await projectApi.list()
    projects.value = data
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  } finally {
    loadingProjects.value = false
  }
}

// 过滤项目（毕设插件）
const filteredGraduationProjects = computed(() => {
  if (!graduationProjectSearchKeyword.value) {
    return projects.value
  }
  const keyword = graduationProjectSearchKeyword.value.toLowerCase()
  return projects.value.filter(p =>
    p.title.toLowerCase().includes(keyword) ||
    (p.student_name && p.student_name.toLowerCase().includes(keyword))
  )
})

// 过滤项目（GitHub插件）
const filteredGithubProjects = computed(() => {
  if (!githubProjectSearchKeyword.value) {
    return projects.value
  }
  const keyword = githubProjectSearchKeyword.value.toLowerCase()
  return projects.value.filter(p =>
    p.title.toLowerCase().includes(keyword) ||
    (p.student_name && p.student_name.toLowerCase().includes(keyword))
  )
})

// 过滤项目（元器件清单插件）
const filteredPartsProjects = computed(() => {
  if (!partsProjectSearchKeyword.value) {
    return projects.value
  }
  const keyword = partsProjectSearchKeyword.value.toLowerCase()
  return projects.value.filter(p =>
    p.title.toLowerCase().includes(keyword) ||
    (p.student_name && p.student_name.toLowerCase().includes(keyword))
  )
})

// 过滤项目（视频回放插件）
const filteredVideoPlaybackProjects = computed(() => {
  if (!videoPlaybackProjectSearchKeyword.value) {
    return projects.value
  }
  const keyword = videoPlaybackProjectSearchKeyword.value.toLowerCase()
  return projects.value.filter(p =>
    p.title.toLowerCase().includes(keyword) ||
    (p.student_name && p.student_name.toLowerCase().includes(keyword))
  )
})

// 全选/全不选
const handleSelectAllProjects = (pluginType: 'graduation' | 'github' | 'parts' | 'video-playback' = 'graduation') => {
  enableAllProjects(projects.value.map(p => p.id), pluginType)
  ElMessage.success('已启用所有项目')
}

const handleDeselectAllProjects = (pluginType: 'graduation' | 'github' | 'parts' | 'video-playback' = 'graduation') => {
  disableAllProjects(pluginType)
  ElMessage.success('已禁用所有项目')
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '进行中': 'primary',
    '已完成': 'success',
    '已暂停': 'warning',
    '已取消': 'info',
  }
  return statusMap[status] || 'info'
}

// 初始化加载项目列表
onMounted(() => {
  // 加载插件设置（全局共享）
  loadPluginSettings()
  if (activeMenu.value === 'plugins') {
    loadProjects()
  }
})

// 监听菜单切换，加载项目列表
watch(activeMenu, (newMenu) => {
  if (newMenu === 'plugins' && projects.value.length === 0) {
    loadProjects()
  }
})

const currentMenuTitle = computed(() => {
  const menuMap: Record<string, string> = {
    templates: '项目模板',
    'log-icons': '日志图标设置',
    plugins: '插件管理',
    'historical-projects': '历史项目设置',
    'token-management': 'Token 管理',
  }
  return menuMap[activeMenu.value] || '系统设置'
})

// 日志图标配置
const { iconConfig, getIcon, updateIcon, resetToDefault } = useLogIconConfig()
const showIconSelectorDialog = ref(false)
const editingAction = ref<LogActionType | null>(null)
const selectedIcon = ref<keyof typeof availableIcons | null>(null)
const iconSearchKeyword = ref('')

const editingActionName = computed(() => {
  if (!editingAction.value) return ''
  return logActionNames[editingAction.value]
})

const filteredIcons = computed(() => {
  if (!iconSearchKeyword.value) return iconNames
  const keyword = iconSearchKeyword.value.toLowerCase()
  return iconNames.filter(name => name.toLowerCase().includes(keyword))
})

const getLogIcon = (action: LogActionType) => {
  return getIcon(action)
}

const currentIconName = (action: LogActionType): string => {
  return iconConfig.value[action] || 'InfoFilled'
}

const showIconSelector = (action: LogActionType) => {
  editingAction.value = action
  selectedIcon.value = iconConfig.value[action]
  iconSearchKeyword.value = ''
  showIconSelectorDialog.value = true
}

const selectIcon = (iconName: keyof typeof availableIcons) => {
  selectedIcon.value = iconName
}

const confirmIconSelection = () => {
  if (!editingAction.value || !selectedIcon.value) return
  updateIcon(editingAction.value, selectedIcon.value)
  ElMessage.success('图标设置已保存')
  showIconSelectorDialog.value = false
}

const resetLogIcons = () => {
  ElMessageBox.confirm(
    '确定要重置所有日志图标为默认配置吗？',
    '确认重置',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    resetToDefault()
    ElMessage.success('已重置为默认配置')
  }).catch(() => {})
}

const handleMenuSelect = (index: string) => {
  activeMenu.value = index
}

const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadTemplates = async () => {
  try {
    // 确保默认模板存在
    await stepTemplateApi.ensureDefault()
    templates.value = await stepTemplateApi.list()
  } catch (error) {
    ElMessage.error('加载模板列表失败')
  }
}

// 处理模板操作
const handleTemplateAction = async (command: string, template: StepTemplate) => {
  switch (command) {
    case 'view':
      viewingTemplate.value = template
      showViewDialog.value = true
      break
    case 'copy':
      await copyTemplate(template)
      break
    case 'edit':
      if (!template.is_default) {
        editTemplate(template)
      } else {
        ElMessage.warning('默认模板不可编辑，请复制后编辑')
      }
      break
    case 'rename':
      await renameTemplate(template)
      break
    case 'delete':
      await deleteTemplate(template)
      break
  }
}

const editTemplate = (template: StepTemplate) => {
  if (template.is_default) {
    ElMessage.warning('默认模板不可编辑，请复制后编辑')
    return
  }
  editingTemplate.value = template
  showCreateTemplateDialog.value = true
}

// 复制模板
const copyTemplate = async (template: StepTemplate) => {
  try {
    const copyData = {
      name: `${template.name} - 副本`,
      description: template.description || '',
      steps: [...template.steps]
    }
    
    // 检查名称是否已存在，如果存在则添加序号
    let finalName = copyData.name
    let counter = 1
    while (templates.value.some(t => t.name === finalName)) {
      finalName = `${template.name} - 副本${counter}`
      counter++
    }
    copyData.name = finalName
    
    await stepTemplateApi.create(copyData)
    ElMessage.success('模板复制成功')
    await loadTemplates()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '复制模板失败')
  }
}

// 重命名模板
const renameTemplate = async (template: StepTemplate) => {
  renamingTemplate.value = template
  newTemplateName.value = template.name
  showRenameDialog.value = true
}

const confirmRename = async () => {
  if (!renamingTemplate.value || !newTemplateName.value.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }
  
  // 检查名称是否已存在
  if (templates.value.some(t => t.id !== renamingTemplate.value!.id && t.name === newTemplateName.value.trim())) {
    ElMessage.warning('模板名称已存在')
    return
  }
  
  try {
    await stepTemplateApi.update(renamingTemplate.value.id, {
      name: newTemplateName.value.trim()
    })
    ElMessage.success('重命名成功')
    showRenameDialog.value = false
    renamingTemplate.value = null
    newTemplateName.value = ''
    await loadTemplates()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '重命名失败')
  }
}

const deleteTemplate = async (template: StepTemplate) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板"${template.name}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await stepTemplateApi.delete(template.id)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleTemplateSuccess = () => {
  showCreateTemplateDialog.value = false
  editingTemplate.value = null
  loadTemplates()
}

// 历史项目设置
const loadingSettings = ref(false)
const savingSettings = ref(false)
const historicalProjectSettings = ref<Array<{
  key: string
  name: string
  description: string
  value: boolean
}>>([
  {
    key: 'enable_attachment_management',
    name: '附件管理',
    description: '允许对历史项目进行附件上传、下载、删除等操作',
    value: false
  },
  {
    key: 'enable_todo_management',
    name: '待办管理',
    description: '允许为历史项目创建和管理待办事项',
    value: false
  },
  {
    key: 'enable_log_management',
    name: '日志管理',
    description: '允许查看和管理历史项目的操作日志',
    value: false
  },
  {
    key: 'enable_part_management',
    name: '配件管理',
    description: '允许为历史项目管理配件清单',
    value: false
  },
])

const loadHistoricalProjectSettings = async () => {
  loadingSettings.value = true
  try {
    const settings = await systemSettingsApi.list()
    const settingsMap = new Map(settings.map(s => [s.key, s.value]))
    
    historicalProjectSettings.value.forEach(setting => {
      if (settingsMap.has(setting.key)) {
        setting.value = settingsMap.get(setting.key)!
      }
    })
  } catch (error) {
    console.error('加载历史项目设置失败:', error)
    ElMessage.error('加载设置失败')
  } finally {
    loadingSettings.value = false
  }
}

const handleSettingChange = async (key: string, value: boolean) => {
  savingSettings.value = true
  try {
    await systemSettingsApi.update(key, { value })
    ElMessage.success('设置已保存')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存设置失败')
    // 恢复原值
    const setting = historicalProjectSettings.value.find(s => s.key === key)
    if (setting) {
      setting.value = !value
    }
  } finally {
    savingSettings.value = false
  }
}

onMounted(() => {
  loadTemplates()
  if (activeMenu.value === 'historical-projects') {
    loadHistoricalProjectSettings()
  }
})

// 获取设置图标
const getSettingIcon = (key: string) => {
  const iconMap: Record<string, any> = {
    'enable_attachment_management': Paperclip,
    'enable_todo_management': List,
    'enable_log_management': DocumentAdd,
    'enable_part_management': Grid,
  }
  return iconMap[key] || Setting
}

// Token 管理
const loadingDevices = ref(false)
const loadingLogs = ref(false)
const loggingOutAll = ref(false)
const revokingDeviceId = ref<number | null>(null)
const activeDevices = ref<RefreshTokenInfo[]>([])
const loginLogs = ref<LoginLog[]>([])

// Token 持续时间设置
const loadingTokenDuration = ref(false)
const savingTokenDuration = ref(false)
const tokenDurationSettings = ref({
  access_token_expire_minutes: 15,
  refresh_token_expire_days: 30
})

// 加载 Token 持续时间设置
const loadTokenDuration = async () => {
  loadingTokenDuration.value = true
  try {
    const settings = await systemSettingsApi.getTokenDuration()
    tokenDurationSettings.value = {
      access_token_expire_minutes: settings.access_token_expire_minutes,
      refresh_token_expire_days: settings.refresh_token_expire_days
    }
  } catch (error: any) {
    console.error('加载 Token 持续时间设置失败:', error)
    if (error.response?.status !== 404) {
      ElMessage.error('加载设置失败')
    }
  } finally {
    loadingTokenDuration.value = false
  }
}

// 保存 Token 持续时间设置
const saveTokenDuration = async () => {
  savingTokenDuration.value = true
  try {
    await systemSettingsApi.updateTokenDuration({
      access_token_expire_minutes: tokenDurationSettings.value.access_token_expire_minutes,
      refresh_token_expire_days: tokenDurationSettings.value.refresh_token_expire_days
    })
    ElMessage.success('Token 持续时间设置已保存')
  } catch (error: any) {
    console.error('保存 Token 持续时间设置失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存设置失败')
  } finally {
    savingTokenDuration.value = false
  }
}

// 获取设备名称
const getDeviceName = (device: RefreshTokenInfo) => {
  if (device.device_info) {
    return device.device_info
  }
  // 如果没有设备信息，根据 IP 或其他信息生成名称
  if (device.ip_address) {
    return `设备 (${device.ip_address})`
  }
  return '未知设备'
}

// 判断是否为当前设备
const isCurrentDevice = (device: RefreshTokenInfo) => {
  // 这里可以根据实际情况判断，比如比较 token 或 IP
  // 简化处理：假设最新的设备是当前设备
  return activeDevices.value.length > 0 && device.id === activeDevices.value[0].id && !device.is_revoked
}

// 加载设备列表
const loadDevices = async () => {
  // 检查用户是否已登录
  const userStore = useUserStore()
  if (!userStore.isAuthenticated || !userStore.token) {
    console.warn('[Token Management] User not authenticated, skipping device load')
    return
  }
  
  loadingDevices.value = true
  try {
    console.log('[Token Management] Loading devices, token exists:', !!userStore.token)
    const devices = await authApi.getRefreshTokens()
    activeDevices.value = devices
  } catch (error: any) {
    console.error('加载设备列表失败:', error)
    // 401 错误时不跳转，只显示警告（可能是 token 过期，但其他功能可能还能用）
    if (error.response?.status === 401) {
      console.warn('[Token Management] Devices API returned 401, but continuing...')
      // 不显示错误消息，也不跳转，让用户继续使用其他功能
      // 如果真的是认证问题，其他 API 也会失败，request.ts 的拦截器会处理
    } else {
      ElMessage.warning('加载设备列表失败，但不影响其他功能')
    }
  } finally {
    loadingDevices.value = false
  }
}

// 加载登录日志
const loadLoginLogs = async () => {
  // 检查用户是否已登录
  const userStore = useUserStore()
  if (!userStore.isAuthenticated || !userStore.token) {
    console.warn('[Token Management] User not authenticated, skipping login logs load')
    return
  }
  
  loadingLogs.value = true
  try {
    console.log('[Token Management] Loading login logs, token exists:', !!userStore.token)
    const logs = await authApi.getLoginLogs(50)
    loginLogs.value = logs
  } catch (error: any) {
    console.error('加载登录日志失败:', error)
    // 401 错误时不跳转，只显示警告（可能是 token 过期，但其他功能可能还能用）
    if (error.response?.status === 401) {
      console.warn('[Token Management] Login logs API returned 401, but continuing...')
      // 不显示错误消息，也不跳转，让用户继续使用其他功能
      // 如果真的是认证问题，其他 API 也会失败，request.ts 的拦截器会处理
    } else {
      ElMessage.warning('加载登录日志失败，但不影响其他功能')
    }
  } finally {
    loadingLogs.value = false
  }
}

// 撤销设备
const handleRevokeDevice = async (tokenId: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要撤销此设备的访问权限吗？',
      '确认撤销',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    revokingDeviceId.value = tokenId
    await authApi.revokeRefreshToken(tokenId)
    ElMessage.success('设备已撤销')
    await loadDevices()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '撤销设备失败')
    }
  } finally {
    revokingDeviceId.value = null
  }
}

// 登出所有设备
const handleLogoutAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要登出所有设备吗？这将撤销所有刷新令牌，您需要重新登录。',
      '确认登出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    loggingOutAll.value = true
    await authApi.logoutAll()
    ElMessage.success('已登出所有设备')
    // 登出后跳转到登录页
    const { useUserStore } = await import('@/stores/user')
    const userStore = useUserStore()
    userStore.logout()
    window.location.href = '/login'
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '登出失败')
    }
  } finally {
    loggingOutAll.value = false
  }
}

// 获取日志状态文本
const getLogStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'success': '登录成功',
    'failed': '登录失败',
    'locked': '账户锁定',
    'blocked': '账户禁用',
  }
  return statusMap[status] || status
}

// 获取日志状态样式类
const getLogStatusClass = (status: string) => {
  return {
    'log-success': status === 'success',
    'log-failed': status === 'failed' || status === 'locked' || status === 'blocked',
  }
}

// 获取日志状态标签类型
const getLogStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    'success': 'success',
    'failed': 'danger',
    'locked': 'warning',
    'blocked': 'danger',
  }
  return typeMap[status] || 'info'
}

// 监听菜单切换，加载历史项目设置
watch(activeMenu, (newMenu) => {
  if (newMenu === 'historical-projects') {
    loadHistoricalProjectSettings()
  }
  if (newMenu === 'plugins' && projects.value.length === 0) {
    loadProjects()
  }
  if (newMenu === 'token-management') {
    // 顺序加载，避免并发请求导致的问题
    // 先加载 Token 持续时间（这个最重要）
    loadTokenDuration()
    // 然后加载设备列表和登录日志
    loadDevices()
    loadLoginLogs()
  }
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.settings-layout {
  height: 100%;
}

.settings-sidebar {
  margin-bottom: 20px;
}

.sidebar-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.settings-menu {
  border-right: none;
}

.settings-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  border-radius: 6px;
  margin-bottom: 4px;
}

.settings-menu :deep(.el-menu-item.is-active) {
  background: #ecf5ff;
  color: #409eff;
}

.settings-content {
  margin-bottom: 20px;
}

.content-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  min-height: calc(100vh - 100px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.templates-section {
  padding: 20px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.section-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.section-desc {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.templates-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.template-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
}

.template-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
  transform: translateY(-2px);
}

.template-item.is-default {
  border-color: #67c23a;
  background: linear-gradient(to right, #f0f9ff, #fff);
  position: relative;
}

.template-item.is-default::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #67c23a;
  border-radius: 8px 0 0 8px;
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.template-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.template-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.6;
}

.template-steps-preview {
  margin-bottom: 12px;
}

.steps-label {
  font-size: 13px;
  color: #909399;
  margin-right: 8px;
}

.steps-tags {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.step-tag {
  margin: 0;
}

.template-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.template-steps-count {
  font-weight: 500;
  color: #606266;
}

.template-time {
  color: #909399;
}

.template-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.template-detail {
  padding: 10px 0;
}

.detail-item {
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
}

.detail-item.steps-list {
  flex-direction: column;
}

.detail-label {
  font-weight: 600;
  color: #606266;
  min-width: 100px;
  flex-shrink: 0;
}

.detail-value {
  color: #303133;
  flex: 1;
}

.steps-container {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  max-height: 300px;
  overflow-y: auto;
}

.step-detail-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 8px;
  background: #fff;
  border-radius: 4px;
  border-left: 3px solid #409eff;
  transition: all 0.2s;
}

.step-detail-item:hover {
  background: #ecf5ff;
  transform: translateX(4px);
}

.step-detail-item:last-child {
  margin-bottom: 0;
}

.step-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.step-name {
  color: #303133;
  font-size: 14px;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .settings-page {
    padding: 12px;
    min-height: auto;
  }

  .settings-page :deep(.el-card__body) {
    padding: 12px !important;
  }

  .settings-layout {
    margin: 0 !important;
  }

  .settings-layout .el-col {
    padding-left: 0 !important;
    padding-right: 0 !important;
  }

  .settings-sidebar {
    margin-bottom: 12px;
  }

  .sidebar-card :deep(.el-card__body) {
    padding: 8px !important;
  }

  .settings-menu {
    display: flex;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    white-space: nowrap;
    padding: 4px 0;
  }

  .settings-menu :deep(.el-menu-item) {
    display: inline-flex;
    height: 40px;
    line-height: 40px;
    padding: 0 16px;
    margin-bottom: 0;
    margin-right: 4px;
    flex-shrink: 0;
  }

  .settings-menu :deep(.el-menu-item span) {
    font-size: 13px;
  }

  .page-title {
    font-size: 15px;
  }

  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    padding-bottom: 12px;
    margin-bottom: 16px;
  }

  .section-title h3 {
    font-size: 16px;
  }

  .section-desc {
    font-size: 12px;
  }

  .template-item {
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }

  .template-header {
    margin-bottom: 8px;
  }

  .template-name {
    font-size: 14px;
  }

  .template-description {
    font-size: 13px;
    margin-bottom: 8px;
  }

  .template-steps-preview {
    margin-bottom: 8px;
  }

  .template-meta {
    flex-wrap: wrap;
    gap: 8px;
    font-size: 11px;
  }

  .template-actions {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 4px;
  }

  .template-actions .el-button {
    padding: 5px 10px;
    font-size: 12px;
  }

  /* 插件设置移动端优化 */
  .plugin-info {
    padding: 12px;
  }

  .plugin-header {
    flex-wrap: wrap;
    gap: 8px;
  }

  .plugin-icon {
    font-size: 20px;
  }

  .plugin-name {
    font-size: 15px;
  }

  .plugin-description {
    font-size: 12px;
    margin-bottom: 12px;
  }

  .plugin-status-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 10px 12px;
  }

  .status-actions {
    width: 100%;
    justify-content: stretch;
  }

  .status-actions .el-button {
    flex: 1;
  }

  .projects-container {
    max-height: 300px;
  }

  .project-item {
    padding: 10px 12px;
  }

  .project-title {
    font-size: 13px;
  }

  .project-meta {
    font-size: 11px;
    flex-wrap: wrap;
  }

  .setting-tip {
    font-size: 11px;
    padding: 8px 10px;
  }

  .plugin-features {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .feature-item {
    font-size: 12px;
  }

  /* Token管理移动端优化 */
  .token-duration-content {
    gap: 16px;
  }

  .duration-label {
    font-size: 13px;
  }

  .duration-hint {
    font-size: 11px;
  }

  .duration-input-group {
    flex-wrap: wrap;
  }

  .duration-input-group .el-input-number {
    width: 100% !important;
  }

  .duration-actions {
    flex-direction: column;
  }

  .duration-actions .el-button {
    width: 100%;
  }

  .duration-tip {
    font-size: 12px;
    padding: 10px;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .info-label {
    min-width: auto;
    font-size: 12px;
  }

  .info-value {
    font-size: 13px;
  }

  /* 对话框优化 */
  .settings-page :deep(.el-dialog) {
    width: 96% !important;
    margin-top: 3vh !important;
  }

  .settings-page :deep(.el-dialog__header) {
    padding: 12px !important;
  }

  .settings-page :deep(.el-dialog__body) {
    padding: 12px !important;
    max-height: 70vh;
  }

  .settings-page :deep(.el-dialog__footer) {
    padding: 12px !important;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .settings-page :deep(.el-dialog__footer .el-button) {
    width: 100%;
    margin: 0;
  }

  /* 图标选择器 */
  .icon-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    max-height: 250px;
  }

  .icon-option {
    padding: 12px 8px;
  }

  .icon-label {
    font-size: 10px;
  }
}

@media (max-width: 480px) {
  .settings-page {
    padding: 8px;
  }

  .settings-menu :deep(.el-menu-item) {
    padding: 0 12px;
  }

  .settings-menu :deep(.el-menu-item span) {
    font-size: 12px;
  }

  .section-title h3 {
    font-size: 15px;
  }

  .template-item {
    padding: 10px;
  }

  .projects-container {
    max-height: 250px;
  }
}

.setting-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #ffffff;
}

.setting-item-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.setting-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 8px;
  padding: 12px;
  background-color: #f0f9ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
}

.setting-tip .el-icon {
  color: #409eff;
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}

.log-icons-settings-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.log-icons-settings-body {
  padding: 20px 0;
}

.log-icons-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.log-icon-item {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s;
}

.log-icon-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.icon-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.icon-item-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.action-code {
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}

.icon-item-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.preview-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.preview-icon {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
}

.icon-name {
  font-size: 14px;
  color: #606266;
  font-family: monospace;
}

.icon-selector {
  padding: 10px 0;
}

.icon-search {
  margin-bottom: 20px;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fafafa;
}

.icon-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  border: 2px solid #ebeef5;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
  gap: 8px;
}

.icon-option:hover {
  border-color: #409eff;
  background: #ecf5ff;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.icon-option.is-selected {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.icon-label {
  font-size: 12px;
  color: #606266;
  text-align: center;
  word-break: break-all;
}

.plugins-settings-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.plugins-settings-body {
  padding: 20px 0;
}

.plugin-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.plugin-item {
  padding: 0;
}

.plugin-info {
  padding: 20px;
}

.plugin-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.plugin-icon {
  font-size: 24px;
  color: #409eff;
}

.plugin-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.plugin-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 20px;
}

.plugin-settings {
  margin: 20px 0;
}

.plugin-status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.status-actions {
  display: flex;
  gap: 8px;
}

.plugin-projects-list {
  margin-top: 16px;
}

.projects-search {
  margin-bottom: 16px;
}

.projects-container {
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fff;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
}

.project-item:last-child {
  border-bottom: none;
}

.project-item:hover {
  background: #f5f7fa;
}

.project-item.is-enabled {
  background: #ecf5ff;
  border-left: 3px solid #409eff;
}

.project-item.is-enabled:hover {
  background: #d9ecff;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.project-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.meta-item {
  flex-shrink: 0;
}

.meta-divider {
  color: #dcdfe6;
}

.setting-tip {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  margin-top: 12px;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 4px;
}

.setting-tip .el-icon {
  color: #909399;
  font-size: 14px;
  margin-top: 2px;
  flex-shrink: 0;
}

.plugin-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.feature-item .el-icon {
  color: #67c23a;
  font-size: 16px;
}

/* 历史项目设置样式 */
.historical-projects-settings-section {
  padding: 20px 0;
}

.historical-projects-settings-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.historical-settings-card {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.historical-settings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px;
}

.historical-setting-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 24px;
  background: #ffffff;
  border: 2px solid #ebeef5;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.historical-setting-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #dcdfe6;
  transition: all 0.3s;
}

.historical-setting-item.is-enabled {
  border-color: #67c23a;
  background: linear-gradient(to right, #f0f9ff 0%, #ffffff 8%);
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.12);
}

.historical-setting-item.is-enabled::before {
  background: linear-gradient(180deg, #67c23a 0%, #85ce61 100%);
  width: 4px;
}

.historical-setting-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  border-color: #409eff;
}

.historical-setting-item.is-enabled:hover {
  box-shadow: 0 6px 20px rgba(103, 194, 58, 0.2);
  border-color: #67c23a;
}

.setting-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  flex-shrink: 0;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.historical-setting-item.is-enabled .setting-icon-wrapper {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.historical-setting-item:hover .setting-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.setting-icon {
  color: #ffffff;
}

.setting-content {
  flex: 1;
  min-width: 0;
}

.setting-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 16px;
}

.setting-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.setting-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
}

.setting-status-tag {
  flex-shrink: 0;
  font-weight: 500;
}

.setting-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.setting-features {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.feature-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  background: #f0f9ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

.feature-badge .el-icon {
  font-size: 14px;
}

.feature-badge.disabled {
  background: #f5f7fa;
  color: #909399;
  border-color: #e4e7ed;
}

.settings-tip-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f4ff 100%);
  border: 1px solid #b3d8ff;
  border-radius: 12px;
  border-left: 4px solid #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.tip-icon {
  font-size: 24px;
  color: #409eff;
  flex-shrink: 0;
  margin-top: 2px;
}

.tip-content {
  flex: 1;
}

.tip-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.tip-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .historical-setting-item {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .setting-icon-wrapper {
    align-self: center;
  }

  .setting-header-row {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .setting-title-group {
    flex-direction: column;
    align-items: flex-start;
  }

  .settings-tip-card {
    flex-direction: column;
    gap: 12px;
  }
}

/* Token 管理样式 */
.token-management-section {
  padding: 20px 0;
}

.token-management-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.token-info-card,
.token-duration-card,
.devices-card,
.login-logs-card {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.token-duration-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 8px 0;
}

.duration-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.duration-label-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.duration-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.duration-hint {
  font-size: 12px;
  color: #909399;
}

.duration-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.duration-unit {
  font-size: 14px;
  color: #606266;
}

.duration-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
}

.duration-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: #f0f9ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.duration-tip .el-icon {
  color: #409eff;
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.token-info-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  min-width: 140px;
}

.info-value {
  font-size: 14px;
  color: #303133;
}

.devices-list,
.login-logs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px 0;
}

.device-item,
.log-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #ffffff;
  transition: all 0.3s;
}

.device-item:hover,
.log-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.device-item.is-current {
  border-color: #67c23a;
  background: linear-gradient(to right, #f0f9ff 0%, #ffffff 5%);
}

.device-icon,
.log-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #f5f7fa;
  flex-shrink: 0;
}

.device-item.is-current .device-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: #ffffff;
}

.log-success .log-icon {
  background: #f0f9ff;
  color: #67c23a;
}

.log-failed .log-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.device-info,
.log-info {
  flex: 1;
  min-width: 0;
}

.device-header,
.log-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.device-name,
.log-status {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.device-details,
.log-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
}

.detail-row.error {
  color: #f56c6c;
}

.detail-row .el-icon {
  font-size: 14px;
}

.device-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .device-item,
  .log-item {
    flex-direction: column;
    gap: 12px;
  }

  .device-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>

