/**
 * 主题配置
 * 导出主题变量供 TypeScript 使用
 */

export const theme = {
  colors: {
    black: '#000000',
    white: '#ffffff',
    gray: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#eeeeee',
      300: '#e0e0e0',
      400: '#bdbdbd',
      500: '#9e9e9e',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
    },
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
  },
  borderRadius: {
    none: '0',
    sm: '2px',
    md: '4px',
    lg: '8px',
    full: '9999px',
  },
  borderWidth: {
    thin: '1px',
    medium: '2px',
    thick: '3px',
  },
  shadows: {
    none: 'none',
    xs: '0 1px 2px rgba(0, 0, 0, 0.05)',
    sm: '0 1px 3px rgba(0, 0, 0, 0.08)',
    md: '0 2px 6px rgba(0, 0, 0, 0.1)',
    lg: '0 4px 12px rgba(0, 0, 0, 0.12)',
  },
  typography: {
    fontFamily: {
      base: "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif",
      mono: "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace",
    },
    fontSize: {
      xs: '12px',
      sm: '14px',
      base: '16px',
      lg: '18px',
      xl: '20px',
      '2xl': '24px',
      '3xl': '30px',
    },
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  transitions: {
    fast: '150ms ease',
    base: '200ms ease',
    slow: '300ms ease',
  },
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
  },
} as const

/**
 * 获取 CSS 变量值
 */
export function getCSSVar(variable: string): string {
  if (typeof window !== 'undefined') {
    return getComputedStyle(document.documentElement).getPropertyValue(variable).trim()
  }
  return ''
}

/**
 * 主题工具函数
 */
export const themeUtils = {
  /**
   * 获取颜色
   */
  color: (name: keyof typeof theme.colors) => {
    return `var(--color-${name})`
  },
  
  /**
   * 获取间距
   */
  spacing: (size: keyof typeof theme.spacing) => {
    return `var(--spacing-${size})`
  },
  
  /**
   * 获取圆角
   */
  radius: (size: keyof typeof theme.borderRadius) => {
    return `var(--radius-${size})`
  },
  
  /**
   * 获取阴影
   */
  shadow: (size: keyof typeof theme.shadows) => {
    return `var(--shadow-${size})`
  },
}

