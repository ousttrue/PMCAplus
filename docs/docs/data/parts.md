[文化ヒナゲシ制作所雑記帳 PMCAパーツリストv2.0の仕様について](http://matosus304.blog106.fc2.com/blog-entry-236.html)

```
PMCA Parts list v2.0

SETDIR ./parts/
```

## joint とtype が連結されて木になる

type が頭側の接続で、joint がお尻側の接続になる。

```
[name] セーラー服上半身01(スカート,長袖)
[comment] 普通の長袖セーラー服、縦リボン
[type] root
[path] ub_mt_slr001_l_sk.pmd
[joint] head,hand,lb_sk,body_acce
[pic] ub_mt_slr001_l_sk.png

NEXT
```

根本に固定で `root` joint が存在していて、
`type == root` である parts が選択肢になる。
`セーラー服上半身01(スカート,長袖) ` には4つの `joint` があって、
`joint` 名と一致する `type` の parts を選択できる。

- type=root: セーラー服上半身01(スカート,長袖)
  - joint=head => type=head の parts を接続できる
  - joint=hand => type=hand の parts を接続できる
  - joint=lb_sk => type=lb_sk の parts を接続できる
  - joint=body_acce => type=body_acce の parts を接続できる

## class PARTS

```py
@dataclasses.dataclass
class PARTS:
    name: str
    joint: list[str]
    path: str = ""
    comment: str = ""
    type: list[str] = dataclasses.field(default_factory=list)
    props: dict[str, str] = dataclasses.field(default_factory=dict)
```

## Model tab で parts 選択ができる
