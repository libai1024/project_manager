/**
 * 文件类型图标工具函数
 * 根据文件扩展名返回对应的 Element Plus 图标组件名称
 */
import {
  Document,
  Picture,
  VideoPlay,
  Headset,
  Folder,
} from '@element-plus/icons-vue'

// PDF 图标需要自己实现或使用自定义SVG
// 这里我们使用 Document 作为基础，后续可以通过 CSS 或自定义组件来区分

export type FileIconType = 'pdf' | 'word' | 'excel' | 'ppt' | 'wps' | 'archive' | 'image' | 'video' | 'audio' | 'text' | 'code' | 'default'

/**
 * 根据文件名获取文件类型图标
 */
export function getFileIcon(fileName: string): string {
  const ext = fileName.toLowerCase().split('.').pop() || ''

  // PDF
  if (ext === 'pdf') return 'pdf'

  // Word (包括 WPS 和 OpenDocument)
  if (['doc', 'docx', 'wps', 'wpt', 'odt', 'rtf'].includes(ext)) return 'word'

  // Excel (包括 WPS 和 OpenDocument)
  if (['xls', 'xlsx', 'csv', 'et', 'ods'].includes(ext)) return 'excel'

  // PowerPoint (包括 WPS 和 OpenDocument)
  if (['ppt', 'pptx', 'dps', 'wpp', 'odp'].includes(ext)) return 'ppt'

  // 压缩包
  if (['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'zipx'].includes(ext)) return 'archive'

  // 图片 (包括 HEIC/HEIF 和 RAW 格式)
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'tiff', 'tif', 'heic', 'heif', 'raw', 'cr2', 'nef', 'dng', 'psd'].includes(ext)) return 'image'

  // 视频 (主流格式)
  if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', 'm4v', '3gp', 'mpeg', 'mpg', 'ogv', 'ts', 'mts', 'm2ts', 'vob'].includes(ext)) return 'video'

  // 音频 (主流格式)
  if (['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a', 'wma', 'aiff', 'aif', 'au', 'opus', 'oga', 'ape', 'mid', 'midi'].includes(ext)) return 'audio'

  // 文本
  if (['txt', 'md', 'log', 'ini', 'conf', 'cfg'].includes(ext)) return 'text'

  // 代码文件
  if (['js', 'jsx', 'ts', 'tsx', 'vue', 'html', 'css', 'scss', 'less', 'py', 'java', 'cpp', 'c', 'h', 'go', 'rs', 'php', 'rb', 'sh', 'bat', 'cmd', 'ps1', 'yaml', 'yml', 'json', 'xml', 'swift', 'kt', 'scala', 'lua', 'sql'].includes(ext)) return 'code'

  return 'default'
}

/**
 * 获取文件类型图标的颜色
 */
export function getFileIconColor(fileType: FileIconType): string {
  const colorMap: Record<FileIconType, string> = {
    pdf: '#dc3545',      // 红色
    word: '#2b579a',     // 蓝色
    excel: '#1d6f42',    // 绿色
    ppt: '#d04423',      // 橙色
    wps: '#0066cc',      // 蓝色
    archive: '#ff9800',  // 橙色
    image: '#e91e63',    // 粉色
    video: '#9c27b0',    // 紫色
    audio: '#00bcd4',    // 青色
    text: '#607d8b',     // 蓝灰色
    code: '#673ab7',     // 深紫色
    default: '#409eff',  // Element Plus 默认蓝色
  }
  return colorMap[fileType] || colorMap.default
}

/**
 * 获取文件类型显示名称
 */
export function getFileTypeName(fileType: FileIconType): string {
  const nameMap: Record<FileIconType, string> = {
    pdf: 'PDF',
    word: 'Word',
    excel: 'Excel',
    ppt: 'PowerPoint',
    wps: 'WPS',
    archive: '压缩包',
    image: '图片',
    video: '视频',
    audio: '音频',
    text: '文本',
    code: '代码',
    default: '文件',
  }
  return nameMap[fileType] || nameMap.default
}

