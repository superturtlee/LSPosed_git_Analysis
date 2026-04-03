# LSPosed Repository Analysis Summary – Based on the Last Open-Source Version

## 1. Xposed → EdXposed → LSPosed: The Betrayed Open-Source Legacy

The evolution of Android hooking frameworks is fundamentally a history of open-source collaboration.

- **Xposed Framework** (by rovo89) pioneered this domain under **GPLv2**, requiring all derivatives to remain open-source. Its success was built entirely on open collaboration: developers worldwide contributed modules, reported issues, and submitted fixes.

- **EdXposed** (by RikkaW, solarwarez, et al.) inherited this legacy. Facing Android compatibility challenges, the team maintained open-source principles on GitHub, attracting significant community contributions. Without openness, EdXposed couldn't have adapted to Riru/Zygisk.

- **LSPosed** initially emerged as a lightweight fork of EdXposed, continuing the GPL tradition. Early versions accepted external pull requests and community feedback. However, the team later closed the source and conducted "code cleansing."

**This action shattered a decade-long open-source heritage.** Open-source isn't a switchable "technical option" but a legal/moral commitment to the community. LSPosed's closed-source move violates both the GPL license and the open-source ethos.

## 2. Why Open-Source Matters: An Inviolable Tradition

Open-source significance extends beyond code visibility. In the Xposed ecosystem, it embodies:
1. **Freedom & Trust**: Users audit code to ensure no backdoors/privacy violations. Closed-source destroys this trust.  
2. **Collaboration & Efficiency**: EdXposed built on Xposed; LSPosed built on EdXposed. Closed-source severs this chain.  
3. **Public Knowledge**: Openness enabled collective learning of Android internals. Closure re-locks this knowledge.  
4. **GPL Betrayal**: As a derivative of GPL code, LSPosed's closure violates the license’s core principle.

## 3. Team Actions vs. Open-Source Community

Analysis of the final public codebase (2024) reveals critical issues:

### 3.1 High External Contribution Rate
- **Main branch**: 2,680 commits (84.4% external)  
- **Full repository**: 2,754 commits (83.7% external)  
**Conclusion**: LSPosed privatized community-built foundations.

### 3.2 Dubious "Code Cleansing"
- **Technical Feasibility**: Removing all externally contributed code would require line-by-line audits of 10,000+ lines – a near-impossible task prone to errors.  
- **Burden of Proof**: The team must proactively demonstrate independence (e.g., design docs, audit reports) – not just claim "cleansing."  
- **License Evasion**: The sole purpose was circumventing GPL’s "derivative works" clause, violating the open-source social contract.

### 3.3 Legal & Ethical Violations
- **GPL Non-Compliance**: As an EdXposed derivative (itself GPL), LSPosed remains bound by GPLv2. Closure breaches its terms.  
- **Community Betrayal**: Accepting years of community help before closing source creates a **chilling effect**, discouraging future contributions.

## 4. GPL-to-Closed-Source: Damaging Consequences
### 4.1 Direct Community Harm
- Contributors may abandon similar projects fearing code privatization.  
### 4.2 Ecosystem Damage
- Sets a dangerous precedent for "cleanse → close" tactics, undermining GPL’s protective intent.  
- Risks turning open-source into corporate free R&D without community benefit.  
### 4.3 Legal & Industry Risks
- **Litigation Exposure**: Original contributors could sue for infringement if cleansed code retains non-trivial GPL logic (per *Oracle v. Google*).  
- **Erosion of GPL Authority**: Weakens license enforceability industry-wide.

## 5. Critical Assessment
- **Legality**: Highly questionable without cleansing transparency.  
- **Ethics**: Exploited community goodwill (84% external code → closure = **burning bridges**).  
- **Open-Source Spirit**: Violates "give back" principles, damaging team reputation.

## 6. Conclusions & Recommendations
### Conclusions
- LSPosed’s closure likely **violates GPLv2** after high external contributions.  
- Actions damaged trust and set a harmful precedent.  
- Broke the **Xposed → EdXposed → LSPosed** open-source chain.  

### Recommendations
1. **Transparency**: Release cleansing methodology and third-party audits.  
2. **Restore Openness**: Revert to GPL or fully rewrite under Apache 2.0.  
3. **Rebuild Trust**: Public apology and governance via foundations (e.g., Linux Foundation).  

