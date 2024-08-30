


## 20240823 
1. 按照科室、医生、病种，完成常规查询
2. 测试所有案例
3. 增加保存功能
## 20240827
1. 完成RAG中的examples添加
2. 完成RAG的所有测试案例

## 20240830
stramlit v6
功能
1. 添加add_example功能
2. 第一次提问为question， 第二次提问为reget_info，
    因此，如果第一个得到了正确回答，
    应该点击重置或刷新页面
    否则再次提问会将 上次的question合并，造成提问不准确
3. 已基本实现所有测试案例的测试工作
4. semantic_result类型检查，不为str，则自动重新提交question查询


##  TODO
