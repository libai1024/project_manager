/**
 * 日期工具函数
 *
 * 提供统一的日期处理函数，消除代码重复。
 * 符合国内互联网企业级规范。
 */

/**
 * 格式化日期
 * @param date 日期字符串或Date对象
 * @param format 格式化模板，默认 'YYYY-MM-DD'
 * @returns 格式化后的日期字符串
 *
 * @example
 * formatDate('2024-01-15') // '2024-01-15'
 * formatDate(new Date(), 'YYYY年MM月DD日') // '2024年01月15日'
 */
export function formatDate(
  date: string | Date | null | undefined,
  format: string = 'YYYY-MM-DD'
): string {
  if (!date) return ''

  const d = typeof date === 'string' ? new Date(date) : date

  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期时间
 * @param date 日期字符串或Date对象
 * @param format 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns 格式化后的日期时间字符串
 *
 * @example
 * formatDateTime('2024-01-15T10:30:00') // '2024-01-15 10:30:00'
 */
export function formatDateTime(
  date: string | Date | null | undefined,
  format: string = 'YYYY-MM-DD HH:mm:ss'
): string {
  return formatDate(date, format)
}

/**
 * 格式化为简短日期（中文格式）
 * @param date 日期字符串或Date对象
 * @returns 格式化后的日期字符串
 *
 * @example
 * formatDateCN('2024-01-15') // '2024年1月15日'
 */
export function formatDateCN(date: string | Date | null | undefined): string {
  if (!date) return ''

  const d = typeof date === 'string' ? new Date(date) : date

  if (isNaN(d.getTime())) return ''

  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

/**
 * 获取相对时间描述
 * @param date 日期字符串或Date对象
 * @returns 相对时间描述
 *
 * @example
 * getRelativeTime('2024-01-15') // '今天' / '昨天' / '3天前' / '2024-01-15'
 */
export function getRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return ''

  const d = typeof date === 'string' ? new Date(date) : date

  if (isNaN(d.getTime())) return ''

  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const target = new Date(d.getFullYear(), d.getMonth(), d.getDate())
  const diffDays = Math.floor((today.getTime() - target.getTime()) / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '昨天'
  if (diffDays === 2) return '前天'
  if (diffDays < 7) return `${diffDays}天前`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)}个月前`

  return formatDate(d)
}

/**
 * 获取友好时间描述
 * @param date 日期字符串或Date对象
 * @returns 友好时间描述
 *
 * @example
 * getFriendlyTime('2024-01-15T10:30:00') // '刚刚' / '5分钟前' / '今天 10:30' / '2024-01-15'
 */
export function getFriendlyTime(date: string | Date | null | undefined): string {
  if (!date) return ''

  const d = typeof date === 'string' ? new Date(date) : date

  if (isNaN(d.getTime())) return ''

  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)

  if (diffSeconds < 60) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`

  const isToday = formatDate(d) === formatDate(now)
  if (isToday) return `今天 ${formatDate(d, 'HH:mm')}`

  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (formatDate(d) === formatDate(yesterday)) {
    return `昨天 ${formatDate(d, 'HH:mm')}`
  }

  if (diffHours < 24 * 7) return getRelativeTime(d)

  return formatDate(d)
}

/**
 * 检查日期是否过期
 * @param date 日期字符串或Date对象
 * @returns 是否过期
 */
export function isExpired(date: string | Date | null | undefined): boolean {
  if (!date) return false

  const d = typeof date === 'string' ? new Date(date) : date

  if (isNaN(d.getTime())) return false

  return d.getTime() < Date.now()
}

/**
 * 检查日期是否是今天
 * @param date 日期字符串或Date对象
 * @returns 是否是今天
 */
export function isToday(date: string | Date | null | undefined): boolean {
  if (!date) return false

  const d = typeof date === 'string' ? new Date(date) : date

  if (isNaN(d.getTime())) return false

  return formatDate(d) === formatDate(new Date())
}

/**
 * 获取月份范围
 * @param date 日期字符串或Date对象
 * @returns 月份开始和结束日期
 */
export function getMonthRange(date: string | Date = new Date()): { start: Date; end: Date } {
  const d = typeof date === 'string' ? new Date(date) : date

  const start = new Date(d.getFullYear(), d.getMonth(), 1)
  const end = new Date(d.getFullYear(), d.getMonth() + 1, 0)

  return { start, end }
}

/**
 * 获取本周范围
 * @param date 日期字符串或Date对象
 * @returns 本周开始和结束日期
 */
export function getWeekRange(date: string | Date = new Date()): { start: Date; end: Date } {
  const d = typeof date === 'string' ? new Date(date) : new Date(date)

  const day = d.getDay() || 7 // 将周日的0转换为7

  const start = new Date(d)
  start.setDate(d.getDate() - day + 1)
  start.setHours(0, 0, 0, 0)

  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  end.setHours(23, 59, 59, 999)

  return { start, end }
}
