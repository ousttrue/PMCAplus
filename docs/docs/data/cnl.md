# cnl ファイル

一体分の組立情報。
partslist, materiallist, transformlist を足したような感じ。

## header

```
PMCA sample1
PMCAv0.0.6 sample1


```

## PARTS

木構造になっている。
Childで子が始まり、Parentで終わる。

```
PARTS
[Name] セーラー服上半身01(スカート,半袖)
[Path] ./parts/ub_mt_slr001_s_sk.pmd
[Child]
[Name] 顔f01
[Path] ./parts/head_mt001_1.pmd
[Child]
[Name] 前髪01
[Path] ./parts/hair_mf1_mt001.pmd
[Child]
[Name] 後髪02
[Path] ./parts/hair_mr1_mt002.pmd
[Child]
None
[Parent]
[Parent]
None
None
[Parent]
[Name] 腕01b
[Path] ./parts/arm1_mt001b.pmd
[Child]
None
[Parent]
[Name] スカート下半身01(スカート)
[Path] ./parts/lb_sk_mt001.pmd
[Child]
[Name] 靴_ローポリ
[Path] ./parts/shoes1_mt01.pmd
[Child]
None
[Parent]
[Parent]
None
[Parent]
```

## MATERIAL

```
MATERIAL
[Name] mt_shoes1
[Sel] 外履き
NEXT
[Name] mt_sock1
[Sel] 白
NEXT
[Name] mt_hair
[Sel] 青色01
NEXT
[Name] mt_slr1_s
[Sel] 紺色
NEXT
[Name] mt_ribbon1
[Sel] 赤
NEXT
[Name] mt_blz1_l
[Sel] ストライプネクタイ
NEXT
[Name] mt_slr1_l
[Sel] 黒地白襟
NEXT
[Name] mt_eye
[Sel] 青
NEXT
[Name] mt_pants
[Sel] ブルマ
NEXT
[Name] mt_skirt1
[Sel] 紺色
NEXT
```

## TRANSFORM

```
TRANSFORM
[Scale] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
BONES
[Name]
[Length] 1.000000
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name]
[Length] 1.000000
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 上半身
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 右腕
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 右腕捩
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 右ひじ
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 右手捩
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 左腕
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 左腕捩
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 左ひじ
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 左手捩
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 下半身
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 右足
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 右ひざ
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 左足
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 左ひざ
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 右ｽｶｰﾄ前
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 右ｽｶｰﾄ後
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 左ｽｶｰﾄ前
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
NEXT
[Name] 左ｽｶｰﾄ後
[Length] 0.905785
[Thick] 1.000000
[Pos] 0.000000 0.000000 0.000000
[Rot] 0.000000 0.000000 0.000000
```
