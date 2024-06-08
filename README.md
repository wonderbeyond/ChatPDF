## 参考资料

* [Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
* [利用LangChain實作ChatPDF](https://edge.aif.tw/express-langchain-chatpdf/)
* [Hands-On with RAG: Step-by-Step Guide to Integrating Retrieval Augmented Generation in LLMs](https://blog.demir.io/hands-on-with-rag-step-by-step-guide-to-integrating-retrieval-augmented-generation-in-llms-ac3cb075ab6f)
* [Using Sentence Transformers at Hugging Face](https://huggingface.co/docs/hub/sentence-transformers)

## 快速开始

### 1. 更新 submodule

```
git submodule update --init --recursive
git submodule foreach git lfs pull
```

### 2. 配置 `~/.config/chatpdf.yaml`

`~/.config/chatpdf.yaml` 用于服务端配置，样例如下：

```yaml
openrouter_api_key: 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
chunk_size_for_summary: 10240
chunk_size_for_summary_overlay: 256
chunk_size_for_corpus: 1024
chunk_size_for_corpus_overlap: 64
```

### 3. 安装服务端依赖并运行

```shell
pip install -r requirements.txt
python -m chatpdf.app  # only for development
```

### 4. 安装 Web 前端依赖并运行

```shell
cd web-ui
npm install
npm run prepare
npm run dev
```

## 技术选型

* LLM 服务: OpenRouter “Mistral 7B Instruct”
* Embedding 生成: sentence-transformers (models: BAAI/bge-large-zh-v1.5)
* 后台服务: FastAPI
* Web UI: SvelteKit + SMUI

## 实现思路

### 1. 摘要生成

1. 利用 pypdf 库将 PDF 文件转换为文本；
2. 将文本分解为多个 Chunks（避免超过 LLM 的上下文长度限制）；
3. 分别将 Chunks 提交给 LLM 服务，获取摘要；
4. 请求 LLM 服务将多个摘要合并为一个摘要。

### 2. 基于 PDF 问答

1. 利用 pypdf 库将 PDF 文件转换为文本；
2. 将文本分解成语料库；
3. 为所有语料生成 Embedding 向量；
4. 把用户问题转换成 Embedding 向量；
5. 利用向量搜索算法，从语料库中检索出相似的语料；
6. 把用户问题和相关语料合并在一起，请求 LLM 生成回答。

## 核心模块（服务端）

* chatpdf.llm_client: 对 LLM 服务进行的封装，便于未来拓展为多服务（或本地模型）支持。
* chatpdf.embedding: Embedding 生成与相似性搜索。
* chatpdf.summarizing: 为文章（特别针对长文）生成摘要的底层工具。
* chatpdf.chat: 维持一个对话的底层支持模块。
* chatpdf.app: Web API 服务模块。

## 已知限制&问题

* 个人缺乏足够的硬件配置来有效运行本地 LLM 模型，考虑以后拓展。
* LLM 支持选用的是 OpenRouter 的免费 API，有流量限制，网络也不太稳定。
  （目前项目处于 Demo 阶段，以后可以考虑拓展）
* 后台程序内部多处使用了磁盘缓存和临时存储，逻辑调整之后可能需要手动清理缓存。
* 后台服务运行时会维护多个对话（Chat）的生命周期，但暂未对对话做持久化存储。
