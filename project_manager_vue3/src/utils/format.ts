/**
 * 格式化工具函数
 *
 * 提供统一的数据格式化函数。
 * 符合国内互联网企业级规范。
 */

/**
 * 格式化金额（分转元）
 * @param amount 金额（分）
 * @param decimals 小数位数
 * @returns 格式化后的金额字符串
 *
 * @example
 * formatMoney(12345) // '123.45'
 */
export function formatMoney(amount: number | string | null | undefined, decimals: number = 2): string {
  if (amount === null || amount === undefined || amount === '') return '0.00'

  const num = typeof amount === 'string' ? parseFloat(amount) : amount

  if (isNaN(num)) return '0.00'

  return (num / 100).toFixed(decimals)
}

/**
 * 格式化金额（元，带千分位）
 * @param amount 金额（元）
 * @param decimals 小数位数
 * @returns 格式化后的金额字符串
 *
 * @example
 * formatCurrency(12345.67) // '12,345.67'
 */
export function formatCurrency(
  amount: number | string | null | undefined,
  decimals: number = 2
): string {
  if (amount === null || amount === undefined || amount === '') return '0.00'

  const num = typeof amount === 'string' ? parseFloat(amount) : amount

  if (isNaN(num)) return '0.00'

  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

/**
 * 格式化金额（带货币符号）
 * @param amount 金额（元）
 * @param symbol 货币符号
 * @returns 格式化后的金额字符串
 *
 * @example
 * formatPrice(12345.67) // '¥12,345.67'
 */
export function formatPrice(
  amount: number | string | null | undefined,
  symbol: string = '¥'
): string {
  return `${symbol}${formatCurrency(amount)}`
}

/**
 * 格式化百分比
 * @param value 数值
 * @param decimals 小数位数
 * @returns 格式化后的百分比字符串
 *
 * @example
 * formatPercent(0.1234) // '12.34%'
 */
export function formatPercent(
  value: number | string | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined || value === '') return '0%'

  const num = typeof value === 'string' ? parseFloat(value) : value

  if (isNaN(num)) return '0%'

  return `${(num * 100).toFixed(decimals)}%`
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @param decimals 小数位数
 * @returns 格式化后的文件大小字符串
 *
 * @example
 * formatFileSize(1024) // '1.00 KB'
 * formatFileSize(1048576) // '1.00 MB'
 */
export function formatFileSize(
  bytes: number | string | null | undefined,
  decimals: number = 2
): string {
  if (bytes === null || bytes === undefined || bytes === '') return '0 B'

  const num = typeof bytes === 'string' ? parseInt(bytes, 10) : bytes

  if (isNaN(num) || num === 0) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  const k = 1024
  const i = Math.floor(Math.log(num) / Math.log(k))

  return `${(num / Math.pow(k, i)).toFixed(decimals)} ${units[i]}`
}

/**
 * 格式化数字（带千分位）
 * @param num 数字
 * @returns 格式化后的数字字符串
 *
 * @example
 * formatNumber(1234567) // '1,234,567'
 */
export function formatNumber(num: number | string | null | undefined): string {
  if (num === null || num === undefined || num === '') return '0'

  const n = typeof num === 'string' ? parseFloat(num) : num

  if (isNaN(n)) return '0'

  return n.toLocaleString('zh-CN')
}

/**
 * 格式化手机号（隐藏中间4位）
 * @param phone 手机号
 * @returns 格式化后的手机号
 *
 * @example
 * formatPhone('13812345678') // '138****5678'
 */
export function formatPhone(phone: string | null | undefined): string {
  if (!phone) return ''

  if (phone.length !== 11) return phone

  return `${phone.slice(0, 3)}****${phone.slice(7)}`
}

/**
 * 格式化邮箱（隐藏部分字符）
 * @param email 邮箱
 * @returns 格式化后的邮箱
 *
 * @example
 * formatEmail('test@example.com') // 't***@example.com'
 */
export function formatEmail(email: string | null | undefined): string {
  if (!email) return ''

  const atIndex = email.indexOf('@')
  if (atIndex < 1) return email

  const name = email.slice(0, atIndex)
  const domain = email.slice(atIndex)

  const maskedName = name.length > 1
    ? `${name[0]}${'*'.repeat(Math.min(name.length - 1, 3))}`
    : name

  return `${maskedName}${domain}`
}

/**
 * 格式化银行卡号（每4位一组）
 * @param cardNumber 银行卡号
 * @returns 格式化后的银行卡号
 *
 * @example
 * formatBankCard('6222021234567890123') // '6222 0212 3456 7890 123'
 */
export function formatBankCard(cardNumber: string | null | undefined): string {
  if (!cardNumber) return ''

  return cardNumber.replace(/\s/g, '').replace(/(\d{4})/g, '$1 ').trim()
}

/**
 * 截断字符串
 * @param str 字符串
 * @param maxLength 最大长度
 * @param suffix 后缀
 * @returns 截断后的字符串
 *
 * @example
 * truncate('这是一个很长的字符串', 5) // '这是一个很...'
 */
export function truncate(
  str: string | null | undefined,
  maxLength: number,
  suffix: string = '...'
): string {
  if (!str) return ''

  if (str.length <= maxLength) return str

  return str.slice(0, maxLength - suffix.length) + suffix
}

/**
 * 首字母大写
 * @param str 字符串
 * @returns 首字母大写的字符串
 */
export function capitalize(str: string | null | undefined): string {
  if (!str) return ''

  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * 驼峰转短横线
 * @param str 字符串
 * @returns 短横线格式字符串
 *
 * @example
 * camelToKebab('helloWorld') // 'hello-world'
 */
export function camelToKebab(str: string): string {
  return str.replace(/([A-Z])/g, '-$1').toLowerCase()
}

/**
 * 短横线转驼峰
 * @param str 字符串
 * @returns 驼峰格式字符串
 *
 * @example
 * kebabToCamel('hello-world') // 'helloWorld'
 */
export function kebabToCamel(str: string): string {
  return str.replace(/-([a-z])/g, (_, char) => char.toUpperCase())
}
