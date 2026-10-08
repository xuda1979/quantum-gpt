import re

with open("research/RESEARCH-REPORT.tex", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove list markers and wrappers
text = re.sub(r'\\begin\{itemize\}', '', text)
text = re.sub(r'\\end\{itemize\}', '', text)
text = re.sub(r'\\begin\{enumerate\}', '', text)
text = re.sub(r'\\end\{enumerate\}', '', text)

# For \item and \item[bold], we want to turn them into inline or paragraph text
# Replace \item \textbf{...} with \par \textbf{...}
text = re.sub(r'\\item\s*\\textbf\{', r'\\par \\textbf{', text)
# Just normal \item -> \par
text = re.sub(r'\\item\s*', r'\\par ', text)

# Remove the previously added renewcommands that visually hid bullets since we removed the lists entirely
text = re.sub(r'\\renewcommand\{\\labelitemi\}\{\}\n', '', text)
text = re.sub(r'\\renewcommand\{\\labelitemii\}\{\}\n', '', text)
text = re.sub(r'\\renewcommand\{\\labelitemiii\}\{\}\n', '', text)
text = re.sub(r'\\renewcommand\{\\labelitemiv\}\{\}\n', '', text)
text = re.sub(r'\\renewcommand\{\\labelenumi\}\{\}\n', '', text)
text = re.sub(r'\\renewcommand\{\\labelenumii\}\{\}\n', '', text)
text = re.sub(r'\\renewcommand\{\\labelenumiii\}\{\}\n', '', text)
text = re.sub(r'\\renewcommand\{\\labelenumiv\}\{\}\n', '', text)

# 2. Fix translationese ("翻译腔") -> Professional academic Chinese
replacements = {
    # Intro / General
    "本章关键结论：": "核心结论：",
    "这意味着": "这表明",
    "由于": "这是因为",
    "非常关键": "至关重要",
    "非常重要": "极其关键",
    "我们当前使用的是": "目前采用",
    "当前实现": "现有实现",
    "很多未通过不是“完全不会”，而是": "大量未通过用例并非由于模型缺乏基本理解，而是因为",
    "差一点": "存在细微偏差",
    "差一个分支": "缺失一个重要分支",
    "但是": "然而",
    "这四个组实验的数据规模、初始化状态与训练预算并不完全相同": "上述四组实验在数据规模、初始状态与计算预算方面存在差异",
    "只有最终 loss 还不够。": "仅评估最终的损失值（Loss）尚显不足。",
    "可以比较它们在中途和末尾的变化": "需要对比其在训练中期与收敛时的差异",
    "四个验证 task 全部是当前模型薄弱点": "该部分验证任务集中考察当前模型的薄弱环节",
    "更重要的是": "值得一提的是",
    "简言之：": "综上所述，",
    "这意味着模型必须在新任务背景和新说话方式下完成迁移。": "这要求模型应对任务设定与表述模式的双重分布偏移，从而完成高难度的综合迁移。",
    "这个边界必须写清楚": "必须明确界定该能力边界",
    "如果不把这些 near-miss 用可学习的 reward 表达出来": "若无法将此类边缘失效（near-miss）转化为可学习的有效强化信号",
    "而不是只看“有没有跑完若干 step”": "而非机械地关注迭代轮次",
    "这就意味着": "这充分说明",
    "它把“训练信号质量”当成一等公民": "本方案将“训练信号的优质性”视作核心",
    "它从测试源或行为提示中抽取若干锚点": "本方法从测试用例或行为指令中主动提取核心锚点",
    "这些反馈作为部分信用写回 reward，可以显著提高 RL 的信号密度。": "此类反馈将被转化为奖赏系统中的局部信用，从而为强化学习提供更为密集的优化信号。",
    "我们当前": "当前项目",
    "这 4 个验证任务": "上述 4 项验证任务"
}

for old, new in replacements.items():
    text = text.replace(old, new)

# Write back
with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(text)
print("Formatting complete")
