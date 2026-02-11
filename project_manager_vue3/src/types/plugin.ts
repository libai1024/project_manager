/**
 * 插件系统类型定义
 */

// 毕设文件类型
export type GraduationFileType = 
  | 'task_book'           // 任务书
  | 'opening_report'      // 开题报告
  | 'midterm_report'      // 中期报告
  | 'demo_video'          // 演示视频
  | 'thesis_draft'        // 毕业论文（初稿）
  | 'thesis_final'        // 毕业论文（终稿）
  | 'defense_ppt'         // 答辩PPT
  | 'defense_record'      // 答辩辅导记录
  | 'guidance_record'     // 指导记录

// 毕设文件类型配置
export const graduationFileTypes: Record<GraduationFileType, {
  label: string
  icon: string
  accept?: string  // 文件类型限制
}> = {
  task_book: {
    label: '任务书',
    icon: 'Document',
    accept: '.doc,.docx,.pdf'
  },
  opening_report: {
    label: '开题报告',
    icon: 'Document',
    accept: '.doc,.docx,.pdf'
  },
  midterm_report: {
    label: '中期报告',
    icon: 'Document',
    accept: '.doc,.docx,.pdf'
  },
  demo_video: {
    label: '演示视频',
    icon: 'VideoPlay',
    accept: '.mp4,.avi,.mov,.wmv'
  },
  thesis_draft: {
    label: '毕业论文（初稿）',
    icon: 'Document',
    accept: '.doc,.docx,.pdf'
  },
  thesis_final: {
    label: '毕业论文（终稿）',
    icon: 'Document',
    accept: '.doc,.docx,.pdf'
  },
  defense_ppt: {
    label: '答辩PPT',
    icon: 'Document',
    accept: '.ppt,.pptx'
  },
  defense_record: {
    label: '答辩辅导记录',
    icon: 'Document',
    accept: '.doc,.docx,.pdf,.txt'
  },
  guidance_record: {
    label: '指导记录',
    icon: 'Document',
    accept: '.doc,.docx,.pdf,.txt'
  }
}

// 附件标记
export interface AttachmentTag {
  attachment_id: number
  plugin_id: string
  tag_type: string
  tag_value: string
}

// 插件接口
export interface Plugin {
  id: string
  name: string
  description: string
  enabled: boolean
  component?: any
}

