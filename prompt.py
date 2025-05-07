spec_prompt = """
你是UI设计专家。请参考我的页面描述，描述图片中的页面，给出页面的布局结构、基本颜色样式、页面组件结构，必须全面的描述图片中的所有组件。参考描述如下：
                1. 布局结构
界面采用清晰的后台管理系统布局，左侧为导航栏，主体内容区域采用白色卡片式布局，数据展示清晰直观，整体布局简洁大方。

2. 颜色样式
系统使用蓝色作为主色调，搭配红色、绿色、橙色等辅助色彩，涉及到icon时采用红色党建风格。数据卡片使用纯白背景，图表采用蓝粉对比色展示数据，整体配色专业清爽。


4. 页面组件结构
    4.1 顶部导航
从左到右分别是：
系统名称：党建logo+智慧党建系统
组织概览、一级菜单等导航项，分别是一个页签，组织概览选中时为红色
用户信息及通知
    4.2 左侧菜单
数据概览
异常检测
数据分析
实时监管
数据管理等功能模块
排列紧凑，分别由对应icon和菜单名组成菜单项
    4.3 数据总览区
一行包括5个数据卡片，展示党委、党总支、党支部、党小组、党员等核心数据，5个卡片占满一行
每个卡片包含一个对应图标、标题和数值。卡片背景色为玻璃质感渐变色，色彩透明度较高，卡片本身带有阴影
    4.4 组织架构图
    标题为组织名单
以横向的流程图方式展示组织层级关系
每个流程图节点包含编号、名称
通过虚线连接表示上下级关系
主要内容包括：欧尚汽车党委事业部-长安福特党委-长安马自达党委-江北发动机厂党总支-渝北工厂党小组-研发系统党支部-凯程汽车党小组
    4.5 党员分析区
   一行分为两个主要容器，每个容器包括两个图表
左侧容器包括两个部分，左边为党员性别结构环形图，右边为学历分布环形图
右侧容器包括两个表格，左边党员年龄分布表，右侧是党员年龄表
图表配有清晰的图例和数据标注
    4.6 底部操作栏
保存进度、返回、提交等操作按钮，靠右侧
采用蓝色主按钮突出主要操作
"""

code_prompt = '''你是前端代码专家，精通 React、Ant Design 和 Recharts。请根据页面描述，详细还原页面的功能和样式，生成有效的 `App.js` 代码。**请确保代码中不包含多余的多行字符串（""""）或注释**，并使用内联 CSS 样式，不要引用css外部文件。请分步骤思考，确保代码结构清晰且可直接编译。页面描述如下：

{spec_input}
'''
code_prompt_new = """
You are a front-end code expert, proficient in React, Ant Design, and Recharts. Based on the following page description, **fully** replicate the page's functionality and style, and generate valid `App.js` code. 

**Ensure that every component is fully implemented, and do not omit any part**. 

Please use inline CSS styles and make sure the code structure is clear and directly compilable. 

Think step by step and implement each part of the page incrementally. The page description is as follows:

'''{spec_input}'''

Please return your answer as the following:

```jsx
{generated_code}
"""

spec_prompt_new = """
You are a UI design expert. Describe the layout, color styles, and component structure of the UI page provided by the user. 

Please provide a detailed description of all components in the graphic, including the styles, layout, and colors of each component, ensuring clarity, accuracy, and conciseness. 

Below is an example of a description specification.

1. **Layout Structure**: The interface adopts a backend management layout, with a navigation bar on the left and a white card-based layout for the main content area, displaying data in a clear and simple manner.

2. **Color Styles**: The primary color is blue, with auxiliary colors including red, green, and orange. Icons use a red党建 (party building) style. The card background is pure white, and the charts use a blue-pink contrast for data visualization.

3. **Component Structure**:
   - **Top Navigation**: Includes system name, navigation menus, user information, and notifications.
   - **Left Menu**: Contains modules like data overview, anomaly detection, data analysis, etc., each with a corresponding icon.
   - **Data Overview Section**: One row contains 5 data cards displaying different data, with glass-like gradient backgrounds and shadows on the cards.
   - **Organizational Structure Diagram**: A horizontal flowchart showing the organizational hierarchy, with dashed lines indicating upper-lower relationships.
   - **Party Member Analysis Section**: The left side includes pie charts for gender and education distribution, and the right side includes tables for age distribution and party member ages.
   - **Bottom Action Bar**: Contains action buttons, with the main button highlighted in blue.
"""

spec_v1_dsx = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整的信息，并进行给出尽可能还原的UI描述。请根据提供的UI图片，从以下两个层面全面解析界面内容，并尽可能详细地还原其设计细节与意图：
一、页面级信息分析
请对整个页面进行宏观层面的描述与拆解，包括但不限于以下内容：
整体描述 ： 
    页面的主要功能或目的（例如：展示型页面、操作面板、用户引导流程等）
    页面所处的产品场景或使用情境（移动端/桌面端、B端/C端、高交互性/静态浏览）
页面构成 ： 
    页面模块划分（头部、导航、主内容区、侧边栏、底部等）
    各模块之间的层级关系与视觉权重
    主要的信息流路径与用户动线分析
视觉风格 ： 
    设计风格 ：是拟物、扁平、Material Design、Neumorphism 还是其他自定义风格？
    色彩体系 ：主要使用的主色、辅助色、强调色及其用途；是否使用渐变、透明度变化或状态色？
    整体调性 ：是专业严谨、轻松活泼、科技感、复古风还是其他情绪氛围？
    排版风格 ：对齐方式（左对齐/居中/右对齐）、网格系统的使用情况

二、组件级信息分析
请识别并列出页面中的各个UI组件，并分别从以下三个维度进行描述：
承载信息 ：组件内展示的实际内容（文字、图标、图片、数据图表等）    
承担的功能 ：组件的作用（按钮用于提交？卡片用于跳转？输入框用于数据录入？）
组件的类型 ：包含的基础组件类型（按钮、输入框、标签、下拉菜单、开关等）和复合组件类型（卡片、模态弹窗、列表项、时间轴、步骤条等）

"""

spec_derive_dsx = """
你是一个经验丰富的UI设计师，擅长UI风格和组件布局的衍生设计。
我会向你给出一段UI的文本描述，请你在不改变原有信息结构、功能模块和交互逻辑的前提下，探索新的视觉表达方式与界面组织形式。
你可以改变其中的页面结构、布局、组件类型、视觉风格等（并且请着重改变其中的组件类型），但你仍旧需要输出格式相同的UI描述性文本。
用于衍生的UI文本如下：{spec_input}
"""
