/**
 * 验证工具函数
 *
 * 提供统一的数据验证函数。
 * 符合国内互联网企业级规范。
 */

/**
 * 验证邮箱
 * @param email 邮箱地址
 * @returns 是否有效
 */
export function isValidEmail(email: string | null | undefined): boolean {
  if (!email) return false

  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

/**
 * 验证手机号（中国大陆）
 * @param phone 手机号
 * @returns 是否有效
 */
export function isValidPhone(phone: string | null | undefined): boolean {
  if (!phone) return false

  const re = /^1[3-9]\d{9}$/
  return re.test(phone)
}

/**
 * 验证URL
 * @param url URL地址
 * @returns 是否有效
 */
export function isValidUrl(url: string | null | undefined): boolean {
  if (!url) return false

  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证是否为空
 * @param value 值
 * @returns 是否为空
 */
export function isEmpty(value: unknown): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim().length === 0
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 验证是否非空
 * @param value 值
 * @returns 是否非空
 */
export function isNotEmpty(value: unknown): boolean {
  return !isEmpty(value)
}

/**
 * 验证是否为数字
 * @param value 值
 * @returns 是否为数字
 */
export function isNumber(value: unknown): boolean {
  if (typeof value === 'number') return !isNaN(value)
  if (typeof value === 'string') return !isNaN(parseFloat(value)) && isFinite(parseFloat(value))
  return false
}

/**
 * 验证是否为整数
 * @param value 值
 * @returns 是否为整数
 */
export function isInteger(value: unknown): boolean {
  if (!isNumber(value)) return false
  const num = typeof value === 'string' ? parseFloat(value) : value as number
  return Number.isInteger(num)
}

/**
 * 验证是否为正整数
 * @param value 值
 * @returns 是否为正整数
 */
export function isPositiveInteger(value: unknown): boolean {
  if (!isInteger(value)) return false
  const num = typeof value === 'string' ? parseInt(value, 10) : value as number
  return num > 0
}

/**
 * 验证是否在范围内
 * @param value 值
 * @param min 最小值
 * @param max 最大值
 * @returns 是否在范围内
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}

/**
 * 验证字符串长度
 * @param str 字符串
 * @param min 最小长度
 * @param max 最大长度
 * @returns 是否在范围内
 */
export function isLengthInRange(
  str: string | null | undefined,
  min: number,
  max: number
): boolean {
  if (!str) return min === 0
  return str.length >= min && str.length <= max
}

/**
 * 验证密码强度
 * @param password 密码
 * @returns 强度等级（0-4）
 *
 * 0: 无效
 * 1: 弱
 * 2: 中
 * 3: 强
 * 4: 非常强
 */
export function getPasswordStrength(password: string | null | undefined): number {
  if (!password) return 0

  let strength = 0

  // 长度检查
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++

  // 包含小写字母
  if (/[a-z]/.test(password)) strength++

  // 包含大写字母
  if (/[A-Z]/.test(password)) strength++

  // 包含数字
  if (/\d/.test(password)) strength++

  // 包含特殊字符
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++

  return Math.min(strength, 4)
}

/**
 * 验证密码是否符合要求
 * @param password 密码
 * @param options 选项
 * @returns 是否符合要求
 */
export function isValidPassword(
  password: string | null | undefined,
  options: {
    minLength?: number
    requireUppercase?: boolean
    requireLowercase?: boolean
    requireNumber?: boolean
    requireSpecial?: boolean
  } = {}
): boolean {
  if (!password) return false

  const {
    minLength = 8,
    requireUppercase = true,
    requireLowercase = true,
    requireNumber = true,
    requireSpecial = false
  } = options

  if (password.length < minLength) return false
  if (requireUppercase && !/[A-Z]/.test(password)) return false
  if (requireLowercase && !/[a-z]/.test(password)) return false
  if (requireNumber && !/\d/.test(password)) return false
  if (requireSpecial && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) return false

  return true
}

/**
 * 验证用户名
 * @param username 用户名
 * @param options 选项
 * @returns 是否有效
 */
export function isValidUsername(
  username: string | null | undefined,
  options: {
    minLength?: number
    maxLength?: number
    allowChinese?: boolean
  } = {}
): boolean {
  if (!username) return false

  const {
    minLength = 3,
    maxLength = 20,
    allowChinese = true
  } = options

  if (username.length < minLength || username.length > maxLength) return false

  // 允许字母、数字、下划线，可选中文
  const pattern = allowChinese
    ? /^[\u4e00-\u9fa5a-zA-Z0-9_]+$/
    : /^[a-zA-Z0-9_]+$/

  return pattern.test(username)
}

/**
 * 验证身份证号（中国大陆）
 * @param idCard 身份证号
 * @returns 是否有效
 */
export function isValidIdCard(idCard: string | null | undefined): boolean {
  if (!idCard) return false

  // 15位或18位
  const re = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
  return re.test(idCard)
}

/**
 * 验证文件扩展名
 * @param filename 文件名
 * @param allowedExtensions 允许的扩展名列表
 * @returns 是否允许
 */
export function isValidFileExtension(
  filename: string | null | undefined,
  allowedExtensions: string[]
): boolean {
  if (!filename || !allowedExtensions.length) return false

  const ext = filename.slice(filename.lastIndexOf('.')).toLowerCase()
  return allowedExtensions.map(e => e.toLowerCase()).includes(ext)
}

/**
 * 验证文件大小
 * @param fileSize 文件大小（字节）
 * @param maxSize 最大大小（字节）
 * @returns 是否在限制内
 */
export function isValidFileSize(fileSize: number, maxSize: number): boolean {
  return fileSize > 0 && fileSize <= maxSize
}
