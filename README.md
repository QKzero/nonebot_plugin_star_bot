# star_bot
基于NoneBot2的娱乐和功能性插件。

## 关于
- 此项目作为Q群娱乐和功能性插件，仅作学习交流使用。
- 此项目可能会持续有更新或修复，包括对有的功能推倒重做。
- 资源文件位于项目根目录（若没有则会自动生成文件夹），为了避免不必要的麻烦，请自行准备素材。

## 功能列表
### 已实现的功能
- [x] 东方DOTS赛后数据分析
- [x] 今日老婆
- [x] 车万老婆
- [x] 戳一戳和开头at发送表情

## 配置相关
- 需要全局配置项
```python
star_group: List[int] # 允许使用的群号
```
- `项目根目录/star_bot/emoji/` 放置用于戳一戳和at的表情素材
- `项目根目录/star_bot/touhou_wife/picture` 放置车万老婆所使用的美术素材，名字改为角色名字，若不使用可忽略。