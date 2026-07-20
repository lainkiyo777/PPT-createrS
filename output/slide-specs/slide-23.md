# Slide 23 Specification

page_type: action-plan
title: 下一步聚焦鲁棒性、闭环和考核口径
key_message: 近期应补充多 seed 和分层诊断并打通两阶段，随后对齐 ±25% 偏差、低出力免考核与费用口径。
layout: 左侧用三条并行但不同长度的行动跑道表示“模型鲁棒性、闭环验证、考核口径”；每条只放 2–3 个动作，最右侧汇聚到“现场可验证”。
visual_style: YCFD-IMAGE-DECK-v2；深蓝行动路线，青绿代表技术任务，琥珀代表考核规则；画面有前进感，避免甘特图小字。
image_prompt: "Use case: productivity-visual. 16:9 Chinese action-plan slide. Exact title: ‘下一步聚焦鲁棒性、闭环和考核口径’. Three forward tracks ending at ‘现场可验证’: Track 1 ‘模型鲁棒性｜多随机种子｜分 horizon / 风机 / 风速 / 风向诊断’; Track 2 ‘闭环验证｜clean checkpoint 回评 full｜阶段一接入 MoE｜重算 MAE / RMSE / R²’; Track 3 ‘考核口径｜±25% 合格率｜低出力 3% 免考核｜偏差电量与费用’. Dark navy, cyan technical tracks, amber assessment track, large Chinese labels, no tiny Gantt chart, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 短期计划、中期计划和考核口径
    editable: false
dependencies:
  - slide-22
qa_checklist:
  - 考核口径必须逐字显示“±25% 合格率”；数学符号必须是加减号“±”，禁止误写为“+25%”或“-25%”
  - 三类行动与具体任务准确
  - ±25% 和低出力 3% 口径准确
  - 行动顺序可执行
  - 无不必要的项目管理小字

