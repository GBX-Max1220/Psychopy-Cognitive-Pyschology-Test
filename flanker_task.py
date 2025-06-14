from psychopy import visual, core, event, gui, data
import numpy as np
import os
import csv
from datetime import datetime

# 实验信息
exp_info = {
    '参与者ID': '',
    '年龄': '',
    '性别': ['男', '女', '其他'],
    '惯用手': ['右手', '左手', '双手']
}

# 显示对话框收集参与者信息
dlg = gui.DlgFromDict(dictionary=exp_info, title='Flanker侧抑制任务')
if not dlg.OK:
    core.quit()  # 如果用户取消，则退出程序

# 创建数据文件夹
data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# 创建输出文件名
date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"{data_folder}/flanker_task_{exp_info['参与者ID']}_{date_str}.csv"

# 设置窗口
win = visual.Window(
    size=(1024, 768),
    fullscr=True,
    monitor="testMonitor",
    color=[-1, -1, -1],
    units="pix"
)

# 创建文本刺激
instruction_text = visual.TextStim(
    win=win,
    text="""
    欢迎参加Flanker侧抑制任务实验！
    
    在实验中，您将看到一系列字母。请专注于中央的字母，并根据中央字母按下相应的按键：
    
    如果中央字母是 H 或 K，请按 F 键
    如果中央字母是 S 或 C，请按 J 键
    
    请忽略周围的字母，只关注中央字母。
    
    实验将分为多个试次，每次试次开始时会出现一个"+"符号，然后会出现字母。
    请在看到字母后尽快做出反应。
    
    请在确认理解后，按空格键开始实验。
    """,
    height=24,
    color=[1, 1, 1],
    wrapWidth=800
)

fixation = visual.TextStim(
    win=win,
    text="+",
    height=30,
    color=[1, 1, 1]
)

stim_text = visual.TextStim(
    win=win,
    text="",
    height=40,
    color=[1, 1, 1]
)

feedback_text = visual.TextStim(
    win=win,
    text="",
    height=30,
    color=[1, 1, 1]
)

# 实验结束文本
end_text = visual.TextStim(
    win=win,
    text="""
    实验已完成！
    
    感谢您的参与！
    
    本实验代码由郭佰鑫开发
    如有问题请联系微信: MaxGBX
    """,
    height=24,
    color=[1, 1, 1],
    wrapWidth=800
)

# 实验条件
conditions = [
    # 无关条件 (H/K)
    {"stimulus": "SSSHSSS", "correct_key": "f", "condition": "incompatible"},
    {"stimulus": "SSSKSSS", "correct_key": "f", "condition": "incompatible"},
    
    # 相关条件 (S/C)
    {"stimulus": "SSSCSSS", "correct_key": "j", "condition": "compatible"},
    {"stimulus": "SSSSSSS", "correct_key": "j", "condition": "compatible"},
    
    # 无干扰条件 (C)
    {"stimulus": "C", "correct_key": "j", "condition": "no_distractor"},
    {"stimulus": "H", "correct_key": "f", "condition": "no_distractor"}
]

# 复制条件以创建多个试次
trials = conditions * 5  # 每种条件重复5次
np.random.shuffle(trials)  # 随机打乱试次顺序

# 显示指导语
instruction_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

# 实验开始
results = []

for trial in trials:
    # 清空按键缓冲区
    event.clearEvents()
    
    # 呈现注视点 (1-2秒随机)
    fixation.draw()
    win.flip()
    fixation_time = np.random.uniform(1.0, 2.0)
    core.wait(fixation_time)
    
    # 呈现刺激
    stim_text.setText(trial["stimulus"])
    stim_text.draw()
    win.flip()
    
    # 记录刺激呈现时间
    stim_onset = core.getTime()
    
    # 设置刺激呈现时间为1秒
    core.wait(1.0)
    
    # 清空屏幕
    win.flip()
    
    # 等待反应，设置超时时间
    response = None
    rt = None
    keys = event.getKeys(keyList=['f', 'j', 'escape'], timeStamped=True)
    
    if keys:
        for key, press_time in keys:
            if key == 'escape':
                core.quit()  # 用户选择退出
            else:
                # 只记录第一个有效按键
                if response is None:
                    response = key
                    rt = press_time - stim_onset
    
    # 判断是否正确
    correct = response == trial["correct_key"] if response else False
    
    # 呈现反馈
    if response:
        if correct:
            feedback_text.setText("√")
            feedback_text.setColor([0, 1, 0])  # 绿色
        else:
            feedback_text.setText("×")
            feedback_text.setColor([1, 0, 0])  # 红色
    else:
        feedback_text.setText("请更快反应！")
        feedback_text.setColor([1, 1, 0])  # 黄色
    
    feedback_text.draw()
    win.flip()
    core.wait(0.5)
    
    # 记录结果
    results.append({
        "trial": len(results) + 1,
        "condition": trial["condition"],
        "stimulus": trial["stimulus"],
        "response": response,
        "rt": rt if rt else float('nan'),
        "correct": correct
    })
    
    # 试次间间隔
    win.flip()
    core.wait(0.5)

# 导出数据
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["trial", "condition", "stimulus", "response", "rt", "correct"])
    writer.writeheader()
    writer.writerows(results)

# 显示实验结束信息
end_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

# 关闭窗口
win.close()
core.quit()
