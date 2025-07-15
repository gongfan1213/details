将文本任务里面基于token的处理思路，迁移到tool-call当中，

工具调用就是行动token

文本任务:cot=token

用BLEU或者ROUGE等衡量生成文本与黄金答案在token或者字符层面的相似程度

如具体的machine translation  summarization等任务

agent当总


cot=工具调用就是

planning

process accuracy衡量实际toolcalll序列和理想动作的匹配程度，

根据工具调用的反馈结果作为反馈来实现反思，


类似于reasoning model的Long cot当中的wait or but处的反思类似

任务过程节点显现化

应规定流程

