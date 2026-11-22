# STM32 电控组第一阶段作业

## 完成情况

| 序号 | 任务 | 状态 | 实现说明 |
|:--:|---|---|---|
| 1 | LED 500ms 闪烁（HAL_Delay） | √ | `main.c` 主循环 |
| 2 | LED 500ms 闪烁（不用 HAL_Delay） | √ | 使用Tim1每250ms进行一次更新中断，在中断服务函数中翻转一次GPIO|
| 3 | 按键 EXTI 控制 LED + 20ms 消抖 | √ | `task3` 分支：按键中断 + 20ms 软件消抖 |
| 4 | 提交 GitHub 仓库 | √ | 本仓库 |
| 5 | 选做：短按/长按 | √ | `task5` 分支：短按切换 LED 开关，长按进入/退出闪烁 |
| 6 | 选做：双击 | × | 未做 |

## 备注
- 第一项任务在main这个branch的Core/Src/main.c , 第95到101行代码
- 第二项任务在task2这个branch的Core/Src/main.c 
- 第三项任务在task3
- 第五项任务在task5
