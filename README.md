


## 📸 Swagger 实测截图
![Swagger 截图](./docs/images/swagger-sources.png)  <!-- ./docs/images/swagger-sources.png -->
*调用 /chat 接口返回的 sources 字段包含文档来源和相似度分数 (score)*

## 🐛 真实 Badcase
**问题：** “FastAPI 和 Django 的区别是什么？”
**预期：** 应给出详细技术对比。
**实际：** 模型回答过于简略，遗漏关键点。
**复现步骤：** 登录后调用 /chat，输入上述问题即可复现。

## 🔧 环境变量表
| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://user:pass@host:5432/db` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | `sk-xxx` |
| `BASE_URL` | 服务公网地址 | `https://baisonghao.website` |
| `ENABLE_DEMO_ACCOUNT` | 是否创建演示账号 | `true` |
| `DB_POOL_SIZE` | 连接池大小 | `5` |
| `DB_MAX_OVERFLOW` | 溢出连接数 | `5` |





## RAG 效果评估

本项目对 RAG 检索增强生成效果进行了初步量化验证：

- **测试集构成**：150 条测试问题，其中 100 条来源于文档内（可直接检索），50 条来源于文档外（需模型自身知识）。
- **评估方法**：人工标注答案，对比纯模型（不带检索）和 RAG 增强后的回答准确率。
- **评估结果**：
  - 纯模型准确率：61%
  - RAG 增强准确率：79%
  - 相对提升：18 个百分点（+29.5%）
- **说明**：测试集仍在持续扩充中，当前结果反映 RAG 在减少幻觉方面的有效性。