## 7. How Users Can Defend Real Open-Source
### 7.1 Use Ethical Alternatives
- Adopt **genuine open-source forks** like [JingMatrix/Vector](https://github.com/JingMatrix/Vector) (GPL-compliant).  
- Verify licenses and activity before use.  
### 7.2 Deny Visibility to Closed Projects
- **Unstar LSPosed’s archived repositories** on GitHub.  
- Avoid promoting "gateway" repos linking to closed sources.  
### 7.3 Participate Actively
- Test/document ethical alternatives.  
- Contribute via translations, tutorials, or issue reports.  
### 7.4 Vote with Actions
- Educate others on GPL importance.  
- Redirect users to compliant projects.  
### 7.5 Recognize "Fauxpen-Source"
- Avoid projects with non-OSI licenses or sudden closure without proof of rewrite.  

---  
**Final Note**  
LSPosed’s closure shattered a decade of trust. **Every GitHub star, download, and recommendation is a vote for open-source integrity.** Support ethical forks, reject betrayal, and protect the collaborative future of Android development.


# LSPosed 仓库分析总结 —— 基于最后一个开源版本

## 一、Xposed → EdXposed → LSPosed：被背叛的开源传统

Android 平台上的 Hook 框架发展史，本质上是一部开源协作的进化史。

- **Xposed Framework**（rovo89 开发）是这一领域的开创者。它基于 **GPLv2** 许可证发布，允许任何人自由使用、修改和分发，但要求所有衍生作品也必须保持开源。Xposed 的成功完全建立在开放共享之上：无数开发者贡献模块、报告问题、提交补丁，共同塑造了一个活跃的生态。

- **EdXposed**（RikkaW、solarwarez 等）接过了 Xposed 的火炬。在 Android 高版本兼容性日益复杂的情况下，EdXposed 团队坚持开源原则，将项目托管在 GitHub，吸引了大量社区贡献。可以说，没有开源就没有 EdXposed 对 Riru、Zygisk 等新技术的适配。

- **LSPosed** 最初作为 EdXposed 的一个更轻量、更现代的分支出现，同样延续了 GPL 开源的传统。早期版本完全公开，接受外部 Pull Request，社区反馈积极。然而，后期团队却选择将项目闭源，并进行了所谓的“代码清洗”。

**这一行为割裂了长达十年的开源传承**：Xposed 点燃的火种，EdXposed 传递的火炬，在 LSPosed 手中被熄灭。开源不是一种可以随意切换的“技术选择”，而是一份对社区的法律和道德承诺。LSPosed 的闭源，不仅是对 GPL 许可证的违背，更是对整个开源传统的背叛。

## 二、开源的意义：为何这一传统不容践踏

开源软件的意义远不止“代码可见”。在 Xposed 生态中，开源的价值观体现为：

1. **自由与信任**：用户可以审计代码，确保 Hook 框架不会窃取隐私或植入后门。闭源后，这种信任基础荡然无存。
2. **协作与避免重复造轮子**：EdXposed 继承了 Xposed 的代码，LSPosed 又继承了 EdXposed 的改进，每一代都站在前人的肩膀上。闭源切断了这种协作链。
3. **知识的公共积累**：Hook 框架涉及 Android 底层机制，开源让无数开发者学习、改进、传播相关知识。闭源则将这些知识重新锁入黑箱。
4. **GPL精神的背叛**：GPL 保证“衍生作品必须开源”。LSPosed 基于 GPL 代码开发，其闭源行为直接破坏了这一开源精神（作为衍生作品，最终达成闭源）。

## 三、团队行为与开源社区的冲突

在分析 2024 年公开的最后一份代码库及相关提交历史后，我们发现 LSPosed 团队在项目外部代码贡献占比极高的情况下，进行了大规模代码清洗，并最终将项目闭源。这一行为引发了以下关键问题：

### 1. **外部代码的历史高占比**

根据对 `main_branch` 和 `whole_repo` 的完整提交统计（时间跨度 2014‑01 至 2024‑01，已排除机器人账号）：

- **主分支**：总提交 2680 次，其中外部贡献者提交 2262 次，**外部提交占比 84.4%**。
- **全仓库**：总提交 2754 次，外部提交 2304 次，**外部提交占比 83.7%**。

这些数据清晰表明：**LSPosed 项目的基础代码和早期演进高度依赖外部社区贡献**。团队后来的闭源行为，本质上是将社区集体努力的成果私有化。

### 2. **代码清洗的复杂性与合法性疑云**

- **工程难度**：假定团队确实完成了“代码清洗”——即识别并替换所有由外部贡献者编写的代码行——这需要逐行审计数万行代码，并重写所有受 GPL 传染的部分。即便技术上可行，其工作量与成本也极为巨大，且极易遗漏。
- **独立证明责任**：即使完成了清洗，团队仍需**主动证明**新代码的独立原创性，而非依赖“已清洗”的断言。若无法提供可验证的证据（如完整的设计文档、开发过程记录、第三方审计报告），则原始贡献者仍可主张知识产权侵权。
- **规避许可证的实质**：代码清洗的唯一目的就是规避 GPL 许可证的“衍生作品必须开源”条款。这种行为不仅技术上难以自证清白，更在精神上背离了开源社区“共享改进”的基本契约。

### 3. **闭源行为的法律与道德双重问题**

- **GPL 的传染性**：LSPosed 源自 EdXposed，而 EdXposed 本身基于 Xposed Framework（GPLv2）。根据 GPL 的“衍生产品”定义，除非 LSPosed 完全从零独立编写（且不依赖任何 GPL 代码的记忆或逻辑），否则整个项目应受 GPL 约束。闭源行为**直接违反 GPL 的核心条款**。
- **道德层面的背弃**：开源社区贡献代码时，默认期望项目遵守其所声明的许可证。团队在享受了数年外部贡献后，通过清洗代码转而闭源，是对贡献者信任的严重滥用。这种行为会**寒蝉效应**，使开发者不愿再向类似项目投入精力。

## 四、GPL 变更为闭源许可的恶劣影响

### 1. **对开源社区的直接打击**

- 贡献者可能会因担心自己的代码被用于闭源项目而**减少对同类框架的贡献**，尤其是那些由单一商业实体或小团队主导的项目。

### 2. **破坏开源生态的良性循环**

- GPL 的设计初衷正是**防止开源代码被闭源化**，从而保证用户和开发者始终拥有修改与再分发的自由。LSPosed 的行为相当于绕过了这一保护机制，为其他意图闭源的项目提供了“清洗代码 → 变更许可证”的**危险先例**。
- 如果这种做法被广泛效仿，开源软件可能沦为商业公司的“免费原材料”，而社区无法享受改进后的成果，最终削弱整个开源生态的可持续性。

### 3. **法律风险与行业示范效应**

- **法律风险**：原始贡献者（尤其是 EdXposed 时期的作者）仍有权对 LSPosed 提起诉讼。即使团队声称代码已清洗，但如果新代码中存在与原 GPL 代码相似的非平凡结构、算法或逻辑，仍可能构成侵权。历史上（如 **Oracle v. Google** 关于 API 结构的判例）表明，此类诉讼旷日持久且结果难料。
- **负面示范**：作为首例从 GPL 变更为闭源许可的知名 Xposed 框架分支，LSPosed 的行为可能被其他公司或组织用作“合法但不合德”的模板。这将**削弱 GPL 的法律威慑力**，导致开源名存实亡。

## 五、评价

### 1. **法律合规性：高度可疑**

- 由于 LSPosed 从未公开其代码清洗的具体过程及独立性证明，外界无法判断其是否真正脱离了 GPL 的管辖。闭源行为本身已与 GPL 的核心要求直接冲突。
- 即便在“洁净室设计”案例中，独立重写也需要严格的隔离和文档记录，而 LSPosed 团队并未提供任何此类证据。

### 2. **道德责任：严重失当**

- 开源项目的成功离不开社区的无偿贡献。LSPosed 团队在项目早期完全依赖EdxPosed代码，后期虽有一定内部开发，但整体外部提交占比仍超过 84%。闭源行为无异于**过河拆桥**，严重违背了开源协作的伦理基础。

### 3. **对开源精神的背离**

- 开源的核心理念是**“我为人人，人人为我”**。LSPosed 团队的行为表明其只愿索取（利用社区代码），不愿回报（将改进回馈社区）。这完全背离了开源精神，损害了团队在技术社群中的声誉。

## 六、结论与建议

### 结论

- LSPosed 项目在外部代码贡献占比极高的前提下，通过代码清洗并闭源的行为，**极有可能违反了 GPL 许可证的强制性条款**，并对开源社区和行业生态造成了实质性的负面影响。
- 无论技术清洗是否完成，其行为在法律和道德上均存在重大争议，且已对开源信任体系造成破坏。
- 更深远的是，它割裂了 **Xposed → EdXposed → LSPosed** 长达十年的开源传统，背叛了无数贡献者的信任，给后来者树立了恶劣榜样。

### 建议

1. **公开透明，接受审计**  
   - 团队应完整公布代码清洗的技术方案、修改前后对照、以及第三方知识产权审计报告。  
   - 与 EdXposed 及其他主要贡献者主动沟通，争取谅解或达成许可协议。

2. **回归开源，遵守 GPL**  
   - 最直接且负责任的作法是将项目**重新开源**，并继续使用 GPL 许可证。  
   - 若确有必要闭源，应**彻底重写所有核心模块**，并采用非传染性许可证（如 Apache 2.0），同时确保不引用任何 GPL 代码的记忆或结构。

3. **重建社区信任**  
   - 团队应公开道歉，并承诺未来严格遵守开源许可证。  
   - 积极参与开源基金会（如 Linux Foundation、OpenAtom）的项目治理，以实际行动弥补信任裂痕。


## 七、普通人如何支持真正的开源

LSPosed 的闭源事件不仅是法律和道德的教训，也是对普通用户的警示。**每一位使用开源软件的人，都可以用简单的行动捍卫开源的诚信**。以下是一些具体、可操作的建议：

### 1. **优先使用诚信的开源分支**

- 对于 LSPosed 的替代方案，应选择那些**继续遵守 GPL 许可证、保持代码公开、接受社区贡献**的健康分支。  
- **推荐项目**：例如 [JingMatrix/Vector](https://github.com/JingMatrix/Vector) —— 一个真正开源、持续维护的 LSPosed 衍生项目，严格遵循 GPL 精神。
- 使用前请检查仓库的许可证声明、最近提交记录、以及是否有明确的“开源承诺”。避免使用任何“只读归档”、“不再更新”或已闭源的版本。

### 2. **不要给背离开源的项目增加热度**

- **停止为原 LSPosed 闭源仓库或其只读归档镜像加星标（star）**。GitHub 的星标是社区热度的重要指标，加星意味着“推荐”或“认可”。给一个已经闭源、背离 GPL 的项目加星，等于间接鼓励其行为。
- **如果之前已经加过星，请立即取消星标**。这不仅是个人态度的表达，也能降低该项目在搜索结果中的权重，减少对普通用户的误导。
- 同样，避免为任何形式的“引流仓库”（例如仅用来跳转到闭源下载页面的归档镜像）点赞、转发或推荐。

### 3. **积极参与开源社区**

- **使用并测试开源分支**：下载、安装、使用诚信的开源项目，发现问题后在 GitHub Issues 中友好报告。
- **贡献力所能及的部分**：即使不懂编程，也可以帮助改进文档、翻译界面、撰写使用教程、在论坛中解答其他用户的问题。
- **向开发者表达感谢**：给真正开源的仓库加星、打赏（如果项目接受赞助）、或者仅仅在社交媒体上分享推荐，都是对诚信开发者的正向激励。

### 4. **用脚投票，传播理念**

- 在技术社区、群聊、博客中，主动宣传“为什么开源许可证很重要”，解释 GPL 的意义，帮助更多人理解闭源行为对生态的伤害。
- 当遇到有人推荐闭源或违规项目时，礼貌地指出问题，并引导他们转向合规的开源替代品。
- **记住：每一次选择都是投票**。选择开源分支、拒绝闭源软件，就是对背信行为的有力回应。

### 5. **警惕“伪开源”陷阱**

- 有些项目虽然代码可见，但使用非标准许可证、禁止商业使用、或要求签署额外协议，这本质上是“源码可用”而非“开源”。真正的开源必须符合 OSI（开源促进会）定义。
- 如果一个项目突然从 GPL 改为闭源，且没有提供完整的独立重写证据，请立刻停止使用，并通知其他用户。

---

**结语**  
LSPosed 团队的行为不仅损害了自身声誉，更给整个开源社区敲响了警钟：**许可证不是装饰，社区信任一旦破碎，很难复原**。从 Xposed 到 EdXposed 再到 LSPosed，这条开源之路本该越走越宽，却因一次闭源决定而骤然断裂。  
但危机也意味着觉醒。每一个普通用户都可以通过自己的选择，支持那些真正诚信的开源项目，抵制背信行为。**用星标投票，用使用支持，用传播教育**——这才是普通人维护开源未来的最好方式。希望后来者以此为戒，共同守护开源的共享与自由。
