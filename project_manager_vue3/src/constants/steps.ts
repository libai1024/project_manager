/**
 * 默认步骤常量
 *
 * 定义项目创建时的默认步骤列表
 */

/**
 * 默认步骤列表
 */
export const DEFAULT_STEPS: string[] = [
  '已接单',
  '已规划',
  '硬件完成',
  '软件完成',
  '软硬调试',
  '实物验收',
  '实物邮寄',
  '论文框架',
  '论文初稿',
  '论文终稿',
  '答辩辅导',
  '毕设通过',
  '已结账'
]

/**
 * 步骤序号映射（用于快速查找）
 */
export const STEP_INDEX_MAP: Record<string, number> = DEFAULT_STEPS.reduce(
  (acc, step, index) => {
    acc[step] = index
    return acc
  },
  {} as Record<string, number>
)

/**
 * 获取步骤序号
 * @param stepName 步骤名称
 * @returns 序号（从0开始），未找到返回-1
 */
export function getStepIndex(stepName: string): number {
  return STEP_INDEX_MAP[stepName] ?? -1
}

/**
 * 检查是否为最后一个步骤
 * @param stepName 步骤名称
 * @returns 是否为最后一个
 */
export function isLastStep(stepName: string): boolean {
  return stepName === DEFAULT_STEPS[DEFAULT_STEPS.length - 1]
}

/**
 * 检查是否为结账步骤
 * @param stepName 步骤名称
 * @returns 是否为结账步骤
 */
export function isSettlementStep(stepName: string): boolean {
  return stepName === '已结账'
}
